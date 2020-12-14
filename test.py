import json
import time
from coinmarketcapapi import CoinMarketCapAPI,CoinMarketCapAPIError
import requests
import pickle

#open file to secure api key 
with open ('coinmarketcap API Key.txt','r') as file_cmcapi:
    cmc_api_token=file_cmcapi.readline()

with open ('line API key.txt','r') as file_lineapi:
    line_api_token=file_lineapi.readline()

#parameters for request
url_line = 'https://notify-api.line.me/api/notify'
headers = {'content-type':'application/x-www-form-urlencoded','Authorization':'Bearer '+line_api_token}


#get coin dict from a file using pickle
def readfiletodict(filename):
    with open (filename,'rb') as file_to_read:
        coin_price_dict=dictionary = pickle.load(file_to_read)
        return coin_price_dict

def writedicttofile(write_dict,filename):
    with open(filename, "wb") as file_to_write:
        pickle.dump(write_dict, file_to_write)
    

cmc = CoinMarketCapAPI(cmc_api_token)
coin_name_list=['BTC','ETH','XRP','LTC','BCH','LINK','ADA','DOT','BNB','YFI','LUNA']
coin_price_dict=readfiletodict('coinpricedict.txt')
coin_signal=readfiletodict('coinsignal.txt')

#check the index of the coin name
def getcoinlist():
    coin_index_list=[]
    alldata= cmc.cryptocurrency_listings_latest(limit=100)
    coin_alldata=alldata.data
    for i in range(0,100):
        if coin_alldata[i]['symbol'] in coin_name_list:
            coin_index_list.append(i)
    return coin_index_list


def getcoinprice():
    #call the data from the list limit mean top 100
    alldata= cmc.cryptocurrency_listings_latest(limit=100)
    coin_alldata=alldata.data
    coin_index=getcoinlist()
    for coin in coin_index:
        coin_name=coin_alldata[coin]['symbol']
        coin_price=coin_alldata[coin]['quote']['USD']['price']
        if coin_name not in coin_signal:
            coin_signal[coin_name]="-"
        if coin_name not in coin_price_dict:
            coin_price_dict[coin_name]=[coin_price]
        else:
            coin_price_dict[coin_name].append(coin_price)
    writedicttofile(coin_price_dict,'coinpricedict.txt')
    writedicttofile(coin_signal,'coinsignal.txt')
    print('coin price dictionary is',coin_price_dict)

#calculate Simple Moving Average
def sma(lst_sum,n):
    summ=0
    if len(lst_sum)>n:
        use_lst=lst_sum.reverse()
        use_lst=lst_sum[0:n]
        print("use_lst",use_lst)
        for value in use_lst:
            summ+=value
    else:
        for value in lst_sum:
            summ+=value
    use_lst=lst_sum.reverse()
    return summ/n

#check for signal
def calculatesma():
    for coin_name,coin_price in coin_price_dict.items():
        sma15=sma(coin_price,15)
        sma30=sma(coin_price,30)
        #send buy signal
        if sma15 > sma30 and coin_signal[coin_name] != "Buy":
            msg = "Buy Signal For "+str(coin_name)+"@ $ "+str(coin_price[-1])
            r = requests.post(url_line, headers=headers, data = {'message':msg})
            print(r.text)
            coin_signal[coin_name] = "Buy"
            writedicttofile(coin_signal,'coinsignal.txt')
        #send sell signal
        elif sma30 > sma15 and coin_signal[coin_name] != "Sell":
            msg="Sell Signal For  "+str(coin_name)+"@ $ "+str(coin_price[-1])
            r = requests.post(url_line, headers=headers, data = {'message':msg})
            print(r.text)
            coin_signal[coin_name] = "Sell"
            writedicttofile(coin_signal,'coinsignal.txt')
    print('coin signal is',coin_signal)
    
def main():
    getcoinprice()
    calculatesma()

while(True):
    print(time.ctime())
    main()
    time.sleep(3600)
