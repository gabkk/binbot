import time
import traceback
import logging
from windows_display import Window
from binance.enums import *
from binance.exceptions import BinanceAPIException, BinanceRequestException, BinanceWithdrawException
from binance.websockets import BinanceSocketManager

#remove this
import sys

help_str = [' AVAILABLE COMMANDS\n', \
            ' ad -> to add a new coin, ex: ac iota\n',\
            ' rm -> to rm an existing coin, ex: rm iota\n'\
            '  wa -> display_wallet\n'\
            '  order -> pass an order\n'\
            '  quit -> exit binbot'\
            ]

class Command():
    def __init__(self, client, coins_in_request, coins_in_balance, market_prices):
        self._window = Window(client)
        self._window.init_list_of_price(coins_in_balance, market_prices)
        self._coins = coins_in_request
        self._coins_in_balance = coins_in_balance
        self._client = client
        self._list_coins = []
        self._old_order_coins_price = []
        self.bot_list = []
        self._bm = BinanceSocketManager(client)
        self._bm.start_multiplex_socket(coins_in_request, self._window.display_prices)
        self._bm.start()

    def display_help(self):
        self._window.result_display_spec(self._window.result_cmd_window, help_str)

    def display_in_logger(self, str):
        self._window.logger.clear()
        self._window.logger.addstr(1, 1, str)
        self._window.logger.border()
        self._window.logger.refresh()


    def add_coin_fct(self, command):
        command = command.split(" ", 2)[1]
        ret_is_valid = command.find("/")
        if ret_is_valid == -1:
            return "error format sould be COIN1/COIN2", self._coins
        is_pair_exist = 0
        new_coin = command.split("/", 2)[0]
        change_coin = command.split("/", 2)[1]
        self.display_in_logger(new_coin.upper() + change_coin.upper())
        prices = self._client.get_all_tickers()
        for pair in  prices:
            if str(pair["symbol"]) == new_coin.upper() + change_coin.upper():
                self._window.display_window.clear()
                self._window.display_window.refresh()
                self._window.update_price(pair)
                self._window.first_draw = 0
                self._window.print_prices()
                is_pair_exist = 1
                break

        if is_pair_exist == 0:
            self.display_in_logger("error Pair doesn't exist")
            return "error Pair doesn't exist", self._coins

        new_coin = new_coin.lower() + change_coin + "@aggTrade"
        self.display_in_logger("add : " + new_coin)
        self.display_in_logger("list : " + str(self._coins))

        if new_coin not in self._coins:
            self._coins.append(new_coin)
        else:
            return "coin already register: " + new_coin + "\n", self._coins            
        return "new coin add to list: " + new_coin + "\n", self._coins

    #TODO Fix bug rm redraw all
    def del_coin_fct(self, command):
        command = command.split(" ", 2)[1]
        self.display_in_logger(str(command))
        if command == "all":
            self._coins = []
            self._window.remove_all_coin()
            self._window.display_window.clear()
            self._window.display_window.refresh()
            self._window.first_draw = 0
            self._window.print_prices()
            return "delete all coin in list" + str(), self._coins
        
        ret_is_valid = command.find("/")
        if ret_is_valid == -1:
            return "error format sould be COIN1/COIN2", self._coins
        is_pair_exist = 0
        new_coin = command.split("/", 2)[0]
        change_coin = command.split("/", 2)[1]

        #TODO check rm all doesn't work proprely
        coin_symbole = new_coin.lower() + change_coin.lower() + "@aggTrade"

        #DEBUG
        #self.display_in_logger("Symbol: "+coin_symbole + "list of coins: " + str(self._coins))

        if coin_symbole in self._coins:
            self._coins.remove(coin_symbole)
            self._window.remove_coin(coin_symbole)
            self._window.display_window.clear()
            self._window.display_window.refresh()
            self._window.first_draw = 0
            self._window.print_prices()
            return "new coin delete to list: " + coin_symbole + "\n", self._coins
        else:
            return "coin doesn't exist" + "\n", self._coins

    def check_order(self,command):
        tab = command.split()
        len_tab= len(tab)
        if len_tab <= 1:
            self._window.display_order_usage()
            self._window.result_cmd_window.border()
            self._window.result_cmd_window.refresh()
            return 0, tab
        elif len_tab > 1 and len_tab < 5:
            if tab[1] == "ls":
                self._window.display_all_orders(5)
            self._window.result_cmd_window.border()
            self._window.result_cmd_window.refresh()
            return 0, tab

        if tab[1] != "b" and tab[1] != "s":
            self._window.result_cmd_window.addstr(1, 1, "Error:" + command + " should be b / s" )
            self._window.display_order_usage()
            self._window.result_cmd_window.border()
            self._window.result_cmd_window.refresh()
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


    def send_order(self, result, command, curpos):
        self._window.result_cmd_window.clear()
        self._window.redraw_command_line(command, curpos)
        ret_check, tab = self.check_order(result) 
        if ret_check == 1:
            self._window.display_sending_order(tab, self._client)
        else:
            self._window.result_cmd_window.border()
            self._window.result_cmd_window.refresh()

    def parse_cmd(self, history, command, curpos):
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
            self.send_order(result, command, curpos)
            return history
        else:
            result = "Unknow command '" + fcommand + "'"
        history.append(result)
        #TODO normal usage doesn't work with logger debug
        if len(history) > 5:
            history = []
        self._window.result_display(self._window.logger, history)
        return history

    def close(self):
        self._window.close_ncurses()
        self._bm.close()

    def bot_info(self):
        self._window.display_bot_info(self.bot_list)

    def main_loop(self):
        history = []
        command = [" "]
        curpos = 0
        first_char = 0
        char = ''
        change_menu = 0
        #TODO TODO This function seems to work
        #coin_total: 4639.076 qty_total: 1037.0 price:0.00420616
        #coin_total: 4639.076 qty_total: 2926.0 price:0.01712692
        #coin_total: 4639.076 qty_total: 3856.0 price:0.02713372
        #coin_total: 4639.076 qty_total: 4639.076 price:0.03573972524
        #[{'symbol': 'TRXBTC', 'price_token': '0.00000770'}]
        
        #self.get_all_trades()

# Removed in main
#        self._old_order_coins_price = get_all_trades(self._client, self._coins_in_balance)
#        self._window.set_old_prices(self._old_order_coins_price)


        #TODO check if i need this
#        market_prices = self._client.get_symbol_ticker()
#        coin_in_balance = self.get_coin_in_balance()
#        self._window.init_list_of_price(coin_in_balance, market_prices)

        while char != "27":
            self._window.display_menu()
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
                        self._window.result_display(self._window.result_cmd_window, history)
                        change_menu = 1
                    elif char == "266":
                        self._window.set_menu_value("wallet") 
                        change_menu = 1
                    elif char == "267":
                        self._window.set_menu_value("order") 
                        change_menu = 1
                    elif char == "268":
                        self._window.set_menu_value("bot")
                        self.bot_info()
                        change_menu = 1
#                        self._window.result_display(self._window.result_cmd_window, history)
                    elif  curpos > 0 and curpos < len(command):
                        command.insert(curpos, char)
                else:                
                    if char == "10":
                        history = self.parse_cmd(history, command, curpos)
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
                if change_menu == 1:
                    if self._window.menu_view == "wallet":
                        self._window.display_wallet()
                    elif self._window.menu_view == "order":
                        self._window.result_cmd_window.clear()
                        self._window.display_all_orders(1)
                        self._window.result_cmd_window.border()
                        self._window.result_cmd_window.refresh()
                    change_menu = 0
                # Display the current payload
                self.display_in_logger("Main loop: " + str(self._coins))

            except Exception as e:
                logging.error(traceback.format_exc())
                print "ERROR" + str(e)
                time.sleep(1500)
                raise
        print("OUT BECAUSE OF " + str(command))
        self.close()