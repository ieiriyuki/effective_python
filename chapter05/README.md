# Chapter 5 クラスと継承

## 37 組み込み型の深い入れ子にせず、クラスを作る

tuple, namedtuple, dataclass, class

複雑になってきたら dataclass 以上を使う

## 38 単純なインターフェースには関数を使う

```python
cur = {"1": 1, "2": 2}

x = defaultdict(
    list,  # 第一引数は callable
    cur,  # iterable じゃないと怒られる, リストでも怒られる
)

class Foo:
    def __init__():
        pass

    # インスタンス自体を呼び出せる
    def __callable__():
        return 0

foo = Foo()
assert callable(foo)
```

## 39 @classmethodポリモルフィズムを使ってオブジェクトをジェネリックに構築する

```py
class AbFoo():
    def __init__():
        pass

    def func_x():
        raise NotImplementedError

    @classmethod
    def create_foo():
        raise NotImplementedError


class SpFoo(AbFoo()):
    def __init__():
        pass

    def func_x():
        print("x")

    @classmethod
    def create_foo():
        return cls
```
