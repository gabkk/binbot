import scrapy
import requests
import time
from scrapy.crawler import CrawlerRunner
from scrapy.selector import Selector
from twisted.internet import reactor, task
from twisted.internet.task import LoopingCall

user = '14974301'
key = 'RCV9NqYdMxt7R0'
old_gainer = []

class ListingSpider(scrapy.Spider):
    name = "listing"
    def start_requests(self):
        urls = [
            'https://coinmarketcap.com/exchanges/binance/',
            'https://coinmarketcap.com/exchanges/cryptopia/'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def get_currencies(self, response, platform_name, xpath_ref):
        filename = platform_name + '_listing'
        with open(filename, 'wb') as f:
            currency = []
            listing_pair = Selector(text=response.body).xpath(".//a[starts-with(@href,'" + xpath_ref + "')]//text()").extract()
            for x in listing_pair:
                splitter = x.split("/")
                if 'BTC' in splitter[0]:
                    currency.append(splitter[1])
                elif 'BTC' in splitter[1]:
                    currency.append(splitter[0])
            for y in currency:
                f.write(y + '\n')
            self.log('Saved file %s' % filename)

    def parse(self, response):
        if 'binance' in response.url:
            self.get_currencies(response, 'binance', 'https://www.binance.com/trade.html?symbol=')
        elif 'cryptopia' in response.url:
            self.get_currencies(response, 'cryptopia', 'https://www.cryptopia.co.nz/Exchange?market=')

class GainersSpider(scrapy.Spider):
    name = "gainers"

    def start_requests(self):
        urls = [
            'https://coinmarketcap.com/gainers-losers/#gainers-1h',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        global old_gainer
        filename = 'one_hour_gainers'
        cryptopia = 'cryptopia_listing'
        currencies_list = []
        with open(cryptopia, 'r') as crypt_file:
            currencies_list = [line.rstrip('\n') for line in crypt_file]
            gainers_list = []
        top_gainers = Selector(text=response.body).xpath(".//div[contains(@id, 'gainers-1h')]//tr[starts-with(@id, 'id-gainers')]//td[contains(@class, 'text-left')]//text()").extract()
        for gainer in top_gainers:
            gainers_list.append(gainer)
        lst = set(gainers_list) & set(currencies_list)
        if (set(lst) != set(old_gainer)):
            old_gainer = lst
            message = "TOP GAINERS:%s :" % time.ctime(time.time())
            for l in lst:
                message = message + " " + l
            payload = {'user': user, 'pass': key, 'msg': message}
            r = requests.post('https://smsapi.free-mobile.fr/sendmsg?', params=payload)

def run_crawl():
    """
    Run a spider within Twisted. Once it completes,
    wait 5 seconds and run another spider.
    """
    runner = CrawlerRunner({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        })
    listing = runner.crawl(ListingSpider)
    deferred = runner.crawl(GainersSpider)
    return deferred

lc = LoopingCall(run_crawl)
lc.start(200)

reactor.run()
