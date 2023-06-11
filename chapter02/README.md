# Chapter 2 リストと辞書

## 11 シーケンスのスライス

スライスにアンパックして代入するとシーケンスを短くしたり長くしたりできる

```python
a = [0, 1, 2, 3, 4]
print(a)
# [0, 1, 2, 3, 4]
a[1:4] = ["a", "b"]
print(a)
# [0, 'a', 'b', 4]
```

## 12 ストライドとスライスを同時に使わない

## 13 catch-all アンパックを行う

```python
a = [1, 2, 3, 4]
x, y, *other = a
print(x, y, other)
# 1 2 [3, 4]
```

## 14 key 引数でソートする

```python
tools.sort(key=lambda x: x.name)
```

## 15 辞書の挿入順序に依存しているか注意する

型チェックとかする

## 16 欠損キーの処理に get を使う

デフォルト値が安価で変更可能な場合で、例外が少ないのなら setdefault を使う

## 17 setdefault ではなく defaultdict を使う

## 18 `__missing__` でキー依存デフォルト値を作成する
