# 필요한 라이브러리 설치
# matplotlib에서 한글을 표시하기 위한 나눔고딕 폰트 설치 및 설정
!sudo apt-get install -y fonts-nanum
!sudo fc-cache -fv
!rm -rf ~/.cache/matplotlib
!pip install folium
!pip install pandas
!pip install geopy

import pandas as pd
import folium
from folium.plugins import HeatMap
from geopy.geocoders import Nominatim
import time
import matplotlib.pyplot as plt

# Colab에서 폰트 설정
# 맑은고딕 대신 어디서든 사용하기 쉬운 나눔고딕을 사용합니다.
plt.rc('font', family='NanumGothic')
print("폰트 설정 완료.")

# Geopy의 Nominatim Geocoder 초기화
# Nominatim 서비스는 'User-Agent'를 요구합니다.
geolocator = Nominatim(user_agent="geocoder_application")

# CSV 파일 불러오기
# 'euc-kr' 인코딩은 한국어 CSV 파일에 자주 사용됩니다.
# 만약 오류가 발생하면 'utf-8' 또는 'cp949'로 변경해 보세요.
try:
    df = pd.read_csv('data4map.csv', encoding='euc-kr')
    print("CSV 파일 불러오기 성공!")
except UnicodeDecodeError:
    print("인코딩 오류! 'utf-8' 또는 다른 인코딩으로 다시 시도합니다.")
    df = pd.read_csv('data4map.csv', encoding='utf-8')

# 주소 변환을 위한 컬럼 조합
# 속도 개선을 위해 'province'와 'city'만 사용하여 주소를 단순화합니다.
df['short_address'] = df['province'] + ' ' + df['city']
addresses = df['short_address'].tolist()


# 주소를 위도, 경도로 변환하는 함수
def geocode_nominatim(address):
    """
    주소를 Nominatim 서비스를 이용하여 위도, 경도로 변환합니다.
    API 호출 시 일시적인 대기 시간을 둡니다 (서비스 사용 제한 방지).
    """
    try:
        # 단순화된 주소로 검색 시도
        location = geolocator.geocode(address, timeout=10)
        if location:
            return location.latitude, location.longitude
        else:
            print(f"'{address}'에 대한 좌표를 찾을 수 없습니다.")
            return None, None
    except Exception as e:
        print(f"지오코딩 중 오류가 발생했습니다: {e}")
        return None, None

# 주소를 변환하여 위도(latitude)와 경도(longitude) 리스트 생성
latitudes = []
longitudes = []

print("\n주소를 좌표로 변환하는 중...")
for i, address in enumerate(addresses):
    lat, lon = geocode_nominatim(address)
    if lat and lon:
        latitudes.append(lat)
        longitudes.append(lon)
    # Nominatim 서비스 사용 제한을 피하기 위해 넉넉히 1초씩 대기
    time.sleep(1)
    if (i + 1) % 10 == 0:
        print(f"{i + 1}번째 주소 처리 완료.")

# 변환된 좌표로 데이터프레임 생성
map_data = pd.DataFrame({'latitude': latitudes, 'longitude': longitudes})
print(f"\n총 {len(map_data)}개의 유효한 좌표를 얻었습니다.")

# 대한민국 중심 좌표를 기준으로 지도 생성
korea_center = [37.5665, 126.9780]
m = folium.Map(location=korea_center, zoom_start=7, tiles="OpenStreetMap")

# 위도, 경도 리스트를 기반으로 히트맵 생성
heat_data = [[row['latitude'], row['longitude']] for index, row in map_data.iterrows()]
HeatMap(heat_data).add_to(m)

# 지도를 HTML 파일로 저장
m.save('korea_heatmap_nominatim.html')
print("\n히트맵 지도가 'korea_heatmap_nominatim.html' 파일로 저장되었습니다.")
