# Chapter 6 メタクラスと属性

## 44 getメソッドやsetメソッドは使わず属性をそのまま使う

後になって、属性が設定されたときに特別な振る舞いが必要となる場合は、`@property`デコレータと対応する`setter`属性をマイグレートすればいい

```py
class Foo():
    def __init__(self, x):
        self.x = x  # setterを呼び出す

    @property
    def x(self):
        return x

    @x.setter
    def x(self, x):
        if x < 0:
            raise ValueError("x must be greator than or equal to 0")
        self.x = x
```

## 45 属性をリファクタリングする代わりに@propertyを考える

注: 繰り返し`@property`を拡張するハメになったらクラスをリファクタリングする時期でしょう

## 46 再利用可能な@propertyメソッドにディスクリプタを使う

```py
from weakref import WeakKeyDictionary


class Grade:
    def __init__(self):
        self._values = {}

    def __get__(self, instance, instance_type):
        if instance is None:
            return self
        return self._values.get(instance, 0)

    def __set__(self, instance, value):
        if not (0 <= value <= 100):
            raise ValueError
        self._values[instance] = value


class Exam:
    math_grade = Grade()
    writing_grade = Grade()
    science_grade = Grade()


first_exam = Exam()
first_exam.writing_grade = 82
second_exam = Exam()
second_exam.writing_grade = 75
print(f"first: {first_exam.writing_grade}, second: {second_exam.writing_grade}")
# first: 82, second: 75
```

## 47 遅延属性には__getattr__, __getattribute__, __setattr__を使う

`super()`で無限再帰に入るのを防ぐ

```py
class LazyRecord:
    def __init__(self):
        self.exists = 5

    def __getattr__(self, name):
        value = f"Value for {name}"
        setattr(self, name, value)
        return value


x = LazyRecord()
print("before:", x.__dict__)
print("foo:", x.foo)
print("after:", x.__dict__)


class ValidatingRecord:
    def __init__(self):
        self.exists = 5

    def __getattribute__(self, name):
        print(f"* called __getattribute__({name!r})")
        try:
            value = super().__getattribute__(name)
            print(f"* found {name!r}, returning {value!r}")
            return value
        except AttributeError:
            value = f"Value for {name}"
            print(f"* setting {name!r} to {value!r}")
            setattr(self, name, value)
            return value


y = ValidatingRecord()
print("exists:", y.exists)
print("first foo:", y.foo)
print("second foo:", y.foo)
```

## 48 サブクラスを__init_subclass__で検証する

- typeを継承したメタクラスの__new__で検証できる
- メタクラスは1つしか指定できないため, 異なる観点の検証がしにくい
- __init_subclass__を活用できる
