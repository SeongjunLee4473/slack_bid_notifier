#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""나라장터 학술연구용역 공고 모니터링 및 슬랙 알림 스크립트

본 스크립트는 데이터 OpenAPI를 사용하여 나라장터에 새로 게시되는
학술연구용역 분야의 입찰 공고를 주기적으로 확인합니다. 새로운 공고가 발견되면
지정된 슬랙(Slack) 채널로 알림을 전송하여 신속하게 정보를 공유합니다.

본 스크립트는 '나라장터'와 같은 국내 서비스 용어의 명확성을 위해 한국어로 작성되었습니다.

아래 env_path는 본인의 환경변수 경로로 수정해주세요.

주요 기능:
  - 지정된 키워드 목록을 기반으로 공고 검색
  - 실행 시간에 따라 동적으로 검색 기간 설정 (예: 월요일 오전, 평일 오전 등)
  - '수의계약' 공고를 제외하여 관련성 높은 정보만 필터링
  - 이전에 알림을 보낸 공고는 중복 전송하지 않도록 상태 관리

Example:
    터미널에서 직접 실행하여 새로운 공고를 확인할 수 있습니다.
    $ python your_script_name.py
"""

__author__ = "이성준 (Seongjun Lee)"
__created_on__ = "2024-08-14"
__last_modified__ = "2025-09-04"

# ====================================================================================#
# 기본 설정
# ====================================================================================#

# 라이브러리 불러오기
import os
import requests
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime, timedelta

# 전역 변수 및 설정
# Webhook URL 불러오기
env_path = '/home/seongjun/.env'
load_dotenv(env_path)
slack_webhook_url = os.getenv('SLACK_WEBHOOK_BID_URL')

# 이전에 조회된 공고 목록을 저장하여 중복 알림 방지를 위한 변수 선언
previous_bids = []

# --- 함수 정의 ---
def send_slack_notification(message):
    """지정된 메시지를 슬랙 채널로 전송합니다.

    Args:
        message (str): 슬랙으로 보낼 텍스트 메시지.

    Returns:
        bool: 메시지 전송 성공 시 True, 실패 시 False를 반환합니다.
    """
    payload = {"text": message}
    try:
        response = requests.post(slack_webhook_url, json=payload)
        if response.status_code != 200:
            print(f"슬랙 알림 전송 실패: 상태 코드 {response.status_code}")
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"슬랙 알림 전송 중 오류 발생: {e}")
        return False

def fetch_new_bids():
    """나라장터 API를 호출하여 최신 입찰 공고를 가져옵니다.

    실행 시점에 따라 조회 기간을 동적으로 설정하며, 지정된 키워드와 업종 코드를
    기반으로 공고를 검색합니다. '수의계약'은 결과에서 제외됩니다.

    Returns:
        tuple: (pandas.DataFrame, str, str) 형태의 튜플.
               - 첫 번째 요소: 조회된 공고 목록이 담긴 데이터프레임.
               - 두 번째 요소: 조회 시작 시각 (YYYYMMDDHHMM).
               - 세 번째 요소: 조회 종료 시각 (YYYYMMDDHHMM).
    """
    current_time = datetime.now()

    # 실행 시점에 따라 조회 기간 동적 설정
    if current_time.weekday() == 0 and current_time.hour == 9:  # 월요일 오전 9시
        # 금요일 18시 ~ 월요일 09시
        inqryBgnDt = (current_time - timedelta(days=2, hours=15)).strftime('%Y%m%d%H%M')
        inqryEndDt = current_time.strftime('%Y%m%d%H%M')
    elif current_time.weekday() in [1, 2, 3, 4] and current_time.hour == 9:  # 화~금 오전 9시
        # 전일 18시 ~ 당일 09시
        inqryBgnDt = (current_time - timedelta(hours=15)).strftime('%Y%m%d%H%M')
        inqryEndDt = current_time.strftime('%Y%m%d%H%M')
    else:  # 그 외 시간 (주기적인 확인용)
        # 현재 시간부터 1시간 전까지
        inqryBgnDt = (current_time - timedelta(hours=1)).strftime('%Y%m%d%H%M')
        inqryEndDt = current_time.strftime('%Y%m%d%H%M')

    # API 요청 파라미터 설정
    end_point = "http://apis.data.go.kr/1230000/ad/BidPublicInfoService"
    operation = "getBidPblancListInfoServcPPSSrch"
    # WARNING: API 서비스 키 또한 환경 변수로 관리하는 것이 안전합니다.
    # 예: ServiceKey = os.getenv('G2B_API_KEY')
    ServiceKey = "xRUuN88FgTSyqrTnD4CS9dijQGMOlS8bI0m5KwmQwF36OHos33wW9BYIfHjzyFuH3aRThLrdRtE4Rx5rYKAZ2A=="

    params = {
        'ServiceKey': ServiceKey,
        'type': 'json',
        'numOfRows': 100,
        'pageNo': 1,
        'inqryDiv': '1', # 조회 구분 (1: 공고게시일시)
        'indstrytyCd': '1169', # 업종코드 (학술.연구용역)
        'inqryBgnDt': inqryBgnDt,
        'inqryEndDt': inqryEndDt
    }

    keywords = [
        "위성", "원격탐사", "공간정보", "자료동화", "지구", "환경", "기후변화",
        "자연재해", "수재해", "홍수", "가뭄", "산불", "수자원", "지하수",
        "수질", "강우", "레이더", "토양수분", "수문기상", "농업 생산량", "관개", "산림"
    ]

    all_bids_df = pd.DataFrame()

    # 각 키워드별로 API 요청 및 결과 취합
    for keyword in keywords:
        params['bidNtceNm'] = keyword

        try:
            response = requests.get(f"{end_point}/{operation}", params=params, timeout=10)
            response.raise_for_status()  # 200 OK가 아닐 경우 예외 발생

            data = response.json()
            items = data.get("response", {}).get("body", {}).get("items", [])

            if not items:
                continue

            # '수의계약' 공고 필터링
            filtered_items = [
                item for item in items
                if "수의계약" not in item.get("cntrctCnclsMthdNm", "")
            ]

            if filtered_items:
                keyword_df = pd.DataFrame(filtered_items)
                all_bids_df = pd.concat([all_bids_df, keyword_df], ignore_index=True)

        except requests.exceptions.RequestException as e:
            print(f"'{keyword}' 키워드 검색 중 API 요청 오류: {e}")

    # 중복된 공고 제거 (공고번호 기준)
    if not all_bids_df.empty:
        all_bids_df = all_bids_df.drop_duplicates(subset=['bidNtceNo'])

    return all_bids_df, inqryBgnDt, inqryEndDt


def monitor_bids():
    """새로운 입찰 공고를 모니터링하고, 발견 시 슬랙으로 알림을 보냅니다.

    `fetch_new_bids` 함수를 호출하여 최신 공고를 가져온 뒤,
    전역 변수 `previous_bids`와 비교하여 새로운 공고가 있는지 확인합니다.
    """
    global previous_bids
    new_bids_df, inqryBgnDt, inqryEndDt = fetch_new_bids()

    time_info = f"조회 기간: {inqryBgnDt[:8]} {inqryBgnDt[8:]} ~ {inqryEndDt[:8]} {inqryEndDt[8:]}"

    if new_bids_df.empty:
        message = f"🔍 새로 게시된 관련 공고가 없습니다.\n{time_info}"
        print(message)
        send_slack_notification(message)
        return

    # 공고명 리스트 생성
    current_bids = new_bids_df["bidNtceNm"].tolist()

    # 이전에 없었던 새로운 공고만 필터링
    new_entries = [bid for bid in current_bids if bid not in previous_bids]

    if new_entries:
        print(f"📢 {len(new_entries)}개의 새로운 공고를 발견했습니다.")
        for bid_name in new_entries:
            # 해당 공고의 상세 정보 추출
            bid_info = new_bids_df[new_bids_df["bidNtceNm"] == bid_name].iloc[0]
            link = bid_info["bidNtceDtlUrl"]

            message = (
                f"📢 새로운 학술연구용역 공고!\n\n"
                f"▪️ 공고명: *{bid_name}*\n"
                f"▪️ 링크: {link}\n\n"
                f"_{time_info}_"
            )
            send_slack_notification(message)
    else:
        message = f"✅ 이전에 알려드린 공고 외에 새로운 내용은 없습니다.\n{time_info}"
        print(message)
        send_slack_notification(message)

    # 다음 조회를 위해 현재 공고 목록을 이전 목록으로 업데이트
    previous_bids = current_bids

# ====================================================================================#
# 스크립트 실행
# ====================================================================================#
if __name__ == "__main__":
    monitor_bids()
