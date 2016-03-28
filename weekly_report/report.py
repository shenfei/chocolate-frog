# coding: utf-8

from __future__ import absolute_import
from datetime import datetime, timedelta
from dateutil.parser import parse as time_parse
from pytz import reference

from trello import TrelloClient

from config import (
    TRELLO_CONFIG,
    BOARD_ID,
    DOING_LISTS,
    DONE_LISTS,
    DEV_MEMBERS
)


def get_trello_client(config):
    api_key = config['api_key']
    api_secret = config['api_secret']
    oauth_token = config['oauth_token']
    oauth_token_secret = config['oauth_token_secret']

    return TrelloClient(api_key=api_key, api_secret=api_secret,
                        token=oauth_token, token_secret=oauth_token_secret)


def convert_to_local_time(time):
    local_tz = reference.LocalTimezone()
    time = time.astimezone(local_tz)
    return time.replace(tzinfo=None)


def get_doing_cards(client, board_id, doing_lists, dev_members):
    board = client.get_board(board_id)
    doing_cards = []
    for list_id in doing_lists:
        doing_list = board.get_list(list_id)
        cards = doing_list.list_cards()
        for card in cards:
            card.fetch()
            members = [dev_members.get(m_id, None) for m_id in card.member_id]
            members = filter(None, members)
            try:
                begin_date = card.latestCardMove_date
            except:
                begin_date = card.create_date
            begin_date = convert_to_local_time(begin_date)
            lasting_time = datetime.today() - begin_date
            url = str(card.url)
            doing_cards.append((card.name, url, members, lasting_time.days))
    return doing_cards


def get_done_cards(client, board_id, done_lists, dev_members, date_range):
    board = client.get_board(board_id)
    done_cards = []
    for list_id in done_lists:
        done_list = board.get_list(list_id)
        cards = done_list.list_cards()
        for card in cards:
            card.fetch()
            try:
                done_date = card.latestCardMove_date
            except:
                continue
            done_date = convert_to_local_time(done_date)
            if not (date_range[0] <= done_date.date() <= date_range[1]):
                continue
            members = [dev_members.get(m_id, None) for m_id in card.member_id]
            members = filter(None, members)
            done_cards.append((card.name, str(card.url), members))
    return done_cards


def get_done_checklist(client, board_id, doing_lists, done_lists,
                       dev_members, date_range):
    board = client.get_board(board_id)
    list_ids = doing_lists + done_lists
    done_check_items = []
    for list_id in list_ids:
        board_list = board.get_list(list_id)
        cards = board_list.list_cards()
        for card in cards:
            card.fetch()
            if not card.checklists:
                continue
            card.fetch_actions('updateCheckItemStateOnCard')
            card_url = str(card.url)
            for action in card.actions:
                check_time = time_parse(action['date'])
                check_time = convert_to_local_time(check_time)
                if not (date_range[0] <= check_time.date() <= date_range[1]):
                    continue
                # insure the current state is complete
                if str(action['data']['checkItem']['state']) != 'complete':
                    continue
                member = dev_members.get(action['idMemberCreator'], None)
                if not member:
                    continue
                check_item = action['data']['checkItem']['name'].encode('utf8')
                done_check_items.append((check_item, card_url, member))
    return done_check_items


def generate_weekly_report(day=datetime.today()):
    date_begin = (day - timedelta(days=7)).date()
    date_end = (day - timedelta(days=1)).date()
    date_range = (date_begin, date_end)

    client = get_trello_client(TRELLO_CONFIG)
    done_cards = get_done_cards(client, BOARD_ID, DONE_LISTS,
                                DEV_MEMBERS, date_range)
    done_check_items = get_done_checklist(client, BOARD_ID, DOING_LISTS,
                                          DONE_LISTS, DEV_MEMBERS, date_range)
    doing_cards = get_doing_cards(client, BOARD_ID, DOING_LISTS, DEV_MEMBERS)

    report_text = '**上周工作情况:**\n----------\n'

    report_text += '\n**上周完成的卡片:**\n'
    for name, url, members in done_cards:
        member_str = '' if not members else ", ".join(members)
        report_text += '- [%s](%s), 参与人: %s\n' % (name, url, member_str)

    report_text += '\n**上周完成的事项:**\n'
    for check_item, url, member in done_check_items:
        report_text += '- [%s](%s), 参与人: %s\n' % (check_item, url, member)

    report_text += '\n**正在进行的卡片:**\n'
    for name, url, members, lasting_days in doing_cards:
        member_str = '' if not members else ", ".join(members)
        line = '- [%s](%s), 参与人: %s, 已持续天数 %s\n'
        report_text += line % (name, url, member_str, lasting_days)

    return report_text
