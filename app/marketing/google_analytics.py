# -*- coding: utf-8 -*-
"""Hello Analytics Reporting API V4."""

from django.conf import settings

from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
AUTH_JSON = settings.GOOGLE_ANALYTICS_AUTH_JSON


def initialize_analyticsreporting():
    import logging

    logging.getLogger('googleapicliet.discovery_cache').setLevel(logging.ERROR)
    """Initializes an Analytics Reporting API V4 service object.

    Returns:
        An authorized Analytics Reporting API V4 service object.

    """
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(
        AUTH_JSON, SCOPES)

    # Build the service object.
    analytics = build('analyticsreporting', 'v4', credentials=credentials)

    return analytics


def get_report(analytics, VIEW_ID):
    """Queries the Analytics Reporting API V4.

    Args:
        analytics: An authorized Analytics Reporting API V4 service object.

    Returns:
        The Analytics Reporting API V4 response.
    """
    return analytics.reports().batchGet(
        body={
            'reportRequests': [{
                'viewId': VIEW_ID,
                'dateRanges': [{'startDate': '1daysAgo', 'endDate': 'today'}],
                'metrics': [{'expression': 'ga:sessions'}],
                #'dimensions': [{'name': 'ga:country'}]
            }]
        }).execute()


def get_response(response):
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

            for _, values in enumerate(dateRangeValues):
                # print('Date range: ' + str(i))
                for _, value in zip(metricHeaders, values.get('values')):
                    # print(metricHeader.get('name') + ': ' + value)
                    return value


def run(VIEW_ID):
    """Run analytics reporting against the view.

    Args:
        VIEW_ID: ID of the view.

    Returns:
        response: An Analytics Reporting API V4 response.

    """
    analytics = initialize_analyticsreporting()
    response = get_report(analytics, VIEW_ID)
    return get_response(response)
