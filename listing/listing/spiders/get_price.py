import requests
import simplejson as json
from decimal import Decimal
from threading import Thread
import time
from time import sleep

user = '14974301'
key = 'RCV9NqYdMxt7R0'
price_min = Decimal("0.00000500")

def price_crawling():
    global price_min
    r = requests.get('https://www.cryptopia.co.nz/api/GetMarkets/BTC/')
    obj = json.loads(r.text)
    for x in obj['Data']:
        for k, v in x.iteritems():
            if ('Label' in k) and ('HAC/BTC' in v):
                last_price = Decimal(x['LastPrice'])
                if (price_min < last_price):
                    price_min = last_price
                    message = "%s: LastPrice: %s" % (time.ctime(time.time()), x['LastPrice'])
                    payload = {'user': user, 'pass': key, 'msg': message}
                    r = requests.post('https://smsapi.free-mobile.fr/sendmsg?', params=payload)

def call_at_interval(period, callback, args):
    while True:
        sleep(period)
        callback(*args)

def setInterval(period, callback, *args):
    Thread(target=call_at_interval, args=(period, callback, args)).start()

setInterval(20, price_crawling)
