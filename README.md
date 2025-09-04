<p align="center">
<img style="max-width:100%;"
src="./main.png"
alt="Main"/>
</p>

---

# 📩 Slack 나라장터 입찰 공고 알리미
이 프로젝트는 파이썬(Python)으로 작성된 스크립트로, 조달청 나라장터 API를 통해 특정 조건의 신규 입찰 공고를 주기적으로 확인하고, 새로운 공고가 있을 경우 슬랙(Slack)으로 실시간 알림을 보내주는 자동화 스크립트입니다.

주기적인 알림 설정을 위해서는 `crontab` (Linux/MacOS) 혹은 `작업 스케줄러` (Windows) 기능을 통해 원하는 시간에 자동으로 공고를 모니터링할 수 있습니다.

`slack_bid.py` 코드 내 검색 키워드는 수문 원격탐사, 기후 등에 대한 연구 과제 입찰 공고를 검색하기 위해 설정되었으며, 사용자의 관심 키워드에 맞게 수정 가능합니다.

---

## 주요 기능
* 🔍 맞춤 공고 검색: `학술연구용역 분야`에서 `위성`, `원격탐사` 등 지정된 여러 키워드에 해당하는 공고를 검색합니다.
* 🚫 불필요한 정보 필터링: `수의계약`과 같이 관련성이 낮은 공고는 결과에서 제외하여 핵심 정보만 추출합니다.
* 🧠 중복 알림 방지: 이미 알림을 보낸 공고는 다시 보내지 않도록 상태를 관리하여 불필요한 중복 알림을 방지합니다.
* ⏰ 자동 스케줄링 실행: Linux의 `crontab`을 이용해 원하는 시간(예: 매주 월~금, 오전 9시부터 오후 6시 사이, 정각마다)에 스크립트를 자동으로 실행할 수 있습니다.
* 💬 실시간 Slack 알림: 새로운 공고가 발견되면 공고명과 상세 링크를 포함한 메시지를 `Slack Bot`으로 즉시 전송합니다.

---

## 사용 방법
### 1. 사전 준비
#### 필수 라이브러리 설치
스크립트 실행에 필요한 파이썬 라이브러리를 설치합니다.

```bash
pip install requests pandas python-dotenv
```

#### 환경 변수 설정 (`.env` 파일)
스크립트가 있는 경로 또는 원하는 위치에 .env 파일을 생성하고, 아래와 같이 슬랙 웹훅 URL과 나라장터 API 키를 입력합니다. 보안을 위해 민감한 정보는 코드에서 분리하여 관리하는 것이 좋습니다.

```vim
# .env 파일 예시
SLACK_WEBHOOK_BID_URL="https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK_URL"

# 나라장터 API 키는 코드에 직접 입력하거나, 아래처럼 환경 변수로 관리할 수 있습니다.
# G2B_API_KEY="YOUR_NARAJANGTEO_API_KEY"
```

#### 스크립트 내 경로 수정
`slack_bid.py` 파일을 열어 `.env` 파일의 경로를 실제 위치에 맞게 수정합니다.

```python
# slack_bid.py
# ...
# Webhook URL 불러오기
env_path = '/home/seongjun/.env' # ".env 파일이 있는 실제 경로"로 수정하세요.
load_dotenv(env_path)
# ...
```

---

### 2. 스크립트 실행
#### 수동 실행 (테스트용)
서버에서 스크립트가 정상적으로 동작하는지 테스트하려면 터미널에서 직접 실행합니다.

```bash
python3 /path/to/your/slack_bid.py
```

#### 자동 실행 (`crontab` 등록)
리눅스 서버에 스크립트를 자동으로 실행하도록 스케줄을 등록합니다.
- 터미널에 `crontab -e` 명령어를 입력하여 `crontab` 편집기를 엽니다.
- 아래 내용을 복사하여 파일의 맨 아래에 추가합니다. (주의: 파이썬 경로와 스크립트 경로는 반드시 본인의 환경에 맞게 수정해야 합니다.)
- 파일을 저장하고 편집기를 닫으면 해당 스케줄이 자동으로 등록됩니다.
```vim
# 매주 월요일부터 금요일까지, 매 정각에 slack_bid.py 스크립트 실행
0 9-18 * * 1-5 /usr/bin/python3 /home/seongjun/github/slack_bid_notifier/slack_bid.py
```

`0 9-18 * * * 1-5`
&emsp;실행 주기를 의미합니다. (월-금, 오전 9시 ~ 오후 6시, 정각마다)
`/usr/bin/python3`
&emsp;파이썬 실행 파일의 절대 경로입니다. `which python3` 명령어로 확인 후 정확한 경로를 입력하세요.
`/home/seongjun/github/slack_bid_notifier/slack_bid_notifier.py`
&emsp;스크립트 파일의 절대 경로입니다. 사용자의 경로에 맞게 수정이 필요합니다.

---

## 코드 수정 및 맞춤 설정
스크립트 내부의 일부 변수를 수정하여 검색 조건을 변경할 수 있습니다.
- `keywords`: 공고를 검색할 키워드 목록을 수정하거나 추가할 수 있습니다.
- `indstrytyCd`: 업종 코드를 변경하여 다른 분야의 공고를 검색할 수 있습니다. (예: 1169는 학술.연구용역)

---

Author & Developed by: [Seongjun Lee](mailto:seongjunlee4473@gmail.com?subject=Questions%20for%20GitHub%20projects) @ Jan 2025

---

