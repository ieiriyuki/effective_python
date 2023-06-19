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

- GILは本質的に、優先度の高いスレッドが実行中のスレッドを割り込んで制御を奪うプリエンプティブマルチスレッド処理で影響されることを防止する相互排他ロックです (mutex)
- GILは同時に1つのスレッドしか進行できないようにしています
- マルチスレッドによってプログラムが一時に複数のことをしているとわかりやすくなる
- ある種のシステムコールを行う際に生じるブロッキングIOを扱うため

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

- データ構造に対するスレッドの演算は、Pythonインタプリタがバイトコードを実行する合間に割り込むことが可能
- 3.9以前と3.10でLockを使わないときの振る舞いが違うっぽい

```py
import sys
from threading import Lock, Thread

class LockCounter:
    def __init__(self):
        self.lock = Lock()
        self.count = 0

    def increment(self, offset):
        with self.lock:
            self.count += offset

def worker(sensor_index, how_many, counter):
    for _ in range(how_many):
        counter.increment(1)

how_many = 10**5
counter = LockCounter()

threads = []
for i in range(5):
    t = Thread(target=worker,
                args=(i, how_many, counter))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

expected = how_many * 5
found = counter.count
print(f"exp: {expected}, act: {found}, ver: {sys.version}")
#  exp: 500000, act: 500000, ver: 3.8.17 (default, Jun 14 2023, 19:06:21)
# exp: 500000, act: 500000, ver: 3.9.17 (main, Jun 14 2023, 18:58:46)
# exp: 500000, act: 500000, ver: 3.10.9 (main, Dec  8 2022, 01:46:27)
```

## 55 スレッド間の協調作業にはQueueを使う

- 何度もpollしてcpu時間を消費する
- done_queueがビジーウェイトになる
- 作業者スレッドに抜け出すためのシグナルを送れない
- パイプラインの渋滞で、プログラムがどこかでクラッシュする

```py
from queue import Queue
from threading import Lock, Thread
import time

class Job:
    def __init__(self, n: int):
        self.n = n

def download(x: Job):
    print(x.n, "d")
    return Job(n=x.n)

def resize(x: Job):
    print(x.n, "r")
    return Job(n=x.n)

def upload(x: Job):
    print(x.n, "u")
    return Job(n=x.n)

class ClosableQueue(Queue):
    SENTINEL = object()

    def close(self):
        self.put(self.SENTINEL)

    def __iter__(self):
        while True:
            item = self.get()
            try:
                if item is self.SENTINEL:
                    return
                yield item
            finally:
                self.task_done()

class StoppableWorker(Thread):
    def __init__(self, func, in_queue, out_queue):
        super().__init__()
        self.func = func
        self.in_queue = in_queue
        self.out_queue = out_queue

    def run(self):
        for item in self.in_queue:
            result = self.func(item)
            self.out_queue.put(result)

def start_thread(count, *args):
    threads = [StoppableWorker(*args) for _ in range(count)]
    for t in threads: t.start()
    return threads

def stop_threads(closable_queue, threads):
    for _ in threads: closable_queue.close()
    closable_queue.join()
    for t in threads: t.join()

down_queue = ClosableQueue()
res_queue = ClosableQueue()
up_queue = ClosableQueue()
done_queue = ClosableQueue()

down_threads = start_thread(3, download, down_queue, res_queue)
res_threads = start_thread(3, resize, res_queue, up_queue)
up_threads = start_thread(3, upload, up_queue, done_queue)

for i in range(100): down_queue.put(Job(i))

stop_threads(down_queue, down_threads)
stop_threads(res_queue, res_threads)
stop_threads(up_queue, up_threads)
print(done_queue.qsize(), "q finished")
```

## 56 並行性が必要な場合をどのように認知するかを知っておく

下記でマルチスレッドにする場合、セルを生成するプロセスを並列化 (ファンアウト) する

```py
ALIVE = "*"
EMPTY = "-"

class Grid:
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.rows = []
        for _ in range(self.height):
            self.rows.append([EMPTY] * self.width)

    def get(self, y, x):
        return self.rows[y % self.height][x % self.width]

    def set(self, y, x, state):
        self.rows[y % self.height][x % self.width] = state

    def __str__(self):
        text = "\n".join(["".join(self.rows[i]) for i in range(self.height)])
        return text

grid = Grid(5, 9)
grid.set(0, 3, ALIVE)
grid.set(1, 4, ALIVE)
grid.set(2, 2, ALIVE)
grid.set(2, 3, ALIVE)
grid.set(2, 4, ALIVE)
print(grid)

def count_neighbors(y, x, get):
    n_ = get(y - 1, x + 0)
    ne = get(y - 1, x + 1)
    e_ = get(y + 0, x + 1)
    se = get(y + 1, x + 1)
    s_ = get(y + 1, x + 0)
    sw = get(y + 1, x - 1)
    w_ = get(y + 0, x - 1)
    nw = get(y - 1, x - 1)
    neighbor_states = [n_, ne, e_, se, s_, sw, w_, nw]
    count = 0
    for state in neighbor_states:
        if state == ALIVE:
            count += 1
    return count

def game_logic(state, neighbors):
    if state == ALIVE:
        if neighbors < 2:
            return EMPTY
        elif neighbors > 3:
            return EMPTY
    else:
        if neighbors == 3:
            return ALIVE
    return state

def step_cell(y, x, get, set):
    state = get(y, x)
    neighbors = count_neighbors(y, x, get)
    next_state = game_logic(state, neighbors)
    set(y, x, next_state)

def simulate(grid):
    next_grid = Grid(grid.height, grid.width)
    for y in range(grid.height):
        for x in range(grid.width):
            step_cell(y, x, grid.get, next_grid.set)
    return next_grid

for i in range(5):
    grid = simulate(grid)
    print()
    print(grid)
```