# import scrapy
# from scrapy.selector import Selector
#
# class ListingSpider(scrapy.Spider):
#     name = "listing"
#     def start_requests(self):
#         urls = [
#             'https://coinmarketcap.com/exchanges/binance/',
#             'https://coinmarketcap.com/exchanges/cryptopia/'
#         ]
#         for url in urls:
#             yield scrapy.Request(url=url, callback=self.parse)
#
#     def get_currencies(self, response, platform_name, xpath_ref):
#         filename = platform_name + '_listing'
#         with open(filename, 'wb') as f:
#             currency = []
#             listing_pair = Selector(text=response.body).xpath(".//a[starts-with(@href,'" + xpath_ref + "')]//text()").extract()
#             for x in listing_pair:
#                 splitter = x.split("/")
#                 if 'BTC' in splitter[0]:
#                     currency.append(splitter[1])
#                 elif 'BTC' in splitter[1]:
#                     currency.append(splitter[0])
#             for y in currency:
#                 f.write(y + '\n')
#             self.log('Saved file %s' % filename)
#
#     def parse(self, response):
#         if 'binance' in response.url:
#             self.get_currencies(response, 'binance', 'https://www.binance.com/trade.html?symbol=')
#         elif 'cryptopia' in response.url:
#             self.get_currencies(response, 'cryptopia', 'https://www.cryptopia.co.nz/Exchange?market=')
