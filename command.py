help_str = [' AVAILABLE COMMANDS\n', \
            ' ad -> to add a new coin, ex: ac iota\n',\
            ' rm -> to rm an existing coin, ex: rm iota\n'\
            ' wa -> display_wallet\n'\
            ]

class Command():
    def __init__(self, window, bm, client):
        self._window = window
        self._bm = bm
        self._coins = []
        self._client = client
        self._list_coins = []

    def display_help(self):
        self._window.result_display_spec(self._window.result_cmd_window, help_str)

    def display_wallet(self):
        coin_in_balance = []
        personal_info = self._client.get_account()
        for k, v in personal_info.iteritems():
            if k == "balances":
                balance = v
        for coin in balance:
            if float(coin['locked']) != 0 or float(coin['free']) != 0:
                coin_in_balance.append(coin)

        self._window.result_cmd_window.clear()
        self._window.result_cmd_window.border()
        i = 1
        for coin in coin_in_balance:
            self._window.result_cmd_window.addstr(i, 1, str(coin['asset']) + ":" + str(coin['free']) + ", locked: " + str(coin['locked']))
            i += 1
        self._window.result_cmd_window.refresh()

    def add_coin_fct(self, command):
        new_coin = command.split(" ", 2)[1]
        new_coin = new_coin.lower() + "btc@aggTrade"
        if new_coin not in self._coins:
            self._coins.append(new_coin)
        else:
            return "coin already register: " + new_coin + "\n", self._coins            
        return "new coin add to list: " + new_coin + "\n", self._coins

    def del_coin_fct(self, command):
        new_coin = command.split(" ", 2)[1]
        coin_symbole = new_coin.upper() + "BTC"
        new_coin = new_coin.lower() + "btc@aggTrade"
        if new_coin in self._coins:
            self._coins.remove(new_coin)
            self._window.remove_coin(coin_symbole)
            return "new coin delete to list: " + new_coin + "\n", self._coins
        else:
            return "coin doesn't exist" + "\n", self._coins
        self._window.display_window.refresh()


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
        elif "wa" in command:
            self.display_wallet()
            return history
        else:
            result = "Unknow command"
        history.append(result)
        self._window.result_display(self._window.result_cmd_window, history)
        return history

    def main_loop(self):
        history = []
        while True:
            command = str(self._window.my_raw_input(0, 0, 'Enter your command (help):'))
            if "quit" in command:
                break
            else:
                history = self.parse_cmd(history, command)
        self._window.close_ncurses()
        self._bm.close()
