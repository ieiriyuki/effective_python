# Chapter 8 頑健性と性能

## 65 try/except/else/finallyを活用する

## 66 contextlibとwith文をtry/finallyの代わりに考える

`with func() as foo`で受けるには`yield`する

## 67 ローカルクロックにはdatetimeを使う

```py
import pytz
from datetime import datetime

time_format = "%Y-%m-%d %H:%M:%S"
arrival_nyc = "2019-03-16 23:33:24"
nyc_dt_naive = datetime.strptime(arrival_nyc, time_format)
eastern = pytz.timezone("US/Eastern")
nyc_dt = eastern.localize(nyc_dt_naive)
print(nyc_dt)
utc_dt = pytz.utc.normalize(nyc_dt.astimezone(pytz.utc))
print(utc_dt)
pacific = pytz.timezone("US/Pacific")
sf_dt = pacific.normalize(utc_dt.astimezone(pacific))
print(sf_dt)
# 2019-03-16 23:33:24-04:00
# 2019-03-17 03:33:24+00:00
# 2019-03-16 20:33:24-07:00
```

## 68 copyregでpickleを信頼できるようにする

- シリアライズされたものに新バージョンがないか
- クラスの名前変更があったら

```py
import copyreg, pickle

class BetterGameState:
    def __init__(self, level=0, points=0):
        self.level = level
        self.points = points

def pickle_game_state(game_state):
    kwargs = game_state.__dict__
    kwargs["version"] = 2
    return unpickle_game_state, (kwargs,)

def unpickle_game_state(kwargs):
    if kwargs.pop("version", 1) == 1:
        kwargs.pop("lives")

    return BetterGameState(**kwargs)

copyreg.pickle(BetterGameState, pickle_game_state)
```

## 69 精度が特に重要な場合はdecimalを使う

有理数を使いたければfractions.Fractionを使う
```py
from decimal import Decimal, ROUND_UP

print(Decimal("2.1"))
print(Decimal(2.1))
# 2.1
# 2.100000000000000088817841970012523233890533447265625

x = Decimal("0.05") * Decimal(5) / Decimal(60)
print(x, round(x, 2))
# 0.004166666666666666666666666667 0.00
rounded = x.quantize(Decimal("0.01"), rounding=ROUND_UP)
print(rounded)
# 0.01
```

## 70 最適化の前にプロファイル

```py
from bisect import bisect_left
from cProfile import Profile
from pstats import Stats
from random import randint

def insertion_sort(data):
    result = []
    for value in data:
        insert_value(result, value)
    return result

def insert_value(result, value):
    i = bisect_left(result, value)
    result.insert(i, value)

max_size = 10 ** 4
data = [randint(0, max_size) for _ in range(max_size)]
test = lambda: insertion_sort(data)

profiler = Profile()
profiler.runcall(test)

stats = Stats(profiler)
stats.strip_dirs()
stats.sort_stats("cumulative")
stats.print_stats()

#          30003 function calls in 0.026 seconds
#
#   Ordered by: cumulative time
#
#   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
#        1    0.000    0.000    0.026    0.026 main.py:18(<lambda>)
#        1    0.002    0.002    0.026    0.026 main.py:6(insertion_sort)
#    10000    0.004    0.000    0.024    0.000 main.py:12(insert_value)
#    10000    0.018    0.000    0.018    0.000 {method 'insert' of 'list' objects}
#    10000    0.003    0.000    0.003    0.000 {built-in method _bisect.bisect_left}
#        1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
```

```py
from cProfile import Profile
from pstats import Stats

def my_utility(a, b):
    c = 1
    for i in range(100):
        c += a * b

def first_func():
    for _ in range(1000):
        my_utility(4, 5)

def second_func():
    for _ in range(10):
        my_utility(1, 3)

def my_program():
    for _ in range(20):
        first_func()
        second_func()

test = lambda: my_program()

profiler = Profile()
profiler.runcall(test)

stats = Stats(profiler)
stats.strip_dirs()
stats.sort_stats("cumulative")
stats.print_callers()

#    Ordered by: cumulative time
#
# Function                                          was called by...
#                                                       ncalls  tottime  cumtime
# main.py:22(<lambda>)                              <-
# main.py:17(my_program)                            <-       1    0.000    0.150  main.py:22(<lambda>)
# main.py:9(first_func)                             <-      20    0.003    0.149  main.py:17(my_program)
# main.py:4(my_utility)                             <-   20000    0.146    0.146  main.py:9(first_func)
#                                                          200    0.001    0.001  main.py:13(second_func)
# main.py:13(second_func)                           <-      20    0.000    0.001  main.py:17(my_program)
# {method 'disable' of '_lsprof.Profiler' objects}  <-
```

## 71 生産者消費者キューにはdequeのほうがよい

- listのpopは再代入が発生するため特に遅い, O(N)
- dequeは(多分連結リストなので)速い, O(1)

```py
# popを使うと遅い
import timeit

def print_results(count, tests):
    avg_iteration = sum(tests) / len(tests)
    print(f"count {count:>5,} takes {avg_iteration:.6f}s")
    return count, avg_iteration

def list_pop_benchmark(count):
    def prepare(): return list(range(count))

    def run(queue):
        while queue:
            queue.pop(0)

    tests = timeit.repeat(
        setup="queue=prepare()",
        stmt="run(queue)",
        globals=locals(),
        repeat=1000,
        number=1
    )
    return print_results(count, tests)

def print_delta(before, after):
    before_count, before_time = before
    after_count, after_time = after
    growth = 1 + (after_count - before_count) / before_count
    slowdown = 1 + (after_time - before_time) / before_time
    print(f"{growth:>4.1f}x data size, {slowdown:>4.1f}x time")

baseline = list_pop_benchmark(100)
for count in (1000, 2000, 3000, 4000, 5000):
    print()
    comparison = list_pop_benchmark(count)
    print_delta(baseline, comparison)
# count   100 takes 0.000005s
#
# count 1,000 takes 0.000087s
# 10.0x data size, 16.5x time
#
# count 2,000 takes 0.000266s
# 20.0x data size, 50.7x time
#
# count 3,000 takes 0.000566s
# 30.0x data size, 108.0x time
#
# count 4,000 takes 0.000978s
# 40.0x data size, 186.6x time
#
# count 5,000 takes 0.001487s
# 50.0x data size, 283.9x time
```

dequeを使うと速くなる
```py
import timeit, collections
from random import random

class Email:
    def __init__(self, sender, receiver, message):
        self.sender = sender
        self.receiver = receiver
        self.message = message

class NoMailError(Exception): pass

def try_receive_email():
    if random() > 0.5:
        return Email(1, 2, 3)
    else:
        raise NoMailError

def produce_emails(queue):
    while True:
        try:
            email = try_receive_email()
        except NoMailError:
            return
        else:
            queue.append(email)

def consume_one_email(queue):
    if not queue:
        return
    email = queue.popleft()

def my_end_func():
    if random() > 0.9:
        return False
    else:
        return True

def loop(queue, keep_running):
    while keep_running():
        produce_emails(queue)
        consume_one_email(queue)

loop(collections.deque(), my_end_func)

def print_results(count, tests):
    avg_iteration = sum(tests) / len(tests)
    print(f"count {count:>5,} takes {avg_iteration:.6f}s")
    return count, avg_iteration

def deque_popleft_benchmark(count):
    def prepare(): return collections.deque(range(count))

    def run(queue):
        while queue:
            queue.popleft()

    tests = timeit.repeat(
        setup="queue=prepare()",
        stmt="run(queue)",
        globals=locals(),
        repeat=1000,
        number=1
    )
    return print_results(count, tests)

def print_delta(before, after):
    before_count, before_time = before
    after_count, after_time = after
    growth = 1 + (after_count - before_count) / before_count
    slowdown = 1 + (after_time - before_time) / before_time
    print(f"{growth:>4.1f}x data size, {slowdown:>4.1f}x time")

baseline = deque_popleft_benchmark(100)
for count in (1000, 2000, 3000, 4000, 5000):
    print()
    comparison = deque_popleft_benchmark(count)
    print_delta(baseline, comparison)

# count   100 takes 0.000002s
#
# count 1,000 takes 0.000018s
# 10.0x data size,  8.9x time
#
# count 2,000 takes 0.000034s
# 20.0x data size, 16.8x time
#
# count 3,000 takes 0.000048s
# 30.0x data size, 23.9x time
#
# count 4,000 takes 0.000064s
# 40.0x data size, 32.3x time
#
# count 5,000 takes 0.000081s
# 50.0x data size, 40.8x time
```

## 72 ソート済みシーケンスの探索にはbisectを考える

## 73 優先度付きキューでheapqの使い方を知っておく

- heapqでずっと高速になる
- 全ての本が貸出状態で期限を超えるとキューのサイズを超えるかもしれない
- 貸出可能な最大サイズを制限しておく

```py
import functools, random, timeit
from heapq import heappush, heappop

@functools.total_ordering
class Book:
    def __init__(self, title, due_date):
        self.title = title
        self.due_date = due_date

    def __lt__(self, other):
        return self.due_date < other.due_date

def add_book(queue, book):
    heappush(queue, book)

class NoOverdueBooks(Exception): pass

def print_results(count, tests):
    avg_iteration = sum(tests) / len(tests)
    print(f"count {count:>5,} takes {avg_iteration:.6f}s")
    return count, avg_iteration

def heap_overdue_benchmark(count):
    def prepare():
        to_add = list(range(count))
        random.shuffle(to_add)
        return [], to_add

    def run(queue, to_add):
        for i in to_add:
            heappush(queue, i)
        while queue:
            heappop(queue)

    tests = timeit.repeat(
        setup="queue, to_add = prepare()",
        stmt="run(queue, to_add)",
        globals=locals(),
        repeat=100,
        number=1
    )
    return print_results(count, tests)

def print_delta(before, after):
    before_count, before_time = before
    after_count, after_time = after
    growth = 1 + (after_count - before_count) / before_count
    slowdown = 1 + (after_time - before_time) / before_time
    print(f"{growth:>4.1f}x data size, {slowdown:>4.1f}x time")

baseline = heap_overdue_benchmark(100)
for count in [1000, 2000, 3000]:
    print()
    comparison = heap_overdue_benchmark(count)
    print_delta(baseline, comparison)

# count   100 takes 0.000022s
#
# count 1,000 takes 0.000196s
# 10.0x data size,  8.9x time
#
# count 2,000 takes 0.000336s
# 20.0x data size, 15.2x time
#
# count 3,000 takes 0.000517s
# 30.0x data size, 23.3x time
```

## 74 bytes型のゼロコピー処理にはmemoryviewとbytearrayを考える

- memoryviewは、オブジェクトのスライスの読み書きにゼロコピーインターフェースを提供する
- bytearrayは、socket.recv_fromのようなゼロコピーデータ読み込みに使われる変更可能なbytesのような型を提供する
