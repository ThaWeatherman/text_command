import utils


def main():
    sms = utils.SMSParser()
    cmd = utils.CommandParser()

    msgs = sms.get_messages()
    for msg in msgs:
        if msg['from'] == 'Me:':
            sms.delete_message(msg['id'])
            continue
        sms.set_sender(msg['from'])
        response = cmd.parse_msg(msg['text'])
        sms.set_msg(response)
        sms.send()
        sms.delete_message(msg['id'])


if __name__ == '__main__':
    main()
