import time
from twisted.internet import reactor
from binance.client import Client
from binance.websockets import BinanceSocketManager
from display_ncurses import Window

result = "No command"
coins = ["TRXBTC"]
coin_selected = ""
coin_prices = {}
window = 0


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
    pos = 1
    coin_prices.update({msg['data']['s']: msg['data']['p']})
    display_window = window.get_display_window()
    for k, v in coin_prices.items():
        display_window.addstr(pos, 1, k + " ,price: " + v)
        pos += 1
    display_window.refresh()


def main():
    global result
    global window
    cles, secret = get_credential()
    client = Client(cles, secret)
    window = Window()
    bm = BinanceSocketManager(client)
    bm.start_multiplex_socket(['ethbtc@aggTrade'], process_m_message)
    bm.start()

    # main thread, waiting for user's command.
    while True:
        command = str(window.my_raw_input(0, 0, 'Enter your command:'))
        if "quit" in command:
            bm.close()
            break
        elif "add coin" in command:
            result = add_coin_fct(command)
        else:
            result = "Unknow command"
    window.close_ncurses()
    reactor.stop()

if __name__ == "__main__":
    main()
