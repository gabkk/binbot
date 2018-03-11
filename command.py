from binance.enums import *
from binance.exceptions import BinanceAPIException, BinanceRequestException, BinanceWithdrawException


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
    def __init__(self, window, bm, client, coins_in_request, coins_in_balance):
        self._window = window
        self._bm = bm
        self._coins = coins_in_request
        self._coins_in_balance = coins_in_balance
        self._client = client
        self._list_coins = []
        self._old_order_coins_price = []

    def display_help(self):
        self._window.result_display_spec(self._window.result_cmd_window, help_str)

    def add_coin_fct(self, command):
        new_coin = command.split(" ", 2)[1]
        prices = self._client.get_all_tickers()
        #TODO improve this
        tmp_dict = []
        for pair in  prices:
            if str(pair["symbol"]) == new_coin.upper() + "BTC":
                self._window.update_price(pair)
                tmp_dict.append({'asset': new_coin.upper()})
                break
        #TODO improve this
        self._window.init_list_of_price(tmp_dict, prices)

        new_coin = new_coin.lower() + "btc@aggTrade"
        if new_coin not in self._coins:
            self._coins.append(new_coin)
        else:
            return "coin already register: " + new_coin + "\n", self._coins            
        return "new coin add to list: " + new_coin + "\n", self._coins

    #TODO Fix bug rm redraw all
    def del_coin_fct(self, command):
        new_coin = command.split(" ", 2)[1]
        if new_coin == "all":
            for x in self._coins:
                self._coins.remove(x)
                self._window.remove_all_coin()
            self._window.init_list_of_price([],[])
            return "delete all coin in list" + str(), self._coins
        coin_symbole = new_coin.upper() + "BTC"
        new_coin = new_coin.lower() + "btc@aggTrade"
        if new_coin in self._coins:
            self._coins.remove(new_coin)
            self._window.remove_coin(coin_symbole)
            #TODO dirty fix this
            self._window.init_list_of_price([],[])
            return "new coin delete to list: " + new_coin + "\n", self._coins
        else:
            return "coin doesn't exist" + "\n", self._coins

    def check_order(self,command):
        tab = command.split()
        if len(tab) < 5:
            self._window.display_order_usage()
            self._window.display_all_orders(5)
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
        self._window.result_cmd_window.clear()
        ret_check, tab = self.check_order(command)        
        if ret_check == 1:
            self._window.display_sending_order(tab, self._client)

        self._window.result_cmd_window.border()
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
            self._window.display_wallet()
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

    def calcul_average(self, trade, total_qty_coin, total_price, coin_total):
        # dict = [{"symbol": asset+"BTC", "price_token":float] 
        # trade['price']["isBuyer"]["commission"]["time"]['qty']
        # price
        qty = float(trade['qty'])
        price = float(trade['price'])
        if trade['isBuyer'] == False:
            total_qty_coin -= qty
            #TODO trade['commission']
            total_price -= qty*price
        elif trade['isBuyer'] == True and coin_total >= total_qty_coin + qty:
            total_qty_coin += qty
            #TODO trade['commission']
            total_price += qty*price
        elif coin_total < total_qty_coin + qty:
            diff = coin_total - total_qty_coin
            total_qty_coin += diff
            total_price += diff*price
#        print "coin_total: "+str(coin_total)+" qty_total: "+str(total_qty_coin)+" price:"+str(total_price)
        return total_qty_coin, total_price


# TODO CALCULATE ONLY FOR COIN THAT IS UP TO 1 IN BALANCE TO LIMITE CALLS
    def get_all_trades(self):
        for coin in self._coins_in_balance:
            coin_locked = float(coin['locked'])
            coin_free = float(coin['free'])
            coin_total = coin_locked + coin_free 
            asset = str(coin['asset'])
            trades_btc = []
            trades_eth = []
            try:
                trades_btc = self._client.get_my_trades(symbol=asset+"BTC", limit=10)
                trades_eth = self._client.get_my_trades(symbol=asset+"ETH", limit=10)
            except:
                #TODO HANDLE THIS
                pass
            # Sort trades by last trade
            trades_btc.sort(reverse=True, key=lambda x:x[u'time'])
            total_qty_coin = 1.
            total_price = 0.
 #           print "!!!!!!!!!!!!!!!!!!!!!!! TODO check if zero don't append"
 #           print str(trades_btc)

            for trade_btc in trades_btc:
                total_qty_coin, total_price = self.calcul_average(trade_btc, total_qty_coin, total_price, coin_total)
#                print "QTY"+str(total_qty_coin)+"PRICE"+str(total_price)
                if coin_total == total_qty_coin:
                    break
            if total_qty_coin != 0:
                self._old_order_coins_price.append({"symbol":asset+"BTC","price_token":"{:.8f}".format(total_price/total_qty_coin)})
            #print str(pair_price)
            total_price = 0
            total_qty_coin = 0
            for trade_eth in trades_eth:
                total_qty_coin, total_price = self.calcul_average(trade_eth, total_qty_coin, total_price, coin_total)
#                print "QTY"+str(total_qty_coin)+"PRICE"+str(total_price)
                if coin_total == total_qty_coin:
                    break
            if total_qty_coin != 0:
                self._old_order_coins_price.append({"symbol":asset+"ETH","price_token":"{:.8f}".format(total_price/total_qty_coin)})
            #print str(pair_price)

    def main_loop(self):
        history = []
        command = [" "]
        curpos = 0
        first_char = 0
        char = ''

        #TODO TODO This function seems to work
        #coin_total: 4639.076 qty_total: 1037.0 price:0.00420616
        #coin_total: 4639.076 qty_total: 2926.0 price:0.01712692
        #coin_total: 4639.076 qty_total: 3856.0 price:0.02713372
        #coin_total: 4639.076 qty_total: 4639.076 price:0.03573972524
        #[{'symbol': 'TRXBTC', 'price_token': '0.00000770'}]
        
        self.get_all_trades()
        self._window.set_old_prices(self._old_order_coins_price)
        #TODO check if i need this
#        market_prices = self._client.get_symbol_ticker()
#        coin_in_balance = self.get_coin_in_balance()
#        self._window.init_list_of_price(coin_in_balance, market_prices)
        while char != "27":
            try:
                #command = raw_input('Prompt ("stop" to quit): ')
#                char = str(self._window.my_raw_input(0, 0, 'Enter your command (help):' + ", raw: "+ str(self._window.rows)+ ", col: "+str(self._window.columns)))
                char = str(self._window.my_raw_input(0, 0, 'Enter your command (help):'+str(char)))
                if int(char) > 255:
                    if char == "258":
                        self._window.redraw_command_line(command, curpos)
                        #TODO ADD HISTORY
                        #command.insert(curpos, char)
                    elif char == "259":
                        self._window.redraw_command_line(command, curpos)
                        #TODO ADD HISTORY
                        #command.insert(curpos, char)
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
                    elif char == "265":
                        self._window.set_menu_value("history") 
                    elif char == "266":
                        self._window.set_menu_value("wallet") 
                    elif char == "267":
                        self._window.set_menu_value("order") 
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
                        if len(command) and curpos == 0 and first_char == 0:
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
                self._window.close_ncurses()
                raise
                break
        self.close()