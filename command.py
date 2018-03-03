from binance.enums import *
from binance.exceptions import BinanceAPIException, BinanceRequestException, BinanceWithdrawException
import datetime
import time


#remove this
import sys

help_str = [' AVAILABLE COMMANDS\n', \
            ' ad -> to add a new coin, ex: ac iota\n',\
            ' rm -> to rm an existing coin, ex: rm iota\n'\
            ' wa -> display_wallet\n'\
            ' order -> pass an order\n'\
            ' quit -> exit binbot'\
            ]

class Command():
    def __init__(self, window, bm, client, coins):
        self._window = window
        self._bm = bm
        self._coins = coins
        self._client = client
        self._list_coins = []

    def display_help(self):
        self._window.result_display_spec(self._window.result_cmd_window, help_str)

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

    def display_wallet(self):
        self._window.result_cmd_window.clear()
        self._window.result_cmd_window.addstr(1, 1, "Qty")
        self._window.result_cmd_window.addstr(1, 20, "Order")
        self._window.result_cmd_window.addstr(1, 30, "Total")
        #TODO get only symbol from account
        #Check execpions
        market_prices = self._client.get_symbol_ticker()
        coin_in_balance = self.get_coin_in_balance()
        i = 3
        for coin in coin_in_balance:
            vbtc = ""
            for lm in market_prices:
                if str(lm['symbol'][:-3]) == str(coin['asset']):
                    vbtc = (float(coin['free']) + float(coin['locked'])) * float(lm['price'])
                    vbtc = "{:.8f}".format(vbtc)
                    break
            locked = ""
            if float(coin['locked']) <= 0.:
                locked = "0"
            else:
                locked = "{:.2f}".format(float(coin['locked']))
            self._window.result_cmd_window.addstr(i, 1, str(coin['asset']) + ":" + str("{:.2f}".format(float(coin['free']))))
            self._window.result_cmd_window.addstr(i, 20, locked)
            self._window.result_cmd_window.addstr(i, 30, vbtc)
            i += 1
        self._window.result_cmd_window.border()
        self._window.result_cmd_window.refresh()

    def add_coin_fct(self, command):
        new_coin = command.split(" ", 2)[1]
        prices = self._client.get_all_tickers()
        for pair in  prices:
            if str(pair["symbol"]) == new_coin.upper() + "BTC":
                self._window.update_price(pair)
        self._window.print_prices()

        new_coin = new_coin.lower() + "btc@aggTrade"
        if new_coin not in self._coins:
            self._coins.append(new_coin)
        else:
            return "coin already register: " + new_coin + "\n", self._coins            
        return "new coin add to list: " + new_coin + "\n", self._coins

    def del_coin_fct(self, command):
        new_coin = command.split(" ", 2)[1]
        self._window.display_window.clear()
        if new_coin == "all":
            for x in self._coins:
                self._coins.remove(x)
                self._window.remove_all_coin()
            self._window.print_prices()
            return "delete all coin in list" + str(), self._coins
        coin_symbole = new_coin.upper() + "BTC"
        new_coin = new_coin.lower() + "btc@aggTrade"
        if new_coin in self._coins:
            self._coins.remove(new_coin)
            self._window.remove_coin(coin_symbole)
            self._window.print_prices()
            return "new coin delete to list: " + new_coin + "\n", self._coins
        else:
            return "coin doesn't exist" + "\n", self._coins

    def display_order_usage(self):
        self._window.result_cmd_window.addstr(2, 2, "Error expected format : ")
        self._window.result_cmd_window.addstr(3, 2, "order [b/s] [COIN] [QTY] [PRICE 1BTC = 100000000]")
        self._window.result_cmd_window.addstr(4, 2, "ex: order b     trx    32    100")

    def display_all_orders(self, offset):
        all_orders = self._client.get_open_orders()
        for x in range(len(all_orders)):
            #Pos after USAGE
            self._window.result_cmd_window.addstr(x + offset, 2,
                                                    all_orders[x]["side"]
                                                    + " " + all_orders[x]["symbol"] 
                                                    + " price:" + all_orders[x]["price"]
                                                    + " quantity:" + all_orders[x]["origQty"]
                                                    + " time: " + datetime.datetime.fromtimestamp(int(all_orders[x]["time"])/1000).strftime('%Y-%m-%d %H:%M:%S')
                                                    )

    def check_order(self,command):
        tab = command.split()
        if len(tab) < 5:
            self.display_order_usage()
            self.display_all_orders(5)
            return 0, tab
        if tab[1] != "b" and tab[1] != "s":
            self._window.result_cmd_window.addstr(1, 1, "Error:" + command + " should be b / s" )
            self.send_order_usage()
            return 0, tab
        try:
            int(tab[3])
        except ValueError:
            self._window.result_cmd_window.addstr(1, 1, str(tab[3])+" is not a number")
            return 0, tab
        else:
            tab[3] = int(tab[3])        
        try:
            int(tab[4])
        except ValueError:
            self._window.result_cmd_window.addstr(1, 1, str(tab[3])+" is not a number")
            return 0, tab
        else:
            tab[4] = int(tab[4])
        if tab[1] == "b":
            tab[1] = SIDE_BUY
        if tab[1] == "s":
            tab[1] = SIDE_SELL
        tab[2] = tab[2].upper()+"BTC"

        return 1, tab


    def send_order(self, command):

        # API
        #   order = client.create_test_order(symbol='TRXBTC',side="SELL",type=ORDER_TYPE_LIMIT,timeInForce=TIME_IN_FORCE_GTC,quantity=1,price='1.00000010',timestamp=int(time.time()))
        #   
        #   {u'orderId': 30637958, u'clientOrderId': u'qvukDLzCXL2dhuj8iihdqa', u'origQty': u'1.00000000', u'symbol': u'T
        #   RXBTC', u'side': u'SELL', u'timeInForce': u'GTC', u'status': u'NEW', u'transactTime': 1519493840477, u'type': u'LIMIT', u'price':
        #   u'1.00000010', u'executedQty': u'0.00000000'}
        self._window.result_cmd_window.clear()
        self._window.result_cmd_window.border()
        ret_check, tab = self.check_order(command)        
        if ret_check == 1:
            self._window.result_cmd_window.addstr(1, 1, "Process "+ tab[1] + ", " + tab[2]) 
            self._window.result_cmd_window.addstr(2, 1, "Quantity:"+ str(float(tab[3])))
            self._window.result_cmd_window.addstr(3, 1, "Price satoshi: "+ str(tab[4]))
            self._window.result_cmd_window.addstr(4, 1, "Total Btc:"+ str(float(tab[4])/100000000*float(tab[3])))
            self._window.result_cmd_window.refresh()
            #Fixer CE RAW INPUT
            command = str(self._window.my_raw_input( 0, 0, 'Are you sure(y/n):'))
            self._window.result_cmd_window.clear()
            if command == "y":
                try:
                    ret = self._client.create_order(symbol=tab[2],
                                            side=tab[1],
                                            type=ORDER_TYPE_LIMIT,
                                            timeInForce=TIME_IN_FORCE_GTC,
                                            quantity=tab[3],
                                            price=str(float(tab[4])/100000000),
                                            timestamp=int(time.time()))
                except BinanceAPIException as e:
                    self._window.result_cmd_window.addstr(2, 1, "Failed" + " Api code" + str(e.code) + ", message:" + e.message)
                    pass
                else:
                    self._window.result_cmd_window.addstr(2, 1, "SUCCED"+str(tab)+ ", ret:" + str(ret) )
            else:
                self._window.result_cmd_window.addstr(2, 1, "Command Canceled" )
        self._window.result_cmd_window.refresh()



    def parse_cmd(self, history, command):
        result = ""
        for c in command:
            result = result + c
        fcommand = result.split(" ", 2)[0]
        if "help" in fcommand:
            self.display_help()
            return history
        if "ad" in fcommand:
            result, self._coins = self.add_coin_fct(result)
            self._bm.start_multiplex_socket(self._coins, self._window.display_prices)
        elif "rm" in fcommand:
            result, self._coins = self.del_coin_fct(result)
            self._bm.close()
            self._bm.start_multiplex_socket(self._coins, self._window.display_prices)
        elif "wa" in fcommand:
            self.display_wallet()
            return history
        elif "order" in fcommand:
            self.send_order(result)
            return history
        else:
            result = "Unknow command '" + fcommand + "'"
        history.append(result)
        self._window.result_display(self._window.result_cmd_window, history)
        return history

    def close(self):
        self._window.close_ncurses()
        self._bm.close()

    def main_loop(self):
        history = []
        command = [" "]
        curpos = 0
        first_char = 0
        char = ''
        while char != "27":
            try:
                #command = raw_input('Prompt ("stop" to quit): ')
                char = str(self._window.my_raw_input(0, 0, 'Enter your command (help):'))
                if int(char) > 255:
                    if char == "258":
                        command.insert(curpos, char)
                    elif char == "259":
                        command.insert(curpos, char)
                    elif curpos > 0 and char == "260":
                        # KEY_LEFT
                        curpos -= 1
                        self._window.redraw_command_line(command, curpos)
                    elif char == "261" and curpos < len(command):
                        # KEY_RIGHT
                        curpos += 1
                        self._window.redraw_command_line(command, curpos)
                    elif curpos > 0 and char == "263":
                        # RETURN
                        command.pop(curpos-1)
                        curpos -= 1
                        self._window.redraw_command_line(command, curpos)
                    elif  curpos > 0 and curpos < len(command):
                        command.insert(curpos, char)
                else:                
                    if char == "10":
                        history = self.parse_cmd(history, command)
                        command = [""]
                        curpos = 0
                        char = ''                    
                        first_char = 0
                    elif char != "":
                        if curpos == 0 and first_char == 0:
                            command[0] = chr(int(char))
                            first_char = 1
                        else:
                            command.insert(curpos, chr(int(char)))
                            #command.insert(curpos, chr(int(char)))
                        curpos += 1
                        #self._window.print_char_from_user()
                    self._window.redraw_command_line(command, curpos)


            except:
                print str(command)
                self.close()
                raise
        self.close()