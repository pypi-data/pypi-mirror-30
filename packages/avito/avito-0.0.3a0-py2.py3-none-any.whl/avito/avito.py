# -*- coding: utf-8 -*-
import requests
import random
import json
import argparse, sys
from bs4 import BeautifulSoup as bs
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

user_agent_list = [
    'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1',
    'Mozilla/5.0 (Linux; U; Android 4.4.2; en-us; SCH-I535 Build/KOT49H) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30',
    'Mozilla/5.0 (Linux; Android 7.0; SM-G930V Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.125 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 7.0; SM-A310F Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.91 Mobile Safari/537.36 OPR/42.7.2246.114996',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_2 like Mac OS X) AppleWebKit/537.51.2 (KHTML, like Gecko) OPiOS/10.2.0.93022 Mobile/11D257 Safari/9537.53',
    'Mozilla/5.0 (Linux; Android 7.0; SAMSUNG SM-G955U Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/5.4 Chrome/51.0.2704.106 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 6.0; Lenovo K50a40 Build/MRA58K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.137 YaBrowser/17.4.1.352.00 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; U; Android 7.0; en-us; MI 5 Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/53.0.2785.146 Mobile Safari/537.36 XiaoMi/MiuiBrowser/9.0.3',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows Phone 8.0; Trident/6.0; IEMobile/10.0; ARM; Touch; Microsoft; Lumia 950)'
]


def get_phone_number(req=None):
    if is_url(req):
        url = req
    elif str(req).isdigit():
        url = 'https://m.avito.ru/%s' % str(req)
    else:
        return None

    user_agent = random.choice(user_agent_list)
    headers = {'User-Agent': user_agent}
    r = requests.get(url, headers=headers)
    referer = r.url
    soup = bs(r.text, "html.parser")

    try:
        phone_url = soup.select_one('a.action-show-number')['href']
    except TypeError:
        return 'Wrong parameter.'

    url = 'https://m.avito.ru/%s%s' % (phone_url, '?async')
    headers = {'Referer': url, 'User-Agent': user_agent}
    r = requests.get(url, headers=headers)

    return json.loads(r.text)['phone']


def is_url(url):
    return urlparse(str(url)).scheme != ""


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(get_phone_number(sys.argv[1]))
