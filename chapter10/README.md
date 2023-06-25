# 協働作業

## 82 コミュニティのモジュールをどこで見つけられるかを知っておく

## 83 隔離された複製可能な依存関係のために仮想環境を使う

## 84 全ての関数、クラス、モジュールについてdocstringを書く

https://peps.python.org/pep-0257/

## 85 モジュールの構成にパッケージを用い、安定したAPIを提供する

## 86 実施環境を構成するのにモジュールのスコープのコードを考える

```py
if __main__.TESTING:
    db = TestDatabase
else:
    db = ProdDatabase
```

## 87 APIからの呼び出し元を分離するために、ルート例外を定義する

## 88 循環依存を取り除く方法を知っておく

- リファクタリングで依存木の底を変える
- モジュールでは定義だけ行い、各モジュールのconfigure関数を用意する
- 動的インポートで関数内などでインポートする

## 89 リファクタリングと利用のマイグレーションにwarningsを考える

- warnings.simplefilter("error")で例外として出力できる
- テストを失敗させることができる
- プロダクションではlogging.captureWarningsによりログ出力させるのを検討する
- `with warnings.catch_warnings(recode=True)`をテストで使う

```py
import warnings
def require(name, value, default):
    if value is not None:
        return value
    warnings.warn(
        f"{name} will be required soon, update your code",
        DeprecationWarning,
        stacklevel=3,
    )
    return default
```

## 90 バグを回避するために静的解析を検討する

- `from __future__ import annotation`により後で定義されるクラスなどへの依存を適切に扱える
- 全てに型ヒントをつけるのはコスパが悪い
- 多数の呼び出し元がいるところ、APIのインターフェースなどが有効

```py
from __future__ import annotation

class FirstClass:
    def __init__(self, value: SecondClass):  # 普通はこれまで定義されていないのでエラる
        self.value = value

class SecondClass: pass
```
