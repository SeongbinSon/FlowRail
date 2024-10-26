from flask import Flask, render_template, request
import glob
import json
import requests
import networkx as nx
import heapq


file_list = [f"FlowRail/Subway_DT/DT-json/Line{i}.json" for i in range(1,9)]

data_list = []

for file_name in file_list:
    with open(file_name, 'r', encoding='utf-8') as file:
        data = json.load(file)
        data_list.append(data)

edges = [

]

for i, data in enumerate(data_list):
    print(f"Data from {file_list[i]}")
    row = data['StationDstncReqreTimeHm']['row']
    for i in range(len(row)-1):
        startStn = row[i]['SBWY_STNS_NM']
        endStn = row[i+1]['SBWY_STNS_NM']
        duration = row[i+1]['HM']
        time = duration.split(":")
        a = int(time[0])
        b = int(time[1])
        duration = a*60 + b
        tp = (startStn,endStn,duration)
        edges.append(tp)

# 그래프 생성
G = nx.DiGraph()
for start, end, duration in edges:
    G.add_edge(start, end, weight=duration)

def find_shortest_path(start_station, end_station):
    if start_station not in G or end_station not in G:
        return "역 정보가 없습니다.", ""

    try:

        length, path = nx.single_source_dijkstra(G, start_station, end_station, weight='weight')
        path_str = ' -> '.join(path)
        return path_str, length
    except nx.NetworkXNoPath:
        return "경로가 없습니다.", ""

if __name__ == '__main__':

    start_station = input("출발역을 입력하세요: ")
    end_station = input("도착역을 입력하세요: ")

    # 최단 경로 찾기
    path, distance = find_shortest_path(start_station, end_station)
    
    # 결과 출력
    print(f"경로: {path}")
    print(f"소요 시간: {distance} 초")



