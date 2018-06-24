import time
from twisted.internet import reactor
from binance.client import Client
from binance.websockets import BinanceSocketManager
from command import Command
from windows_display import Window
from helper_client import get_all_trades

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
    window = Window(client)
    bm = BinanceSocketManager(client)
    global_info = client.get_account()
    market_prices = client.get_symbol_ticker()


    coins_in_requete = ['btcusdt@aggTrade']
    coins_in_balance = []
    for k, v in global_info.iteritems():
        if k == "balances":
            for coin in v:
                if float(coin['locked']) != 0. or float(coin['free']) != 0.:
                    coins_in_requete.append(str(coin['asset']).lower()+"btc@aggTrade")
                    coins_in_balance.append(coin)
    # Initialize a first list of price regarding our coins instead of waiting from
    # the socket to return a new value   

    #Retrieve old orders
    #TODO improve this
    #old_order_coins_price = get_all_trades(client, coins_in_balance)
    #window.set_old_prices(old_order_coins_price)

    window.init_list_of_price(coins_in_balance, market_prices)

    if bm.start_multiplex_socket(coins_in_requete, window.display_prices):
        bm.start()
        # main thread, waiting for user's command.
        command = Command(window, bm, client, coins_in_requete, coins_in_balance)
        command.main_loop()

    reactor.stop()

if __name__ == "__main__":
    main()
