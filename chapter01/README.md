# Chapter 1

## 2 PEP8

- プロテクテッド属性には先頭のアンダースコアをつける `_protected`
- プライベート属性は2つアンダースコアをつける `__private`
- `if len(a_list) == 0` ではなく `if not a_list`
- 絶対インポートを使う

## 3 bytes と str の違い

```python
a = b"h\x65llo"
print(list(a), a)

# [104, 101, 108, 108, 111] b'hello'

a = "a\u0300 propos"
print(list(a), a)

# ['a', '̀', ' ', 'p', 'r', 'o', 'p', 'o', 's'] à propos
```

## 4 `f""` を使う

## 5 式が複雑になってきたら、より小さな部分に分けてロジックをヘルパー関数に移す

## 6 複数代入アンパックをする

## 7 range ではなく enumerate を使う

## 8 イテレータの並列に zip を使う

## 9 for や while の後で else を使わない

## 10 `:=` 代入式を活用する
