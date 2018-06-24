import curses
import time
import datetime
import os
from binance.enums import *
from binance.exceptions import BinanceAPIException, BinanceRequestException, BinanceWithdrawException

class Window():

    def __init__(self, client):
        
        # TODO Change this prices of 
        self._coin_prices = {}
        self._coin_prices_old = {}
        self._old_order_coins_price = []

        # create stdscr
        self.stdscr = curses.initscr()
        self.stdscr.clear()
        self.stdscr.nodelay(True)

        # allow echo, set colors
        curses.noecho()
        curses.cbreak()
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_RED, -1)
        curses.init_pair(2, curses.COLOR_GREEN, -1)
        curses.init_pair(3, curses.COLOR_BLUE, -1)
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLUE)
        self.color = 0


        # TODO Make this proprely already call in commande
        self._client = client
        # Set each windows size
        rows, columns = os.popen('stty size', 'r').read().split()
        self.first_draw = 0
        self.redraw = 0
        self.rows = rows
        self.columns = columns
        self.tot_column_len_price = 0
        self.size_display_windows = int(rows) / 3
        # where BTC price start
        self.size_top_menu = 5

        size_logger = 6
        size_cmd_windows = 3
        size_result_cmd_windows = int(rows) - (self.size_top_menu + self.size_display_windows + size_cmd_windows + size_logger)

        pos_top_menu = 0
        pos_display_windows = pos_top_menu + self.size_top_menu
        pos_cmd_windows = pos_display_windows + self.size_display_windows
        pos_result_cmd_windows = pos_cmd_windows + size_cmd_windows
        pos_logger = pos_result_cmd_windows + size_result_cmd_windows

        #TODO change this parameter
        self.menu_view = "history"
        self.display_menu_window = curses.newwin(self.size_top_menu, int(columns), pos_top_menu, 0)
        self.display_window = curses.newwin(self.size_display_windows, int(columns), pos_display_windows, 0)
        self.cmd_window = curses.newwin(size_cmd_windows, int(columns), pos_cmd_windows, 0)
        self.result_cmd_window = curses.newwin(size_result_cmd_windows, int(columns), pos_result_cmd_windows, 0)
        self.logger = curses.newwin(size_logger, int(columns), pos_logger, 0)
        self.cmd_window.keypad(1)
        self.cmd_window.box()
        curses.curs_set(0)

        # Set each windows border
        self.display_window.border()
        self.result_cmd_window.border()
        self.logger.border()
        self.cmd_window.refresh()
        self.result_cmd_window.refresh()
        self.display_window.refresh()
        self.logger.refresh()

    def display_in_logger(self, str):
        self.logger.clear()
        self.logger.addstr(1, 1, str)
        self.logger.border()
        self.logger.refresh()

    def init_list_of_price(self, coin_in_balance, market_prices):
        # x = {u'symbol': u'BNBBTC', u'price': u'0.04661000'}
        # x['symbol'] = BNBBTC
        # coin = {u'locked': u'1316.00000000', u'asset': u'XVG', u'free': u'0.18300000'}
        # coin['asset'] = BTC
        self.display_window.clear()
        if len(coin_in_balance) > 0:        
            for coin in coin_in_balance:
                for x in market_prices:
                    if str(x['symbol']) == str(coin['asset'])+"BTC":
                        self._coin_prices.update({str(x['symbol']): x["price"]})
                        self._coin_prices_old.update({str(x['symbol']): x["price"]})
        self.display_window.refresh()
        self.print_prices()

    def get_prices(self):
        return self._coin_prices

    def get_coin_in_balance(self):
        coin_in_balance = []
        perso_info = {}
        global_info = self._client.get_account()
        for k, v in global_info.iteritems():
            if k == "balances":
                for coin in v:
                    if float(coin['locked']) != 0. or float(coin['free']) != 0.:
                        coin_in_balance.append(coin)
        return coin_in_balance

    def my_raw_input(self, r, c, prompt_string):
        test = ""
        #self.cmd_window.erase()
        self.cmd_window.border()
        self.cmd_window.addstr(r, c, prompt_string)
        #input = self.cmd_window.getstr(r + 1, c + 1)
        self.display_window.refresh()
        test = self.cmd_window.getch()

        return test

    def print_char_from_user(self):
        self.cmd_window.erase()

    #TODO store coin.prices in the same place -> commande _coins _list_coins duplicated ?
    def remove_all_coin(self):
        i = 1
        for k, v in self._coin_prices.items():
            i += 1
            # Don't delete btcusdt, we need one coin to use the websocket
            # and call print_coins which update the price
            if k == "BTCUSDT":
                continue
            del self._coin_prices[k]
            del self._coin_prices_old[k]

    #TODO store coin.prices in the same place -> commande _coins _list_coins duplicated ?
    def remove_coin(self, coin):
        # coin_price: {'XLMBTC': u'0.00003129'}
        # coin: trxbtc@aggTrade
        i = 1
        coin = coin.split("@", 2)[0].upper()
        self.display_in_logger("coin: "+ str(coin) + "  !! coin_price: " + str(self._coin_prices))
        for k, v in self._coin_prices.items():
            i += 1
            if k == coin:
                del self._coin_prices[k]
                del self._coin_prices_old[k]

    #TODO make this better
    def redraw_command_line(self, command, curpos):
        i = 1
        result = " "
        self.cmd_window.clear()
        for d in command:
            if i-1 == curpos:
                self.cmd_window.addstr(1, i, str(d), curses.color_pair(3))
            else:
                self.cmd_window.addstr(1, i, str(d))
            result = result + d
            i+=1
        self.cmd_window.refresh()

    # TODO DIRTY
    def result_display_spec(self, screen, history):
        screen.clear()
        screen.border()
        i = 1
        for result in history:
            screen.addstr(i, 1, result)
            i += 1
            if i > 20:
                break
        screen.refresh()

    # TODO DIRTY Create generic display function
    def result_display(self, screen, history):
        screen.clear()
        screen.border()
        i = 1
        for result in history:
            screen.addstr(i, 1, str(result) + " iter = " + str(i))
            i += 1
        screen.refresh()

    def set_old_prices(self, old_order_coins_price):
        self._old_order_coins_price = old_order_coins_price

    def set_menu_value(self, value):
        self.first_draw = 0
        self.menu_view = value

    def update_price(self, pair):
        self._coin_prices.update({str(pair["symbol"]): pair["price"]})
        self._coin_prices_old.update({str(pair["symbol"]): pair["price"]})

    def display_menu(self):
        self.display_menu_window.clear()
        self.display_in_logger("Value of menue.view" + self.menu_view)
        if self.menu_view == "history":
            self.display_menu_window.addstr(1, 1, "  History  ", curses.color_pair(4))
            self.display_menu_window.addstr(1, len("  History  "), "  Wallet  ", curses.color_pair(3))
            self.display_menu_window.addstr(1, len("  History  "+"  Wallet  "), "  Order  ", curses.color_pair(3))
            self.display_menu_window.addstr(1, len("  History  "+"  Wallet  "+"  Order  "), "  Bot  ", curses.color_pair(3))
        elif self.menu_view == "order":
            self.display_menu_window.addstr(1, 1, "  History  ", curses.color_pair(3))
            self.display_menu_window.addstr(1, len("  History  "), "  Wallet  ", curses.color_pair(3))
            self.display_menu_window.addstr(1, len("  History  "+"  Wallet  "), "  Order  ", curses.color_pair(4))
            self.display_menu_window.addstr(1, len("  History  "+"  Wallet  "+"  Order  "), "  Bot  ", curses.color_pair(3))
        elif self.menu_view == "wallet":
            self.display_menu_window.addstr(1, 1, "  History  ", curses.color_pair(3))
            self.display_menu_window.addstr(1, len("  History  "), "  Wallet  ", curses.color_pair(4))
            self.display_menu_window.addstr(1, len("  History  "+"  Wallet  "), "  Order  ", curses.color_pair(3))
            self.display_menu_window.addstr(1, len("  History  "+"  Wallet  "+"  Order  "), "  Bot  ", curses.color_pair(3))
        elif self.menu_view == "bot":
            self.display_menu_window.addstr(1, 1, "  History  ", curses.color_pair(3))
            self.display_menu_window.addstr(1, len("  History  "), "  Wallet  ", curses.color_pair(3))
            self.display_menu_window.addstr(1, len("  History  "+"  Wallet  "), "  Order  ", curses.color_pair(3))
            self.display_menu_window.addstr(1, len("  History  "+"  Wallet  "+"  Order  "), "  Bot  ", curses.color_pair(4))
        self.display_menu_window.border()
        self.display_menu_window.refresh()

    #TODO store tab[3 -4] as float
    def display_sending_order(self, tab, client):
        # API
        #   order = client.create_test_order(symbol='TRXBTC',side="SELL",type=ORDER_TYPE_LIMIT,timeInForce=TIME_IN_FORCE_GTC,quantity=1,price='1.00000010',timestamp=int(time.time()))
        #   
        #   {u'orderId': 30637958, u'clientOrderId': u'qvukDLzCXL2dhuj8iihdqa', u'origQty': u'1.00000000', u'symbol': u'T
        #   RXBTC', u'side': u'SELL', u'timeInForce': u'GTC', u'status': u'NEW', u'transactTime': 1519493840477, u'type': u'LIMIT', u'price':
        #   u'1.00000010', u'executedQty': u'0.00000000'}
        self.result_cmd_window.clear()
        self.result_cmd_window.addstr(1, 1, "Process "+ tab[1] + ", " + tab[2]) 
        self.result_cmd_window.addstr(2, 1, "Quantity:"+ str(float(tab[3])))
        self.result_cmd_window.addstr(3, 1, "Price satoshi: "+ str(tab[4]))
        self.result_cmd_window.addstr(4, 1, "Total Btc:"+ str(float(tab[4])/100000000*float(tab[3])))
        self.result_cmd_window.refresh()
        self.result_cmd_window.border()

        command = str(self.my_raw_input( 0, 0, 'Are you sure(PRESS y to confirm):'))
        self.result_cmd_window.clear()
        self.result_cmd_window.refresh()
        self.result_cmd_window.border()
        #ADD SUCCED ORDER WITH ID SOMEWHERE TO REMOVE IT
        if int(command) == 121:
            try:
                ret = client.create_order(symbol=tab[2],
                                        side=tab[1],
                                        type=ORDER_TYPE_LIMIT,
                                        timeInForce=TIME_IN_FORCE_GTC,
                                        quantity=tab[3],
                                        price='{0:.8f}'.format(float(tab[4])/100000000),
                                        timestamp=int(time.time()))
            except BinanceAPIException as e:
                self.result_cmd_window.addstr(2, 1, "Failed" + " Api code" + str(e.code) + ", message:" + e.message)
                pass
            else:
                self.result_cmd_window.addstr(2, 1, "SUCCED"+str(tab)+ ", ret:" + str(ret) )
        else:
            self.result_cmd_window.addstr(2, 1, "Command Canceled" )

    def display_all_orders(self, offset):
        all_orders = self._client.get_open_orders()
        for x in range(len(all_orders)):
            #Pos after USAGE
            self.result_cmd_window.addstr(x + offset, 2,
                                                all_orders[x]["side"]
                                                + " " + all_orders[x]["symbol"] 
                                                + " price:" + all_orders[x]["price"]
                                                + " quantity:" + all_orders[x]["origQty"]
                                                + " time: " + datetime.datetime.fromtimestamp(int(all_orders[x]["time"])/1000).strftime('%Y-%m-%d %H:%M:%S')
                                                )
        self.result_cmd_window.border()
        self.result_cmd_window.refresh()

    def display_order_usage(self):
        self.result_cmd_window.clear()
        self.result_cmd_window.addstr(2, 2, "Error expected format : ")
        self.result_cmd_window.addstr(3, 2, "order [b/s] [COIN] [QTY] [PRICE 1BTC = 100000000]")
        self.result_cmd_window.addstr(4, 2, "ex:   Order  b     trx    32    100")

    def display_bot_info(self, bot_list):
        if len(bot_list) == 0:
            self.result_cmd_window.clear()
            self.result_cmd_window.addstr(2, 2, "Not bot available ")
            self.result_cmd_window.addstr(3, 2, "bot add NAME <OPTION STARTEGIE>")
            self.result_cmd_window.addstr(4, 2, "bot list stategie")
            self.result_cmd_window.border()
            self.result_cmd_window.refresh()
        #self.result_cmd_window.addstr(3, 2, "order [b/s] [COIN] [QTY] [PRICE 1BTC = 100000000]")
        #self.result_cmd_window.addstr(4, 2, "ex:   Order  b     trx    32    100")



    def display_wallet(self):
        #TODO Check la largeur de windows
        self.result_cmd_window.clear()
        self.result_cmd_window.addstr(1, 1, "Coin")
        self.result_cmd_window.addstr(1, 10, "Q-Free")
        self.result_cmd_window.addstr(1, 20, "Q-Order")
        self.result_cmd_window.addstr(1, 30, "Q-Total")
        self.result_cmd_window.addstr(1, 45, "V-Token")
        self.result_cmd_window.addstr(1, 65, "V-Total btc")
        self.result_cmd_window.addstr(1, 80, "BTC/BUY")
        self.result_cmd_window.addstr(1, 95, "ETH/BUY")
        
        #self.old_trade = 


        #TODO get only symbol from account
        #Check execpions
        market_prices = self._client.get_symbol_ticker()
        coin_in_balance = self.get_coin_in_balance()

        i = 3
#        self.check_bying_price(coin_in_balance)
        for coin in coin_in_balance:
            vbtc = ""
            value_per_token = ""
            asset = str(coin['asset'])
            coin_locked = float(coin['locked'])
            coin_free = float(coin['free'])
            # Skip this coin if we have less than one
            if coin_free + coin_locked < 1:
                continue
            for lm in market_prices:
                if str(lm['symbol'][:-3]) == asset:
                    vbtc = (coin_free + coin_locked) * float(lm['price'])
                    vbtc = "{:.8f}".format(vbtc)
                    value_per_token = lm['price']
                    break
            locked = ""
            if coin_locked <= 0.:
                locked = "0"
            else:
                locked = "{:.2f}".format(coin_locked)
            if coin_locked + coin_free >= 0.:
                coin_name = asset + " "
                free_coin = str("{:.2f}".format(coin_free))
                total_coin = str(coin_locked + coin_free)
                #trades = client.get_my_trades(symbol='TRXBTC')
                #for trade in trades:
                #    if x['isBuyer']:

                self.result_cmd_window.addstr(i, 1, coin_name)
                self.result_cmd_window.addstr(i, 10, free_coin)
                self.result_cmd_window.addstr(i, 20, locked)
                self.result_cmd_window.addstr(i, 30, total_coin)
                self.result_cmd_window.addstr(i, 45, str(value_per_token))
                self.result_cmd_window.addstr(i, 65, vbtc)
                if len(self._old_order_coins_price) > 0:
                    for coins_trades in self._old_order_coins_price:
                        if coins_trades['symbol'][:-3] == asset:
                            if coins_trades['symbol'][-3:] == "BTC":
                                self.result_cmd_window.addstr(i, 80, coins_trades['price_token'])
                            elif coins_trades['symbol'][-3:] == "ETH":
                                self.result_cmd_window.addstr(i, 95, coins_trades['price_token'])
                i += 1
        self.result_cmd_window.border()
        self.result_cmd_window.refresh()


    def print_prices(self):
 #       if len(self._coin_prices_old) != len(self._coin_prices):
 #           self.display_window.clear()
 #       self.display_window.clear()
        klen = 0
        #We start to display other coin at position 3, Btc start at 1
        pos_raw = 1
        pos_col = 1
        column_tot = 1

        # TODO make it works actually the function display_orders is called too often
        # it raise an exception
        if self.first_draw == 0:
            if self.menu_view == "wallet":
                self.display_wallet()
            elif self.menu_view == "order":
                self.result_cmd_window.clear()
                self.display_all_orders(1)

        #CLEAN OLD PRICE
        if self.first_draw == 10:
            self.redraw = 1
            self.display_window.clear()
            self.display_window.border()
            self.display_window.refresh()

        if len(self._coin_prices) > 0:
            #TODO add a check if too much coin
            for k, v in self._coin_prices.items():
                if k in self._coin_prices_old:
                    if str(k) == "BTCUSDT":
                        # change this by responsive pos 
                        self.display_window.addstr(3, 70, "The King ")
                        klen = len("The King ") + 70
                        if self.first_draw == 0 or self.redraw == 1:
                            v = "{:.2f}".format(float(v))
                            self.color = curses.color_pair(0)
                        elif float(self._coin_prices_old[k]) > float(v):
                            v = "{:.2f}".format(float(v))
                            self.color = curses.color_pair(1)
                        elif float(self._coin_prices_old[k]) < float(v):
                            v = "{:.2f}".format(float(v))
                            self.color = curses.color_pair(2)
                        elif float(self._coin_prices_old[k]) == float(v):
                            continue
                        self.display_window.addstr(3, klen, v, self.color)
                    elif k != "":
                        self.display_window.addstr(pos_raw, pos_col,  str(k) + " ,price: ")
                        klen = len( str(k) + " ,price: ") + pos_col
                        if self.first_draw == 0 or self.redraw == 1:
                            self.color = curses.color_pair(0)
                        elif float(self._coin_prices_old[k]) > float(v):
                            self.color = curses.color_pair(1)
                        elif float(self._coin_prices_old[k]) < float(v):
                            self.color = curses.color_pair(2)
                        elif float(self._coin_prices_old[k]) == float(v):
                            pos_raw += 1
                            self.tot_column_len_price = len(v) + klen
                            if pos_raw + 1 == self.size_display_windows:
                                pos_col = self.tot_column_len_price + 1
                                pos_raw = 1
                            continue
                        self.display_window.addstr(pos_raw, klen, str(v), self.color)
                        self.tot_column_len_price = len(v) + klen
                        # self.display_in_logger("size windows" +str(self.size_display_windows)+" len_price"+str(self.tot_column_len_price)+" ,raw:" + str(pos_raw))
                        pos_raw += 1
                        if pos_raw + 1 == self.size_display_windows:
                            pos_col = self.tot_column_len_price + 1
                            pos_raw = 1

                #else:
                #    self.display_window.addstr(pos, 1, k + " ,price: ")
                #    self.display_window.addstr(pos, klen, v, curses.color_pair(0))
        self.first_draw += 1
        self.redraw = 0
        self.display_window.border()
        self.display_window.refresh()

    def display_prices(self, msg):
        #global compteur
        self._coin_prices.update({msg['data']['s']: msg['data']['p']})
        self.print_prices()
        self._coin_prices_old.update({msg['data']['s']: msg['data']['p']})

    def close_ncurses(self):
        curses.nocbreak()
        curses.noecho()
        curses.endwin()
