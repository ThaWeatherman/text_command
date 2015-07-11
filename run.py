from flask import Flask
from flask import request
from flask import redirect
import twilio.twiml

import utils


app = Flask(__name__)
cmd = utils.CommandParser()


def say_price(resp, text):
    resp.say(text)
    resp.say('Goodbye.')
    resp.hangup()


@app.route('/', methods=['POST'])
def root():
    if 'Body' not in request.form and 'From' not in request.form:
        return 'lol'
    msg = request.form['Body']
    resp_msg = cmd.parse_msg(msg)
    resp = twilio.twiml.Response()
    resp.message(resp_msg)
    return str(resp)


@app.route('/welcome', methods=['GET', 'POST'])
def call_welcome():
    resp = twilio.twiml.Response()
    resp.say('Hello and welcome to the text command voice application.')
    resp.redirect(url='/api/call_menu')
    return str(resp)


@app.route('/api/call_menu', methods=['GET', 'POST'])
def call_menu():
    resp = twilio.twiml.Response()
    resp.say('Please listen closely to the following menu options.')
    with resp.gather(numDigits=1, action='/api/handle_call_menu', method='POST') as g:
        g.say('To get the current prices of various precious metals, press 1. '\
              'To get the current prices of various digital currencies, press 2. '\
              'To repeat these options, press 3.')
    return str(resp)


@app.route('/api/handle_call_menu', methods=['GET', 'POST'])
def handle_call_menu():
    digit = request.values.get('Digits', None)
    if digit == '1':
        redirect('/api/metals_menu')
    elif digit == '2':
        redirect('/api/digital_menu')
    else:
        redirect('/api/call_menu')


@app.route('/api/metals_menu', methods=['GET', 'POST'])
def metals_menu():
    resp = twilio.twiml.Response()
    resp.say('Please listen closely to the following menu options')
    with resp.gather(numDigits=1, action='/api/handle_metals_menu', method='POST') as g:
        g.say('To get the current price of gold, press 1. To get the current '\
              'price of silver, press 2. To get the current price of platinum'\
              ', press 3. To get the current price of palladium, press 4. To '\
              'repeat these options, press 5.')
    return str(resp)


@app.route('/api/handle_metals_menu', methods=['GET', 'POST'])
def handle_metals_menu():
    p = utils.PreciousMetalPrices()
    digit = request.values.get('Digits', None)
    resp = twilio.twiml.Response()
    if digit == '1':
        text = p.get_price('gold')
        return say_price(resp, text)
    elif digit == '2':
        text = p.get_price('silver')
        return say_price(resp, text)
    elif digit == '3':
        text = p.get_price('platinum')
        return say_price(resp, text)
    elif digit == '4':
        text = p.get_price('palladium')
        return say_price(resp, text)
    else:
        redirect('/api/metals_menu')


@app.route('/api/digital_menu', methods=['GET', 'POST'])
def digital_menu():
    resp = twilio.twiml.Response()
    resp.say('Please listen closely to the following menu options.')
    with resp.gather(numDigits=1, action='/api/handle_digital_menu', method='POST') as g:
        g.say('To get the current price of Bitcoin, press 1. To get the current '\
              'price of litecoin, press 2. To repeat these options, press 3.')
    return str(resp)


@app.route('/api/handle_digital_menu', methods=['GET', 'POST'])
def handle_digital_menu():
    d = utils.DigitalCurrencyPrices()
    digit = request.values.get('Digits', None)
    resp = twilio.twiml.Response()
    if digit == '1':
        text = d.get_price('btc')
        return say_price(resp, text)
    elif digit == '2':
        text = d.get_price('ltc')
        return say_price(resp, text)
    else:
        redirect('/api/digital_menu')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7777)
