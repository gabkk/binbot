import time
from twisted.internet import reactor
from binance.client import Client
from command import Command
from helper_client import get_all_trades

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
    cles, secret = get_credential()
    client = Client(cles, secret)

    global_info = client.get_account()
    market_prices = client.get_symbol_ticker()


    coins_in_request = ['btcusdt@aggTrade']
    coins_in_balance = []
    for k, v in global_info.iteritems():
        if k == "balances":
            for coin in v:
                if coin['asset'] != "btc" and float(coin['locked']) != 0. or float(coin['free']) != 0.:
                    coins_in_request.append(str(coin['asset']).lower()+"btc@aggTrade")
                    coins_in_request.append(str(coin['asset']).lower()+"btc@ticker")
                    coins_in_balance.append(coin)
    # Initialize a first list of price regarding our coins instead of waiting from
    # the socket to return a new value

    #Retrieve old orders
    #TODO improve this
    #old_order_coins_price = get_all_trades(client, coins_in_balance)
    #window.set_old_prices(old_order_coins_price)

    # main thread, waiting for user's command.
    command = Command(client, coins_in_request, coins_in_balance, market_prices)
    try:
        command.main_loop()
    except Exception as e:
        print "ERROR" + str(e)
        raise

    reactor.stop()

if __name__ == "__main__":
    main()
