from __future__ import division

import requests
from bs4 import BeautifulSoup
from googlevoice import Voice


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


    def construct_message(self, metal, tds):
        return metal.upper() + ' Bid: ' + tds[0].string + '\nAsk: ' + tds[1].string


    def get_price(self, metal):
        '''
        Valid values of metal are: Gold, Silver, Platinum, Palladium
        '''
        tds = self.get_entry(metal.lower())
        return self.construct_message(metal, tds)


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

class SMSParser(object):
    def __init__(self):
        self.voice = Voice()
        self.sender = ''
        self.msg = ''


    def login(self):
        self.voice.login()


    def send(self):
        self.login()
        self.voice.send_sms(self.sender, self.msg)


    def extractsms(self, htmlsms) :
        """
        extractsms  --  extract SMS messages from BeautifulSoup tree of Google Voice SMS HTML.

        Output is a list of dictionaries, one per message.
        """
        msgitems = []
        #   Extract all conversations by searching for a DIV with an ID at top level.
        tree = BeautifulSoup(htmlsms)
        conversations = tree.find_all("div", attrs={"id" : True}, recursive=False)
        for conversation in conversations :
            #       For each conversation, extract each row, which is one SMS message.
            rows = conversation.find_all(attrs={"class" : "gc-message-sms-row"})
            for row in rows:
                msgitem = {"id" : conversation["id"]}
                spans = row.find_all("span",attrs={"class" : True}, recursive=False)
                for span in spans:
                    cl = span["class"][0].replace('gc-message-sms-', '')
                    msgitem[cl] = (" ".join(span.find_all(text=True))).strip()
                msgitems.append(msgitem)
        return msgitems


    def get_messages(self):
        self.login()
        self.voice.sms()
        messages = self.extractsms(self.voice.sms.html)
        return messages


    def delete_message(self, msg_id):
        self.login()
        for msg in self.voice.sms().messages:
            if msg.id == msg_id:
                msg.delete()


    def set_sender(self, sender):
        self.sender = sender


    def set_msg(self, msg):
        self.msg = msg


class CommandParser(object):
    def __init__(self):
        self.valid_commands = ['weather', 'btc', 'ltc', 'gold', 'silver', 'platinum', 'palladium', 'help']
        self.weather_commands = ['zipcode']
        self.weather = Weather('')
        self.metals = PreciousMetalPrices()
        self.digital = DigitalCurrencyPrices()
        self.helps = {
                'btc': 'Send "btc" to get latest average price of Bitcoin',
                'ltc': 'Send "ltc" to get latest average price of Litcoin',
                'gold': 'Send "gold" to get latest price of Gold from APMEX',
                'silver': 'Send "silver" to get latest price of Silver from APMEX',
                'platinum': 'Send "platinum" to get latest price of Platinum from APMEX',
                'palladium': 'Send "palladium" to get latest price of Palladium from APMEX',
                'weather': '"weather [option]". Valid options are: zipcode\n"weather zipcode [zip]" for weather in specified USA zipcode'
                }
        self.general_help = 'Valid commands: ' + ', '.join(self.valid_commands) + '\nSend "help [command]" for specifics'


    def help_respond(self, params):
        if len(params) == 1:
            return self.general_help
        if params[1] not in self.valid_commands:
            return self.general_help
        return self.helps[params[1]]


    def parse_msg(self, msg):
        '''
        Valid commands: weather, btc, ltc, gold, silver, palladium, platinum, help
        '''
        text = msg.strip().lstrip().lower()
        params = text.split(' ')
        if params[0] not in self.valid_commands:
            return 'Invalid command: send "help" for a list of valid commands'
        if params[0] == 'help':
            return self.help_respond(params)
        if params[0] == 'btc':
            return self.digital.get_price('btc')
        if params[0] == 'ltc':
            return self.digital.get_price('ltc')
        if params[0] == 'gold':
            return self.metals.get_price('gold')
        if params[0] == 'silver':
            return self.metals.get_price('silver')
        if params[0] == 'platinum':
            return self.metals.get_price('platinum')
        if params[0] == 'palladium':
            return self.metals.get_price('palladium')
        if params[0] == 'weather':
            if not len(params) > 1:
                return self.helps['weather']
            if params[1] not in self.weather_commands:
                return self.helps['weather']
            if params[1] == 'zipcode':
                if not len(params) > 2:
                    return self.helps['weather']
                if not params[2].isnumeric():
                    return self.helps['weather']
                if len(params[2]) != 5:
                    return 'Valid zipcode is 5 digits'
                return self.weather.weather_by_zipcode(params[2])
