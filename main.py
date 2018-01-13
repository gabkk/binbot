import time
import curses
from twisted.internet import reactor
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


def print_coins(symbol_list, price_list):
    for coin in coins:
        try:
            index = symbol_list.index(coin)
        except ValueError:
            pass
        else:
            print(str(symbol_list[index])+" ,price: "+str(price_list[index]))


def display_coins(screen):
    pos = 0
    for k, v in coin_prices.items():
        screen.addstr(pos, 4, k + " ,price: " + v)
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
    if "BTC" not in (new_coin):
        new_coin = new_coin.upper() + "BTC"
    coins.append(new_coin)
    return "new coin add to list: " + new_coin + "\n"


def result_display(screen, result):
    while True:
        screen.addstr(1, 0, result)
        time.sleep(0.5)
        screen.refresh()


def process_m_message(msg):
    global coin_prices
    coin_prices.update({msg['data']['s']: msg['data']['p']})
    display_coins(display_window)
    display_window.refresh()


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
    cmd_window = curses.newwin(3, 70, 13, 0)

    cmd_window.border()
    display_window.border()
    result_cmd_window.border()

    bm.start_multiplex_socket(['ethbtc@aggTrade'], process_m_message)
    bm.start()

    # main thread, waiting for user's command.
    while True:
        command = str(my_raw_input(cmd_window, 0, 0, 'Enter your command:'))
        if "quit" in command:
            bm.close()
            break
        elif "add coin" in command:
            result = add_coin_fct(command)
        else:
            result = "Unknow command"

    teardown(cmd_window)
    teardown(display_window)
    curses.endwin()
    reactor.stop()

if __name__ == "__main__":
    cles, secret = get_credential()
    client = Client(cles, secret)
    main()
