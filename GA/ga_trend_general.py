"""Hello Analytics Reporting API V4."""

from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import pprint


SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
KEY_FILE_LOCATION = './gx_real_google_key.json'
VIEW_ID = '183002932'

def initialize_analyticsreporting():
  """Initializes an Analytics Reporting API V4 service object.

  Returns:
    An authorized Analytics Reporting API V4 service object.
  """
  credentials = ServiceAccountCredentials.from_json_keyfile_name(
      KEY_FILE_LOCATION, SCOPES)

  # Build the service object.
  analytics = build('analyticsreporting', 'v4', credentials=credentials)

  return analytics


def get_report(analytics):
  """Queries the Analytics Reporting API V4.

  Args:
    analytics: An authorized Analytics Reporting API V4 service object.
  Returns:
    The Analytics Reporting API V4 response.
  """
  return analytics.reports().batchGet(
      body={
        'reportRequests': [
        {
          'viewId': VIEW_ID,
          # 'dateRanges': [{'startDate': '7daysAgo', 'endDate': 'today'}],
          'dateRanges': [{'startDate': '2019-07-01', 'endDate': '2019-07-24'}],
           # 실제로 분류할 컬럼들
          'dimensions': [{'name':'ga:date'}],
          'metrics': [{'expression': 'ga:users'},{'expression': 'ga:newUsers'},{'expression': 'ga:bounceRate'}]
        }]
      }
  ).execute()


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
    """insert into ods_google.ga_general (data_date, users, newUsers, bounceRate) VALUES %s""",
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

def gadata_to_array(data):
  # { 'reports': [ { 'columnHeader': { 'dimensions': ['ga:date'],
  #                                  'metricHeader': { 'metricHeaderEntries': [ { 'name': 'ga:users',
  #                                                                               'type': 'INTEGER'},
  #                                                                             { 'name': 'ga:newUsers',
  #                                                                               'type': 'INTEGER'},
  #                                                                             { 'name': 'ga:bounceRate',
  #                                                                               'type': 'PERCENT'},
  #                                                                             { 'name': 'ga:sessions',
  #                                                                               'type': 'INTEGER'}]}},
  #                'data': { 'maximums': [ { 'values': [ '997',
  #                                                      '844',
  #                                                      '91.91919191919192',
  #                                                      '1163']}],...
  #### .get 쓰면 key error 피할 수 있다.
  report = data['reports'][0]
  data_rows = report.get('data',{}).get('rows',[])
  # 날짜 데이터와 여러 metric들 얻기
  from datetime import datetime
  
  report_array = list(map(lambda x: [datetime.strptime(x['dimensions'][0],'%Y%m%d').strftime('%Y-%m-%d')]
                                    +x['metrics'][0].get('values',[])
                                    ,data_rows))
  return report_array


def main():
  analytics = initialize_analyticsreporting()
  response = get_report(analytics)
  pp = pprint.PrettyPrinter(indent=2)
  pp.pprint(response)
  report_array = gadata_to_array(response)
  print(report_array)
  db_connect(report_array)

if __name__ == '__main__':
  main()