# pico-info-mon

「温度・湿度・不快指数・今日と明日の天気・ニュース」を表示するインフォメーションモニタです。

Raspberry Pi Pico WとDHT22（温湿度センサ）とOLED（128×64）を使います。

DHT22を使って温度と湿度、不快指数を取得します。また、APIを使って天気とニュースを取得します。

----

## 開発環境

・MicroPython(v1.20.0)

・Thonny(v4.1.4)

----

## 作例

![動作](img/example.gif)

実際の動作の様子です。

筐体は3Dプリンタ（光造形）で作製しています。

STLファイルは[case.stl](https://github.com/underMHz/pico-info-mon/blob/main/case.stl)にあります。

----

## 使用部品

- [Raspberry Pi Pico W](https://amzn.asia/d/fJI15SC)
    - :warning: 通信するので「W」付きのPicoを使う。
- [DHT22（温湿度センサ）](https://amzn.asia/d/5zzBtHi)
- [OLED（128×64）](https://amzn.asia/d/5zzBtHi)
    - :warning: ドライバICがSH1106のものとSSD1306のものがある。今回使ったのは「SH1106」のもの。
- [そのほかいろいろ](https://amzn.asia/d/8PSwdhR)
    - :warning: 全てAmazonのリンクなので、もしリンク切れしている場合は各自で検索してください。
 
----

## 接続

|PicoW|OLED|DHT22|
|:--|:--|:--|
|`3V3`|`VCC`|`VCC`|
|`GND`|`GND`|`GND`|
|`GPIO26`|`SDA`||
|`GPIO27`|`SCL(SCK)`||
|`GPIO28`||`DATA`|

![ピンアサイン](img/picow_pin.png)

----

## ファイル構成

- ThonnyからPython Package Index(PyPI)からインストールするライブラリ

`micropython_uasyncio`

`micropython_urequests`

- 外部でインストールしてから追加するライブラリ

`sh1106.py`
https://github.com/robert-hh/SH1106/blob/master/sh1106.py

`PicoDHT22.py`
https://github.com/danjperron/PicoDHT22/blob/main/PicoDHT22.py

- 使用するフォント

`misakifont`（美咲フォント）
https://github.com/Tamakichi/pico_MicroPython_misakifont/tree/main/misakifont

❓美咲フォントについて
https://littlelimit.net/misaki.htm

RASPBERRY PI PICO<br>
│&nbsp;&nbsp;main.py<br>
│&nbsp;&nbsp;PicoDHT22.py<br>
│&nbsp;&nbsp;sh1106.py<br>
│<br>
├─lib<br>
│&nbsp;&nbsp;&nbsp;&nbsp;├─micropython_uasyncio-3.1.1.dist-info<br>
│&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;（略）<br>
│&nbsp;&nbsp;&nbsp;&nbsp;│<br>
│&nbsp;&nbsp;&nbsp;&nbsp;├─micropython_uasyncio.core-2.3.dist-info<br>
│&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;（略）<br>
│&nbsp;&nbsp;&nbsp;&nbsp;│<br>
│&nbsp;&nbsp;&nbsp;&nbsp;├─micropython_urequests-0.9.1.dist-info<br>
│&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;（略）<br>
│&nbsp;&nbsp;&nbsp;&nbsp;│<br>
│&nbsp;&nbsp;&nbsp;&nbsp;├─uasyncio<br>
│&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;（略）<br>
│&nbsp;&nbsp;&nbsp;&nbsp;│<br>
│&nbsp;&nbsp;&nbsp;&nbsp;└─urequests<br>
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;（略）<br>
│<br>
└─misakifont<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;（略）<br>
        
----
