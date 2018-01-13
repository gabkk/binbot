import time
import curses
import threading 

#import json
#import curses
#import time
#from menupb import *
from binance.client import Client
from binance.websockets import BinanceSocketManager
global client
result = "No command"
coins = ["TRXBTC"]
coin_selected = ""
coin_prices = {}
display_window = 0

def teardown(screen):
    # reverse everything that you changed about the terminal
    curses.nocbreak()
    screen.keypad(False)
    curses.echo()
    # restore the terminal to its original state
    curses.endwin()

def print_coins(symbol_list, price_list):
    for coin in coins:
        try:
            index = symbol_list.index(coin)
        except ValueError:
            pass
        else:
            print(str(symbol_list[index]) + " ,price: " + str(price_list[index]))

def display_coins(screen):
    pos = 0
    for k , v in coin_prices.items():
        screen.addstr(pos , 4, k + " ,price: " + v)
        pos += 1


def my_raw_input(window, r, c, prompt_string):
    curses.echo()
    window.addstr(r, c, prompt_string)
    window.refresh()
    input = window.getstr(r + 1, c)
    return input

def get_credential():
    filepath = 'credential'
    cles = ""
    secret = ""  
    with open(filepath) as fp:  
       for cnt, line in enumerate(fp):
            if "SECRET" in line:
                secret = line.split("=", 2)[1][:-1]
            elif "CLES" in line:
                cles = line.split("=", 2)[1][:-1]
    return cles, secret

def add_coin_fct(command):
    new_coin = command.split(" ", 3)[2]
    if not "BTC" in (new_coin):
        new_coin = new_coin.upper() + "BTC"
    coins.append(new_coin)
    return "new coin add to list: " + new_coin + "\n"

def result_display(screen):
    while True:
        screen.addstr(1 , 1 , result)
        time.sleep(0.5)
        screen.refresh()

def process_m_message(msg):
    global coin_prices
    coin_prices.update({msg['data']['s']:msg['data']['p']})
    display_coins(display_window)
    display_window.refresh()

class Thread_result (threading.Thread):
    def __init__(self, display):
        threading.Thread.__init__(self)
        self.display = display
    def run(self):
        result_display(self.display)

def main():
    global result
    global display_window
    bm = BinanceSocketManager(client)
    # create stdscr
    stdscr = curses.initscr()
    stdscr.clear()

    # allow echo, set colors
    curses.echo()
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()

    display_window = curses.newwin(10, 30, 0, 0)
    result_cmd_window = curses.newwin(3, 70, 10, 0)
    command_window = curses.newwin(3, 70, 13, 0)

    command_window.border()
    display_window.border()
    result_cmd_window.border()

    bm.start_multiplex_socket(['bnbbtc@aggTrade', 'neobtc@aggTrade'], process_m_message)
    bm.start()
    # thread to refresh display_window
    # thread1 = myThread(display_window)
    # thread1.start()
    thread2 = Thread_result(result_cmd_window)
    thread2.start()

    # main thread, waiting for user's command.
    while True:
        command = my_raw_input(command_window, 0, 0, 'Enter your command (add coin NAME):')
        if command == 'quit':
            break
        elif "add coin" in command:
            result = add_coin_fct(command)
        elif command in coins:
            coin_selected = command
        else:
            result = "Unknow command"

    curses.endwin()
    teardown(command_window)
    teardown(display_window)

#    processmenu(menu_data)
#    curses.endwin()
#   bm.close()
#    os.system('clear')


if __name__ == "__main__":
    cles, secret = get_credential()
    client = Client(cles, secret)
    main()