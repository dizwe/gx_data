
#%%
import requests
import json
import os
# r = requests.get('https://api.github.com/repos/klaytn/klaytn', auth=('user', 'pass'))

CLIENT_ID = '90508261b5b51a86ad44'
CLIENT_SECRET = os.getenv('GITHUB_SECRET')
r = requests.get('https://api.github.com/users/klaytn/repos?&client_id={}&client_secret={}'.format(CLIENT_ID,CLIENT_SECRET))

repository_list = json.loads(r.text)

def get_issue_pull_info(repo_name):
    # issue에 pull request도 포함되어있음
    # pull_request라는 key가 있으면 pull request임-> 고로 두개 볼 필요가 없나?
    # 페이지가 있으므로 whil해서 길이 파악하기 
    open_pull_count=closed_pull_count=open_issue_count=closed_issue_count = 0
    page = 1
    while True:    
        r3 = requests.get('https://api.github.com/repos/klaytn/{}/issues?state=all&page={}&client_id={}&client_secret={}'.format(repo_name,page,CLIENT_ID,CLIENT_SECRET))
        data_list = json.loads(r3.text)
        if len(data_list)==0:
            return [open_pull_count,closed_pull_count,open_issue_count,closed_issue_count]  
        # state로 filter 하면 될 듯 
        pull_list = list(filter(lambda x : 'pull_request' in x,data_list))
        issue_list = list(filter(lambda x : 'pull_request' not in x,data_list))
        open_pull_count += len(list(filter(lambda x : x['state']=='open',pull_list)))
        closed_pull_count += len(list(filter(lambda x : x['state']=='closed',pull_list)))
        open_issue_count += len(list(filter(lambda x : x['state']=='open',issue_list)))
        closed_issue_count += len(list(filter(lambda x : x['state']=='closed',issue_list)))
        page = page+1 

def get_basic_repoinfo(one_repo):
    repo_name = one_repo.get('name', '')
    [open_pull_count,closed_pull_count,open_issue_count, closed_issue_count] = get_issue_pull_info(repo_name)
    print([open_pull_count,closed_pull_count,open_issue_count,closed_issue_count])
    # star, watch, fork, pull requests, issue(open_issue, close_issue)
    # 이상해.. watch라는 값이 star와 무조건 똑같이 나옴
    return {'name':repo_name,
            'stargazers_count':one_repo.get('stargazers_count', 0),
            'watchers_count':one_repo.get('watchers_count', 0),
            'forks_count':one_repo.get('forks_count', 0),
            'open_pull_count':open_pull_count,
            'closed_pull_count':closed_pull_count,
            'open_issue_count':open_issue_count,
            'closed_issue_count':closed_issue_count}

repoinfo_list = list(map(get_basic_repoinfo, repository_list))


#%%
from datetime import datetime

def gitdata_to_array(data):
    column_list = ['name','stargazers_count','watchers_count','forks_count','open_pull_count','closed_pull_count','open_issue_count','closed_issue_count']
    def column_combine_lambda(x):
        now = datetime.now()
        k = [now.strftime("%Y-%m-%d")]
        for one_column in column_list:
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
    """insert into ods_google.github_general (data_date, name, stargazers_count,watchers_count,forks_count,open_pull_count,closed_pull_count,open_issue_count,closed_issue_count) VALUES %s""",
    data)
    print(cursor.query)
    connection.commit()
  
    # record = cursor.fetchall() # fetchone(), fetchmanxy(), fetcthall().
  
  except (Exception, psycopg2.Error) as error :
      print("Error while connecting to PostgreSQL", error)
  finally:
      #closing database connection.
          if(connection):
              cursor.close()
              connection.close()

data_array = gitdata_to_array(repoinfo_list)
db_connect(data_array)

#%%
# 엄청 자세한 내용 많이 나오는데, 필요하면 쓰고 아니면 안쓰기(일단 r3로 거르자)
# r2 = requests.get('https://api.github.com/repos/klaytn/klaytn/pulls?state=all&page=1')
# pull_list = json.loads(r2.text)
# # state로 filter 하면 될 듯 
# print(len(pull_list))

