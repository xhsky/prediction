#!/usr/bin/env python
# *-* coding:utf8 *-*
# sky

"""
综合评价模型
"""

import json
import sys, io
import datetime
from dateutil.relativedelta import relativedelta

def format_data(data, request):
    """
        格式化数据为以下:
    """

    """
    raw_data_dict={
        (system, indicator, timepoint): [
                [region, {{year:N}, {year:N}}], 
                [region, {{year:N}, {year:N}}]
            ]
    }

    degree_of_change_args_dict={
        (system, indicator, timepoint): [
                [region, {{year:N}}], 
                [region, {{year:N}}]
            ]
        
    }

    inter_data_dict={
        (system, indicator, timepoint): [
                [region, {{year:N}, {year:N}}], 
                [region, {{year:N}, {year:N}}]
            ]
    }

    development_result_data_dict={
        {(system, indicator, timepoint):[
            (region, {{year:N}, {year:N}}), 
            (region, {{year:N}, {year:N}})
            ]
        }
    }
    """

    raw_data_dict={}
    for system_name in request:
        for region in data:
            for request_indicator in request[system_name]:
                if request_indicator != "periods":
                    for data_indicator in data[region]:
                        if request_indicator == data_indicator:
                            for request_timepoint in request[system_name][request_indicator]:
                                raw_data=data[region][request_indicator][request_timepoint]

                                key=(system_name, request_indicator, request_timepoint)
                                if key not in raw_data_dict:
                                    raw_data_dict[key]=[[region, raw_data]]
                                else:
                                    raw_data_dict[key].append([region, raw_data])
    return raw_data_dict

def trans_time_low(datee):                                                                                                                                                   
    """
        季度时间转换小写
    """
    quarter_map={                                                                                                                                                            
            "一": 1,                                                                                                                                                         
            "二": 4,                                                                                                                                                         
            "三": 7,                                                                                                                                                         
            "四": 10                                                                                                                                                         
            }                                                                                                                                                                
    quarter=datee[5]                                                                                                                                                         
    quarter=quarter_map[quarter]                                                                                                                                             
    datee=f"{datee[0:5]}{quarter}{datee[6:]}"                                                                                                                                
    return datee            

def trans_time_cap(datee):                                                                                                                                               
    """
        季度时间转成大写
    """
    quarter_map={                                                                                                                                                        
	    "03": "一",                                                                                                                                                  
	    "06": "二",                                                                                                                                                  
	    "09": "三",                                                                                                                                                  
	    "12": "四"                                                                                                                                                   
	    }                                                                                                                                                            
    quarter=datee[5:7]                                                                                                                                                    
    quarter=quarter_map[quarter]                                                                                                                                         
																					 
    datee=f"{datee[0:5]}{quarter}{datee[7:]}"                                                                                                                   
    return datee                  

def development_degree_of_change(data_dict, period):
    "获取变动度的时间和数据"
    degree_of_change_data_dict={}
    time_list=sorted(data_dict, reverse=True)
    for time in time_list:
        pre_time=get_pre_date(period, time)
        if pre_time in time_list:
            degree_of_change_data_dict[time]=(data_dict[time]*100)/data_dict[pre_time]-100
    return degree_of_change_data_dict

def get_pre_date(period, begin_date_str):
    """
        获取给定时间的前一个时间
    """
    if period=="year":
        begin_date=datetime.datetime.strptime(begin_date_str, "%Y年")
        pre_date=datetime.datetime.strptime(begin_date_str, "%Y年")-relativedelta(years=1)
        pre_date=pre_date.strftime('%Y年')
    elif period=="quarter":
        begin_date_str=trans_time_low(begin_date_str)
        begin_date=datetime.datetime.strptime(begin_date_str, "%Y年%m季度")
        pre_date=datetime.datetime.strptime(begin_date_str, "%Y年%m季度")-relativedelta(months=1)
        pre_date=pre_date.strftime('%Y年%m季度')
        pre_date= trans_time_cap(pre_date)
    elif period=="month":
        begin_date=datetime.datetime.strptime(begin_date_str, "%Y年%m月")
        pre_date=datetime.datetime.strptime(begin_date_str, "%Y年%m月")-relativedelta(months=1)
        pre_date=pre_date.strftime('%Y年%m月')
    return pre_date

def merge(level_inter_args_dict, development_inter_args_dict, request):
    """
    数据结构转换:

    inter_data_dict={
        (system, indicator, timepoint):[
            (region, {{year1:N}, {year2:N}}), 
            (region, {{year1:N}, {year2:N}})
            ]
        
    }
    --->
    args_dict={
        (system, region, time_point):{
            year1:[(N1: weight), (N2: weight)], 
            year2:[(N1: weight), (N2: weight)]
        }
    --->
    args_dict={
        (system, region, time_point):{
            year:avg_N
            year:avg_N
        }
    """

    level_args_dict={}
    development_args_dict={}
    for i in level_inter_args_dict:
        for j in level_inter_args_dict[i]:
            key=(i[0], j[0], i[2])
            if key not in level_args_dict:
                level_args_dict[key]={}
                for time1 in j[1]:
                    level_args_dict[key][time1]=[(j[1][time1], request[i[0]][i[1]][i[2]]["weight"])]
            else:
                for time2 in j[1]:
                    level_args_dict[key][time2].append((j[1][time2], request[i[0]][i[1]][i[2]]["weight"]))

    for i in development_inter_args_dict:
        for j in development_inter_args_dict[i]:
            key=(i[0], j[0], i[2])
            if key not in development_args_dict:
                development_args_dict[key]={}
                for time1 in j[1]:
                    development_args_dict[key][time1]=[(j[1][time1], request[i[0]][i[1]][i[2]]["weight"])]
            else:
                for time2 in j[1]:
                    development_args_dict[key][time2].append((j[1][time2], request[i[0]][i[1]][i[2]]["weight"]))

    value_sum=0
    weight_sum=0
    for i in level_args_dict:
        for time in level_args_dict[i]:
            for n in level_args_dict[i][time]:
                value_sum=value_sum + n[0]*n[1]
                weight_sum=weight_sum + n[1]

            avg_data=value_sum/weight_sum
            level_args_dict[i][time]=avg_data

    value_sum=0
    weight_sum=0
    for i in development_args_dict:
        for time in development_args_dict[i]:
            for n in development_args_dict[i][time]:
                value_sum=value_sum + n[0]*n[1]
                weight_sum=weight_sum + n[1]

            avg_data=value_sum/weight_sum
            development_args_dict[i][time]=avg_data

    return level_args_dict, development_args_dict

def comprehensive_evaluation_mode(data, request, weight):
    """
        综合评价模型
    """
    raw_args_dict=format_data(data, request)

    degree_of_change_args_dict={}
    level_inter_args_dict={}
    development_inter_args_dict={}

    for i in raw_args_dict:
        level_inter_args_dict[i]=[]
        development_inter_args_dict[i]=[]
        degree_of_change_args_dict[i]=[]
        for j in raw_args_dict[i]:
            level_inter_args_dict[i].append([j[0], {}])
            development_inter_args_dict[i].append([j[0], {}])
            degree_of_change_args_dict[i].append([j[0], {}])

    for i in raw_args_dict:
        if i != "weight":
            calculation_type=request[i[0]][i[1]][i[2]]["type"]
            period=request[i[0]]["period"]
            #print(f"{i=} {calculation_type=}, {period=}")
            
            # 变动度
            for index, item in enumerate(raw_args_dict[i]):
                degree_of_change_data_dict=development_degree_of_change(item[1], period)
                degree_of_change_args_dict[i][index]=[item[0], degree_of_change_data_dict]
                #print(f"{item=}, {degree_of_change_data_dict=}")

            if calculation_type==0:
                interval=request[i[0]][i[1]][i[2]]["interval"]
                level_interval=interval["level"]
                development_interval=interval["development"]
                #print(f"{level_interval=}, {development_interval=}")
                for type_0_index, type_0_item in enumerate(raw_args_dict[i]):
                    for key_time in degree_of_change_data_dict:
                        # level compute
                        if type_0_item[1][key_time] >= level_interval[0] and type_0_item[1][key_time] <= level_interval[1]:
                            level_inter_args_dict[i][type_0_index][1][key_time]=100
                        else:
                            level_inter_args_dict[i][type_0_index][1][key_time]=0

                        # development compute
                        if degree_of_change_data_dict[key_time] >= development_interval[0] and degree_of_change_data_dict[key_time] <= development_interval[1]:
                            development_inter_args_dict[i][type_0_index][1][key_time]=100
                        else:
                            development_inter_args_dict[i][type_0_index][1][key_time]=0

            else: 
                for key_time in degree_of_change_data_dict:
                    level_data_list=[]
                    for value in raw_args_dict[i]:
                        level_data_list.append(value[1][key_time])
                    #print(f"{level_data_list=}")
                    for type_1_index, type_1_item in enumerate(raw_args_dict[i]):
                        current_data=type_1_item[1][key_time] 
                        if current_data is None:
                            current_data=0
                        max_data=max(level_data_list)
                        min_data=min(level_data_list)
                        difference=max_data-min_data
                        if difference==0:
                            level_data=0
                        else:
                            if calculation_type==1:
                                level_data=(current_data-min_data)*weight[0] / difference + weight[1]
                            elif calculation_type==-1:
                                level_data=(max_data-current_data)*weight[0] / difference + weight[1]
                        level_inter_args_dict[i][type_1_index][1][key_time]=level_data

                    development_data_list=[]
                    for value in degree_of_change_args_dict[i]:
                        development_data_list.append(value[1][key_time])
                    for type_1_index, type_1_item in enumerate(raw_args_dict[i]):
                        current_data=type_1_item[1][key_time] 
                        if current_data is None:
                            current_data=0
                        max_data=max(development_data_list)
                        min_data=min(development_data_list)
                        difference=max_data-min_data
                        if difference == 0:
                            development_data=0
                        else:
                            if calculation_type==1:
                                development_data=(current_data-min_data)*weight[0] / difference + weight[1]
                            elif calculation_type==-1:
                                development_data=(max_data-current_data)*weight[0] / difference + weight[1]
                        development_inter_args_dict[i][type_1_index][1][key_time]=development_data

    level_args_dict, development_args_dict=merge(level_inter_args_dict, development_inter_args_dict, request)

    level_weight, development_weight=request["weight"]
    comprehensive_dict={}
    for i in level_args_dict:
        comprehensive_dict[i]={}
        for j in development_args_dict:
            if i==j:
                for time in level_args_dict[i]:
                    comprehensive_dict[i][time]=level_args_dict[i][time] * level_weight + development_args_dict[i][time] * development_weight
    return comprehensive_dict

def main():
    """
    data_json={
        "data": {
            "region1":{
                "indicator1":{
                    "time_point1":{
                        "2020":N, 
                        "2021":N, 
                        ...
                    }, 
                    ...
                }, 
                ...
            }, 
            "region2":{}
        }, 
        "request":{
            "system1":{
                "indicator1": {
                    "time_point1": {
                        "type": 0,                       // 1: 正向, -1: 逆向, 0: 区间
                        "interval":{                    // 只当value为0时使用interval指定区间
                            level: [min, max],           //水平计算区间
                            development: [min, max]      //发展计算区间
                            }, 
                        "weight":N                      //指标权重
                    }, 
                    "time_point2": {
                        "type": 1             // 1: 正向, -1: 逆向, 0: 区间
                        }, 
                        "weight":N                      //指标权重
                    }
                "indicator2": {}
                "period": "year"               // 该体系下数据日期的格式: year|month|quarter
            }, 
            "system2":{
            }, 
            "weight": [0.5, 0.5]           // [水平权重, 发展权重]
        }
    }
    """

    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    data_json=sys.argv[1]
    arg_dict=json.loads(data_json)
    #with open("./data_eva.json", "r", encoding="utf8") as f:
    #    arg_dict=json.load(f)

    weight=[20, 80]
    data=arg_dict.get("data")
    request=arg_dict.get("request")
    comprehensive_dict=comprehensive_evaluation_mode(data, request, weight)

    """
    # 数据转换
    result={
        (region, timepoint, time): [(system, N), (system, N)]
    }
    """
    result={}
    for i in comprehensive_dict:
        for time in comprehensive_dict[i]:
            key=(i[1], i[2], time)
            if key not in result:
                result[key]=[(i[0], comprehensive_dict[i][time])]
            else:
                result[key].append((i[0], comprehensive_dict[i][time]))

    """
    # 赋中文值
    """
    merge_dict={"result": []}
    for i in result:
        temp={"地区":i[0], "时点":i[1], "时间":i[2]}
        for j in result[i]:
            temp[j[0]]=round(j[1], 2)
        merge_dict["result"].append(temp)

    print(json.dumps(merge_dict, ensure_ascii=False))
    
if __name__ == "__main__":
    """
    地区-->指标-->时点(两个)--》变动度 --》发展总指数

    地区-->指标-->时点--》水平指数(临时值) --》水平指数
    """
    main()
