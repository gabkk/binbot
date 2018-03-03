import curses
import os

class Window():

    def __init__(self):
        
        # TODO Change this prices of 
        self._coin_prices = {}
        self._coin_prices_old = {}

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
        curses.init_pair(3, -1, curses.COLOR_WHITE)
        self.color = 0

        # Set each windows size
        rows, columns = os.popen('stty size', 'r').read().split()
        self.display_window = curses.newwin(14, int(columns), 0, 0)
        self.cmd_window = curses.newwin(6, int(columns), 14, 0)
        self.cmd_window.keypad(1)
        self.cmd_window.box()
        curses.curs_set(0)
        self.result_cmd_window = curses.newwin(40, int(columns), 20, 0)

        # Set each windows border
        self.display_window.border()
        self.result_cmd_window.border()
        self.cmd_window.refresh()
        self.result_cmd_window.refresh()
        self.display_window.refresh()

    def get_prices(self):
        return self._coin_prices

    def print_char_from_user(self):
        self.cmd_window.erase()

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

    def my_raw_input(self, r, c, prompt_string):
        test = ""
        #self.cmd_window.erase()
        self.cmd_window.border()
        self.cmd_window.addstr(r, c, prompt_string)
        #input = self.cmd_window.getstr(r + 1, c + 1)
        self.display_window.refresh()
        test = self.cmd_window.getch()

        return test

    def remove_all_coin(self):
        i = 1
        for k, v in self._coin_prices.items():
            i += 1
            self.result_cmd_window.addstr(i, 20, str(k))
            del self._coin_prices[k]
            del self._coin_prices_old[k]
        self.display_window.refresh()

    def remove_coin(self, coin):
        i = 1
        self.display_window.clear()
        for k, v in self._coin_prices.items():
            i += 1
            self.result_cmd_window.addstr(i, 20, str(k)+"/"+coin)
            self.result_cmd_window.refresh()            
            if k == coin:
                del self._coin_prices[k]
                del self._coin_prices_old[k]
        self.display_window.refresh()


    def print_prices(self):
 #       if len(self._coin_prices_old) != len(self._coin_prices):
 #           self.display_window.clear()
        self.display_window.clear()
        klen = 0
        #We start to display other coin at position 3, Btc start at 1
        pos = 3
        if len(self._coin_prices) > 0:
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
                    elif k != "":
                        self.display_window.addstr(pos, 1,  str(k) + " ,price: ")
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
        curses.noecho()
        curses.endwin()
