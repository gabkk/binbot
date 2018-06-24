
def calcul_average(trade, total_qty_coin, total_price, coin_total):
    # dict = [{"symbol": asset+"BTC", "price_token":float] 
    # trade['price']["isBuyer"]["commission"]["time"]['qty']
    # price
    qty = float(trade['qty'])
    price = float(trade['price'])
    if trade['isBuyer'] == False:
        total_qty_coin -= qty
        #TODO trade['commission']
        total_price -= qty*price
    elif trade['isBuyer'] == True and coin_total >= total_qty_coin + qty:
        total_qty_coin += qty
        #TODO trade['commission']
        total_price += qty*price
    elif coin_total < total_qty_coin + qty:
        diff = coin_total - total_qty_coin
        total_qty_coin += diff
        total_price += diff*price
#        print "coin_total: "+str(coin_total)+" qty_total: "+str(total_qty_coin)+" price:"+str(total_price)
    return total_qty_coin, total_price


def get_all_trades(client, coins_in_balance):
#    print coins_in_balance
    old_order_coins_price = []
    for coin in coins_in_balance:
        if str(coin['asset']) == "BTC" or str(coin['asset']) == "ETH":
            continue
        coin_locked = float(coin['locked'])
        coin_free = float(coin['free'])
        coin_total = coin_locked + coin_free 
        if float(coin_total) < 0.001:
            continue
        asset = str(coin['asset'])
        trades_btc = []
        trades_eth = []

        #TODO improve this DEGUELLLASSSEEE
        try:
            trades_btc = client.get_my_trades(symbol=asset+"BTC", limit=10)
            trades_eth = client.get_my_trades(symbol=asset+"ETH", limit=10)
        except:
            #TODO HANDLE THIS
            print asset
            raise

#        print str(trades_btc)
        # Sort trades by last trade
        trades_btc.sort(reverse=True, key=lambda x:x[u'time'])
        total_qty_coin = 1.
        total_price = 0.
#           print "!!!!!!!!!!!!!!!!!!!!!!! TODO check if zero don't append"
#           print str(trades_btc)

        for trade_btc in trades_btc:
            total_qty_coin, total_price = calcul_average(trade_btc, total_qty_coin, total_price, coin_total)
#                print "QTY"+str(total_qty_coin)+"PRICE"+str(total_price)
            if coin_total == total_qty_coin:
                break
        if total_qty_coin != 0:
            old_order_coins_price.append({"symbol":asset+"BTC","price_token":"{:.8f}".format(total_price/total_qty_coin)})
#            print str(old_order_coins_price)
        #print str(pair_price)
        total_price = 0
        total_qty_coin = 0
        for trade_eth in trades_eth:
            total_qty_coin, total_price = calcul_average(trade_eth, total_qty_coin, total_price, coin_total)
#                print "QTY"+str(total_qty_coin)+"PRICE"+str(total_price)
            if coin_total == total_qty_coin:
                break
        if total_qty_coin != 0:
            old_order_coins_price.append({"symbol":asset+"ETH","price_token":"{:.8f}".format(total_price/total_qty_coin)})
   

    return old_order_coins_price