# text_command

This app was originally written to use Google Voice. 
Feel free to dig through the commit history if you really want that. 
I will warn you that the PyGoogleVoice library only works sometimes. 
There are also so many forks of it that I don't know which I used that worked. 
I could only get it to work on my personal laptop, which is not very practical.

## Description

This app receives text messages and responds accordingly to them. 
The messages contain a command that the application understands. 
Upon receiving a command the application generates the proper response and sends 
it back via Twilio.

This application is an outgrowth of me wanting silver prices when I do not have internet access. 
I decided to use Google Voice (since I'm a cheapo) since when I do not have internet access I will 
usually still have cell access.

### Commands

`weather`: Get the weather for a specified zipcode. Send `weather zipcode *****` where 
`*****` is the target zipcode.  
`btc', 'ltc': Get the current average price of Bitcoin or Litecoin. Uses [Preev](http://preev.com).  
`gold`, `silver`, `platinum`, `palladium`: Get the current price of the desired precious metal. 
Prices are based on [APMEX](https://www.apmex.com).  
`stock`: Uses the Yahoo Finance API to retrieve current stock prices for the specified stock. 
Example: `stock GOOG`.  
`time`: Get the current local time for the specified location. Example: `time California`.

This list may be updated in the future as more functionality is added.

## Usage

This runs a [Flask](http://flask.pocoo.org/) web application to handle incoming messages. 
You will need a Twilio paid account and some publicly accessible server to run this.

### Dependencies

Go make an account with [Twilio](https://www.twilio.com). Buy a number for $1 a month. 
It does not matter where the number is from: all that matters is that it can receive SMS.

Next, make an account at DigitalOcean (assuming you do not already have your own server). 
I run my website off of a droplet there, so I already had one. Small servers are cheap, and 
you will not regret having one. Just make a Linux server.

On your server you will need to install the necessary libraries (and Python). Assuming you 
are on Ubuntu (since most people use it):

```
apt-get install python python-pip python-dev build-essential git
pip install --upgrade pip
git clone https://github.com/ThaWeatherman/text_command.git
cd text_command
pip install -r requirements.txt
```

These commands assume you are the `root` user. If you are not, then just tack a `sudo` on the front. 
This should take care of everything you need.

### Configuring

Create an account at [TimezoneDB](http://timezonedb.com/) and get an API key. 
You will notice there is a file called `config.ini.sample` in the repository. 
Rename it to `config.ini` then open it and replace the text `somekey` with your API key from TimezoneDB. 

Now go back to Twilio and select "Numbers" along the top. On that page, click on the number you created.
This will take you to a configuration area. Under "SMS & MMS" click the "URL" radio button then in the 
"Request URL" field enter the IP address of your server. Say your server's public IP is `108.234.56.78`: 
then you would enter `http://108.234.56.78:7777` where `7777` is the port the application runs on. Hit save.

### Running

```
cd text_command
python run.py
```

Now just text your Twilio number `help` to get a list of commands and you are ready to go!

### Notes

If you created a DigitalOcean droplet, note that it installs `iptables` as a firewall. You will need to make 
sure any firewall you have installed is not blocking traffic to TCP port 7777.
