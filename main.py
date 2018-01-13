import sys, os, json, time, datetime, math, curses, thread

#import json
#import curses
#import time
#from menupb import *
from binance.client import Client
from binance.websockets import BinanceSocketManager
global client
coins = ["TRXBTC"]
coin_selected = ""

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

def display_coins(symbol_list, price_list, screen):
    pos = 4
    for coin in coins:
        try:
            index = symbol_list.index(coin)
        except ValueError:
            pass
        else:
            screen.addstr(pos , 4, str(symbol_list[index]) + " ,price: " + str(price_list[index]))
            pos += 1

def start_binance(client):

    #print(client.get_symbol_ticker())
    symbol_list = []
    price_list = []
    all_coins = client.get_symbol_ticker()
    for coin in all_coins:
        symbol_list.append(coin['symbol'])
        price_list.append(coin['price'])
        #print_coins(symbol_list, price_list)
    return symbol_list, price_list

def win_coin_display(window):
    while True:
        symbol_list, price_list = start_binance(client)
        time.sleep(0.5)
        display_coins(symbol_list, price_list, window)
        window.refresh()

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
    return "new coin add to list: " + new_coin

result = ""

def result_display(screen):
    while True:
        screen.addstr(4 , 4, "aaaa")

def main():
    bm = BinanceSocketManager(client)
    # create stdscr
    stdscr = curses.initscr()
    stdscr.clear()

    # allow echo, set colors
    curses.echo()
    curses.start_color()
    curses.use_default_colors()

    display_window = curses.newwin(10, 30, 0, 0)
    result_cmd_window = curses.newwin(3, 70, 13, 0)
    command_window = curses.newwin(3, 70, 10, 0)

    command_window.border()
    display_window.border()
    result_cmd_window.border()

    # thread to refresh display_window
    thread.start_new_thread(win_coin_display, (display_window,))

    # thread to refresh display_window
    thread.start_new_thread(result_display, (result_cmd_window,))

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
            command_window.addstr(1, 0, ' '*len(command))
    curses.endwin()
    teardown(command_window)
    teardown(display_window)
    print test

#    processmenu(menu_data)
#    curses.endwin()
#   bm.close()
#    os.system('clear')


if __name__ == "__main__":
    cles, secret = get_credential()
    client = Client(cles, secret)
    main()