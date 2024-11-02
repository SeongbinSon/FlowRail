from flask import Flask, render_template, request, session
import requests
import pandas as pd
import networkx as nx
from collections import defaultdict

app = Flask(__name__)
app.secret_key = 'test_session_key'
df = pd.read_csv("./FlowRail/static/distance_station.csv",encoding='cp949')

column_name_mapping = {
    '연번': 'index',
    '역명': 'station_name',
    '호선': 'line_number',
    '소요시간' : 'time',
    '역간거리(km)' : 'stn_distance',
    '호선별누계(km)' : 'line_total'
}

df.rename(columns=column_name_mapping, inplace=True)
print("\nUpdated column names:")
print(df)

line_number = {
    "1077" : "신분당선",
    "1001" : "1호선",
    "1002" : "2호선",
    "1003" : "3호선",
    "1004" : "4호선",
    "1005" : "5호선",
    "1006" : "6호선",
    "1007" : "7호선",
    "1008" : "8호선",
    "1009" : "9호선",
    "1075" : "수인분당선"
}
number_line = {
    "77" : "1077",
    "1" : "1001",
    "2" : "1002",
    "3" : "1003",
    "4" : "1004",
    "5" : "1005",
    "6" : "1006",
    "7" : "1007",
    "8" : "1008",
    "9" : "1009",
    "75" : "1075"
}
# /* ------------------------------------------------------------------------------------------------ */

@app.route('/')
def hello_world():
    return render_template('form.html', arrivaltime = None , RTSA_firstMsg = None , RTSA_secondMsg = None , SW_INFOLIST = None)

@app.route('/subway')
def test_subway():
    return render_template('search.html')

@app.route('/first')
def test_first_page():
    return render_template('./service_templates/index.html')

@app.route('/check-time')
def test_check_time_page():
    return render_template('./service_templates/check-time.html')

@app.route('/station-search')
def test_station_search_page():
    lineno = request.args.get('lineno')
    if lineno:
        return render_template('./service_templates/station-search.html',lineno = lineno)
    else:
        return render_template('./service_templates/station-search.html',lineno = '1')
@app.route('/DI')
def test_subway_DI():
    return render_template('./service_templates/subway-DI.html')

@app.route('/DT')
def test_subway_DT():
    return render_template('./service_templates/DT.html')

@app.route('/DT_TEST')
def test_subway_DT_TEST():
    return render_template('./service_templates/DT_TEST.html')


# /* ------------------------------------------------------------------------------------------------ */

@app.route('/getform',methods=['POST', 'GET'])
def getForm():
    a = None
    if request.method == 'POST':
        name = request.form['stationName']
        #함수 호출 
        
        # [RTSA] 실시간 역 도착정보 # 활성화 하지 않음
        # RTSA API KEY = 476a4267646572723737724355686d
        RTSA_URL = "http://swopenAPI.seoul.go.kr/api/subway/476a4267646572723737724355686d/json/realtimeStationArrival/1(1 ~ )/5( ~ 5)/(역이름)"

        # [RTP] 열차 실시간 위치 # 활성화 하지 않음
        # RTP API KEY = 795476586f6572723338674d467250
        RTP_URL = "http://swopenAPI.seoul.go.kr/api/subway/795476586f6572723338674d467250/json/realtimePosition/1(1 ~ )/40( ~ 40)/(호선이름)"

        # [RTSA] 첫차 검색
        RTSA_url_First_search = "http://swopenAPI.seoul.go.kr/api/subway/476a4267646572723737724355686d/json/realtimeStationArrival/0/0/"+name

        # [RTSA] TEST #테스트 배드 사용안함
        RTSA_url_test = "http://swopenAPI.seoul.go.kr/api/subway/476a4267646572723737724355686d/json/realtimeStationArrival/1/40/"+name

        # [RTSA 2호선 강남역(1002000222)<TEST>] # 활성화 하지 않음 (테스트 배드 사용 변수)
        RTSA_url_Gangnam = "http://swopenAPI.seoul.go.kr/api/subway/476a4267646572723737724355686d/json/realtimeStationArrival/1/40/"+name

        # [RTP 2호선(1002)<TEST>]
        RTP_url_line2 = "http://swopenAPI.seoul.go.kr/api/subway/795476586f6572723338674d467250/json/realtimePosition/1/40/2호선"
        RTSA_get_info = requests.get(RTSA_url_test) # 실시간 역 도착정보 불러오기
        RTSA_get_info = RTSA_get_info.json()

# /* ------------------------------------------------------------------------------------------------ */
# /* ------------------------------------------------------------------------------------------------ */

        RTP_get_info = requests.get(RTP_url_line2)
        print(RTSA_get_info)
        RTP_get_info = RTP_get_info.json()

        print(RTP_get_info['realtimePositionList'][0]['subwayId'])

        # barvlDt / arvlMsg2 / arvlMsg3 / infolist / ordkey / updnLine 표시
        arrivaltime = RTSA_get_info['realtimeArrivalList'][0]['barvlDt']
        RTSA_firstMsg = RTSA_get_info['realtimeArrivalList'][0]['arvlMsg2']
        RTSA_secondMsg = RTSA_get_info['realtimeArrivalList'][0]['arvlMsg3']
        info_list = [RTSA_get_info['realtimeArrivalList'][0]['btrainNo'], RTSA_get_info['realtimeArrivalList'][0]['recptnDt'], RTSA_get_info['realtimeArrivalList'][0]['arvlMsg2']]
        test_ord = RTSA_get_info['realtimeArrivalList'][0]['ordkey']
        lineupdn = RTSA_get_info['realtimeArrivalList'][0]['updnLine']



    return render_template('subway-DI.html', time=arrivaltime, firstMsg=RTSA_firstMsg, secondMsg=RTSA_secondMsg, SW_INFOLIST = info_list, testord = test_ord , line_check_updn = lineupdn)

# /* ------------------------------------------------------------------------------------------------ */

#subway 기능 구현 테스트배드
@app.route('/getsearch',methods=['POST', 'GET'])
def getsubway():

    #값 초기화
    arrivaltime = 0
    infomation_test = 1
    arvlcode = "default"
    updnline_checker = "default"
    first_info = "default"
    second_info = "default"
    inner_circle_line_to_up_line = 'default'
    outer_circle_line_to_dn_line = 'default'
    trainlinenum = 'default'

    #이름 및 호선 지정
    name = request.form['stationName']
    line = request.form['line']
    line = number_line[line]
    updnline = request.form['updnline']
    print(name,  line, updnline)
# /* ------------------------------------------------------------------------------------------------ */


# /* ------------------------------------------------------------------------------------------------ */

   #열차 검색을 위한 RTSA_url_First_search
    RTSA_url_First_search = "http://swopenAPI.seoul.go.kr/api/subway/476a4267646572723737724355686d/json/realtimeStationArrival/0/40/"+name
    RTSA_url_Second_search = "http://swopenAPI.seoul.go.kr/api/subway/476a4267646572723737724355686d/json/realtimeStationArrival/1/40/"+name
    #RTSA_url_Third_search = "http://swopenAPI.seoul.go.kr/api/subway/476a4267646572723737724355686d/json/realtimeStationArrival/2/40/"+name
    # 실시간 역 도착정보 불러오기
    RTSA_get_info = requests.get(RTSA_url_First_search)
    RTSA_Second_get_info = requests.get(RTSA_url_Second_search)
    #RTSA_Third_get_info = requests.get(RTSA_url_Third_search)

    # 정보 json 변환
    RTSA_get_info = RTSA_get_info.json()
    RTSA_Second_get_info = RTSA_Second_get_info.json()
    #RTSA_Third_get_info = RTSA_url_Third_search.json()
    
    if line == "1002" and updnline == '상행':
        updnline= '내선'

    
    elif line == "1002" and updnline == '하행':
        updnline = '외선'
    
    # subwayList = RTSA_get_info['realtimeArrivalList']
    # ST = 0
    # sec_ST = 0
    # M_ST = 2000
    # sec_M_ST = 2000
    # for i in range(len(subwayList)):
    # test = int(subwayList[i]['barvlDt'])
    # if test <= M_ST:
    #         ST = i
    #         M_ST = int(subwayList[i]['barvlDt'])
    
    # print(ST, M_ST)
    # 2호선 내선순환 조회
    for Timelist in range(len(RTSA_get_info['realtimeArrivalList'])):
        if RTSA_get_info['realtimeArrivalList'][Timelist]['updnLine'] == updnline or  RTSA_get_info['realtimeArrivalList'][Timelist]['updnLine'] == inner_circle_line_to_up_line or RTSA_get_info['realtimeArrivalList'][Timelist]['updnLine'] == outer_circle_line_to_dn_line:
            print("test_first",RTSA_get_info['realtimeArrivalList'][Timelist]['subwayId'])
            if RTSA_get_info['realtimeArrivalList'][Timelist]['subwayId'] == line:
                    
                    arrivaltime = RTSA_get_info['realtimeArrivalList'][Timelist]['barvlDt']
                    infomation_test = RTSA_get_info['realtimeArrivalList'][Timelist]['btrainNo']
                    updnline_checker = RTSA_get_info['realtimeArrivalList'][Timelist]['updnLine']
                    first_info = RTSA_get_info['realtimeArrivalList'][Timelist]['arvlMsg2']
                    second_info = RTSA_get_info['realtimeArrivalList'][Timelist]['arvlMsg3']
                    trainlinenum = RTSA_get_info['realtimeArrivalList'][Timelist]['trainLineNm']

            
                            #arvlcode 한글변환 부분
                    if RTSA_get_info['realtimeArrivalList'][Timelist]['arvlCd'] == "0":
                        arvlcode = "진입"

                    elif RTSA_get_info['realtimeArrivalList'][Timelist]['arvlCd'] == "1":
                        arvlcode = "도착"
                    
                    elif RTSA_get_info['realtimeArrivalList'][Timelist]['arvlCd'] == "2":
                        arvlcode = "출발"

                    elif RTSA_get_info['realtimeArrivalList'][Timelist]['arvlCd'] == "3":
                        arvlcode = "전역출발"

                    elif RTSA_get_info['realtimeArrivalList'][Timelist]['arvlCd'] == "4":
                        arvlcode = "전역진입"
                    
                    elif RTSA_get_info['realtimeArrivalList'][Timelist]['arvlCd'] == "5":
                        arvlcode = "전역도착"

                    elif RTSA_get_info['realtimeArrivalList'][Timelist]['arvlCd'] == "99":
                        arvlcode = "운행중"
                    break
                    



    for S_Timelist in range(len(RTSA_Second_get_info['realtimeArrivalList'])):
        if RTSA_Second_get_info['realtimeArrivalList'][S_Timelist]['updnLine'] == updnline or RTSA_Second_get_info['realtimeArrivalList'][S_Timelist]['updnLine'] == inner_circle_line_to_up_line or RTSA_Second_get_info['realtimeArrivalList'][S_Timelist]['updnLine'] == outer_circle_line_to_dn_line:
            print("test_sec",RTSA_Second_get_info['realtimeArrivalList'][S_Timelist]['subwayId'])
            if RTSA_Second_get_info['realtimeArrivalList'][S_Timelist]['subwayId'] == line:
                    second_arrivaltime = RTSA_Second_get_info['realtimeArrivalList'][S_Timelist]['barvlDt']
                    second_infomation_test = RTSA_Second_get_info['realtimeArrivalList'][S_Timelist]['btrainNo']
                    second_updnline_checker = RTSA_Second_get_info['realtimeArrivalList'][S_Timelist]['updnLine']
                    second_first_info = RTSA_Second_get_info['realtimeArrivalList'][S_Timelist]['arvlMsg2']
                    two_second_info = RTSA_Second_get_info['realtimeArrivalList'][S_Timelist]['arvlMsg3']


                    
                    if RTSA_Second_get_info['realtimeArrivalList'][S_Timelist]['arvlCd'] == "0":
                        sec_arvlcode = "진입"

                    elif RTSA_Second_get_info['realtimeArrivalList'][S_Timelist]['arvlCd'] == "1":
                        sec_arvlcode = "도착"
                    
                    elif RTSA_Second_get_info['realtimeArrivalList'][S_Timelist]['arvlCd'] == "2":
                        sec_arvlcode = "출발"

                    elif RTSA_Second_get_info['realtimeArrivalList'][S_Timelist]['arvlCd'] == "3":
                        sec_arvlcode = "전역출발"

                    elif RTSA_Second_get_info['realtimeArrivalList'][S_Timelist]['arvlCd'] == "4":
                        sec_arvlcode = "전역진입"
                    
                    elif RTSA_Second_get_info['realtimeArrivalList'][S_Timelist]['arvlCd'] == "5":
                        sec_arvlcode = "전역도착"


                    elif RTSA_Second_get_info['realtimeArrivalList'][S_Timelist]['arvlCd'] == "99":
                        sec_arvlcode = "운행중"
                    break

    # [/subway] RTSA Command Terminal
    print("/* ------------------------------------------------------------------------------------------------ */")
    print("/*                                     RTSA Command Terminal                                        */")
    print("/* ------------------------------------------------------------------------------------------------ */")
    print("/* ------------------------------------------------------------------------------------------------ */")
    print(" ")
    print("열차도착예정시간(arrivaltime)")
    print(arrivaltime)
    print(" ")
    print("/* ------------------------------------------------------------------------------------------------ */")
    print(" ")
    print("도착코드 (arvlCd)")
    print(arvlcode)
    print(" ")
    print("/* ------------------------------------------------------------------------------------------------ */")
    print(" ")
    print("열차번호 (btrainNm)")
    print(infomation_test)
    print(" ")
    print("/* ------------------------------------------------------------------------------------------------ */")
    print(" ")
    print("상하행선 구분 (updnLine)")
    print(updnline_checker)
    print(" ")
    print("/* ------------------------------------------------------------------------------------------------ */")
    print(" ")
    print("첫번째 도착 메시지 (arvlMsg2)")
    print(first_info)
    print(" ")
    print("/* ------------------------------------------------------------------------------------------------ */")
    print(" ")
    print("두번째 도착 메시지 (arvlMsg3)")
    print(second_info)
    print(" ")
    print("/* ------------------------------------------------------------------------------------------------ */")
    print("/*                                                                                                  */")
    print("/* ------------------------------------------------------------------------------------------------ */")
    print(infomation_test) # 열차 번호
    print(first_info)
    print(second_info) # 현재 역
    print(arvlcode) # 도착 코드

    return render_template('./service_templates/subway-DI.html', 
                           name = name, 
                           line=line_number[line] ,
                           time = arrivaltime , 
                           arrivalcode = arvlcode , 
                           train_number = infomation_test ,
                           updn_check = updnline_checker , 
                           first_info = first_info ,
                           trainlinenum = trainlinenum,
                           second_info = second_info,
                           second_arrivaltime = second_arrivaltime, 
                           second_infomation_test = second_infomation_test,
                           second_updnline_checker = second_updnline_checker, 
                           second_first_info = second_first_info, 
                           two_second_info = two_second_info,
                           sec_arvlcode = sec_arvlcode,
                           third_info = "0",
                           third_arrivaltime = "0", 
                           third_infomation_test = "0",
                           third_updnline_checker = "0", 
                           third_first_info = "0", 
                           three_second_info = "0")

# /* ------------------------------------------------------------------------------------------------ */
@app.route("/test")
def test():
    return render_template("station_search_test.html")




URL = "http://swopenAPI.seoul.go.kr/api/subway/795476586f6572723338674d467250/json/realtimeStationArrival/0/5/"

def time_to_seconds(time_str):
    if pd.isna(time_str):
        return 0
    parts = time_str.split(':')
    if len(parts) == 2:
        minutes, seconds = map(int, parts)
        return minutes * 60 + seconds
    elif len(parts) == 3:
        hours, minutes, seconds = map(int, parts)
        return hours * 3600 + minutes * 60 + seconds
    else:
        return 0


def create_graph_from_df(df):
    G = nx.Graph()
    stations = defaultdict(set)

    for _, row in df.iterrows():
        station = row['station_name']
        line = row['line_number']
        stations[station].add(line)

    for i in range(len(df) - 1):
        current_station = df.iloc[i]['station_name']
        next_station = df.iloc[i+1]['station_name']
        current_line = df.iloc[i]['line_number']
        next_line = df.iloc[i+1]['line_number']
        seconds = df.iloc[i+1]['second']

        if current_line == next_line:
            G.add_edge((current_station, current_line), (next_station, next_line), weight=seconds, transfer=False)

    # 환승 엣지 추가
    transfer_time = 600  # 환승 시간을 1분(60초)로 가정
    for station, lines in stations.items():
        if len(lines) > 1:
            for line1 in lines:
                for line2 in lines:
                    if line1 != line2:
                        G.add_edge((station, line1), (station, line2), weight=transfer_time, transfer=True)

    return G

def dijkstra(graph, start, end):
    distances = {vertex: float('infinity') for vertex in graph}
    distances[start] = 0
    pq = [(0, start)]
    previous = {vertex: None for vertex in graph}

    while pq:
        current_distance, current_vertex = min(pq)
        pq.remove((current_distance, current_vertex))

        if current_vertex == end:
            path = []
            transfers = []
            while current_vertex:
                path.append(current_vertex)
                if previous[current_vertex] and graph[previous[current_vertex]][current_vertex].get('transfer', False):
                    transfers.append(current_vertex[0])
                current_vertex = previous[current_vertex]
            return path[::-1], distances[end], transfers[::-1]

        for neighbor in graph[current_vertex]:
            distance = current_distance + graph[current_vertex][neighbor]['weight']
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current_vertex
                pq.append((distance, neighbor))

    return None, float('infinity'), []

# DataFrame 전처리
df['second'] = df['time'].apply(time_to_seconds)
G = create_graph_from_df(df)

@app.route("/direction", methods=["POST", "GET"])
def direction():
    global G
    if request.method == "POST":
        start = request.form["startStn"]
        end = request.form["endStn"]

        # DataFrame을 그래프로 변환

        # 출발역과 도착역의 모든 가능한 라인 조합에 대해 최단 경로 계산
        start_lines = [line for station, line in G.nodes() if station == start]
        end_lines = [line for station, line in G.nodes() if station == end]
        print(start_lines, end_lines)

        best_path = None
        best_time = float('infinity')
        best_transfers = []

        for start_line in start_lines:
            for end_line in end_lines:
                path, total_seconds, transfers = dijkstra(G, (start, start_line), (end, end_line))
                if path and total_seconds < best_time:
                    best_path = path
                    best_time = total_seconds
                    best_transfers = transfers

        if best_path is None:
            error_message = "경로를 찾을 수 없습니다."
            return render_template("./service_templates/direction.html", error=error_message)

        # 소요 시간을 시, 분, 초로 변환
        hours, remainder = divmod(best_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        station_path = [station for station, _ in best_path]
        # 경로에서 역 이름만 추출
        print(f"최단 경로: {' -> '.join(station_path)}")
        print(f"총 소요 시간: {hours}시간 {minutes}분 {seconds}초")
        print(f"환승역: {', '.join(best_transfers)}")

        session['path'] = station_path
        session['hours'] = str(hours)
        session['minutes'] = str(minutes)
        session['seconds'] = str(seconds)
        session['start'] = start
        session['end'] = end
        session['best_transfers'] = best_transfers


        return render_template("./service_templates/direction.html", 
                               start=start, 
                               end=end, 
                               path=station_path,
                               hours=hours,
                               minutes=minutes,
                               seconds=seconds,
                               transfers=best_transfers)
    else:
        return render_template("./service_templates/direction.html")
# /* ------------------------------------------------------------------------------------------------ */

@app.route("/direction-test", methods=["POST", "GET"])
def direction():
    global G
    if request.method == "POST":
        start = request.form["startStn"]
        end = request.form["endStn"]

        # DataFrame을 그래프로 변환

        # 출발역과 도착역의 모든 가능한 라인 조합에 대해 최단 경로 계산
        start_lines = [line for station, line in G.nodes() if station == start]
        end_lines = [line for station, line in G.nodes() if station == end]
        print(start_lines, end_lines)

        best_path = None
        best_time = float('infinity')
        best_transfers = []

        for start_line in start_lines:
            for end_line in end_lines:
                path, total_seconds, transfers = dijkstra(G, (start, start_line), (end, end_line))
                if path and total_seconds < best_time:
                    best_path = path
                    best_time = total_seconds
                    best_transfers = transfers

        if best_path is None:
            error_message = "경로를 찾을 수 없습니다."
            return render_template("./service_templates/direction-test.html", error=error_message)

        # 소요 시간을 시, 분, 초로 변환
        hours, remainder = divmod(best_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        station_path = [station for station, _ in best_path]
        # 경로에서 역 이름만 추출
        print(f"최단 경로: {' -> '.join(station_path)}")
        print(f"총 소요 시간: {hours}시간 {minutes}분 {seconds}초")
        print(f"환승역: {', '.join(best_transfers)}")

        session['path'] = station_path
        session['hours'] = str(hours)
        session['minutes'] = str(minutes)
        session['seconds'] = str(seconds)
        session['start'] = start
        session['end'] = end
        session['best_transfers'] = best_transfers


        return render_template("./service_templates/direction-test.html", 
                               start=start, 
                               end=end, 
                               path=station_path,
                               hours=hours,
                               minutes=minutes,
                               seconds=seconds,
                               transfers=best_transfers)
    else:
        return render_template("./service_templates/direction.html")
    
# /* ------------------------------------------------------------------------------------------------ */


def get_train_num_and_arrivaltime(name):
    arrival_First_search = "http://swopenAPI.seoul.go.kr/api/subway/476a4267646572723737724355686d/json/realtimeStationArrival/0/40/"+name
    arrival_Second_search = "http://swopenAPI.seoul.go.kr/api/subway/476a4267646572723737724355686d/json/realtimeStationArrival/1/40/"+name
    arrival_test = "http://swopenAPI.seoul.go.kr/api/subway/476a4267646572723737724355686d/json/realtimeStationArrival/1/40/강남"

    arrival_first = requests.get(arrival_First_search)
    arrival_second = requests.get(arrival_Second_search)
    arrival_test = requests.get(arrival_test)

    arrival_first = arrival_first.json()
    arrival_second = arrival_second.json()
    arrival_test = arrival_test.json()


@app.route("/step/<int:num>")
def step(num):
    
    station_path = session.get('path')
    hours = session.get('hours')
    minutes = session.get('minutes')
    seconds = session.get('seconds')
    start = session.get('start')
    end = session.get('end')
    best_transfers = session.get('best_transfers')
    arrival_first = get_train_num_and_arrivaltime(start)
    arrival_second = get_train_num_and_arrivaltime(start)
    arrival_test = get_train_num_and_arrivaltime(start)

    print("-------------")
    print(station_path)
    print(hours)
    print(minutes)
    print(seconds)
    print(start)
    print(end)
    print(best_transfers)
    print(arrival_first)
    print(arrival_second)
    print(arrival_test)
    print("-------------")


    return render_template('./service_templates/step.html',
                            index = str(num+1),
                            start=start,
                            end=end, 
                            path=station_path,
                            hours=hours,
                            minutes=minutes,
                            seconds=seconds,
                            transfers=best_transfers,
                            arrival_first=arrival_first,
                            arrival_second=arrival_second)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port="8080", debug=True)
