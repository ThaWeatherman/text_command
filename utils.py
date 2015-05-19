from __future__ import division

import requests
from bs4 import BeautifulSoup


class PreciousMetalPrices(object):
    def __init__(self):
        self.url = 'http://www.apmex.com'


    def get_apmex(self):
        req = requests.get(self.url)
        return req.content


    def get_table(self):
        page = self.get_apmex()
        soup = BeautifulSoup(page)
        table = soup.find('table')
        rows = table.find_all(lambda tag: tag.name=='tr')
        return rows


    def get_entry(self, name):
        rows = self.get_table()
        del rows[0]
        for row in rows:
            tds = row.find_all(lambda tag: tag.name=='td')
            if tds[0].string.lower() == name:
                return [tds[1], tds[2]]


    def construct_message(self, tds):
        return 'Bid: ' + tds[0].string + '\nAsk: ' + tds[1].string


    def get_price(self, metal):
        '''
        Valid values of metal are: Gold, Silver, Platinum, Palladium
        '''
        tds = self.get_entry(metal.lower())
        return self.construct_message(tds)


class DigitalCurrencyPrices(object):
    def __init__(self):
        self.btc_url = 'http://preev.com/pulse/units:btc+usd/sources:bitfinex+bitstamp+btce+localbitcoins'
        self.ltc_url = 'http://preev.com/pulse/units:ltc+usd/sources:btce'
        self.url = ''


    def get_avg(self, prices):
        total = sum(prices)
        return total / len(prices)


    def get_price(self, coin):
        if coin == 'btc':
            self.url = self.btc_url
        elif coin == 'ltc':
            self.url = self.ltc_url
        req = requests.get(self.url)
        data = req.json()
        prices = []
        for entry in data[coin]['usd']:
            prices.append(float(data[coin]['usd'][entry]['last']))
        avg = self.get_avg(prices)
        msg = 'Last ' + coin.upper() + ' price: ' + str(avg)
        return msg


class Weather(object):
    def __init__(self, key):
        self.api_key = key
        self.url_base = 'http://api.openweathermap.org/data/2.5/weather?'
        self.zipcode_url = 'zip='
        self.city_search_url = 'q='
        self.temperature_type = '&units=imperial'


    def weather_by_zipcode(self, zipcode):
        url = self.url_base + self.zipcode_url + zipcode + self.temperature_type
        req = requests.get(url)
        data = req.json()
        current_temp = data['main']['temp']
        current_humidity = data['main']['humidity']
        temp_min = data['main']['temp_min']
        temp_max = data['main']['temp_max']
        conditions = data['weather'][0]['description']
        city = data['name']
        msg = 'Weather report for {}: Current Temp - {}F\nCurrent Humidity - {}\nMin Temp - {}F\nMax Temp - {}F\nConditions - {}'.format(\
                city, str(current_temp), str(current_humidity), str(temp_min), str(temp_max), conditions)
        return msg

    
    def weather_by_city(self, city):
        # TODO
        pass
