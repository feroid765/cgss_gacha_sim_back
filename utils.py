# -*- coding: utf-8 -*- 
# %%
import requests
from bs4 import BeautifulSoup, element
import math
import re
import datetime

# %%

#카드 등급 리스트
rarity_list = ['N', 'R', 'SR', 'SSR']

def get_card_info(card_id):
    '''
    Starlight DB에서 제공하는 API(https://github.com/summertriangle-dev/sparklebox/wiki/Objects---card_t)를 이용해 카드 이름, 카드 등급을 가져오고
    아이돌마스터 인벤에서 카드의 한국어 이름을 가져와 입력으로 받은 카드 ID에 대한 카드 정보를 Dict로 반환.
    '''
    result = {}
    res_api = requests.get("https://starlight.kirara.ca/api/v1/card_t/"+card_id).json()['result'][0]
    result['jpn_name'] = res_api['name']
    result['rarity'] = rarity_list[math.floor((res_api['rarity']['rarity']+1)/2) - 1]

    res_inven = requests.get("http://imas.inven.co.kr/dataninfo/card/sl_detail.php?c="+card_id)
    inven = BeautifulSoup(res_inven.text, 'html.parser')
    try:
        result['kor_name'] = inven.select('.detailTitle')[0].text.replace("\n", "").strip()
        if result['kor_name'] == "카드 대사":
            result['kor_name'] = ""
    except:
        result['kor_name'] = ""

    return result

# %%
def get_pickup_lineup_from_ava_list(gacha_id):
    '''
    Starlight DB에서 제공하는 가챠 정보(Examples. https://starlight.kirara.ca/gacha/30577, https://starlight.kirara.ca/gacha/30578)에서
    가챠 정보를 가져오는 함수.
    가챠 id를 받으면 가챠 정보를 dict로 반환함.
    '''
    res = requests.get("https://starlight.kirara.ca/"+"gacha/"+gacha_id)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    ssr_lineup_list = {}
    sr_lineup_list = {}

    common = {'R' : [], 'SR' : [], 'SSR' : []}

    ssr_pickup_list = []
    sr_pickup_list = []

    for i in soup.select('.row_data'):
        rate = i.find('td', text = re.compile(r'\d{1}.\d{3}%')).text
        rate = float(rate[:-1])

        #SSR
        if 'ssr_kc' in i['class']:
            if rate not in ssr_lineup_list.keys():
                ssr_lineup_list[rate] = []
            ssr_lineup_list[rate].append(i['data-cid'])
        #SR
        elif 'sr_kc' in i['class']:
            if rate not in sr_lineup_list.keys():
                sr_lineup_list[rate] = []
            sr_lineup_list[rate].append(i['data-cid'])
        #R, 픽업이 없다고 가정
        else:
            common['R'].append(i['data-cid'])

    #SSR 통상,픽업 분리하는 코드.
    #Rate Class (같은 Rate를 가진 카드끼리 묶어놓은 것) 중 가장 length가 긴 것을 통상 카드들로 취급.
    if len(ssr_lineup_list.keys()) == 1:
        common['SSR'] = ssr_lineup_list[list(ssr_lineup_list.keys())[0]]
    else:
        idx = list(ssr_lineup_list.keys())[0]
        for i in ssr_lineup_list.keys():
            if len(ssr_lineup_list[idx]) < len(ssr_lineup_list[i]):
                idx = i
    
        common['SSR'] = ssr_lineup_list[idx]
        
        for i in ssr_lineup_list.keys():
            if i != idx:
                ssr_pickup_list.append({
                    "rate" : i*len(ssr_lineup_list[i]),
                    "pickup_list" : ssr_lineup_list[i]
                })
        
    #SR 통상 라인업 찾기. 
    #Rate Class (같은 Rate를 가진 카드끼리 묶어놓은 것) 중 가장 length가 긴 것을 통상 카드들로 취급.
    if len(sr_lineup_list.keys()) == 1:
        common['SR'] = sr_lineup_list[list(sr_lineup_list.keys())[0]]
    else:
        idx = list(sr_lineup_list.keys())[0]
        for i in sr_lineup_list.keys():
            if len(sr_lineup_list[idx]) < len(sr_lineup_list[i]):
                idx = i
    
        common['SR'] = sr_lineup_list[idx]
        
        for i in sr_lineup_list.keys():
            if i != idx:
                sr_pickup_list.append({
                    "rate" : i*len(sr_lineup_list[i]),
                    "pickup_list" : sr_lineup_list[i]
                })

    return common, ssr_pickup_list, sr_pickup_list
    

def get_curr_lineup():
    '''
    Starlight DB에서 현재 진행중인 가챠의 ID를 받아서,
    그 ID에 해당하는 가챠 정보를 가져오는 함수.
    '''
    gacha_list = []
    
    res = requests.get("https://starlight.kirara.ca/")
    html = res.text
    soup = BeautifulSoup(html, 'html.parser')

    ID = 0
    rate = {'R' : 85.0, 'SR' : 12.0, 'SSR' : 3.0}
    time = 0
    name = ""

    #Greb current gachas.
    for i in soup.find('p', string = "Current events and gachas:").parent.select('.he_gacha'):
        name = i.find('span', {'class' : 'tlable'}).text
        time = i.find('span', {'class' : 'counter'})['data-count-to']

        full_ava = i.find('a', string = "Full availability list")
        if full_ava != []:
            ID = full_ava['href'].split('/')[2]
            common, ssr_pickup_list, sr_pickup_list = get_pickup_lineup_from_ava_list(ID)
            gacha = {}
            gacha['ID'] = ID
            gacha['rate'] = rate
            gacha['time'] = time
            gacha['name'] = name
            gacha['sr_pickup_list'] = sr_pickup_list
            gacha['ssr_pickup_list'] = ssr_pickup_list
            gacha['common'] = common
            gacha_list.append(gacha)

    return gacha_list