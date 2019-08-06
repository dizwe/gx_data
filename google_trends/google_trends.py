#%%
from pytrends.request import TrendReq
from datetime import datetime
pytrends = TrendReq(hl='en-US', tz=360)

kw_list = ["Blockchain"]
today = datetime.now().strftime("%Y-%m-%d")
pytrends.build_payload(kw_list, cat=13, timeframe=f'2018-05-01 {today}', geo='', gprop='')

#%%
pytrends.interest_over_time()


#%%
data = pytrends.get_historical_interest(kw_list, year_start=2019, month_start=7, day_start=20, hour_start=0, year_end=2019, month_end=8, day_end=1, hour_end=0, cat=0, geo='', gprop='', sleep=0)


#%%
