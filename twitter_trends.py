#%%
import requests
import os

auth_header = {
  'consumer_key': '4RTtiiqxX4ID949CZi7Wnr62M',
  'consumer_secret': os.environ['CONSUMER_SECRET'],
  'access_token_key': '1127968910-XAALt7MLvPZuQzRS33Ksf4RtzaOBy6rXSBMzcHD',
  'access_token_secret': os.environ['ACCESSTOKEN_SECRET'],
}
START = '2019-07-25'
END = '2019-08-02'
q = 'klaytn'
# head = {'authorization':'OAuth oauth_consumer_key'}
# requests.get('https://api.twitter.com/1.1/',)


#%%

import oauth2

def oauth_req(url, key, secret, http_method="GET", post_body=b"", http_headers=None):
    consumer = oauth2.Consumer(key=auth_header['consumer_key'], secret=auth_header['consumer_secret'])
    token = oauth2.Token(key=key, secret=secret)
    client = oauth2.Client(consumer, token)
    resp, content = client.request(url, method=http_method, body=post_body, headers=http_headers)
    return content

#%%
import json
# {q: q,max_id:next_page_max_id,since_id:since_id,count:100}
tweets_bytes = oauth_req(f'https://api.twitter.com/1.1/search/tweets.json?q={q}&until={START}',
                         auth_header['access_token_key'],
                         auth_header['access_token_secret'])
# bytes로 받아져서 수정해줘야 함
tweets = json.loads(tweets_bytes.decode('utf8'))

#%%
##### 시작점 받기
since_id=0
if len(tweets['statuses'])>0: # 아예 tweets이 없을 수도 있음.
    since_id =  tweets['statuses'][0]['id']
    print('created_at',tweets['statuses'][0]['created_at'])
    print('since_id', since_id)
    # return client.get('search/tweets', {q: q,since_id:since_id, until:end, count:100});

#%%
from functools import reduce
import re
raw_data = []
retweet_num, favorite_num, tweets_num = 0,0,0
if since_id != 0: # 빈 내용이 아니라면
    tweets_bytes = oauth_req(f'https://api.twitter.com/1.1/search/tweets.json?q={q}&since_id={since_id}&until={END}&count=100',
                        auth_header['access_token_key'],
                        auth_header['access_token_secret'])
    tweets = json.loads(tweets_bytes.decode('utf8'))
    statuses = tweets['statuses']

    while len(statuses)>0: # 페이지 끝날때까지 확인!
        ## 트윗 확인
        # for status in tweets['statuses']:
        #     print(status.get('text',''))

        raw_data += statuses
        # 몇개 트윗 나왔는지 알아보기(리트윗 포함)
        tweets_num += len(statuses)

        # 리트윗 몇번 일어나는지 확인하기 
        def retweet_reducer(acc,cur):
            # 리트윗 한게 아닐때만 카운트하기, 이렇게 안하면 리트윗 한것들 모두가 본 글 리트윗 수를 가져서 정보가 잘못된다.
            # 좋아요는 리트윗 한건 따로 count 되어서 괜찮음
            if('retweeted_status' not in cur):
                return acc + cur['retweet_count']
            else:
                return acc
        
        retweet_num += reduce(retweet_reducer, statuses, 0)
        favorite_num += reduce(lambda acc,cur: acc + cur['favorite_count'],statuses,0)

        print("-----------START------")
        print(statuses[0]['id'])
        print("-----------END------")
        print(statuses[-1]['id'])

        # 다음 페이지 읽어오기
        t = re.findall("max_id=([0-9]+)&",tweets['search_metadata']['next_results'])[0]
        new_next_page_max_id  = int(re.findall("[0-9]+", t)[0])
        print("-----------NEXT------")
        print(new_next_page_max_id)
        tweets_bytes = oauth_req(f'https://api.twitter.com/1.1/search/tweets.json?q={q}&since_id={since_id}&max_id={new_next_page_max_id}&until={END}&count=100',
                                auth_header['access_token_key'],
                                auth_header['access_token_secret'])
        tweets = json.loads(tweets_bytes.decode('utf8'))
        statuses = tweets['statuses']
    print('retweet_num, favorite_num, tweets_num')
    print(retweet_num, favorite_num, tweets_num)
    
    

#%%
