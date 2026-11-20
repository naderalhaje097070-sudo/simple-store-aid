"""Privacy, delegation and attribution fixtures; live ptrace check precedes credentials."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from egress_trace import sanitize_dns, sanitize_syscalls


class TracePrivacy(unittest.TestCase):
    def test_explicit_dns_connect_is_not_delivery(self):
        v=sanitize_syscalls('12<node> 1700000000.100000 connect(21, {sa_family=AF_INET, sin_port=htons(53), sin_addr=inet_addr("10.0.0.2")}, 16) = 0\n')
        e=v['events'][0]
        self.assertEqual((e['address'],e['port']),('10.0.0.2',53))
        self.assertEqual(e['external_delivery_evidence'],'not_established')
        self.assertEqual(v['unparsed_lines'],0)

    def test_raw_send_has_no_inferred_destination(self):
        v=sanitize_syscalls('12<node> 1700000000.100000 sendto(0x15, 0x123456, 0x44, 0, 0, 0) = -1 ECONNREFUSED (Connection refused)\n')
        self.assertEqual(v['events'][0]['destination_source'],'not_attributed')
        self.assertEqual(v['events'][0]['errno'],'ECONNREFUSED')

    def test_resumed_and_socket_error(self):
        v=sanitize_syscalls('12<node> 1700000000.1 connect(21, {sa_family=AF_INET, sin_port=htons(443), sin_addr=inet_addr("192.0.2.1")}, 16 <unfinished ...>\n12<node> 1700000000.2 <... connect resumed>) = -1 EINPROGRESS (Operation in progress)\n12<node> 1700000000.3 getsockopt(21, SOL_SOCKET, SO_ERROR, [ECONNREFUSED], [4]) = 0\n')
        self.assertEqual(v['events'][1]['sockopt_error'],'ECONNREFUSED')
        self.assertEqual(v['unfinished_calls'],0)

    def test_unknown_or_unfinished_is_visible(self):
        v=sanitize_syscalls('unknown-new-format\n12<node> 1700000000.1 connect(21, 0x123 <unfinished ...>\n')
        self.assertEqual((v['unparsed_lines'],v['unfinished_calls']),(1,1))

    def test_syscall_payload_does_not_enter_receipt(self):
        v=sanitize_syscalls('12<node> 1700000000.1 sendto(21, "sensitive_fixture_needle", 25, 0, NULL, 0) = 25\n')
        self.assertNotIn('sensitive_fixture_needle',json.dumps(v))

    def test_dns_schema_rejects_unknown_fields_and_plain_secret(self):
        value={'type':'node_dns_lookup','pid':1,'timestamp_ms':1,'hostname':'hashed_hostname',
               'hostname_sha256':'a'*64,'callers':[]}
        self.assertEqual(len(sanitize_dns(json.dumps(value))),1)
        for changed in ({**value,'hostname':'sensitive_fixture_needle'}, {**value,'authorization':'needle'}):
            with self.assertRaises(AssertionError): sanitize_dns(json.dumps(changed))

    def test_dns_schema_rejects_freeform_caller(self):
        v={'type':'node_dns_lookup','pid':1,'timestamp_ms':1,'hostname':'localhost','hostname_sha256':'a'*64,
           'callers':[{'file':'sensitive_fixture_needle','file_sha256':'b'*64,'line':1,'column':1}]}
        with self.assertRaises(AssertionError): sanitize_dns(json.dumps(v))

    def test_node_hook_delegates_without_network_or_secret(self):
        hook=Path(__file__).with_name('dns_trace.cjs').resolve()
        source="""const vm=require('node:vm'),fs=require('node:fs'),crypto=require('node:crypto');
        let calls=0,lines=[];const dns={lookup:function(h,o,c){calls++;c(null,'127.0.0.1',4);return 'delegated';},promises:{lookup:async function(h){calls++;return {address:'127.0.0.1',family:4};}}};
        const ctx={require:n=>n==='node:dns'?dns:n==='node:fs'?{appendFileSync:(p,s)=>lines.push(s)}:crypto,process:{pid:1,env:{G1_NODE_DNS_LOG:'fixture'}}};
        vm.runInNewContext(fs.readFileSync(process.argv[1],'utf8'),ctx);
        if(dns.lookup('sensitive_fixture_needle',{},()=>{})!=='delegated')throw Error('delegation');
        dns.promises.lookup('localhost').then(()=>console.log(JSON.stringify({calls,rows:lines.map(JSON.parse)})));
        """
        r=subprocess.run(['node','-e',source,str(hook)],capture_output=True,text=True,check=True)
        self.assertNotIn('sensitive_fixture_needle',r.stdout)
        v=json.loads(r.stdout);self.assertEqual(v['calls'],2)
        self.assertEqual(v['rows'][0]['hostname_sha256'],hashlib.sha256(b'sensitive_fixture_needle').hexdigest())
        for row in v['rows']: sanitize_dns(json.dumps(row))

    def test_native_hook_delegates_and_hashes_without_dns(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source=Path(__file__).with_name('dns_trace.c').resolve()
            (root/'stub.c').write_text('#include <netdb.h>\nint getaddrinfo(const char*a,const char*b,const struct addrinfo*c,struct addrinfo**d){return EAI_NONAME;}\n')
            (root/'probe.c').write_text('#include <netdb.h>\nint main(){struct addrinfo*r=0;return getaddrinfo("sensitive_fixture_needle",0,0,&r)==EAI_NONAME?0:1;}\n')
            for args in [ ['cc','-shared','-fPIC',str(source),'-o',str(root/'trace.so'),'-ldl','-lcrypto','-pthread'],
                          ['cc','-shared','-fPIC',str(root/'stub.c'),'-o',str(root/'stub.so')],
                          ['cc',str(root/'probe.c'),'-o',str(root/'probe')] ]:
                subprocess.run(args,capture_output=True,check=True)
            env=dict(os.environ,LD_PRELOAD=str(root/'trace.so')+':'+str(root/'stub.so'),G1_NATIVE_DNS_LOG=str(root/'log'))
            subprocess.run([str(root/'probe')],env=env,capture_output=True,check=True)
            text=(root/'log').read_text();self.assertNotIn('sensitive_fixture_needle',text)
            rows=sanitize_dns(text);self.assertEqual(rows[0]['hostname_sha256'],hashlib.sha256(b'sensitive_fixture_needle').hexdigest())
            env['G1_NATIVE_DNS_LOG']=str(root/'missing-parent/log')
            self.assertEqual(subprocess.run([str(root/'probe')],env=env,capture_output=True).returncode,125)


def live_strace():
    with tempfile.TemporaryDirectory() as tmp:
        trace=Path(tmp)/'trace'
        command=['strace','-f','-ttt','-Y','-e','trace=connect,sendto,sendmsg,sendmmsg,getsockopt',
                 '-e','raw=sendto,sendmsg,sendmmsg','-o',str(trace),sys.executable,'-c',
                 'import socket;s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);s.sendto(b"G1_DUMMY_PRIVATE_NEEDLE",("127.0.0.1",9))']
        subprocess.run(command,capture_output=True,check=True,timeout=15)
        text=trace.read_text();assert 'G1_DUMMY_PRIVATE_NEEDLE' not in text, 'raw tracer leaked fixture'
        v=sanitize_syscalls(text);assert any(x['syscall']=='sendto' for x in v['events']), 'tracer did not execute'
        assert v['unparsed_lines']==0 and v['unfinished_calls']==0, 'unsupported tracer format'
        print('G1_EGRESS_POINTER_ONLY_TRACER_CONFIRMED')


if __name__=='__main__':
    if sys.argv[1:]==['--live-strace']: live_strace()
    else: unittest.main()
