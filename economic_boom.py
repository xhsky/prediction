#!/usr/bin/env python
# *-* coding:utf8 *-*
# sky

"""
经济景气模型
"""

import json
import sys, io
import datetime
from dateutil.relativedelta import relativedelta
import numpy as np
import pandas as pd

def trans_time_cap(datee):
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

def trans_time_low(datee):
    quarter_map={
            "一": "03", 
            "二": "06", 
            "三": "09", 
            "四": "12"
            }
    quarter=datee[5]
    quarter=quarter_map[quarter]

    datee=f"{datee[0:5]}{quarter}{datee[6:]}"

    return datee

def forecasted_date_fun(date_format, begin_date_str, forecasted_length):
    """返回预测的时间列表, 不包含原始时间.
    """

    if date_format=="year":
        begin_date=datetime.datetime.strptime(begin_date_str, "%Y年")
        end_date=datetime.datetime.strptime(begin_date_str, "%Y年")+relativedelta(years=forecasted_length)
        date_list = [x.strftime('%Y年') for x in list(pd.date_range(start=begin_date, end=end_date, freq='Y'))]
    elif date_format=="quarter":
        begin_date_str=trans_time_low(begin_date_str)
        begin_date=datetime.datetime.strptime(begin_date_str, "%Y年%m季度")
        end_date=datetime.datetime.strptime(begin_date_str, "%Y年%m季度")+relativedelta(months=3*forecasted_length)
        low_date_list = [x.strftime('%Y年%m季度') for x in list(pd.date_range(start="%s" % begin_date, end="%s" % end_date, freq='Q'))]
        date_list=[]
        for i in low_date_list:
            date_list.append(trans_time_cap(i))
    elif date_format=="month":
        begin_date=datetime.datetime.strptime(begin_date_str, "%Y年%m月")
        end_date=datetime.datetime.strptime(begin_date_str, "%Y年%m月")+relativedelta(months=forecasted_length)
        date_list = [x.strftime('%Y年%m月') for x in list(pd.date_range(start="%s" % begin_date, end="%s" % end_date, freq='M'))]
    #date_list.remove(date_list[0])          # 去掉第一个时间(list中已有)
    return date_list

def data_polyfit(data_list, forecasted_length, polyfit_times):
    x=range(len(data_list))
    fx=np.polyfit(x, data_list, polyfit_times)
    p=np.poly1d(fx)
    new_x=range(len(data_list)+forecasted_length)
    new_y=[]
    for y in p(new_x):
        new_y.append(round(y, 2))
    return new_y

def economic_boom_mode(data, request, weight):
    """
        signal_data=[
            {
                指标:
                地区:
                时点:
                时间:
                值: 
            }, 
            {}
        ]

        lines=[
            {
                指标:
                地区:
                时点:
                时间:
                指数:
                拟合值:
            }, 
            {}
        ]
    """
    signal_data=[]
    inter_data={}
    for system in request:
        if system != "forecasted_length" and system != "fit_times" and system != "period":
            for request_indicator in request[system]:
                for region in data:
                    if data[region].get(request_indicator) is not None:
                        for timepoint in data[region][request_indicator]:
                            raw_data_dict=data[region][request_indicator][timepoint]
                            current_value_dict={}
                            # 原始值状态
                            for time in raw_data_dict:
                                temp_indicator_signal={
                                        "指数": system, 
                                        "指标": request_indicator, 
                                        "地区": region, 
                                        "时点": timepoint, 
                                        "时间": time
                                        }
                                value=raw_data_dict[time]
                                if value is None:
                                    value=0
                                    value_status="无状态"
                                else:
                                    status_dict=request[system][request_indicator]["status"]
                                    for status in status_dict:
                                        if value >= status_dict[status][0] and value < status_dict[status][1]:
                                            value_status=status
                                            break
                                    else:
                                        value_status="无状态"
                                    temp_indicator_signal["值"]=value_status
                                    signal_data.append(temp_indicator_signal)

                                current_value_dict[time]=value

                            # 中间值
                            key=(system, region, request_indicator, timepoint)
                            inter_data[key]=[]
                            max_value=max(current_value_dict.values())
                            min_value=min(current_value_dict.values())
                            difference=max_value-min_value
                            for time in current_value_dict:
                                current_value=current_value_dict[time]
                                if difference==0:
                                    median=0
                                else:
                                    median=((current_value-min_value) * weight[0] / difference ) + weight[1]
                                inter_data[key].append((time, median))

    system_temp_data={}
    for indicator_key in inter_data:
        for i in inter_data[indicator_key]:
            system_temp_key=(indicator_key[0], indicator_key[1], indicator_key[3], i[0])
            system_indicator_weight=request[indicator_key[0]][indicator_key[2]]["weight"]
            value=(indicator_key[2], i[1], system_indicator_weight)
            if system_temp_key not in system_temp_data:
                system_temp_data[system_temp_key]=[value, ]
            else:
                system_temp_data[system_temp_key].append(value)

    # system_data,  体系值状态
    system_data={}
    for i in system_temp_data:
        weight_sum=0
        system_value_sum=0
        for j in system_temp_data[i]:
            weight_sum=weight_sum+j[2]
            system_value_sum=system_value_sum+j[1]*j[2]
        if weight_sum == 0:
            print("权重和不可为0")
            exit()
        else:
            system_value=system_value_sum/weight_sum
            key=i[0:3]
            system_status_dict=request[i[0]]["status"]
            for system_status in system_status_dict:
                if system_value >= system_status_dict[system_status][0] and system_value < system_status_dict[system_status][1]:
                    system_value_status=system_status
                    break
            else:
                system_value_status="无状态"
            temp_signal_dict={
                    "指数": i[0], 
                    "指标": i[0], 
                    "地区": i[1], 
                    "时点": i[2], 
                    "时间": i[3],
                    "值": system_value_status
                    }
            signal_data.append(temp_signal_dict)

            value=(i[3], system_value, weight_sum)
            if key not in system_data:
                system_data[key]=[value, ]
            else:
                system_data[key].append(value)

    comprehensive_temp_data={}
    for i in system_data:
        for j in system_data[i]:
            key=(i[1], i[2], j[0])
            value=(j[1], j[2])
            if key not in comprehensive_temp_data:
                comprehensive_temp_data[key]=[value]
            else:
                comprehensive_temp_data[key].append(value)

    comprehensive_data={}
    for i in comprehensive_temp_data:
        key=(i[0], i[1])
        if key not in comprehensive_data:
            comprehensive_data[key]={}
        com_weight_sum=sum([x[1] for x in comprehensive_temp_data[i]])
        value_sum=0
        for j in comprehensive_temp_data[i]:
            value_sum=value_sum+j[0]*j[1]
        value=round(value_sum/com_weight_sum, 2)
        comprehensive_data[key][i[2]]=value

    # fit
    forecasted_length=request["forecasted_length"]
    fit_times=request["fit_times"]
    data_type=request["period"]
    # system fit
    fit_system_data={}
    for i in system_data:
        temp_data_dict={}
        for j in system_data[i]:
            temp_data_dict[j[0]]=j[1]
        sorted_data_list=data_sorting(temp_data_dict, data_type)
        sorted_num_list=[x[1] for x in sorted_data_list]
        fit_date_list=forecasted_date_fun(data_type, sorted_data_list[0][0], len(sorted_data_list)+forecasted_length)
        fit_num_list=data_polyfit(sorted_num_list, forecasted_length, fit_times)
        fit_data_dict=dict(zip(fit_date_list, fit_num_list))
        #print(f"{i=}, {fit_num_list=}, {fit_date_list=}, {fit_data_dict}")
        fit_system_data[i]=fit_data_dict

    # comprehensive fit
    fit_comprehensive_data={}
    for i in comprehensive_data:
        sorted_data_list=data_sorting(comprehensive_data[i], data_type)
        sorted_num_list=[x[1] for x in sorted_data_list]
        fit_date_list=forecasted_date_fun(data_type, sorted_data_list[0][0], len(sorted_data_list)+forecasted_length)
        fit_num_list=data_polyfit(sorted_num_list, forecasted_length, fit_times)
        fit_data_dict=dict(zip(fit_date_list, fit_num_list))
        fit_comprehensive_data[i]=fit_data_dict

    return signal_data, system_data, comprehensive_data, fit_system_data, fit_comprehensive_data

def data_sorting(data_dict, data_type):
    sorted_data_dict={}
    if data_type=="quarter":
        for i in data_dict:
            low_time=trans_time_low(i)
            sorted_data_dict[low_time]=data_dict[i]

        sorted_data_list=[]
        for i in sorted(sorted_data_dict.items(), key=lambda item:item[0]):
            cap_time=trans_time_cap(i[0])
            sorted_data_list.append((cap_time, i[1]))
    else:
        sorted_data_list=sorted(data_dict.items(), key=lambda item:item[0])
    return sorted_data_list

def get_params(request):
    params={"levels":{}}
    params["forecastLength"]=request["forecasted_length"]
    for system in request:
        if system != "forecasted_length" and system != "fit_times" and system != "period":
            params["levels"][system]={}
            for status in request[system]["status"]:
                params["levels"][system][status]=request[system]["status"][status][1]
    return params

def line_data_merge(system_data, comprehensive_data, fit_system_data, fit_comprehensive_data):
    """
        景气模型

        inter_data={
            (system, region, indicator, timepoint): [(time, median_value), ]
        }

        system_temp_data={
            (system, region, timepoint, time): [(indicator, median_value, weight), ]
        }
        system_data={
            (system, region, timepoint): [(time, system_value, weight_sum), ]
        }

        fit_system_data={
            (system, region, timepoint): {
                time: fit_value, 
                time: fit_value
            }
        }

        fit_comprehensive_data={
            (region, timepoint): {
                time: fit_value, 
                time: fit_value
                }
        }

        comprehensive_temp_data={
            (region, timepoint, time):[(system_value, weight_sum), ]
        }

        comprehensive_data={
            (region, timepoint): {
                time: comprehensive_value, 
                time: comprehensive_value
                }
        }

    """
    line_data=[]
    # fit system data
    for i in fit_system_data:
        for fit_time in fit_system_data[i]:
            temp_dict={
                    "指数": i[0], 
                    "地区": i[1], 
                    "时点": i[2], 
                    "时间": fit_time, 
                    "拟合值": fit_system_data[i][fit_time]
                    }
            for system_value in system_data[i]:
                if system_value[0]==fit_time:
                    temp_dict["指数值"]=system_value[1]
                    break
            else:
                temp_dict["指数值"]=None
            line_data.append(temp_dict)
    # fit comprehensive data
    for i in fit_comprehensive_data:
        for fit_time in fit_comprehensive_data[i]:
            temp_dict={
                    "指数": "综合", 
                    "地区": i[0], 
                    "时点": i[1], 
                    "时间": fit_time, 
                    "拟合值": fit_comprehensive_data[i][fit_time]
                    }
            value=comprehensive_data[i].get(fit_time) 
            temp_dict["指数值"]=value
            line_data.append(temp_dict)
    return line_data

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
            "forecasted_length": N,              // 预测长度
            "fit_times": N,                      // 拟合次数
            "period": "year"                     // 数据日期的格式: year|month|quarter
            "system1":{
                "indicator1": {
                    "status":{                  //指标下原始值状态
                        "过冷":[min, max], 
                        "偏冷":[min, max], 
                        "正常":[min, max], 
                        "偏热":[min, max], 
                        "过热":[min, max]
                    }
                    "weight":N                  // 该指标权重值
                }
                "indicator2": {}
                "status":{                     // 体系指数状态
                    "过冷":[min, max], 
                    "偏冷":[min, max], 
                    "正常":[min, max], 
                    "偏热":[min, max], 
                    "过热":[min, max]
                }
            }, 
            "system2":{
            }
        }
    }
    """

    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    #data_json=sys.argv[1]
    #arg_dict=json.loads(data_json)
    with open("./data_boom.json", "r", encoding="utf8") as f:
        arg_dict=json.load(f)

    weight=[20, 80]
    data=arg_dict.get("data")
    request=arg_dict.get("request")
    signal_data, system_data, comprehensive_data, fit_system_data, fit_comprehensive_data=economic_boom_mode(data, request, weight)
    line_data=line_data_merge(system_data, comprehensive_data, fit_system_data, fit_comprehensive_data)
    params_data=get_params(request)

    result={
            "data":{
                "signal": signal_data, 
                "lines": line_data, 
                "params": params_data
                }
            }

    print(json.dumps(result, ensure_ascii=False))
    
if __name__ == "__main__":
    main()
