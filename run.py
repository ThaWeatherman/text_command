from flask import Flask
from flask import request
import twilio.twiml

import utils


app = Flask(__name__)
cmd = utils.CommandParser()


@app.route('/', methods=['POST'])
def root():
    if 'Body' not in request.form and 'From' not in request.form:
        return 'lol'
    msg = request.form['Body']
    resp_msg = cmd.parse_msg(msg)
    resp = twilio.twiml.Response()
    resp.message(resp_msg)
    return str(resp)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7777)
