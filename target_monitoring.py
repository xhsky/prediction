#!/usr/bin/env python
# *-* coding:utf8 *-*
# sky

"""
目标监测模型
"""

import json
import sys, io
import datetime
from dateutil.relativedelta import relativedelta

def target_monitoring_mode(data, request):
    """
        指标监测模型

        data={
            region:{
                indicator:{
                    "time_point1":{
                        time:N, 
                        time:N
                    }
                }
            }
        }
        indicator_data_dict={
            system:{
                region:{
                    indicator:{
                        "time_point1":{
                            time:{
                                score:N, 
                                degree_of_realization:N
                            }
                        }
                    }
                }
            }
        }

        system_data={
            (system, region, timepoint, time):{
                score:[N1, N2], 
                degree_of_realization:[(degree, weight), ()]
            }
        }
        system_data={
            (system, region, timepoint, time):{
                score: N_sum, 
                degree_of_realization: (d_sum, weight_sum)
            }
        }

        total_data={
            (region, timepoint, time):{
                score: [N1, N2]
                degree_of_realization:[(degrdd, weight), ]
            }
        }
        total_data={
            (region, timepoint, time):{
                score: N_sum, 
                degree_of_realization: d_sump
            }
        }
    """
    indicator_data_dict={}
    system_data_dict={}
    for system_name in request:
        indicator_data_dict[system_name]={}
        for region in data:
            indicator_data_dict[system_name][region]={}
            for request_indicator in request[system_name]:
                for data_indicator in data[region]:
                    if request_indicator == data_indicator:
                        indicator_data_dict[system_name][region][request_indicator]={}
                        for request_timepoint in request[system_name][request_indicator]:
                            indicator_data_dict[system_name][region][request_indicator][request_timepoint]={}
                            for request_time in request[system_name][request_indicator][request_timepoint]:
                                # 指标数据
                                indicator_data_dict[system_name][region][request_indicator][request_timepoint][request_time]={}
                                target_type=request[system_name][request_indicator][request_timepoint][request_time]["target"]["type"]
                                target_value=request[system_name][request_indicator][request_timepoint][request_time]["target"]["value"]
                                weight=request[system_name][request_indicator][request_timepoint][request_time]["weight"]
                                if weight is None:
                                    weight=0
                                raw_value=data[region][request_indicator][request_timepoint][request_time]

                                # 判断目标类型
                                if target_type == 1:
                                    if raw_value >= target_value:
                                        degree_of_realization=100
                                    else:
                                        degree_of_realization=round((raw_value/target_value)*100, 2)
                                elif target_type == -1:
                                    if raw_value <= target_value:
                                        degree_of_realization=100
                                    else:
                                        degree_of_realization=round((target_value/raw_value)*100, 2)
                                elif target_type == 0:
                                    if raw_value >= target_value[0] and raw_value <= target_value[1]:
                                        degree_of_realization=100
                                    else:
                                        degree_of_realization=0

                                score=round((weight*degree_of_realization)/100, 2)
                                indicator_data_dict[system_name][region][request_indicator][request_timepoint][request_time]["degree_of_realization"]=degree_of_realization
                                indicator_data_dict[system_name][region][request_indicator][request_timepoint][request_time]["score"]=score

                                # 体系数据, 将score和(degree_of_realization, weith)追加进list
                                key=(system_name, region, request_timepoint, request_time)
                                if key not in system_data_dict:
                                    system_data_dict[key]={
                                            "score":[score, ], 
                                            "degree_of_realization":[(degree_of_realization, weight), ]
                                            }
                                else:
                                    system_data_dict[key]["score"].append(score)
                                    system_data_dict[key]["degree_of_realization"].append((degree_of_realization, weight))

    # 计算体系数据的score, degree_of_realiztion , weight
    for i in system_data_dict:
        system_data_dict[i]["score"]=round(sum(system_data_dict[i]["score"]), 2)
        weight_sum=0
        temp_value=0
        for j in system_data_dict[i]["degree_of_realization"]:
            temp_value=temp_value+(j[0]*j[1])
            weight_sum=weight_sum+j[1]
        system_data_dict[i]["degree_of_realization"]=(round(temp_value/weight_sum, 2), weight_sum)

    # 将体系数据的socre和degree_of_realiztion追加进总体dict
    total_data_dict={}
    for i in system_data_dict:
        key=(i[1], i[2], i[3])
        if key not in total_data_dict:
            total_data_dict[key]={
                    "score":[system_data_dict[i]["score"], ], 
                    "degree_of_realization":[system_data_dict[i]["degree_of_realization"], ]
                    }
        else:
            total_data_dict[key]["score"].append(system_data_dict[i]["score"])
            total_data_dict[key]["degree_of_realization"].append(system_data_dict[i]["degree_of_realization"])

    # 计算总体数据的score和degree_of_realiztion
    for i in total_data_dict:
        total_data_dict[i]["score"]=round(sum(total_data_dict[i]["score"]), 2)
        weight_sum=0
        temp_value=0
        for j in total_data_dict[i]["degree_of_realization"]:
            temp_value=temp_value+(j[0]*j[1])
            weight_sum=weight_sum+j[1]
        total_data_dict[i]["degree_of_realization"]=round(temp_value/weight_sum, 2)

    return indicator_data_dict, system_data_dict, total_data_dict

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
                        "time1":{
                            "target": {
                                "type": N,                  //目标值类型, 1: 大于value, -1: 小于value, 0: 在value之间
                                "value": N/[min, max]       //当type为1或-1时, 值为N; 当type为0时, 值为区间[min, max]
                            },                    
                            "weight":N                       //指标权重
                        }, 
                        "time2":{}
                    }, 
                    "time_point2":{}
                }, 
                "indicator2":{}
            }
            "system2":{
            }
        }
    }
    """

    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    data_json=sys.argv[1]
    arg_dict=json.loads(data_json)
    #with open("./data_target.json", "r", encoding="utf8") as f:
    #    arg_dict=json.load(f)

    data=arg_dict.get("data")
    request=arg_dict.get("request")
    indicator_data_dict, system_data_dict, total_data_dict=target_monitoring_mode(data, request)
    
    # 合并体系, 分类, 总体的数据
    result={"result":[]}
    for system in indicator_data_dict:
        for region in indicator_data_dict[system]:
            for indicator in indicator_data_dict[system][region]:
                for timepoint in indicator_data_dict[system][region][indicator]:
                    for time in indicator_data_dict[system][region][indicator][timepoint]:
                        key=(system, region, indicator, timepoint, time)
                        for system_key in system_data_dict:
                            if set(system_key) < set(key):
                               system_score=system_data_dict[system_key]["score"]
                               system_degree_of_relization=system_data_dict[system_key]["degree_of_realization"][0]
                               for total_key in total_data_dict:
                                   if set(total_key) < set(key):
                                       all_score=total_data_dict[total_key]["score"]
                                       all_degree_of_relization=total_data_dict[total_key]["degree_of_realization"]
                                       result["result"].append(
                                               {
                                                   "体系": system, 
                                                   "地区": region, 
                                                   "指标": indicator, 
                                                   "时点": timepoint, 
                                                   "时间": time, 
                                                   "单项得分": indicator_data_dict[system][region][indicator][timepoint][time]["score"], 
                                                   "单项实现程度": indicator_data_dict[system][region][indicator][timepoint][time]["degree_of_realization"], 
                                                   "分类得分": system_score, 
                                                   "分类实现程度": system_degree_of_relization, 
                                                   "总体得分": all_score, 
                                                   "总体实现程度": all_degree_of_relization
                                           }
                                               )
    print(json.dumps(result, ensure_ascii=False))
    
if __name__ == "__main__":
    """
    地区-->指标-->时点(两个)--》变动度 --》发展总指数

    地区-->指标-->时点--》水平指数(临时值) --》水平指数
    """
    main()
