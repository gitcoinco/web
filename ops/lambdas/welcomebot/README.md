# Gitcoin Slack Welcomebot

[Github](https://github.com/gitcoinco/web/tree/master/ops/lambdas/welcomebot)

The Gitcoin Slack Welcomebot is a [Flask](http://flask.pocoo.org/) application meant to run on [AWS Lambda](https://aws.amazon.com/lambda/) using [Zappa](https://github.com/Miserlou/Zappa).

This bot is intended to be ran as a Python 3.6 AWS Lambda function.

Get started with the welcomebot by running `make init`.

You will need to follow the Slack Bot setup instructions outlined in the [Python Slack Event API client](https://github.com/slackapi/python-slack-events-api) documentation.

The majority of this application resides in [welcomebot/app.py](https://github.com/gitcoinco/web/blob/master/ops/lambdas/welcomebot/app.py)
