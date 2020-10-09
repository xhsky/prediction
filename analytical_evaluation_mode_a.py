#!/usr/bin/env python
# *-* coding:utf8 *-*
# sky

"""
分析评价A模型
"""

import json
import sys, io

def mode_a(data, request, weight):
    """
    """

    median_list=[]
    for system_name in request:
        indicators=request[system_name]
        #print(indicators)
        for region in data:
            for indicator in indicators["indicator"]:
                for indicator_data in data[region]:
                    if indicator.get("indicator") == indicator_data:
                        for timepoint in data[region][indicator_data]:
                            if timepoint == indicator.get("timepoint"):
                                for timee in data[region][indicator_data][timepoint]:
                                    current_column=[]
                                    current_value=data[region][indicator_data][timepoint][timee]
                                    if current_value is None:
                                        current_value=0
                                    for i in data:
                                        column_value=data[i][indicator_data][timepoint][timee] 
                                        if column_value is not None:
                                            current_column.append(column_value)
                                        else:
                                            current_column.append(0)

                                    max_column_value=max(current_column)
                                    min_column_value=min(current_column)
                                    difference=max_column_value-min_column_value
                                    if difference==0:
                                        median=0
                                    else:
                                        median=((current_value-min_column_value) * weight[0] / (max_column_value-min_column_value) ) + weight[1]

                                    median_all=[
                                            (region, indicator_data, timepoint, timee), 
                                            [
                                                (system_name, [round(median, 2)]) 
                                            ]
                                        ]

                                    median_list.append(median_all)
    # 中间结果
    inter_dict={}
    for i in median_list:
        region=i[0][0]
        key=f"{i[1][0][0]}^{i[0][1]}^{i[0][3]}^{i[0][2]}"
        value=i[1][0][1][0]

        if region not in inter_dict:
            temp_dict={}
            temp_dict["地区"]=region
            temp_dict[key]=value
            inter_dict[region]=temp_dict
        else:
            inter_dict[region][key]=value

    inter_list=[]
    for i in inter_dict:
        inter_list.append(inter_dict[i])

    # 最终结果
    median_dict={}
    """
        media_dict={
            (region, indicator_data, timepoint, timee): [
                    (system, [median]), 
                    (system1, [median]), 
                    ...
                ], 
            ...
        }
    """
    for i in median_list:
        key=(i[0][0], i[0][3])
        if key not in median_dict:
            median_dict[key]=i[1]
        else:
            median_dict[key].extend(i[1])

    result_list=[]
    for i in median_dict:
        values=median_dict[i]
        system_dict={}
        """
            system_dict={
                system: [median, median1, ...], 
                system1: [median, median1, ...], 
            }
        """
        for j in values:
            if j[0] not in system_dict:
                system_dict[j[0]]=j[1]
            else:
                system_dict[j[0]].extend(j[1])

        for m in system_dict:
            result=system_dict[m]
            system_dict[m]=round(sum(result)/len(result), 2)

        system_dict["地区"]=i[0]
        system_dict["时间"]=i[1]

        result_list.append(system_dict)

    return inter_list, result_list
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
                "indicator":[
                    {"indicator": "indicator1", "timepoint":"time_point1"}, 
                    {"indicator": "indicator2", "timepoint":"time_point2"}, 
                    ...
                    ]
            }, 
            "system2":{}
        }
    """

    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    data_json=sys.argv[1]
    arg_dict=json.loads(data_json)
    #with open("./data.json", "r", encoding="utf8") as f:
    #    arg_dict=json.load(f)

    weight=[20, 80]
    data=arg_dict.get("data")
    request=arg_dict.get("request")
    inter_list, result_list=mode_a(data, request, weight)

    result_all={
            "temps": [inter_list], 
            "result": result_list
            }
    print(json.dumps(result_all, ensure_ascii=False))
    
if __name__ == "__main__":
    main()
