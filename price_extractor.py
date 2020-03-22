import pandas as pd
import pandas_datareader.data as web


class price_extractor:

    def __init__(self, api, companies):
        print('Initialised Price Extractor')
        self.__api = api
        self.__companies = companies
        pass

    def get_prices(self,  event, start_date, end_date):
        prices = pd.DataFrame()
        symbols = self.__companies['Ticker']
        tmp={}
        for i in symbols:
            try:
                tmp = web.DataReader(i, self.__api, start_date, end_date)
                print('Fetched prices for: '+i)                
            except:
                print('Issue getting prices for: '+i)
            else:
                prices[i] = tmp[event]            
        return prices