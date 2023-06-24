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

