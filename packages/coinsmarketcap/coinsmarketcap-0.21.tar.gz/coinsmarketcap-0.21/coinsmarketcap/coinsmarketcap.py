import urllib.request
from bs4 import BeautifulSoup
import re
import config
import save


__author__ = "ganakidze"


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

        a = row.find('a', class_='currency-name-container')

        market_cap = row.find('td', class_='no-wrap market-cap text-right')

        try:
            market_cap_filtered = config.filter(market_cap.text)
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

def main(json_=False):
    """
    CoinMarketCap.COM Parser
    """
    config.main()

    currencies = []

    currencies.extend(parse(get_html(config.base())))

    filename = config.osCheck()

    if json_:
        save.main(currencies, filename, json_=True)
    else:
        save.main(currencies, filename)

    print("Job's done")


if __name__ == "__main__":
    main(json_=True)
