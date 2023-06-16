# Chapter 4 内包表記とジェネレータ

## 27 mapやfilterの代わりにリスト内包表記を使う

## 28 内包表記では3つ以上の式を避ける

## 29 代入式を使い内包表記での繰り返しをなくす

## 30 リストを返さずにジェネレータを返す

```py
def foo(text):
    if text:
        yield 0
    for index, letter in enumerate(text):
        yield index + 1
```

## 31 引数に対してイテレータを使うときには確実さを優先する

* ジェネレータ関数を使う
* 呼ばれるたびに新たなイテレータを返す関数を受け入れる
* イテレータを実装したコンテナクラスを使う

```py
class ReadVisits:
    def __init__(self, data_path):
        self.data_path = data_path

    def __iter__(self):
        with open(self.data_path) as f:
            for line in f:
                yield int(line)

def normalize(get_iter):
    from collections.abc import Iterator
    if isinstance(get_iter, Iterator):
        raise TypeError
    total = sum(get_iter)
    result = []
    for i in get_iter:
        result.append(i * 100 / total)
    return result

visits = ReadVisits("data.txt")
percentage = normalize(visits)
print(percentage, sum(percentage))
normalize(iter([1, 2, 3]))  # TypeError
```

## 32 大きなリスト内包表記はジェネレータ式を考える

ジェネレータ式はリスト内包表記と同じだが () で括る

`it = (len(x)  for x in ["aa", "bbb", "ccc"])`

## 33 yield from で複数のジェネレータを作る

```py
def child():
    for i in range(100_000):
        yield i

def slow():
    for i in child():
        yield i

def fast():
    yield from child()

import timeit
x = timeit.timeit(
    stmt = "for i in slow(): pass",
    globals=globals(),
    number=50
)
y = timeit.timeit(
    stmt = "for i in fast(): pass",
    globals=globals(),
    number=50
)
print(x, y, sep="\n")
5.013313500006916
4.470528799996828
```

## 34 sendでジェネレータにデータを注入するのは避ける

- https://docs.python.org/ja/3.7/reference/expressions.html#generator.send
- sendを使うと構造も複雑になる

```py
def wave_cascading(amplitude_it, steps):
    import math
    step_size = 2 * 3.14 / steps
    for step in range(steps):
        radians = step * step_size
        fraction = math.sin(radians)
        amplitude = next(amplitude_it)
        output = amplitude * fraction
        yield output

def complex_cascading(amplitude_it):
    yield from wave_cascading(amplitude_it, 3)
    yield from wave_cascading(amplitude_it, 4)
    yield from wave_cascading(amplitude_it, 5)

amplitude = [7, 7, 7, 2, 2, 2, 2, 9, 9, 9, 9, 9]
it = complex_cascading(iter(amplitude))
for amp in amplitude:
    output = next(it)
    print(f"{output:0.1f}")
```

## 35 ジェネレータでthrowによる状態遷移を起こすのは避ける

```py
def check_update():
    import random
    if random.random() < 0.7:
        return False
    return True

class Timer:
    def __init__(self, period):
        self.current = period
        self.period = period

    def reset(self):
        self.current = self.period

    def __iter__(self):
        while self.current:
            self.current -= 1
            yield self.current

timer = Timer(4)
for current in timer:
    if check_update():
        timer.reset()
    print(f"{current}")
```

## 36 イテレータとジェネレータの作業ではitertoolsを使う

- chain
- repeat
- tee
- islice
- takewhile
- dropwhile
- filterfalse
- accumulate
- product
- permutations
- combinations
- combinations_with_replacement
