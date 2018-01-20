class Command():
    def __init__(self, window, bm, client):
        self._window = window
        self._bm = bm
        self._coins = []
        self._client = client
        self._list_coins = []

    def display_help(self):

#        msg1 = ['$ ad // to add a new coin, ex: ac iota\n$ rm // to rm an existing coin, ex: rm iota\nList of coin\n']
#        for coin in msg1:
#            msg1.append(str(coin['symbol'])+'\n')
        self._window.result_display_spec(self._window.result_cmd_window, msg1)
#        return msg1

    def add_coin_fct(self, command):
#        test = self._client.get_symbol_ticker()
        new_coin = command.split(" ", 2)[1]
#       for coin in test:
#          if new_coin.upper()+ "BTC" == coin['symbol']:
        new_coin = new_coin.lower() + "btc@aggTrade"
        #if new_coin in new_coin:
        self._coins.append(new_coin)            
   # else:
    #return "coin doesn't exist"
        return "new coin add to list: " + new_coin + "\n", self._coins

    def del_coin_fct(self, command):
        #test = self._client.get_symbol_ticker()
        new_coin = command.split(" ", 2)[1]
        coin_symbole = command.split(" ", 2)[1].upper() + "BTC"
        new_coin = new_coin.lower() + "btc@aggTrade"
        #for coin in test:
        if new_coin in self._coins:
            self._coins.remove(new_coin)
        #self._window.result_cmd_window.addstr(4, 4, oui)
        self._window.remove_coin(coin_symbole)
#
        #self._window.result_cmd_window.addstr(5, 5, self._coins)

        #if new_coin in self._window._coin_prices:
        #if oui in self._window._coin_prices.values():
        #    del self._window._coin_prices

        self._window.display_window.refresh()
            #else:
            #    return "coin doesn't exist"
        self._window.display_window.clear()
        self._window.display_window.refresh()
        return "new coin delete to list: " + new_coin + "\n", self._coins

    def parse_cmd(self, history, command):
        result = ""
        if "help" in command:
            self.display_help()
            return history
        elif "ad" in command:
            result, self._coins = self.add_coin_fct(command)
            self._bm.start_multiplex_socket(self._coins, self._window.display_prices)
        elif "rm" in command:
            result, self._coins = self.del_coin_fct(command)
            print self._coins
            self._bm.close()
            self._bm.start_multiplex_socket(self._coins, self._window.display_prices)
        else:
            result = "Unknow command"
        history.append(result)
        self._window.result_display(self._window.result_cmd_window, history)
        return history

    def main_loop(self):
        history = []
        while True:
            command = str(self._window.my_raw_input(0, 0, 'Enter your command(help):'))
            if "quit" in command:
                break
            else:
                history = self.parse_cmd(history, command)
        self._window.close_ncurses()
        self._bm.close()
