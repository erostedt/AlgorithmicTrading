import requests
from bs4 import BeautifulSoup
import datetime
import pandas as pd

URL = 'https://www.privataaffarer.se/borsguiden/kalendarium-och-dagens-agenda/borskalender'
CALENDER_TYPES = ['reports','sharedesc','meeting']

def _reps(page):
    soup = BeautifulSoup(page.content, 'html.parser')
    columns = soup.thead
    columns = columns.find_all('th')
    for i in range(len(columns)):
        columns[i] = columns[i].get_text()
    columns.append('Link')    
     
    rows = soup.tbody
    rows = rows.find_all('tr')
    reports = []

    for r in rows:
        report = []
        link = r.a.get('href')
        tds = r.find_all('td')

        for td in tds:
            report.append(td.get_text())

        report.append(link)

        reports.append(report)
                
    return pd.DataFrame(reports, columns=columns)

def _stock_list_ids(page):
    soup = BeautifulSoup(page.content, 'html.parser')
    opts = soup.find('select', {'name':'stockListMarketPlaceId'})
    opts = opts.find_all('option')
    ids = []
    for o in opts[1:]:
        ids.append(o.get('value'))

    return ids


def get_possible_markets():
    return _stock_list_ids(requests.get(URL))

def get_upcoming_events(market):
    ret = {}
    for ctype in CALENDER_TYPES:
        form_data = {'calendartype':ctype, 'majorSectorId':'', 'stockListMarketPlaceId': market}
        ret[ctype] = _reps(requests.post(URL, data=form_data))

    return ret

markets = get_possible_markets()
print(markets)
print(get_upcoming_events(markets[10]))

