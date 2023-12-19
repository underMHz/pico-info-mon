# pico-info-mon

「温度・湿度・不快指数・今日と明日の天気・ニュース」を表示するインフォメーションモニタです。

Raspberry Pi Pico WとDHT22（温湿度センサ）とOLED（128×64）を使います。

DHT22を使って温度と湿度、不快指数を取得します。また、APIを使って天気とニュースを取得します。

----

## 作例

gifgif

実際の動作の様子です。

3Dプリンタ等で筐体を作ると良いかと思います。

もし作ったら後ほどアップします。

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
|`GPIO26`||`SDA`||
|`GPIO27`|`SCL(SCK)`||
|`GPIO28`||`DATA`|

ピンアサインの画像ピンアサインの画像ピンアサインの画像

----

## ファイル構成

WIP

----
