# coding: utf-8

from __future__ import absolute_import
from datetime import datetime
from dateutil.parser import parse as time_parse

from trello import TrelloClient


def get_trello_client(config):
    api_key = config['api_key']
    api_secret = config['api_secret']
    oauth_token = config['oauth_token']
    oauth_token_secret = config['oauth_token_secret']

    return TrelloClient(api_key=api_key, api_secret=api_secret,
                        token=oauth_token, token_secret=oauth_token_secret)


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
            last_dates = datetime.today() - begin_date.replace(tzinfo=None)
            doing_cards.append((card.name, members, last_dates))
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
            done_date = done_date.replace(tzinfo=None)
            if not (date_range[0] < done_date < date_range[1]):
                continue
            members = [dev_members.get(m_id, None) for m_id in card.member_id]
            members = filter(None, members)
            done_cards.append((card.name, members))
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
            for action in card.actions:
                check_time = time_parse(action['date']).replace(tzinfo=None)
                if not (date_range[0] < check_time < date_range[1]):
                    continue
                member = dev_members.get(action['idMemberCreator'], None)
                if not member:
                    continue
                check_item = action['data']['checkItem']['name'].encode('utf8')
                done_check_items.append((member, check_item))
    return done_check_items
