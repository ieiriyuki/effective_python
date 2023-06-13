# Chapter 3 関数

## 19 4個以上の変数が返り値ならアンパックしない

## 20 None ではなく例外を送出する

## 21 クロージャが変数スコープとどう関わるかを把握しておく

参照と代入とで振る舞いが違う

## 22 可変位置引数をつかってすっきりさせる

`def foo(bar, *args)`

ただし、ジェネレータや引数の追加には気を付けること

## 23 キーワード引数にオプションの振る舞いを与える

## 24 複雑なキーワード引数のデフォルトにNoneを使う

docstring で説明する

## 25 キーワード専用引数と位置専用引数で明確にする

- `def func(foo, /, *, kwarg=1):`
- `/` より前が位置引数
- `*` より後がキーワード引数

## 26 functools.wraps を使ってデコレータを作る

```py
def foo(func):
    @wraps
    def wrapper(*args, *kwargs):
        ....
    return wrapper
```