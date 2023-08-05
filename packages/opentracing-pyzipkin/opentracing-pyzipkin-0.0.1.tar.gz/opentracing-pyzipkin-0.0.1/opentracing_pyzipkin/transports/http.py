import requests


def http_transport(encoded_span):
    requests.post(
        'http://10.40.4.130:9411/api/v1/spans',
        data=encoded_span,
        headers={'Content-Type': 'application/x-thrift'},
    )
