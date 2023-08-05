import csv
import urllib.request
from bs4 import BeautifulSoup
import re
import locale
from datetime import datetime

__author__ = "ganakidze"


try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, '')

BASE_URL = 'https://coinmarketcap.com/'


def get_html(url):
    res = urllib.request.urlopen(url)
    return res.read()


def parse(html):
    soup = BeautifulSoup(html, 'html5lib')
    table = soup.find(
        'div', class_='table-fixed-column-mobile compact-name-column')

    currencies = []

    for row in table.find_all('tr')[1:]:
        cols = row.find_all('td')

        a = row.find('a', class_='currency-name-container')

        market_cap = row.find('td', class_='no-wrap market-cap text-right')

        market_cap_filtered = locale.format('%d', float(market_cap.text), True)

        supply = row.find('td', class_='no-wrap text-right circulating-supply')

        supply_filtered = int(re.sub("\D", "", supply.text))

        currencies.append({
            'Currency Name': a.text,
            'Price': cols[3].a.text,
            '24 Hour Volume': cols[4].a.text,
            'Market Capitalization': "${}".format(market_cap_filtered),
            'Circulating Supply': supply_filtered
        })

    return currencies


def save(currencies, path):
    with open(path, 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(('Currency name', 'Price', 'MarketCap',
                         'Volume (24h)', 'Circulating supply'))

        for currency in currencies:
            writer.writerow(
                (currency['Currency Name'],
                 currency['Price'],
                 currency['Market Capitalization'],
                 currency['24 Hour Volume'],
                 currency['Circulating Supply']))


def main():
    """

    CoinMarketCap.COM Parser

    """

    currencies = []

    currencies.extend(parse(get_html(BASE_URL)))

    save(currencies, 'coins-{}.csv'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

    print("Job's done")


if __name__ == "__main__":
    main()

