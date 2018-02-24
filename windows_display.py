import curses
import os

class Window():

    def __init__(self):
        
        # TODO Change this prices of 
        self._coin_prices = {}
        self._coin_prices_old = {}

        # create stdscr
        stdscr = curses.initscr()
        stdscr.clear()

        # allow echo, set colors
        curses.echo()
        curses.curs_set(0)
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)
        self.color = 0

        # Set each windows size
        rows, columns = os.popen('stty size', 'r').read().split()
        self.display_window = curses.newwin(14, int(columns), 0, 0)
        self.cmd_window = curses.newwin(3, int(columns), 14, 0)
        self.result_cmd_window = curses.newwin(25, int(columns), 17, 0)

        # Set each windows border
        self.display_window.border()
        self.result_cmd_window.border()
        self.cmd_window.refresh()
        self.result_cmd_window.refresh()
        self.display_window.refresh()

    def my_raw_input(self, r, c, prompt_string):
        self.cmd_window.clear()
        self.cmd_window.border()
        self.cmd_window.addstr(r, c, prompt_string)
        self.cmd_window.refresh()
        input = self.cmd_window.getstr(r + 1, c + 1)
        return input

    def remove_coin(self, coin):
        for k, v in self._coin_prices.items():
            if k == coin:
                del self._coin_prices[k]
                del self._coin_prices_old[k]
                self.display_window.clear()

    def print_prices(self):
#        if len(self._coin_prices_old) != len(self._coin_prices):
#            self.display_window.clear()
        self.display_window.clear()
        klen = 0
        #We start to display other coin at position 3, Btc start at 1
        pos = 3
        for k, v in self._coin_prices.items():
            if k in self._coin_prices_old:
                if k == 'BTCUSDT':
                    # change this by responsive pos 
                    self.display_window.addstr(1, 20, "The King ")
                    klen = len("The King ") + 21
                    if float(self._coin_prices_old[k]) > float(v):
                        v = "{:.2f}".format(float(v))
                        self.color = curses.color_pair(1)
                    elif float(self._coin_prices_old[k]) < float(v):
                        v = "{:.2f}".format(float(v))
                        self.color = curses.color_pair(2)
                    else:
                        v = "{:.2f}".format(float(v))
                        self.color = curses.color_pair(0)
                    self.display_window.addstr(1, klen, v, self.color)
                else:
                    self.display_window.addstr(pos, 1,  k + " ,price: ")
                    klen = len( k + " ,price: ") + 1
                    if float(self._coin_prices_old[k]) > float(v):
                        self.color = curses.color_pair(1)
                    elif float(self._coin_prices_old[k]) < float(v):
                        self.color = curses.color_pair(2)
                    else:
                        self.color = curses.color_pair(0)

                    self.display_window.addstr(pos, klen, v, self.color)
            #else:
            #    self.display_window.addstr(pos, 1, k + " ,price: ")
            #    self.display_window.addstr(pos, klen, v, curses.color_pair(0))
                pos += 1
        self.display_window.border()
        self.display_window.refresh()

    def update_price(self, pair):
        self._coin_prices.update({str(pair["symbol"]): pair["price"]})
        self._coin_prices_old.update({str(pair["symbol"]): pair["price"]})

    def display_prices(self, msg):
        #global compteur

        self._coin_prices.update({msg['data']['s']: msg['data']['p']})
        if self._coin_prices_old == self._coin_prices:
            return
        self.print_prices()
        self._coin_prices_old.update({msg['data']['s']: msg['data']['p']})

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
            screen.addstr(i, 1, result + " iter = " + str(i))
            i += 1
        screen.refresh()

    def close_ncurses(self):
        curses.nocbreak()
        curses.endwin()
