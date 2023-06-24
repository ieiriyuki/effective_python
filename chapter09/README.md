# Chapter 9 テストとデバッグ

## 75 出力のデバッグにはreprを使う

```py
class Sample:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Sample({self.x!r}, {self.y!r})"

print(repr(5))
print(repr('5'))
print(repr(Sample(1, 2)))
# 5
# '5'
# Sample(1, 2)
```

## 76 関係する振る舞いをTestCaseサブクラスで検証する

## 77 setUp, tearDown, setUpModule, tearDownModuleで他からテストを分離する

- setUp, tearDown: テストメソッドの前後で呼ばれ、テスト環境をセットアップする
- setUpModule, tearDownModule: モジュールレベルのテストハーネス初期化。全テストが終了したら破棄される。

```py
from unittest import TestCase, main

def setUpModule():
    print("* module set up")

def tearDownModule():
    print("* Module clean up")

class IntegrationTest(TestCase):
    def setUp(self) -> None:
        print("set up")

    def tearDown(self) -> None:
        print("clean up")

    def test_end_to_end1(self):
        print("* Test 1")

    def test_end_to_end2(self):
        print("* Test 2")

if __name__ == "__main__":
    main()
# * module set up
# set up
# * Test 1
# clean up
# .set up
# * Test 2
# clean up
# .* Module clean up
#
# ----------------------------------------------------------------------
# Ran 2 tests in 0.000s
#
# OK
```

## 78 モックを使って依存性が複雑なコードをテストする

```py
from datetime import datetime, timedelta
from unittest.mock import Mock, call, patch

def get_food_period(database, species): pass

def get_animals(database, species): pass

def feed_animal(database, name, now): pass

# 引数で与えてテストしやすくする
def do_rounds(database, species, *,
              now_func=datetime.utcnow,
              food_func=get_food_period,
              animals_func=get_animals,
              feed_func=feed_animal):
    now = now_func()
    feeding_timedelta = food_func(database, species)
    animals = animals_func(database, species)

    fed = 0
    for name, last_mealtime in animals:
        if (now - last_mealtime) > feeding_timedelta:
            feed_func(database, name, now)
            fed += 1
    return fed

database = object()
now_func = Mock(spec=datetime.utcnow)
now_func.return_value = datetime(2019, 6, 5, 15, 45)
food_func = Mock(spec=get_food_period)
food_func.return_value = timedelta(hours=3)
animals_func = Mock(spec=get_animals)
animals_func.return_value = [("AAA", datetime(2019, 6, 5, 11, 15)),
                             ("BBB", datetime(2019, 6, 5, 12, 35)),
                             ("CCC", datetime(2019, 6, 5, 12, 55)),]
feed_func = Mock(spec=feed_animal)

result = do_rounds(database, "Meerkat",
                   now_func=now_func,
                   food_func=food_func,
                   animals_func=animals_func,
                   feed_func=feed_func)
assert result == 2

food_func.assert_called_once_with(database, "Meerkat")
animals_func.assert_called_once_with(database, "Meerkat")
feed_func.assert_has_calls([call(database, "AAA", now_func.return_value),
                            call(database, "BBB", now_func.return_value)],
                           any_order=True)

print("outside", get_animals)
with patch("__main__.get_animals"):
    print("inside", get_animals)
print("outside", get_animals)
```

## 79 モックとテストを活用して依存性をカプセル化する

```py
import contextlib, io
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

class ZooDatabase:
    def get_animals(self, species): pass

    def get_food_period(self, species): pass

    def feed_animal(self, name, when): pass

def do_rounds(database, species, *, utcnow=datetime.utcnow):
    now = utcnow()
    feeding_timedelta = database.get_food_period(species)
    animals = database.get_animals(species)
    fed = 0
    for name, last_mealtime in animals:
        if (now - last_mealtime) > feeding_timedelta:
            database.feed_animal(name, now)
            fed += 1
    return fed

database = Mock(spec=ZooDatabase)
print(database.feed_animal)

DATABASE = None

def get_database():
    global DATABASE
    if DATABASE is None:
        DATABASE = ZooDatabase()
    return DATABASE

def main(argv):
    database = get_database()
    species = argv[1]
    count = do_rounds(database, species)
    print(f"Fed {count} {species}")
    return 0

with patch("__main__.DATABASE", spec=ZooDatabase):
    now = datetime.utcnow()
    DATABASE.get_food_period.return_value = timedelta(hours=3)
    DATABASE.get_animals.return_value = [
        ("AAA", now - timedelta(minutes=4.5)),
        ("BBB", now - timedelta(hours=4.5)),
        ("CCC", now - timedelta(hours=3.5)),
    ]
    fake_stdout = io.StringIO()
    with contextlib.redirect_stdout(fake_stdout):
        main(["program name", "Meerkat"])
    found = fake_stdout.getvalue()
    expected = "Fed 2 Meerkat\n"
    assert found == expected
```

## 80 pdbで対話的にデバッグすることを考える

`python -m pdb -c continue file.py`でもできる

```py
import math

def comput_rmse(observed, ideal):
    total_err_2 = 0
    count = 0
    for got, wanted in zip(observed, ideal):
        err_2 = (got - wanted) ** 2
        breakpoint()
        total_err_2 += err_2
        count += 1
    mean_err = total_err_2 / count
    rmse = math.sqrt(mean_err)
    return rmse

result = comput_rmse([1.8, 1.7, 3.2, 6], [2, 1.5, 3, 5])
print(result)
```

## 81 メモリの私用とリークを理解するにはtracemallocを使う

- CPythonのメモリ管理は参照カウント法を使う
