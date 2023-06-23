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
