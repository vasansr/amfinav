from __future__ import print_function

import json
import boto3
import time

"""
This is an API endpoint: given a set of AMFI codes, it returns a JSON
of the NAVs and the date when it was last updated.
"""

s3 = boto3.client('s3')

def timedelta(msg):
    global last, start
    cur = time.time()
    print(round(cur-start, 3), round(cur-last, 3), msg)
    last = cur

def lambda_handler(event, context):
    global last, start
    start = time.time()
    last = start

    # print("Received event: " + json.dumps(event, indent=2))

    bucket = "vasan-amfinavs"
    key = "NAVs.json"
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        navsText = response['Body'].read()
        timedelta("Loaded NAVs file")
        navs = json.loads(navsText)
        timedelta("Parsed NAVs to JSON")
        selectedNavs = {}
        # If passed as a query string via GET, need to split it
        if event.get("codescsv"):
            for code in event["codescsv"].split(','):
                selectedNavs[code] = navs[code]
            return selectedNavs
        # If passed in as JSON request body in a POST, we get an array
        elif event.get("codes"):
            for code in event["codes"]:
                selectedNavs[code] = navs[code]
            return selectedNavs
        # Return the event itself: we couldn't understand the request.
        return event
    except Exception as e:
        print(e)
        raise e
