"""Safe trace receipts. Raw syscall arguments remain private and are never copied."""
import hashlib
import ipaddress
import json
from pathlib import Path
import re
import time
import threading
import os
import subprocess


class ProcessMap:
    """Only UID, TID/TGID/parent and known executable basenames; no cmdline/env."""
    def __init__(self, uid):
        self.uid=uid; self.rows={}; self.exes={}; self.failed=False; self.done=threading.Event()
        self.thread=threading.Thread(target=self.monitor,daemon=True)
        self.thread.start()

    def monitor(self):
        while not self.done.is_set():
            try:
                for proc in Path('/proc').iterdir():
                    if not proc.name.isdigit(): continue
                    try:
                        if proc.stat().st_uid != self.uid: continue
                        if proc.name not in self.exes:
                            result=subprocess.run(['sudo','readlink',str(proc/'exe')],capture_output=True,text=True,timeout=2)
                            if result.returncode:
                                if proc.exists(): self.failed=True
                                continue
                            self.exes[proc.name]=Path(result.stdout.strip()).name
                        executable=self.exes[proc.name]
                        for task in (proc/'task').iterdir():
                            tid=int(task.name)
                            if tid in self.rows: continue
                            fields=dict(line.split(':',1) for line in (task/'status').read_text().splitlines() if ':' in line)
                            self.rows[tid]={'tid':tid,'tgid':int(fields['Tgid']),'parent_pid':int(fields['PPid']),
                                'uid':int(fields['Uid'].split()[0]),'first_seen_ms':int(time.time()*1000),
                                'executable':executable if executable in {'node','workerd','strace'} else 'other_executable'}
                            if len(self.rows)>1024: raise RuntimeError('process-map limit')
                    except (FileNotFoundError,ProcessLookupError): continue
            except Exception:
                self.failed=True; return
            self.done.wait(.1)

    def stop(self):
        self.done.set(); self.thread.join(timeout=2)
        return {'processes':list(self.rows.values()),'read_failed':self.failed,'monitor_stopped':not self.thread.is_alive()}

SAFE_NAMES = {'localhost', 'registry.npmjs.org', 'api.cloudflare.com', 'cloudflare.com',
              'www.cloudflare.com', 'dash.cloudflare.com', 'developers.cloudflare.com', 'hashed_hostname'}
SAFE_MODULES = {'node', 'workerd', 'libc.so.6', 'libuv.so.1', 'dns_trace.so', 'other_module', 'unknown'}
CALLS = {'connect', 'sendto', 'sendmsg', 'sendmmsg', 'getsockopt'}


def sanitize_dns(text):
    rows=[]
    for line in text.splitlines():
        v=json.loads(line)
        common={'type','pid','timestamp_ms','hostname','hostname_sha256'}
        extra={'tid','module','module_offset'} if v.get('type')=='native_getaddrinfo' else {'callers'}
        assert v.get('type') in {'native_getaddrinfo','node_dns_lookup'} and set(v)==common|extra, 'DNS schema'
        assert v['hostname'] in SAFE_NAMES and re.fullmatch('[a-f0-9]{64}',v['hostname_sha256']), 'DNS name'
        assert all(type(v[k]) is int and v[k]>=0 for k in ['pid','timestamp_ms']), 'DNS identity'
        if 'callers' in v:
            assert len(v['callers'])<=6
            for c in v['callers']:
                assert set(c)=={'file','file_sha256','line','column'} and c['file'] in {'wrangler/wrangler-dist/cli.js','wrangler/dist/cli.js','miniflare/dist/src/index.js','undici/lib/core/connect.js','other_file'}
                assert re.fullmatch('[a-f0-9]{64}',c['file_sha256'])
                assert type(c['line']) is int and type(c['column']) is int
        else:
            assert v['module'] in SAFE_MODULES and type(v['tid']) is int and type(v['module_offset']) is int
        rows.append(v)
    return rows


def sanitize_syscalls(text):
    rows=[]; unparsed=0; pending={}
    for line in text.splitlines():
        # No raw line, request bytes, Unix path, comm string or arbitrary error text is emitted.
        m=re.match(r'^(\d+)(?:<([^>]+)>)?\s+(\d+\.\d+)\s+(.+)$',line)
        if not m:
            if line.strip(): unparsed+=1
            continue
        pid,comm,stamp,body=m.groups();pid=int(pid)
        if body.startswith('--- ') or body.startswith('+++ '): continue
        if '<unfinished ...>' in body:
            pending[pid]=(comm,stamp,body.replace('<unfinished ...>',''));continue
        resumed=re.match(r'<\.\.\. (\w+) resumed>(.*)',body)
        if resumed:
            if pid not in pending: unparsed+=1;continue
            comm,stamp,prefix=pending.pop(pid);body=prefix+resumed.group(2)
        c=re.match(r'(\w+)\((0x[0-9a-f]+|[0-9]+)',body)
        if not c or c[1] not in CALLS: unparsed+=1;continue
        call,fd=c[1],int(c[2],0);address=None;port=None
        a=re.search(r'sin_addr=inet_addr\("([0-9.]+)"\)',body)
        a6=re.search(r'inet_pton\(AF_INET6, "([0-9a-fA-F:]+)"',body)
        p=re.search(r'sin(?:6)?_port=htons\((\d+)\)',body)
        if a or a6:
            address=str(ipaddress.ip_address((a or a6)[1]));port=int(p[1]) if p else None

        result=re.search(r'\)\s+=\s+(-?(?:0x[0-9a-f]+|[0-9]+))(?:\s+([A-Z][A-Z0-9_]+))?',body)
        if not result: unparsed+=1;continue
        # Non-IP/unknown-FD events are counted, not silently treated as healthy.
        row={'tid':pid,'comm':comm if comm in {'node','workerd','strace'} else 'other_or_unknown',
             'timestamp_ms':int(float(stamp)*1000),'syscall':call,'fd':fd,
             'address':address,'port':port,'return_value':int(result[1],0),'errno':result[2],
             'external_delivery_evidence':'not_established',
             'destination_source':'explicit_sockaddr' if address is not None else 'not_attributed'}
        so=re.search(r'SOL_SOCKET, SO_ERROR, \[([A-Z][A-Z0-9_]+|0)\]',body)
        if so: row['sockopt_error']=so[1] if so[1] in {'0','ECONNREFUSED','ETIMEDOUT','EHOSTUNREACH','ENETUNREACH','EPERM','EACCES'} else 'other_error'
        if address is not None: row['loopback']=ipaddress.ip_address(address).is_loopback
        rows.append(row)
    return {'events':rows,'unparsed_lines':unparsed,'unfinished_calls':len(pending),
            'syscall_count_is_not_packet_or_unique_connection_count':True,
            'success_return_is_not_external_delivery_proof':True}


def collect(label, started_ms, counters_before, counters_after):
    root=Path('/tmp/g01-runtime');parts={}
    for suffix in ['strace','node-dns','native-dns']:
        p=root/(label+'-'+suffix+'.log')
        assert p.is_file() and p.stat().st_size<8_000_000, 'trace missing/over bound: '+suffix
        parts[suffix]=subprocess.run(['sudo','cat',str(p)],capture_output=True,text=True,check=True,timeout=10).stdout
    v={'phase':label,'started_ms':started_ms,'collected_ms':int(time.time()*1000),
       'native_counters_before':counters_before,'native_counters_after':counters_after,
       'native_packet_delta':{k:counters_after[k]-counters_before[k] for k in counters_before},
       'syscalls':sanitize_syscalls(parts['strace']),
       'node_dns':sanitize_dns(parts['node-dns']),'native_dns':sanitize_dns(parts['native-dns']),
       'private_trace_sha256':{k:hashlib.sha256(s.encode()).hexdigest() for k,s in parts.items()},
       'coverage_limit':'strace descendants; native getaddrinfo when dynamically linked/interposed; Node dns.lookup. Missing hook events do not prove no DNS.'}
    assert v['syscalls']['events'], 'empty syscall evidence'
    v['trace_complete']=v['syscalls']['unparsed_lines']==0 and v['syscalls']['unfinished_calls']==0
    v['completeness_limit']='Unparsed/incomplete lines prevent a complete network attribution claim; raw bytes are never included.'
    return v
