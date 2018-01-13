import tweepy
import parseJson as data
import parseJson
import auth
import time
from tweepy import Stream
from tweepy.streaming import StreamListener

class StreamListener(tweepy.StreamListener):
    def on_data(self, data):
        return True

    def on_status(self, status):
        print(status.text)

    def on_error(self, status_code):
        print status_code
        if status_code == 420:
            return False

def checkTwitter(currency):
    # Stream Track the currency
    streamlistener = StreamListener()
    stream = tweepy.Stream(auth=auth.auth(), listener=streamlistener)
    stream.filter(track=['$' + currency])

def getAnalyst():
    # Get the cryptoanalyst
    file = open("cryptoanalyst.txt", "r")
    return file.read().splitlines()

if __name__ == "__main__":
    parseJson.parseSecret()
    apiTwitter = auth.authentification()
    cryptoanalysts = getAnalyst()
    alltweets = []
    while True:
        try:
            for analyst in cryptoanalysts:
                lastTweetFirst = apiTwitter.user_timeline(screen_name = analyst, count = 1, include_rts = False)[0].text
                alltweets.append(lastTweetFirst)
            print alltweets
        except:
            raise
            continue
        time.sleep(60)
    checkTwitter('BCD')
