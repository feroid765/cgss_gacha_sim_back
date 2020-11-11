# -*- coding: utf-8 -*- 

import json
from utils import get_curr_lineup, get_card_info
import requests
import sqlite3
import time
import sys
from telegram_link import LINK_FOR_SEND_MSG_VIA_TELEGRAM

def init_db(conn):
    '''
    DB 최초 생성 시에만 사용하는 코드
    가챠 정보를 저장할 테이블을 생성함.
    '''
    cur = conn.cursor()
    cur.execute('''CREATE TABLE cards(
        id text primary key,
        name text not null,
        rarity text not null,
        kor_name text
    )''')
    conn.commit()

def save_card_info_to_db(conn, card_id):
    '''
    카드 정보를 DB에 저장하는 함수
    내부적으로 utils.py에 있는 get_card_info 함수를 호출해 카드 정보를 가져옴.
    '''
    cur = conn.cursor()
    sql_find = '''SELECT * FROM cards WHERE id = ?'''
    cur.execute(sql_find, (card_id,))
    rows = cur.fetchall()

    if len(rows) == 0:
        card_info = get_card_info(card_id)
        sql_insert = '''INSERT INTO cards(id, name, rarity, kor_name) VALUES (?, ?, ?, ?)'''
        cur.execute(sql_insert, (card_id, card_info['jpn_name'], card_info['rarity'], card_info['kor_name']))
        conn.commit()

def save_curr_gacha(conn):
    '''
    가챠 정보를 json으로 저장하는 함수
    내부적으로 utils.py에 있는 get_curr_lineup 함수를 호출해 가챠 정보를 가져옴.
    '''
    curr_gachas = []
    pickup = get_curr_lineup()

    if pickup != []:
        for i in pickup:
            ID = i['ID']
            common = i['common']
            for j in i['sr_pickup_list']:
                for k in j['pickup_list']:
                    save_card_info_to_db(conn, k)
            for j in i['ssr_pickup_list']:
                for k in j['pickup_list']:
                    save_card_info_to_db(conn, k)
            with open('gachas/common_'+ID+'.json', 'w') as f:
                json.dump(common, f)
            with open('gachas/pickup_'+ID+'.json', 'w') as f:
                del i['common']
                json.dump(i, f)
            curr_gachas.append(ID)
            for i in common['R']:
                save_card_info_to_db(conn, i)
            for i in common['SR']:
                save_card_info_to_db(conn, i)
            for i in common['SSR']:
                save_card_info_to_db(conn, i)
        with open('curr_gacha.json', 'w') as f:
            json.dump(curr_gachas, f)
    else:
        requests.get(LINK_FOR_SEND_MSG_VIA_TELEGRAM)

def get_kor_name(conn):
    '''
    카드의 한국어 이름을 DB에 저장하는 함수.
    카드가 게임에 추가되자 마자 카드 정보를 제공하는 사이트가 있는 것에 반해,
    한국어 이름을 가져오는 사이트는 한국어 이름 정보가 추가되는 시간에 딜레이가 있기 때문에 
    다른 함수로 만들어 한국어 이름을 가져오는 조건을 다르게 했음.
    '''
    cur = conn.cursor()
    sql_find = '''SELECT id FROM cards WHERE kor_name = ?'''
    sql_update = '''UPDATE cards SET kor_name = ? WHERE id = ?'''
    cur.execute(sql_find, ('',))
    
    rows = cur.fetchall()

    for i in rows:
        card_id = i[0]
        card_info = get_card_info(card_id)
        if card_info['kor_name'] != '' and card_info['kor_name'] != '카드 대사':
            cur.execute(sql_update, (card_info['kor_name'], card_id))
    
    conn.commit()

def init():
    '''
    DB 최초 생성 시에만 사용하는 코드
    가챠 정보를 저장할 DB를 생성함.
    '''
    conn = sqlite3.connect('card_info.db')
    init_db(conn)
    save_curr_gacha(conn)
    conn.close()

def main():
    '''
    일정 시간마다 현재 가챠의만료 시간이 지났는지 확인하고, 
    지났으면 이 파일에 정의 되어 있는 함수들을 호출해 새로운 가챠 정보를 불러옴.
    '''
    k = 1
    while True:
        curr_id = ''
        with open('curr_gacha.json', 'r') as f:
            curr_gacha = json.load(f)
            curr_id = curr_gacha[0]
        
        gacha_end_time = 0.0
        with open('gachas/pickup_'+curr_id+'.json', 'r') as f:
            curr_gacha_info = json.load(f)
            gacha_end_time = float(curr_gacha_info['time'])

        if time.time() > gacha_end_time:
            conn = sqlite3.connect('card_info.db')
            save_curr_gacha(conn)
            conn.close()

        if k%3 == 0:
            conn = sqlite3.connect('card_info.db')
            get_kor_name(conn)
            conn.close()

        time.sleep(300)
            
if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == '--init':
        init()
    else:
        main()