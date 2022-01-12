import json

import pytest
from marketing.google_analytics import get_response


def test_google_analytics_returns_zero_value_if_expected_metric_not_returned():
    ga_incomplete_response = '''{
        "reports": [
            {
            "columnHeader": {
                "metricHeader": {
                "metricHeaderEntries": [
                    {
                    "name": "ga:sessions",
                    "type": "INTEGER"
                    }
                ]
                }
            },
            "data": {
                "totals": [
                {
                    "values": [
                    "0"
                    ]
                }
                ]
            }
            }
        ]
    }'''

    analytics = json.loads(ga_incomplete_response)
    
    parsed_response = get_response(analytics)
    
    assert parsed_response != None
    assert parsed_response == '0'
    
def test_google_analytics_returns_values_with_expected_response():
    ga_expected_response = '''{
        "reports": [{
            "columnHeader": {
                "dimensions": [
                    "ga:country"
                ],
                "metricHeader": {
                    "metricHeaderEntries": [{
                        "name": "ga:sessions",
                        "type": "INTEGER"
                    }]
                }
            },
            "data": {
                "totals": [{
                    "values": [
                        "0"
                    ]
                }],
                "rows": [{
                    "metrics": [{
                        "values": [
                            "2"
                        ]
                    }]
                }]
            }
        }]
    }
    '''
    analytics = json.loads(ga_expected_response)
    
    parsed_response = get_response(analytics)
    
    assert parsed_response == '2'
