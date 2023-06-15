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

## 49 クラスの存在を__init_subclass__で登録する

`__init_subclass__`を定義したクラスを継承したサブクラスで実行される

```py
import json

registry = dict()

def register_class(target_class):
    registry[target_class.__name__] = target_class

class BetterSerializable:
    def __init_subclass__(cls):
        super().__init_subclass__()
        register_class(cls)  # 忘れにくい

    def __init__(self, *args):
        self.args = args

    def serialize(self):
        return json.dumps({
            "class": self.__class__.__name__,
            "args": self.args,
        })

    def __repr__(self):
        name = self.__class__.__name__
        args_str = ", ".join(str(x) for x in self.args)
        return f"{name}({args_str})"

class SubClass(BetterSerializable):
    def __init__(self, *args):
        super().__init__(*args)

def deserialize(data):
    params = json.loads(data)
    name = params["class"]
    target_class = registry[name]
    return target_class(*params["args"])

# register_class(SubClass)  # 忘れがち
print(deserialize('{"class": "SubClass", "args": [1, 2, 3, 4]}'))
```

## 50 クラス属性に__set_name__で注釈を加える

```py
class Field:
    def __init__(self):
        self.name = None
        self.internal_name = None

    def __set_name__(self, owner, name):
        self.name = name
        self.internal_name = "_" + name

    def __get__(self, instance, instance_type):
        if instance is None:
            return self
        return getattr(instance, self.internal_name, "")

    def __set__(self, instance, value):
        setattr(instance, self.internal_name, value)

class FixedCustomer:
    first_name = Field()
    last_name = Field()
    prefix = Field()
    suffix = Field()

cust = FixedCustomer()
print(f"{cust.first_name!r} {cust.__dict__}")
cust.first_name = "Euler"
print(f"{cust.first_name!r} {cust.__dict__}")
```

## 51 合成可能なクラス拡張のためにはメタクラスではなくクラスデコレータを使う

```py
import types
from functools import wraps

trace_types = (types.FunctionType, types.MethodType, types.BuiltinFunctionType, types.BuiltinMethodType, types.MemberDescriptorType, types.ClassMethodDescriptorType,)

def trace_func(func):
    if hasattr(func, "tracing"):
        return func

    @wraps(func)
    def wrapper(*args, **kwargs):
        result = None
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            result = e
            raise
        finally:
            print("foo")

    wrapper.tracing = True
    return wrapper

def trace(klass):
    for k in dir(klass):
        value = getattr(klass, k)
        if isinstance(value, trace_types):
            wrapped = trace_func(value)
            setattr(klass, k, wrapped)
    return klass

@trace
class TraceDict(dict):
    pass

trace_dict = TraceDict([("hi", 1)])
trace_dict["there"] = 2
trace_dict["hi"]
trace_dict["foo"]
```
