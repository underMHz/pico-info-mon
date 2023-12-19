from machine import Pin, I2C
import sh1106
from PicoDHT22 import PicoDHT22

import utime
import network
import urequests
import uasyncio as asyncio

from misakifont import MisakiFont

####################
# OLED
#	GND -> GND
#	VCC -> 3.3V
#	SCK -> GPIO 27 (SCK=SCL) I2C1  (Line 43)
#	SDA -> GPIO 26                 (Line 44)
####################

####################
#	DHT22
#	VCC -> 3.3V
#	SDA -> GPIO 28                 (Line 149)
#	GND -> GND
####################

####################
#	以下は各自で入力
#	ssid = 'YOUR-SSID'                (Line 66)
#	password = 'YOUR-PASSWORD'        (Line 67)
#	location_id = 'YOUR-LOCATION-ID'  (Line 191)
#	news_api_key = 'YOUR-API-KEY'     (Line 228)
####################
'''
フォントの設定
'''
fcolor = 1
# フォントサイズは各行で設定するようにする
mf = MisakiFont()

'''
OLEDの設定と描画用の基本関数
'''
scl = Pin(27)
sda = Pin(26)
i2c = I2C(1, sda=sda, scl=scl, freq=400000)
oled = sh1106.SH1106_I2C(128, 64, i2c)

def show_text(text, x, y, fsize):
    for c in text:
        
        d = mf.font(ord(c))
        show_bitmap(oled, d, x, y, fcolor, fsize)
        x += 8 * fsize
    oled.show()

def show_bitmap(oled, fd, x, y, color, size):
    for row in range(0, 7):
        for col in range(0, 7):
            if (0x80 >> col) & fd[row]:
                oled.fill_rect(int(x + col * size), int(y + row * size), size, size, color)

'''
WiFiに接続するための設定
'''
ssid = 'YOUR-SSID'
password = 'YOUR-PASSWORD'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

# 起動メッセージ
boot_str = '起動中…'
show_text(boot_str, 0, 8, 1)
show_text(ssid, 0, 24, 1)
show_text(password, 0, 32, 1)

# 接続確立まで待機
max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    wait_str = 'WiFi接続中…'
    show_text(wait_str, 0, 48, 1)
    print(wait_str)
    utime.sleep(1)
    
# 基板上のLED点滅用関数
def blink_onboard_led(num_blinks):
    led = machine.Pin('LED', machine.Pin.OUT)
    for i in range(num_blinks):
        led.on()
        utime.sleep(.2)
        led.off()
        utime.sleep(.2)

wlan_status = wlan.status()
blink_onboard_led(wlan_status)
print('Status code:' +str(wlan_status))

# Handle connection error
# Error meanings
# 0  Link Down
# 1  Link Join
# 2  Link NoIp
# 3  Link Up
# -1 Link Fail
# -2 Link NoNet
# -3 Link BadAuth

if wlan_status != 3:
    status_str = '×NG：再起動してください'
    show_text(status_str, 0, 56, 1)
    raise RuntimeError('Wi-Fi connection failed')
else:
    print('Connected')
    status = wlan.ifconfig()
    print('ip = ' + status[0])
    status_str = '◎OK：起動します。'
    show_text(status_str, 0, 56, 1)
    utime.sleep(3)

#画面初期化
oled.fill(0)

'''
各種関数の定義
'''
def show_text_scroll(text, x, y, fsize, scroll_speed):
    for i in range(len(text) * 8 * fsize + 128):  # 文字列の幅 + 画面幅
        oled.fill_rect(0, y, 128, 16, 0)  # 文字列が通過する領域をクリア
        show_text(text, x - i, y, fsize)  # 文字列を描画
        await asyncio.sleep_ms(scroll_speed)

# 日付を取得
def get_formatted_time():
    current_time = utime.localtime()
    formatted_time = '{:d}月{:d}日({}){:02d}:{:02d}'.format(
        current_time[1], current_time[2], 
        ('月', '火', '水', '木', '金', '土', '日')[current_time[6]], 
        current_time[3], current_time[4]
    )
    return formatted_time

# 温湿度を取得
def get_dht22():
    # DHT22センサのピン番号
    dht_pin = 28
    dht22 = PicoDHT22(Pin(dht_pin,Pin.IN,Pin.PULL_UP))

    # 温湿度の取得
    temperature, humidity = dht22.read()

    if temperature is None:
        temperature = '??'
        humidity = '??'
        thi_value = '??'
        judgement = '??'
        
    else:
        # 不快指数THIの計算
        thi_value = 0.81 * temperature + 0.01 * humidity * (0.99 * temperature - 14.3) + 46.3
        # 判定
        if thi_value <= 55:
            judgement = '寒い'
        elif 55 < thi_value <= 60:
            judgement = 'やや寒い'
        elif 60 < thi_value <= 65:
            judgement = '不感'
        elif 65 < thi_value <= 70:
            judgement = '快い'
        elif 70 < thi_value <= 75:
            judgement = '暑くない'
        elif 75 < thi_value <= 80:
            judgement = 'やや暑い'
        elif 80 < thi_value <= 85:
            judgement = '暑い'
        else:
            judgement = '特に暑い'
            
        thi_value = int(thi_value)
        
    return temperature, humidity, thi_value, judgement
    
# 天気予報の取得（API）https://weather.tsukumijima.net/
def get_weather_data():
    weather_url = 'https://weather.tsukumijima.net/api/forecast'
    # location_idは次から取得する（例えば名古屋の天気なら230010） https://weather.tsukumijima.net/primary_area.xml
    location_id = 'YOUR-LOCATION-ID' 
    weather_url_with_id = '{}?city={}'.format(weather_url, location_id)

    response = urequests.get(weather_url_with_id)
    weather_data = response.json()
    response.close()

    if response.status_code == 200:
        # たまにNullが返ってくるので、Nullを「？」表示にする関数
        def handle_null(value):
            return '？' if value is None else str(value)

        # jsonから特定のデータ取得（今日の情報）
        today_weather = handle_null(weather_data['forecasts'][0]['telop'])
        #美咲フォントに「曇」という文字がないため、「雲」という文字に置き換え
        today_weather = today_weather.replace('曇', '雲')
        today_max_temp = handle_null(weather_data['forecasts'][0]['temperature']['max']['celsius'])
        today_min_temp = handle_null(weather_data['forecasts'][0]['temperature']['min']['celsius'])

        # jsonから特定のデータ取得（明日の情報）
        tomorrow_weather = handle_null(weather_data['forecasts'][1]['telop'])
        tomorrow_weather = tomorrow_weather.replace('曇', '雲')
        #美咲フォントに「曇」という文字がないため、「雲」という文字に置き換え
        tomorrow_max_temp = handle_null(weather_data['forecasts'][1]['temperature']['max']['celsius'])
        tomorrow_min_temp = handle_null(weather_data['forecasts'][1]['temperature']['min']['celsius'])
        
    else:
        # サーバーから返って来なかった場合
        today_weather, today_max_temp, today_min_temp = '？', '？', '？'
        tomorrow_weather, tomorrow_max_temp, tomorrow_min_temp = '？', '？', '？'
        
    return today_weather, today_max_temp, today_min_temp, tomorrow_weather, tomorrow_max_temp, tomorrow_min_temp

# ニュースの取得（API）https://newsapi.org/
def get_news_data():
    news_url = 'https://newsapi.org/v2/top-headlines'
    # API Keyは次から取得できる（要登録。メアドのみで無料）。 https://newsapi.org/
    news_api_key = 'YOUR-API-KEY'
    country = 'jp'
    # 返答が多いとメモリが圧迫されるのでNHKのニュースのみに絞る
    query = 'nhk.or.jp'

    # リクエストヘッダーの設定（User-Agentを設定しないとなぜか怒られる。名前はなんでもよさそう）
    headers = {'User-Agent': 'hogehoge'}
    # リクエストパラメータの設定
    params = '?country={}&apiKey={}&q={}'.format(country, news_api_key, query)
    response = urequests.get(news_url + params, headers=headers)
    news_data = response.json()
    response.close()
    
    if response.status_code == 200:
        if not news_data or not news_data['articles']:
            output_article = 'ニュースを取得しています。'
        else:
            output_article = news_data['articles'][0]['title'] + ' = ' + news_data['articles'][0]['description']

    else:
        output_article = 'サーバエラーが起きている可能性があります。'
    print(output_article)
    return output_article

'''
予め表示しておく部分
'''
# 1～2行目を囲うフレームを描画
oled.rect(0, 0, 128, 27, 1)
# 描写が変わらない部分（2行目）
pre_str = '不快指数：　　　●状態：　　'
show_text(pre_str, x=0, y=10, fsize=1)

'''
uasyncioで非同期処理を実現
'''
async def update_first_second_lines():
    while True:
        # フレーム該当部分塗りつぶし（多重描写防止）
        oled.fill_rect (1, 1, 126, 8, 0)
        oled.fill_rect (40, 10, 16, 8, 0)
        oled.fill_rect (96, 10, 16, 8, 0)
        
        # 温湿度取得用関数で各種変数を取得
        temperature, humidity, thi_value, judgement = get_dht22()
        
        # 描画位置初期化
        x = 0
        y = 2

        # 1行目
        fsize = 1
        str1 = '●{}℃ 　●{}％'.format(temperature, humidity)
        show_text(str1, x, y, fsize)

        # 2行目
        fsize = 1
        y += 8
        str2 = '　　　　　{}　　　　　{}'.format(thi_value, judgement)
        show_text(str2, x, y, fsize)
        
        await asyncio.sleep(1)  # 5秒ごとに更新
        
async def update_third_lines():
    while True:
        
        # フレーム該当部分塗りつぶし（多重描写防止）
        oled.fill_rect (1, 18, 126, 8, 0)
        
        # 温湿度取得用関数で各種変数を取得
        temperature, humidity, thi_value, judgement = get_dht22()
        
        # 描画位置初期化
        x = 0
        y = 10

        # 3行目
        fsize = 1
        y += 8
        str3 = '{}'.format(get_formatted_time())
        show_text(str3, x, y, fsize)
        
        await asyncio.sleep(1)  # 5秒ごとに更新
        
async def update_fourth_fifth_lines():
    while True:
        # 天気予報用関数で各種変数を取得
        today_weather, today_max_temp, today_min_temp, tomorrow_weather, tomorrow_max_temp, tomorrow_min_temp = get_weather_data()
        
        # 描画位置初期化
        x = 0
        y = 20
        
        # 4行目
        fsize = 1
        y += 8
        str4 = '今日：{} ↑{}℃↓{}℃'.format(today_weather, today_max_temp, today_min_temp)
        show_text(str4, x, y, fsize)

        # 5行目
        fsize = 1
        y += 8
        str5 = '明日：{} ↑{}℃↓{}℃'.format(tomorrow_weather, tomorrow_max_temp, tomorrow_min_temp)
        show_text(str5, x, y, fsize)

        await asyncio.sleep(300)  # 5分ごとに更新

async def update_last_line():
    while True:
        # 6行目
        fsize = 2
        y = 46
                
        # NEWS用関数で各種変数を取得（1日のリクエスト上限は1,000回）
        output_article = get_news_data()
        str6 = output_article
        
        text_width = len(str6) * 8 * fsize
        frame_width = 128
        animation_start = frame_width

        # 画面の初期化
        oled.fill_rect(0, y, frame_width, 16, 0)  # 指定した範囲をクリア

        # 2分ごとにループを抜ける
        loop_minutes = 2
        
        # アニメーションループ
        for _ in range(int(loop_minutes * 60 / 0.5)):
            oled.fill_rect(0, y, frame_width, 16, 0)  # 指定した範囲をクリア
            show_text(str6, animation_start, y, fsize)
            oled.show()
            animation_start -= 16 * 4
            if animation_start <= -text_width:
                animation_start = frame_width
            await asyncio.sleep(0.5)  # アニメーションの速さ調整
        
        oled.fill_rect(0, y, frame_width, 16, 0)  # 指定した範囲をクリア
        
        # ニュース取得までの読み込みメッセージ
        wait_str = 'ニュース取得中…'
        show_text(wait_str, 0, y, fsize)

# 非同期処理
async def main():
    asyncio.create_task(update_first_second_lines())
    asyncio.create_task(update_third_lines())
    asyncio.create_task(update_fourth_fifth_lines())
    asyncio.create_task(update_last_line())

    while True:
        await asyncio.sleep(1)  # メインループが終わらないように

asyncio.run(main())
