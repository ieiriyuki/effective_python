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

## 40 superを使ってスーパークラスを初期化する

`__init__` で呼び出すと順番のせいで挙動が不安定になる

`super().__init__` でC3線型化によって処理順が決まる

Method Resolution Order

## 41 Mix-inクラスで機能合成を考える

Javaでいろんなinterfaceを継承するようなもんか

Rustでいろんなimplをする感じ

mix-in: インスタンス属性を持たない, `__init__` を呼ぶ必要もない

```py
class XMixin:
    def foo(self):
        pass


class Foo(XMixin):
    def __init__(self):
        pass
```

## 42 プライベート属性よりパブリック属性が好ましい

*みんな大人なんだから*

- `public`
- `_protected`
- `__private`
- 保護フィールドを文書化してサブクラスでどの内部APIを使えるのか説明すると拡張の指針にもなる
- サブクラスとの名前の衝突を気にするときにプライベート属性を使う

## 43 カスタムコンテナ型はcollections.abcを継承する
