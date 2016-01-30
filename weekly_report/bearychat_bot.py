# coding: utf-8

from __future__ import absolute_import
import argparse
from datetime import datetime, timedelta
import requests
import json

from config import bearychat_url, bearychat_channels
from weekly_report.report import generate_weekly_report


def send_weekly_report(url, channel, day):
    report_text = generate_weekly_report(day)
    data = {
        "text":report_text,
        "channel": channel
    }
    headers = {'content-type': 'application/json'}
    response = requests.post(url, data=json.dumps(data), headers=headers)
    return response


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--pre', type=int, default=0)
    parser.add_argument('-c', '--channel')
    args = parser.parse_args()

    channel = bearychat_channels.get(args.channel, None)
    if not channel:
        print 'not valid channel argument'
        exit(1)
    day = datetime.today() - timedelta(days=args.pre)
    send_weekly_report(bearychat_url, channel, day)
