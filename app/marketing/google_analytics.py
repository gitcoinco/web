# -*- coding: utf-8 -*-
"""Hello Analytics Reporting API V4."""

from django.conf import settings

from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
AUTH_JSON = settings.GOOGLE_ANALYTICS_AUTH_JSON


def initialize_analyticsreporting():
    """Initialize an Analytics Reporting API V4 service object.

    Returns:
        An authorized Analytics Reporting API V4 service object.

    """
    import logging

    logging.getLogger('googleapicliet.discovery_cache').setLevel(logging.ERROR)
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(
        AUTH_JSON, SCOPES)

    # Build the service object.
    analytics = build('analyticsreporting', 'v4', credentials=credentials)

    return analytics


def get_report(analytics, view_id):
    """Query the Analytics Reporting API V4.

    Args:
        analytics: An authorized Analytics Reporting API V4 service object.

    Returns:
        The Analytics Reporting API V4 response.

    """
    return analytics.reports().batchGet(
        body={
            'reportRequests': [{
                'viewId': view_id,
                'dateRanges': [{'startDate': '1daysAgo', 'endDate': 'today'}],
                'metrics': [{'expression': 'ga:sessions'}],
                # 'dimensions': [{'name': 'ga:country'}]
            }]
        }).execute()


def get_response(response):
    """Parses and prints the Analytics Reporting API V4 response.

    Args:
        response: An Analytics Reporting API V4 response.

    """
    for report in response.get('reports', []):
        column_header = report.get('columnHeader', {})
        dimension_headers = column_header.get('dimensions', [])
        metric_headers = column_header.get('metricHeader', {}).get('metricHeaderEntries', [])
        
        rows = report.get('data', {}).get('rows', [])
        
        if not rows:
            return '0'
        
        for row in rows:
            dimensions = row.get('dimensions', [])
            date_range_values = row.get('metrics', [])

            for header, dimension in zip(dimension_headers, dimensions):
                print(header + ': ' + dimension)

            for _, values in enumerate(date_range_values):
                # print('Date range: ' + str(i))
                for _, value in zip(metric_headers, values.get('values')):
                    # print(metricHeader.get('name') + ': ' + value)
                    return value


def run(view_id):
    """Run analytics reporting against the view.

    Args:
        view_id: ID of the view.

    Returns:
        response: An Analytics Reporting API V4 response.

    """
    analytics = initialize_analyticsreporting()
    response = get_report(analytics, view_id)
    return get_response(response)
