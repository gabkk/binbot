import json

dataTwitter = []

def parseTwitter(data):
    global dataTwitter
    dataTwitter = data["Twitter param"]

def parseSecret():
    data = json.load(open('secrets_template.json'))
    parseTwitter(data)
