# coding: utf-8

from __future__ import absolute_import
import argparse
from datetime import datetime, timedelta
import requests
import json

from config import bearychat_url, bearychat_channels
from weekly_report.report import generate_weekly_report


def post_report(url, channel, report_text):
    data = {
        "text":report_text,
        "channel": channel
    }
    headers = {'content-type': 'application/json'}
    response = requests.post(url, data=json.dumps(data), headers=headers)
    return response


def send_weekly_report(day):
    report_text = generate_weekly_report(day)
    for channel in bearychat_channels:
        post_report(bearychat_url, channel, report_text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--pre', type=int, default=0)
    args = parser.parse_args()

    day = datetime.today() - timedelta(days=args.pre)
    send_weekly_report(day)
