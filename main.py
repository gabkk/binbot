import time
from twisted.internet import reactor
from binance.client import Client
from binance.websockets import BinanceSocketManager
from command import Command
from windows_display import Window

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


def main():
    global window

    cles, secret = get_credential()
    client = Client(cles, secret)
    window = Window()
    bm = BinanceSocketManager(client)
    bm.start_multiplex_socket([''], window.display_prices)
    bm.start()

    # main thread, waiting for user's command.
    command = Command(window, bm, client)
    command.main_loop()

    reactor.stop()

if __name__ == "__main__":
    main()
