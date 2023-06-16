## Chapter 7 並行性と並列性

## 52 subprocessを使って子プロセスを管理する

```py
import subprocess
import os

def run_encrypt(data):
    env = os.environ.copy()
    env["password"] = "asdfqwerty"
    proc = subprocess.Popen(
        ["openssl", "enc", "-des3", "-pass", "env:password"],
        env=env,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    proc.stdin.write(data)
    proc.stdin.flush()
    return proc

def run_hash(input_stdin):
    return subprocess.Popen(
        ["openssl", "dgst", "-whirlpool", "-binary"],
        stdin=input_stdin,
        stdout=subprocess.PIPE,
    )

procs = []
hash_procs = []
for _ in range(3):
    data = os.urandom(20)

    proc = run_encrypt(data)
    procs.append(proc)

    h_proc = run_hash(proc.stdout)
    hash_procs.append(h_proc)

    proc.stdout.close()
    proc.stdout = None

for proc in procs:
    proc.communicate()
    assert proc.returncode == 0

for proc in hash_procs:
    out, _ = proc.communicate()
    print(out[-10:])
    assert proc.returncode == 0

proc = subprocess.Popen(["sleep", "10"])
try:
    proc.communicate(timeout=0.1)
except:
    proc.terminate()
    proc.wait()

print("exit status", proc.poll())
```

## 53 スレッドはブロッキングIOに使い、並列性に使わない

システムコールの待ちに有効

```py
import select, socket, time
from threading import Thread

def slow_systemcall():
    select.select([socket.socket()], [], [], 0.1)

start = time.time()
threads = []
for _ in range(5):
    thread = Thread(target=slow_systemcall)
    thread.start()
    threads.append(thread)

def compute():
    pass

for i in range(5):
    compute()

for t in threads:
    t.join()

delta = time.time() - start
print(f"{delta:.3f}")
```

## 54 スレッドにおけるデータ競合を防ぐためにLockを使う


