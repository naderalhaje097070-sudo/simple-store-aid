"""Evidence import boundary for the release-finance cleanup step (review fix for PR #98, Strix review 4, CWE-59).

The candidate's evidence lives in /tmp/monjez-c5sale, a tree the confined c5finance identity owns and can rearrange
at any time (links, swaps). Root must never open, walk or read it. This module therefore has two sides:

  export SRC        run AS c5finance (the script is fed on stdin by the runner, from the runner's own checkout).
                    Walks SRC with directory file descriptors and O_NOFOLLOW at every level, so a link anywhere,
                    the top included, is refused rather than followed; only real directories and regular files are
                    taken. Writes an uncompressed tar stream to stdout. Any rejected entry, a SRC that is a link or
                    not a directory, or a limit overrun: no stream body is trusted, the rejection list goes to
                    stderr as JSON and the exit status is 3. A SRC that does not exist exports an empty stream.
  readjson PATH     run AS c5finance: prints the JSON object in PATH (regular file, opened with O_NOFOLLOW), or
                    {} when it does not exist; exit 3 when it is a link or not a regular file or not a JSON object.
  import DEST       run as the runner: reads the stream from stdin into DEST, which must not exist and is created
                    0700. Accepts only regular files and directories, with normalized relative names (no absolute
                    path, no '..', no '.', no backslash, no NUL), no duplicate or colliding name, within the same
                    limits; files are created exclusively (O_EXCL | O_NOFOLLOW), 0600. Exit 0 and a JSON receipt
                    on stdout, otherwise exit 4 with the reason.
"""
import json
import os
import stat
import sys
import tarfile

MAX_ENTRIES = 20000
MAX_BYTES = 512 * 1024 * 1024
READ_FLAGS = os.O_RDONLY | os.O_NOFOLLOW | getattr(os, 'O_CLOEXEC', 0)


def _valid(name):
    parts = name.split('/')
    return (bool(name) and not name.startswith('/') and '\\' not in name and '\0' not in name
            and all(p not in ('', '.', '..') for p in parts))


def export(src):
    out = tarfile.open(fileobj=sys.stdout.buffer, mode='w|', format=tarfile.PAX_FORMAT)
    rejected, count, total = [], 0, 0
    try:
        top = os.open(src, READ_FLAGS | os.O_DIRECTORY)
    except FileNotFoundError:
        out.close()
        return 0
    except OSError as e:   # ELOOP: SRC itself is a link; ENOTDIR: not a directory
        sys.stderr.write(json.dumps({'rejected': ['.'], 'reason': 'evidence root is not a real directory: ' + e.strerror}) + '\n')
        return 3

    def walk(dfd, prefix):
        nonlocal count, total
        with os.scandir(dfd) as it:
            entries = sorted(it, key=lambda e: e.name)
        for e in entries:
            rel = prefix + e.name
            count += 1
            if count > MAX_ENTRIES or not _valid(rel):
                rejected.append(rel); continue
            st = os.stat(e.name, dir_fd=dfd, follow_symlinks=False)
            if stat.S_ISDIR(st.st_mode):
                try:
                    sub = os.open(e.name, READ_FLAGS | os.O_DIRECTORY, dir_fd=dfd)
                except OSError:
                    rejected.append(rel); continue
                try:
                    info = tarfile.TarInfo(rel); info.type = tarfile.DIRTYPE; info.mode = 0o700; info.mtime = 0
                    out.addfile(info)
                    walk(sub, rel + '/')
                finally:
                    os.close(sub)
            elif stat.S_ISREG(st.st_mode):
                try:
                    fd = os.open(e.name, READ_FLAGS, dir_fd=dfd)
                except OSError:
                    rejected.append(rel); continue
                with os.fdopen(fd, 'rb') as f:
                    fst = os.fstat(f.fileno())
                    if not stat.S_ISREG(fst.st_mode) or total + fst.st_size > MAX_BYTES:
                        rejected.append(rel); continue
                    total += fst.st_size
                    info = tarfile.TarInfo(rel); info.size = fst.st_size; info.mode = 0o600; info.mtime = 0
                    out.addfile(info, f)
            else:   # symlink, fifo, socket, device
                rejected.append(rel)

    try:
        walk(top, '')
    finally:
        os.close(top)
    if rejected:
        sys.stderr.write(json.dumps({'rejected': sorted(rejected), 'reason': 'links, non-regular files or limits'}) + '\n')
        return 3
    out.close()
    return 0


def readjson(path):
    try:
        fd = os.open(path, READ_FLAGS)
    except FileNotFoundError:
        print('{}'); return 0
    except OSError as e:
        sys.stderr.write(json.dumps({'rejected': [path], 'reason': e.strerror}) + '\n'); return 3
    with os.fdopen(fd, 'rb') as f:
        if not stat.S_ISREG(os.fstat(f.fileno()).st_mode):
            sys.stderr.write(json.dumps({'rejected': [path], 'reason': 'not a regular file'}) + '\n'); return 3
        try:
            data = json.loads(f.read(MAX_BYTES))
        except ValueError:
            data = None
    if not isinstance(data, dict):
        sys.stderr.write(json.dumps({'rejected': [path], 'reason': 'not a JSON object'}) + '\n'); return 3
    print(json.dumps(data)); return 0


def import_(dest):
    os.mkdir(dest, 0o700)   # fails if it exists (or is a link)
    seen, files, total = {'.'}, 0, 0
    try:
        with tarfile.open(fileobj=sys.stdin.buffer, mode='r|') as tf:
            for m in tf:
                name = m.name.rstrip('/') if m.isdir() else m.name
                parent = name.rsplit('/', 1)[0] if '/' in name else '.'
                if not _valid(name) or name in seen or parent not in seen or len(seen) > MAX_ENTRIES:
                    raise ValueError('invalid, duplicate or orphan name: ' + json.dumps(name))
                path = os.path.join(dest, name)
                if m.isdir():
                    os.mkdir(path, 0o700); seen.add(name)
                elif m.isreg():
                    total += m.size
                    if total > MAX_BYTES:
                        raise ValueError('size limit')
                    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
                    with os.fdopen(fd, 'wb') as f, tf.extractfile(m) as src:
                        while chunk := src.read(1 << 20):
                            f.write(chunk)
                    seen.add(name); files += 1
                else:
                    raise ValueError('non-regular member: ' + json.dumps(name))
    except (tarfile.TarError, ValueError, OSError) as e:
        sys.stderr.write(json.dumps({'import_error': str(e)}) + '\n')
        return 4
    print(json.dumps({'files': files, 'directories': len(seen) - 1, 'bytes': total}))
    return 0


if __name__ == '__main__':
    args = sys.argv[1:]
    cmd = {'export': export, 'readjson': readjson, 'import': import_}.get(args[0] if args else '')
    if not cmd or len(args) != 2:
        raise SystemExit('usage: evidence_import.py {export SRC | readjson PATH | import DEST}')
    raise SystemExit(cmd(args[1]))
