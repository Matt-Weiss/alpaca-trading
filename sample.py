import alpaca_trade_api as tradeapi
import pandas as pd
import requests
import time
from pytz import all_timezones, timezone
from datetime import datetime, timedelta, date

base_url = 'https://paper-api.alpaca.markets'
api_key_id = 'PKMORDL6CT0Q0RHCH64E'
api_secret = 'JjadLifH2GAxNtZfe62JgxB5wlPb4dghdofUE7f5'

api = tradeapi.REST(
    base_url=base_url,
    key_id=api_key_id,
    secret_key=api_secret
)

# print('Getting current ticker data...')
# tickers = api.polygon.all_tickers()
# print('Ticker Count:', len(tickers))
# print('Success.')

# yesterday=date.today() - timedelta(days=1)
# six_days_ago = date.today() - timedelta(days=6)
# calendar = api.get_calendar(start=six_days_ago, end=date.today())
# calendar_today = calendar.pop()
# calendar_last_trade_day = calendar.pop(-1).date
# calendar_two_days_ago = calendar.pop(-2).date
# aapl = api.polygon.historic_agg_v2('AAPL', 1, 'minute', _from=six_days_ago, to=date.today()).df.tail(1000)
# # with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', 250):  # more options can be specified also
# print(aapl)
# print(calendar_today)
# print(calendar_last_trade_day)
# print(calendar_two_days_ago)
# print(date.today() - timedelta(days=1))

# text = 'But I doubt it will run very well'
# new_text = ''

# for char_index in range(len(text)):
#     if char_index % 2 == 0:
#         new_text += text[char_index].upper()
#     else:
#         new_text += text[char_index].lower()

# print(new_text)

nyc = timezone('America/New_York')
today = datetime.today().astimezone(nyc)
today_str = datetime.today().astimezone(nyc).strftime('%Y-%m-%d')
calendar = api.get_calendar(start=today_str)
market_open = None
market_close = None

def set_markets(index):
    market_open = calendar[index].date.replace(
        hour=calendar[index].open.hour,
        minute=calendar[index].open.minute,
        second=0,
        tzinfo=nyc
    ).to_pydatetime()

    market_close = calendar[index].date.replace(
        hour=calendar[index].close.hour,
        minute=calendar[index].close.minute,
        second=0,
        tzinfo=nyc
    ).to_pydatetime()
    return market_open, market_close
    
market_open, market_close = set_markets(0)
if market_close < datetime.now(nyc):
    market_open, market_close = set_markets(1)

print('market_open:', market_open)
print('market_close:', market_close)

# Wait until just before we might want to trade
current_dt = datetime.today().astimezone(nyc)
since_market_open = int((current_dt - market_open).total_seconds())
while since_market_open < 0:
    hours, remainder = divmod(abs(since_market_open), 3600)
    minutes, seconds = divmod(remainder, 60)
    print(f'Market opens in {hours} hours, {minutes} minutes, and {seconds} seconds   \r', end='')
    time.sleep(1)
    current_dt = datetime.today().astimezone(nyc)
    since_market_open = int((current_dt - market_open).total_seconds())
while since_market_open // 60 <= 14:
    minutes, seconds = divmod(since_market_open, 60)
    print(f'Market has been open {minutes} minutes and {seconds} seconds. Delaying trading until Market open 15 minutes    \r', end='')
    time.sleep(1)
    current_dt = datetime.today().astimezone(nyc)
    since_market_open = int((current_dt - market_open).total_seconds())
