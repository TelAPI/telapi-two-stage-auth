from functools import partial
import requests
from requests.auth import HTTPBasicAuth
import logging
import json


class TelApi(object):
    def __init__(self, account_sid, account_token, base_number):
        self.account_sid = account_sid
        self.account_token = account_token
        self.base_number = base_number
        self.url = 'https://api.telapi.com/2011-07-01'

    def get_available_number(self, area_code):
        url = self.url + '/Accounts/%s/AvailablePhoneNumbers/US/Local.json'
        url = url % self.account_sid
        params = {
            'AreaCode': area_code,
            }
        logging.debug(url)
        logging.debug(params)
        numbers = self._call('get', url, params)
        try:
            number = numbers['available_phone_numbers'][0]
            return number['phone_number']
        except IndexError:
            return None

    def add_phone_number(self, area_code, number):
        url = self.url + '/Accounts/%s/IncomingPhoneNumbers'
        url = url % self.account_sid
        params = {
            'PhoneNumber': number,
            'AreaCode': area_code,
            }
        logging.debug(url)
        logging.debug(params)
        return self._call('post', url, params)

    def provision_phone_number(self, area_code):
        while True:
            number = self.get_available_number(area_code)
            try:
                self.add_phone_number(area_code, number)
                return number
            except:
                return number

    def get_phone_number_info(self, number):
        url = self.url + '/Accounts/%s/IncomingPhoneNumbers.json'
        url = url % self.account_sid
        params = {
            'PhoneNumber': number,
            }
        logging.debug(url)
        logging.debug(params)
        resp = self._call('get', url, params)
        return resp['incoming_phone_numbers'][0]

    def send_sms(self, sms_to, sms_body):
        logging.debug(sms_body)
        url = self.url + '/Accounts/%s/SMS/Messages.json'
        url = url % self.account_sid
        params = {
            'AccountSid': self.account_sid,
            'From': self.base_number,
            'To': sms_to,
            'Body': sms_body,
            }
        logging.debug(url)
        logging.debug(params)
        rv = self._call('post', url, params)
        logging.debug(rv)
        return rv

    def send_phone_call(self, phone_number, telml_url):
        url = self.url + '/Accounts/%s/Calls.json'
        url = url % self.account_sid
        params = {
            'Url': telml_url,
            'From': self.base_number,
            'To': phone_number,
            }
        logging.debug(url)
        logging.debug(params)
        rv = self._call('post', url, params)
        logging.info(rv)
        return rv

    def create_conference(self, number, call_handler_url):
        info = self.get_phone_number_info(number)
        url = self.url + '/Accounts/%s/IncomingPhoneNumbers/%s.json'
        url = url % (self.account_sid, info['sid'])
        params = {
            'VoiceUrl': call_handler_url,
            'VoiceMethod': 'POST',
            }
        return self._call('post', url, params)

    def _call(self, method, url, params):
        method = getattr(requests, method)
        func = partial(method, url, auth=HTTPBasicAuth(self.account_sid,
                                                       self.account_token))
        if method == 'get':
            func = partial(func, params=params)
        else:
            func = partial(func, data=params)
        resp = func()
        try:
            resp.raise_for_status()
        except:
            logging.debug(resp.content)
            raise
        logging.debug(resp.content)
        return json.loads(resp.content)
