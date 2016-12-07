import httplib
import json
import boto3
import time

"""
Downloads and saves the current day's NAVs as JSON into an S3 Bucket.
This function is called periodically (all week days), so at any point in
time we have the latest NAVs.json in the S3 bucket for the other function
(the API) to be able to retrieve one or a few MF's NAV.
"""

def timedelta(msg):
    global last, start
    cur = time.time()
    print(round(cur-start, 2), round(cur-last, 2), msg)
    last = cur

def get_navs():
    global last, start
    start = time.time()
    last = start
    conn = httplib.HTTPConnection("portal.amfiindia.com")
    conn.request("GET", "/spages/NAV0.txt")
    resp = conn.getresponse()

    if resp.status == 200:
        timedelta("Connected")
        data = resp.read()
        timedelta("Read data")
        schemes = {}
        lines = data.split("\r\n")
        for line in lines:
            if len(line) > 0 and line[0] >= '0' and line[0] <= '9':
                items = line.split(";")
                schemes[items[0]] = {
                    'code': items[0], 'name': items[3], 'nav': items[4], 'date': items[7]
                }

        timedelta("Parsed")
        schemesJs = json.dumps(schemes)
        timedelta("JSON created")
        s3 = boto3.client('s3')
        s3.put_object(Bucket='vasan-amfinavs', Key='NAVs.json', Body=schemesJs)
        timedelta("Uploaded to S3")
    else:
        print("Error in request", resp.status, resp.reason)

def lambda_handler(event, context):
    get_navs()

if __name__ == "__main__":
    get_navs()
