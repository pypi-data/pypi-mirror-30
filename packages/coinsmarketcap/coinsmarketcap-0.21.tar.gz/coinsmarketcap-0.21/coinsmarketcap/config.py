import locale
import os
import sys
from datetime import datetime
import re

BASE_URL = 'https://coinmarketcap.com/all/views/all/'

def base():
    return BASE_URL

def main():
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except locale.Error:
        locale.setlocale(locale.LC_ALL, '')

def osCheck():
    if sys.platform == 'win32':
        filename = os.getcwd() + '\\coins-{}'.format(datetime.now().strftime('%Y-%m-%d %H-%M-%S'))
    else:
        filename = 'coins-{}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    return filename

def filter(textToFilter):
    finalResult = locale.format('%d', int(re.sub("\D", "", textToFilter)), True)
    return finalResult
