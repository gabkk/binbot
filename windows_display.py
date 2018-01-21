import curses
import os

compteur = 0

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

        # Set each windows size
        rows, columns = os.popen('stty size', 'r').read().split()
        self.display_window = curses.newwin(10, int(columns), 0, 0)
        self.cmd_window = curses.newwin(3, int(columns), 10, 0)
        self.result_cmd_window = curses.newwin(25, int(columns), 13, 0)

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

    def display_prices(self, msg):
        global compteur

        klen = 0
        self._coin_prices.update({msg['data']['s']: msg['data']['p']})
        if self._coin_prices_old == self._coin_prices:
            return
        pos = 1

        if len(self._coin_prices_old) != len(self._coin_prices):
            self.display_window.clear()
        for k, v in self._coin_prices.items():
            color = 0
            if k in self._coin_prices_old:
                self.display_window.addstr(pos, 1,  k + " ,price: ")
                klen = len( k + " ,price: ") + 1
                if float(self._coin_prices_old[k]) > float(v):
                    self.display_window.addstr(pos, klen, v, curses.color_pair(1))
                elif float(self._coin_prices_old[k]) < float(v):
                    self.display_window.addstr(pos, klen, v, curses.color_pair(2))
                compteur += 1
            else:
                self.display_window.addstr(pos, 1, k + " ,price: ")
                self.display_window.addstr(pos, klen, v, curses.color_pair(0))
            pos += 1
        self.display_window.border()
        self._coin_prices_old.update({msg['data']['s']: msg['data']['p']})
        self.display_window.refresh()

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

    def result_display(self, screen, history):
        screen.clear()
        screen.border()
        i = 1
        for result in history:
            screen.addstr(i, 1, result + " iter = " + str(i))
            i += 1
        screen.refresh()

#    def refresh(self, screen, history):

    def close_ncurses(self):
        curses.nocbreak()
        curses.endwin()
