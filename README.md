# API for getting AMFI NAVs

## What is AMFI NAV?

AMFI is the Association of Mutual Funds of India. NAV is the net asset value of a mutual fund. AMFI publishes daily NAVs of all Mutual Funds traded in India. This is available as a plain HTTP request from http://portal.amfiindia.com/spages/NAV0.txt.  

To programmatically consume the big file is a pain. Also, you probably want the NAVs only for
a handful of MFs at any time. This project is to make such an API available.

## The process

The project runs as a couple of Amazon AWS' Lambda services.

   1. A daily cron-job to fetch NAVs form the AMFI URL. The text file is parsed and saved as a JSON file in an S3 bucket. We use Python since it is easiest to parse the file line by line in Python. This is convert navs.py, and is triggered by a Cloud Watch Schedule event.

   2. An AWS API Gateway endpoint that proxies another Lambda service, which acts as the new API, which provides NAVs given one or more Mutual Fund's AMFI codes. For this, we need a trigger from the AWS Gateway API.

To create Lambdas for these, use the AWS console and copy-paste the code.

## Pricing

Currently this is hosted in my private accounts, so the API is not yet public (mainly because of the charges that I'll incur on AWS if made public). If and when this becomes public, I may add API restrictions on how many calls a single client can make so that the charges can be kept to a minimum.

## AWS API Gateway Configuration

This needs to be configured correctly for the API to be accessible. One API endpoint, and two methods GET and POST are created under /.

For the POST method, in the Integration Request, let the body pass through. Now, you can make a call to the API like this:

```
curl --data '{"codes": ["104772","112090"]}' https://<API URL from API Gateway config>
```
For the GET method, in the Integration Request, we need to create templates that convert the input parameters to event variables. This is called Body Mapping Templates even though it's not the body that we are templating.

```
{
  "params": "$input.params()",
  "querystring": "$input.params().querystring",
  "codescsv": "$input.params().querystring.get('codes')",
  "hardCoded": "version-3"
}
```

This lets us make a call to the API like this:

```
curl https://<API URL>?codes=104772,112090
```

Within the Lambda function, the event parameter codescsv will now have the codes parameter's value: 104772,112090.

DON'T FORGET TO DEPLOY after every change to the API Gateway configuration.

### Finding the AMFI NAV

If you know the name of the fund, search for it in the NAV0.txt file (download this from the amfi portal http://portal.amfiindia.com/spages/NAV0.txt).

If you don't want to download the file (or cross check if you got the right one), use http://www.morningstar.in/default.aspx and search for the fund. In the fund's page, you'll find the schem code. For example, search for HDFC Equity Fund, and you'll find 4 options for dividend / growth and direct / regular plans. If you pick HDFC Equity Fund Growth (ie, not the direct plan), You'll see the code next to the title:

HDFC Equity Gr 101762

101763 is the code for this fund.
