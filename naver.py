#%%
##### GET_DATA
import requests
import json
import pprint

headers = {'X-Naver-Client-Id': 'bfTkg54c3nugOrnMU81d',
            'X-Naver-Client-Secret' : os.getenv('NAVER_SECRET')

page = 0
data = []
# https://developers.naver.com/docs/search/news/
# https://developers.naver.com/forum/posts/3786
while True:
    r = requests.get('https://openapi.naver.com/v1/search/news.json?query=카카오 클레이튼&display=100&start={}'.format(100*page+1),headers=headers)
    result = json.loads(r.text)
    if result.get('errorCode','')=='SE03':
        print(result)
        break
    data = data + result['items']
    page = page+1

#%%
##### 추후에 데이터 주기적으로 붙일 수 있는 기능 추가해야 할듯(later)

  
#%%
##### DB에 데이터 넣기
from datetime import datetime

def naverdata_to_array(data):
    # column_list = ['data_date','title ','description','link','original_link']
    column_list = ['pubDate','title','description','link','originallink']
    def column_combine_lambda(x):
        k = []
        for one_column in column_list:
            if one_column=='pubDate':
                # Fri, 26 Jul 2019 10:30:00 +0900
                k.append(datetime.strptime(x['pubDate'],'%a, %d %b %Y %H:%M:%S %z').strftime('%Y-%m-%d'))
            else:
                k.append(x[one_column])
        return k

    return list(map(column_combine_lambda,data))


def db_connect(data):
  import psycopg2
  from psycopg2.extras import execute_values
  import os

  try:
    connection = psycopg2.connect(user = os.getenv('PGUSER'),
                                  password = os.getenv('PGPASSWORD'),
                                  host = os.getenv('PGHOST'),
                                  port = "5432",
                                  database = os.getenv('PGDATABASE'))

    cursor = connection.cursor()
    # cursor.execute("""  """)

    execute_values(cursor,
    """insert into ods_google.naver_news (data_date,title,description,link,original_link) VALUES %s""",
    data)
    connection.commit()
  
    # record = cursor.fetchall() # fetchone(), fetchmanxy(), fetcthall().
  
  except (Exception, psycopg2.Error) as error :
      print("Error while connecting to PostgreSQL", error)
  finally:
      #closing database connection.
      if(connection):
        cursor.close()
        connection.close()

data_array = naverdata_to_array(data)
db_connect(data_array)


#%%
