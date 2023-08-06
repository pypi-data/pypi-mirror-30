from distutils.version import StrictVersion
import webbrowser
import requests
import urllib
import pandas
import json
import io
import ast
import backoff

_map_url = "https://eod.infrontservices.com/feeds.csv"
_ver_url = "https://eod.infrontservices.com/latestVer.txt"
_req_url = "https://eod.infrontservices.com/historical/requests"
_feedmap = pandas.read_csv(_map_url)
_instructions = 'http://infrontfinance.com/support-downloads/infront-desktop-api-for-python'
_latestVer = urllib.request.urlopen(_ver_url)
_latestVer = _latestVer.read()
_latestVer = _latestVer.decode('utf-8-sig').strip()
_localVer = "1.0.9"

# Version check


def ToInstructions():
    print("There is a new version of Infront Desktop API. Would you like to upgrade to version " + _latestVer + "?")
    answer = input("(y/n):")
    if answer == "y":
        webbrowser.open(_instructions)
    else:
        pass


def VersionUpdate():
    if StrictVersion(_latestVer) > StrictVersion(_localVer):
        ToInstructions()

# User credentials
def InfrontConnect(user, password):
    """
    Establish connection for the desktop API for python
    Args:
        user (str): the user name to log in with
        password (str): the password for the given user
    """
    # version control
    VersionUpdate()
    global _username
    _username = user
    global _password
    _password = password
    print('\n Connected to Infront Desktop API for Python 3 version ' + _localVer)
    print('**Disclaimer** \n End-User agrees not to redistribute any such Information and to comply with any \n restrictions placed on such information by the providers thereof, hereunder but \n not limited to acceptance of and compliance with Data Providers’ and/or other \n third party license agreements. \n Customer agrees to indemnify and keep indemnified Infront and its affiliates harmless \n from and against any loss, damage, liability, cost, charges and expenses, including \n reasonable legal fees, arising out of any breach on part of Customer with respect to \n its obligations to obtain prior approvals from appropriate Data Providers and to \n comply with any applicable, conditions, restrictions, or limitations imposed by such \n Data Providers. ')

# Converts user input string to feed and ticker


# def FeedParser(string):
#     feed_id, _ = string.split(':')
#     feednu = int(_feedmap['feednu'][_feedmap['feedcode'] == feed_id])
#     return feednu


# def TickerParser(string):
#     _, ticker_id = string.split(':')
#     return ticker_id

def lookup_feedmap(feed_id):
    try:
        return int(_feedmap['feednu'][_feedmap['feedcode'] == feed_id])
    except:
        raise ValueError("Could find feed ({0})".format(feed_id))

def ListToJSON(string):
    _instruments = []
    for inst in string:
        try:
            feed_id, ticker = inst.split(':')
        except ValueError:
            raise ValueError('Invalid format for ticker: "{0}"'.format(inst))
        feednu = lookup_feedmap(feed_id)
        _dict = {"ticker": ticker, "feed": feednu}
        _instruments.append(_dict)

    return _instruments

@backoff.on_predicate(backoff.expo, lambda x: x['error_code'] == 1, factor=0.05, max_value=10)
def _RequestHistory(url):
    """
    Runs an get request on the given url and retries if it gets error code 1
    Args:
        url (str): the url to use for the get request
    Returns:
        dict of str: the results from the request in a dict
    """
    req_get = requests.get(url).text
    req_dic = ast.literal_eval(req_get)
    if req_dic['error_code'] > 1:
        raise Exception("Response error {0}: {1}".format(
            req_dic['error_code'], req_dic['error_description']))
    return req_dic

def _TryUnpack(data):
    """
    Unpacks the data object into a dataframe object, if the instrument
    has an error, the object will be of type None
    Args:
        data (dict of str): the instrument with historical_trades
    Returns:
        Dataframe or None: the historical_trades with date as index. Returns None data contains an instrument error.
    """
    if "error_code" in data:
        print("Instrument error {0}: '{1}' [{2}:{3}]".format(
            data['error_code'],
            data['error_description'],
            data['feed'],
            data['ticker']))
        return None
    else:
        unpack = data['historical_trades']
        df = pandas.DataFrame(unpack)
        df.set_index('date', inplace=True)
        return df


def GetHistory(tickers, fields, start_date, end_date, adjust_splits=True, adjust_dividend=True):
    """
    Get histroy from tickers
    Args:
        tickers (list of str): the feed and market symbol you want to get history from. \n E.g ["LSE:AAL","OSS:STL"]
        fields (list of str): the fields you want to get data for \n E.g ["last", "volume", "turnover"]
        start_date (str): the start date to get data from in the format 'YYYY-MM-DD'
        end_date (str): the end date to get data from in the format 'YYYY-MM-DD'
        adjust_splits (bool): to adjust splits or not, default = True
        adjust_dividend (bool): to adjust dividend or not, default = True
    Returns:
        Dataframe: the historical trades with date set as index.
    """
    if type(tickers) is not list:
        raise ValueError(
        'You need to input a feed and market symbol as a list with items of type string. \n E.g. ["LSE:AAL","OSS:STL"]')
    if type(fields) is not list:
        raise ValueError(
            'Fields inputs must be of a list with items of type string. \n E.g. ["last","volume","turnover"]')
    if type(start_date) is not str:
        raise ValueError(
            "'start_date' input must be a string in the format 'YYYY-MM-DD' ")
    if type(end_date) is not str:
        raise ValueError(
            "'end_date' input must be a string in the format 'YYYY-MM-DD' ")

    numItems = len(tickers)
    for items in range(len(fields)):
        if fields[items] == 'volume':
            fields[items] = 'prev_volume'

    fields.append('date')

    req_payload = {
        "user": _username,
        "password": _password,
        "context": "user specific context",
        "historical_request": {
            "fields": fields,
            "start_date": start_date,
            "end_date": end_date,
            "adjust_splits": adjust_splits,
            "adjust_dividends": adjust_splits,
            "instruments": ListToJSON(tickers)
        }
    }
    req_post = requests.post(_req_url, json=req_payload, verify=True).text

    req_resp = dict(ast.literal_eval(req_post))
    if req_resp['error_code'] > 1:
        raise Exception("Response error {0}: {1}".format(
            req_resp['error_code'], req_resp['error_description']))

    req_url = req_resp['historical_response']['full_response_url']
    hist_data = _RequestHistory(req_url)['historical_data']

    out = {}
    for item in hist_data:
        out.update({item['ticker']: _TryUnpack(item)})

    return out

# ToMatrixFrom(MySymbols,field) / MySymbols = dict of DFs / field = string, e.g. "last"


def ToMatrixForm(MySymbols, field):
    firstItem = next(iter(MySymbols))
    base = MySymbols[firstItem][field].rename(firstItem)
    skip = base.name
    for key in MySymbols:
        if key != skip:
            toAdd = MySymbols[key][field].rename(key)
            base = pandas.concat([base, toAdd], axis=1, join='inner')
    return base
