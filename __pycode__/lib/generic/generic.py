import os
import sys
# import math
import ctypes # 관리자 권한 요청용
import shutil # 폰트 설치용
import subprocess # 폰트 설치용
import json # json 파일 입출력
# import ast # string to dictionary
from datetime import datetime # 현재 시간 측정
from bs4 import BeautifulSoup # HTML to dictionary

import numpy as np
import pandas as pd

# import matplotlib.pyplot as plt
import matplotlib.font_manager as fm # 폰트 검색용
# import matplotlib.patches as patches


from mpl_toolkits.mplot3d import Axes3D
# from statsmodels.nonparametric.smoothers_lowess import lowess
from pathlib import Path

def get_sorted_indices(original_list):
    # 원래 리스트와 인덱스를 (인덱스, 값) 형태로 결합
    indexed_list = list(enumerate(original_list))
    
    # 값을 기준으로 알파벳 순으로 정렬
    sorted_indexed_list = sorted(indexed_list, key=lambda x: x[1])
    
    # 정렬된 리스트와 원래 인덱스 추출
    sorted_list = [value for index, value in sorted_indexed_list]
    sorted_indices = [index for index, value in sorted_indexed_list]
    
    return sorted_list, sorted_indices

#############################################
#             Dictionary 관련               #
#############################################
def remove_items_with_text_key(my_dict, text):
    """text 키를 가진 모든 딕셔너리 요소를 삭제하는 함수"""
    # 삭제할 키를 저장할 리스트
    keys_to_remove = [key for key, value in my_dict.items() if text in key]

    # 딕셔너리에서 해당 키를 가진 요소 삭제
    for key in keys_to_remove:
        del my_dict[key]

def dict_to_html_table(data_dict):
    """딕셔너리를 HTML 테이블로 변환하는 함수"""
    html = "<table border='1' cellpadding='5'>"
    html += "<tr><th>Key</th><th>Value</th></tr>"
    
    for key, value in data_dict.items():
        html += f"<tr><td>{key}</td><td>{value}</td></tr>"
    
    html += "</table>"
    return html

def html_to_dict(html_data):
    """HTML 테이블 데이터를 딕셔너리로 변환하는 함수"""
    soup = BeautifulSoup(html_data, 'html.parser')
    
    # 빈 딕셔너리 생성
    data_dict = {}
    
    # 테이블 찾기
    table = soup.find('table')
    if not table:
        raise ValueError("HTML에 테이블이 없습니다.")
    
    # 테이블 행들 가져오기 (첫 번째 행은 헤더이므로 건너뜀)
    rows = table.find_all('tr')[1:]
    
    # 각 행에서 key-value 추출
    for row in rows:
        cells = row.find_all('td')
        if len(cells) == 2:  # key와 value 두 개의 셀이 있는지 확인
            key = cells[0].get_text(strip=True)  # 첫 번째 셀: key
            value = cells[1].get_text(strip=True)  # 두 번째 셀: value
            data_dict[key] = value
    
    return data_dict

#############################################
#              JSON 파일 관련               #
#############################################
# 딕셔너리를 JSON 파일로 저장하는 함수
def save_dict_to_json(file_path, dictionary):
    # dictionary 내의 모든 요소가 df일 때
    serializable_dictionary = {}
    for key in dictionary.keys():
        serializable_dictionary[key] = dictionary[key].to_dict()

    with open(file_path, 'w') as json_file:
        json.dump(serializable_dictionary, json_file, indent=4)  # 딕셔너리를 JSON 형식으로 저장

# JSON 파일로부터 딕셔너리를 불러오는 함수
def load_dict_from_json(file_path):
    with open(file_path, 'r') as json_file:
        return json.load(json_file)

#############################################
#                  시간 관련                #
#############################################
def get_current_time():
    # 현재 시간 가져오기
    current_time = datetime.now()

    # "연-월-일-시-분-초" 형식으로 포맷
    return current_time.strftime("%Y-%m-%d-%H-%M-%S")

#############################################
#        Windows 관리자 권한 관련           #
#############################################
def request_admin_rights_windows():
    """Windows에서 관리자 권한 요청"""
    try:
        # 실행할 Python 명령어와 인수
        script = sys.executable
        params = ' '.join([f'"{arg}"' for arg in sys.argv])
        ctypes.windll.shell32.ShellExecuteW(None, "runas", script, params, None, 0)
        sys.exit(0)  # 권한 요청 후 프로그램 종료
    except Exception as e:
        print(f"Failed to elevate to admin privileges: {e}")
        sys.exit(1)
        
#############################################
#             os 경로 관련                  #
#############################################
def create_directory_if_not_exists(directory_path):
    # 디렉토리가 존재하지 않으면 새로 생성
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        
def get_current_file_directory():
    # 현재 파일의 절대 경로 불러오기
    current_file_path = os.path.abspath(__file__)
    # 절대 경로의 상위 경로(파일 디렉토리)의 상위 경로(상위 폴더 디렉토리) 반환
    directory = os.path.dirname(os.path.dirname(current_file_path))
    return directory

#############################################
#    csv파일 <-> Pandas.Dataframe 관련      #
#############################################
def import_csv_file(file_path, skiprows=0, skipcols=0):
    if file_path.exists():
        df_temp = pd.read_csv(file_path, skiprows=skiprows, header=None)
        df = pd.read_csv(file_path, skiprows=skiprows, usecols = list(range(skipcols, df_temp.shape[1])), header=None)
        return df
    else:
        print("Failed to load csv file : " + str(file_path))
        return None

def export_csv_file(file_path, df, index=False, header=False):
    df.to_csv(file_path, index=index, header=header)

#############################################
#          Pandas.Dataframe 관련            #
#############################################
def split_dataframe(df, index, axis=0):
    target_index = []
    if isinstance(index, int):
        target_index.append(index)
    elif isinstance(index, float):
        print("split_dataframe : index가 float으로 입력되었습니다 - int로 변환")
        target_index.append(int(index))
    elif isinstance(index, list) and all(isinstance(i, int) for i in index):
        target_index = index

    if len(target_index) == 0:
        print("split_dataframe : target index의 길이가 0입니다")
        return df
    
    df_output = []

    if axis == 0: # 행 방향으로 분리
        # 데이터 시작 지점 부터 첫 번째 index 까지 slicing
        df_temp = pd.DataFrame("", index=range(target_index[0]), columns=df.columns)
        df_temp = df.iloc[0:target_index[0], :].reset_index(drop=True)
        df_output.append(df_temp)
        for i in range(len(target_index)):
            if i == len(target_index)-1:
                # 마지막 순서
                # 마지막 index 부터 데이터 끝 지점 까지 slicing
                data_length = len(df)-target_index[i]
                df_temp = pd.DataFrame("", index=range(data_length), columns=df.columns)
                df_temp = df.iloc[target_index[i]:len(df)].reset_index(drop=True)
                df_output.append(df_temp)
            else:
                data_length = target_index[i+1]-target_index[i]
                df_temp = pd.DataFrame("", index=range(data_length), columns=df.columns)
                df_temp = df.iloc[target_index[i]:target_index[i+1]].reset_index(drop=True)
                df_output.append(df_temp)
                
    elif axis == 1: # 열 방향으로 분리
        column_labels = df.columns
        # 데이터 시작 지점 부터 첫 번째 index 까지 slicing
        df_temp = pd.DataFrame("", index=df.index, columns=range(target_index[0]))
        df_temp = df.iloc[:, 0:target_index[0]]
        df_temp.columns = column_labels[0:target_index[0]]
        df_output.append(df_temp)
        for i in range(len(target_index)):
            if i == len(target_index)-1:
                # 마지막 순서
                # 마지막 index 부터 데이터 끝 지점 까지 slicing
                data_length = len(df)-target_index[i]
                df_temp = pd.DataFrame("", index=df.index, columns=range(data_length))
                df_temp = df.iloc[:, target_index[i]:df.shape[1]]
                df_temp.columns = column_labels[target_index[i]:df.shape[1]]
                df_output.append(df_temp)
            else:
                data_length = target_index[i+1]-target_index[i]
                df_temp = pd.DataFrame("", index=df.index, columns=range(data_length))
                df_temp = df.iloc[:, target_index[i]:target_index[i+1]]
                df_temp.columns = column_labels[target_index[i]:target_index[i+1]]
                df_output.append(df_temp)

    return df_output

def find_column_from_label(df, target_label):
    column_indices = [i for i, col in enumerate(df.columns) if target_label in col]
    return column_indices

def find_index_from_list(list, value):
    return [index for index, element in enumerate(list) if element == value]

def normalize_dataframe(df):
    return (df - df.min()) / (df.max() - df.min())

def get_max_var(df):
    variance = np.var(df, axis=0) # 열 방향으로 variance 계산
    max_var_col = np.argmax(variance)
    max_val = np.max(variance)

    return max_val, max_var_col

#############################################
#                 폰트 관련                 #
#############################################
def rebuild_font_cache():
    """matplotlib의 폰트 캐시를 강제로 다시 로드"""
    fm._load_fontmanager(try_read_cache=False)
    
def font_exists(font_name):
    rebuild_font_cache()
    fonts = [f.name for f in fm.fontManager.ttflist]
    return font_name in fonts

def check_and_install_oxanium_font():
    font_name = "Oxanium"
    current_file_directory = os.path.dirname(os.path.abspath(__file__))
    ttf_file_path = Path(current_file_directory+"/fonts/Oxanium/Oxanium-Light.ttf") # 설치할 TTF 파일 경로

    if not font_exists(font_name):
        print(f"'{font_name}' font not found. Installing font...")
        install_font(ttf_file_path)
    
def install_font(ttf_file_path):
    """폰트를 설치하는 함수 (TTF 파일 실행)"""
    if os.path.exists(ttf_file_path):
        try:
            if sys.platform == "win32":
                # Windows 폰트 디렉토리로 TTF 파일 복사
                font_dir = os.path.join(os.environ['WINDIR'], 'Fonts')
                shutil.copy(ttf_file_path, font_dir)
                print(f"Copied {ttf_file_path} to {font_dir}")

                # 레지스트리 업데이트 (자동 설치)
                font_name = os.path.basename(ttf_file_path)
                subprocess.run(['reg', 'add', 'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Fonts',
                                '/v', font_name, '/t', 'REG_SZ', '/d', font_name, '/f'], check=True)
                print("Font installed successfully on Windows.")
                
            elif sys.platform == "darwin":
                # macOS: TTF 파일을 ~/Library/Fonts/에 복사
                font_dir = os.path.expanduser('~/Library/Fonts')
                shutil.copy(ttf_file_path, font_dir)
                print(f"Copied {ttf_file_path} to {font_dir}")
                print("Font installed successfully on macOS.")
                
            elif sys.platform == "linux":
                # Linux: TTF 파일을 ~/.fonts/에 복사 후 fc-cache 실행
                font_dir = os.path.expanduser('~/.fonts')
                if not os.path.exists(font_dir):
                    os.makedirs(font_dir)
                shutil.copy(ttf_file_path, font_dir)
                print(f"Copied {ttf_file_path} to {font_dir}")
                
                # 폰트 캐시 갱신
                subprocess.run(['fc-cache', '-f', '-v'], check=True)
                print("Font installed successfully on Linux.")
            
        except PermissionError:
            print("Permission denied. Trying to request admin rights...")
            request_admin_rights_windows()
        
        except Exception as e:
            print(f"Failed to install font: {e}")
            
    else:
        print("Font file not found.")
        
#############################################
#             Loading_Bar 관련              #
#############################################
class Loading_Bar():
    def __init__(self, header, hide_log=False, length=50):
        self.header = header
        self.hide_log = hide_log
        self.length = length

    def set_progress(self, ratio):
        bar   = ' ' * int(ratio * self.length)
        blank = ' ' * (self.length-int(ratio * self.length))

        log = ""
        log += "\033[48;5;245m" + bar   + "\033[0m"
        log += "\033[37m"       + blank + "\033[0m"
        
        if ratio != 1:
            percent_color_code = "\033[33m" # 노랑
        else:
            percent_color_code = "\033[32m" # 초록

        # return f"\r{header}|{bar:<{length}}| {percent_color_code}{ratio:.0%}\033[0m"
        if not self.hide_log:
            print(f"\r{self.header}|{log}| {percent_color_code}{ratio:.0%}\033[0m", end="")

    def finish_progress(self):
        if not self.hide_log:
            print()