import requests
import re
from bs4 import BeautifulSoup


class SmartGet(object):
    UA = 'Mozilla/5.0 (Linux; Android 7.0; SAMSUNG SM-G950U Build/NRD90M)'\
         'AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/5.2 '\
         'Chrome/51.0.2704.106 Mobile Safari/537.36'
    UA_PC = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '\
            ' (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'
    ua_dict = {
        'pc': UA_PC,
        'mobile': UA
    }

    def __init__(self, ua='pc'):
        self.headers = {'User-Agent': SmartGet.ua_dict.get(ua, ua)}

    def get(self, url):
        r = requests.get(url, headers=self.headers)
        r.encoding = self._get_encoding(BeautifulSoup(r.text))
        return r

    def _get_encoding(self, soup):
        """Check Encoding for web page

        1. Check charset
        2. Check content-type
        3. Check content

        """
        encod = soup.meta.get('charset')
        if not encod:
            encod = soup.meta.get('content-type')
            if not encod:
                content = soup.meta.get('content')
                match = re.search('charset=(.*)', content)
                if match:
                    encod = match.group(1)
                else:
                    encod = 'utf-8'
        return encod
