import urllib.request
from bs4 import BeautifulSoup
import re
import locale
from datetime import datetime
import sys
import os
import xlsxwriter
import json

__author__ = "ganakidze"

try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, '')

BASE_URL = 'https://coinmarketcap.com/all/views/all/'


def get_html(url):
    res = urllib.request.urlopen(url)
    return res.read()


def parse(html):
    soup = BeautifulSoup(html, 'html5lib')
    table = soup.find(
        'div', class_='table-responsive compact-name-column')

    currencies = []

    for row in table.find_all('tr')[1:]:
        cols = row.find_all('td')
        # print(cols)

        a = row.find('a', class_='currency-name-container')

        market_cap = row.find('td', class_='no-wrap market-cap text-right')

        try:
            market_cap_filtered = locale.format('%d', int(re.sub("\D", "", market_cap.text)), True)
        except ValueError:
            market_cap_filtered = '?'

        supply = row.find('td', class_='no-wrap text-right circulating-supply')

        try:
            supply_filtered = int(re.sub("\D", "", supply.text))
        except ValueError:
            supply_filtered = "?"

        currencies.append({
            'Currency Name': a.text,
            'Price': cols[4].a.text,
            '24 Hour Volume': cols[6].a.text,
            'Market Capitalization': "${}".format(market_cap_filtered),
            'Circulating Supply': supply_filtered
        })

    return currencies


def save(currencies, path, json_=False):
    if not json_:
        path = "{}.{}".format(path, 'xlsx')
        row = 1
        col = 0
        columns = ['A', 'B', 'C', 'D', 'E']

        workbook = xlsxwriter.Workbook(path)
        worksheet = workbook.add_worksheet()
        bold = workbook.add_format({'bold': True})
        for item in columns:
            worksheet.set_column('%s:%s' % (item, item), 20)

        worksheet.write('A1', 'Currency name', bold)
        worksheet.write('B1', 'Price', bold)
        worksheet.write('C1', 'Market Capitalization', bold)
        worksheet.write('D1', '24 Hour Volume', bold)
        worksheet.write('E1', 'Circulating supply', bold)

        for currency in currencies:
            worksheet.write(row, col, currency['Currency Name'])
            worksheet.write(row, col + 1, currency['Price'])
            worksheet.write(row, col + 2, currency['Market Capitalization'])
            worksheet.write(row, col + 3, currency['24 Hour Volume'])
            worksheet.write(row, col + 4, currency['Circulating Supply'])

            row += 1
    else:
        path = "{}.{}".format(path, "json")
        with open(path,'w') as json_file:
            json.dump(currencies, json_file)


def main(json_=False):
    """
    CoinMarketCap.COM Parser
    """

    if sys.platform == 'win32':
        filename = os.getcwd() + '\\coins-{}'.format(datetime.now().strftime('%Y-%m-%d %H-%M-%S'))
    else:
        filename = 'coins-{}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    currencies = []

    currencies.extend(parse(get_html(BASE_URL)))

    if json_:
        save(currencies, filename, json_=True)
    else:
        save(currencies, filename)

    print("Job's done")


if __name__ == "__main__":
    main(json_=False)
