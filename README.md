# cgss_gacha_sim_back
* [데레스테 가챠 시뮬레이터](https://cgss-gacha.feroid.com)의 백엔드 코드와 데레스테 가챠 정보를 [Starlight DB](https://starlight.kirara.ca)와 에서 크롤링하는 코드가 있는 Repository 입니다.

* 파일 구조 : 
```
 ┣ 📂 gachas (가챠의 정보를 json으로 저장)
 ┃ ┣ 📜 common_30536.json (Ex.가챠 id 30536의 통상 카드 id 정보)
 ┃ ┗ 📜 pickup_30536.js (Ex.가챠 id 30536의 픽업 카드의 확률과 id 정보)
 ┣ 📂 static (프론트엔드 서비스 코드들이 저장되는 폴더, repo에 미포함)
 ┣ 📂 img (프론트엔드 서비스 코드들이 저장되는 폴더, repo에 미포함)
 ┣ 📜 app.js (가챠 정보와 프론트엔드 서비스를 구동하는 node.js코드)
 ┣ 📜 telegram_link.py (오류 정보를 보낼 텔레그램 봇 API 링크 저장, repo에 미포함)
 ┣ 📜 card_info.db (카드 정보를 저장하는 DB)
 ┣ 📜 utils.py (Starlight DB(전반적인 카드, 가챠 정보), 인벤(한국어 이름)에서 가챠, 카드 정보를 크롤링해 파이썬 obj로 반환)
 ┣ 📜 worker.py (utils.py를 이용하여 카드 정보를 DB에, 가챠 정보를 json으로 크롤링)
 ┣ 📜 yarn.lock
 ┗ 📜 package.json
```

* 사용 방법
  * 웹 서비스 : app.js를 module로 import해서 app.use로 사용.
  * 크롤러
```
python worker.py
```

* 용어 설명
  * 데레스테 : 스마트폰용 게임인 "아이돌마스터 신데렐라 걸즈 스타라이트 스테이지" 줄임말.
  * 가챠 : 게임 내 카드를 게임 내 일정 화폐를 내고 뽑는 행위, 며칠마다 카드가 새로 추가되면 등장하는 카드의 확률들이 달라짐.
  * 통상 : 특정 기간에만 뽑을 수 있는 기간 한정 카드와 달리 언제나 뽑을 수 있는 카드.
  * 픽업 : 가챠에서 새로 추가되거나 하는 이유로 뽑힐 확률이 다른 카드보다 높은 카드.