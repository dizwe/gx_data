"""Hello Analytics Reporting API V4."""

from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import pprint

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
KEY_FILE_LOCATION = './gx-data-7f55c361328f.json'
VIEW_ID = '198522093'


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
  return analytics.userActivity().search(
      body=
          {
            "dateRange": {
             'startDate': '2019-07-23', 'endDate': '2019-07-25',
            },
            "viewId": VIEW_ID,
            "user": {
              "type":"CLIENT_ID",
              "userId":"81224557.1563269685",
            },
            "activityTypes": [
              "PAGEVIEW","SCREENVIEW","EVENT"
            ]
          }
  ).execute()



def print_response(response):
  """Parses and prints the Analytics Reporting API V4 response.

  Args:
    response: An Analytics Reporting API V4 response.
  """
  for report in response.get('reports', []):
    columnHeader = report.get('columnHeader', {})
    dimensionHeaders = columnHeader.get('dimensions', [])
    metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])

    for row in report.get('data', {}).get('rows', []):
      dimensions = row.get('dimensions', [])
      dateRangeValues = row.get('metrics', [])

      for header, dimension in zip(dimensionHeaders, dimensions):
        print(header + ': ' + dimension)

      for i, values in enumerate(dateRangeValues):
        print('Date range: ' + str(i))
        for metricHeader, value in zip(metricHeaders, values.get('values')):
          print(metricHeader.get('name') + ': ' + value)


def main():
  analytics = initialize_analyticsreporting()
  response = get_report(analytics)
  pp = pprint.PrettyPrinter(indent=2)
  pp.pprint(response)
  import json

  with open("userActivity.json", "w") as userActivity:
    json.dump(response, userActivity, indent=4, sort_keys=True)
  # print_response(response)

if __name__ == '__main__':
  main()