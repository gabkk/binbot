class Command():
    def __init__(self, window, bm):
        self._window = window
        self._bm = bm
        self._coins = []


    def add_coin_fct(self, command):

        new_coin = command.split(" ", 3)[2]
        if "BTC" not in (new_coin):
            new_coin = new_coin.lower() + "btc@aggTrade"

        #TODO check if the coin exist
        self._coins.append(new_coin)
        return "new coin add to list: " + new_coin + "\n", self._coins


    def main_loop(self):
        history = []
        while True:
            command = str(self._window.my_raw_input(0, 0, 'Enter your command:'))
            if "quit" in command:
                break
            elif "add coin" in command:
                result, self._coins = self.add_coin_fct(command)
                history.append(result)
                self._window.result_display(self._window.result_cmd_window, history)
                result = self._coins
                self._bm.start_multiplex_socket(self._coins, self._window.display_prices)
            else:
                result = "Unknow command"
        self._window.close_ncurses()
        self._bm.close()
