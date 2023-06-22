# Chapter 8 頑健性と性能

## 65 try/except/else/finallyを活用する

## 66 contextlibとwith文をtry/finallyの代わりに考える

`with func() as foo`で受けるには`yield`する

## 67 ローカルクロックにはdatetimeを使う

```py
import pytz
from datetime import datetime

time_format = "%Y-%m-%d %H:%M:%S"
arrival_nyc = "2019-03-16 23:33:24"
nyc_dt_naive = datetime.strptime(arrival_nyc, time_format)
eastern = pytz.timezone("US/Eastern")
nyc_dt = eastern.localize(nyc_dt_naive)
print(nyc_dt)
utc_dt = pytz.utc.normalize(nyc_dt.astimezone(pytz.utc))
print(utc_dt)
pacific = pytz.timezone("US/Pacific")
sf_dt = pacific.normalize(utc_dt.astimezone(pacific))
print(sf_dt)
# 2019-03-16 23:33:24-04:00
# 2019-03-17 03:33:24+00:00
# 2019-03-16 20:33:24-07:00
```

## 68 copyregでpickleを信頼できるようにする
