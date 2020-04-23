#!/usr/bin/env python
# *-* coding:utf8 *-*
# sky

"""
分析评价A模型
"""

import json

def mode_a_bak(data, indicators, weight, system_name):
    """
    地区:
    时点:
    时间:
    体系1:
    """

    median_list=[]
    current_column=[]
    for region in data.keys():
        for indicator in indicators:
            for indicator_data in data[region].keys():
                if indicator == indicator_data:
                    for time_point in data[region][indicator].keys():
                        for timee in data[region][indicator][time_point].keys():
                            current_value=data[region][indicator][time_point][timee]
                            for i in data.keys():
                                current_column.append(data[i][indicator][time_point][timee])

                            max_column_value=max(current_column)
                            min_column_value=min(current_column)
                            difference=max_column_value-min_column_value
                            if difference==0:
                                median=0
                            else:
                                median=((current_value-min_column_value) * weight[0] / (max_column_value-min_column_value) ) + weight[1]

                            median_all=[(region, time_point, timee), [median]]

                            median_list.append(median_all)
    median_dict={}
    for i in median_list:
        if i[0] not in median_dict:
            median_dict[i[0]]=i[1]
        else:
            median_dict[i[0]].extend(i[1])

    result_list=[]
    for i in median_dict.keys():
        values=median_dict[i]
        result_dict={
                "地区": i[0], 
                "时点": i[1], 
                "时间": i[2], 
                system_name: round(sum(values)/len(values), 2)
                }
        result_list.append(result_dict)

    return result_list

def mode_a(data, request, weight):
    """
    地区:
    时点:
    时间:
    体系1:
    """

    median_list=[]
    current_column=[]
    for system_name in request:
        indicators=request[system_name]
        #print(indicators)
        for region in data:
            for indicator in indicators["indicator"]:
                for indicator_data in data[region]:
                    if indicator == indicator_data:
                        for time_point in data[region][indicator].keys():
                            for timee in data[region][indicator][time_point].keys():
                                current_value=data[region][indicator][time_point][timee]
                                for i in data.keys():
                                    current_column.append(data[i][indicator][time_point][timee])

                                max_column_value=max(current_column)
                                min_column_value=min(current_column)
                                difference=max_column_value-min_column_value
                                if difference==0:
                                    median=0
                                else:
                                    median=((current_value-min_column_value) * weight[0] / (max_column_value-min_column_value) ) + weight[1]

                                median_all=[
                                        (region, time_point, timee), 
                                        [
                                            (system_name, [median]) 
                                        ]
                                    ]

                                median_list.append(median_all)
    #print(median_list)
    median_dict={}
    for i in median_list:
        if i[0] not in median_dict:
            median_dict[i[0]]=i[1]
        else:
            median_dict[i[0]].extend(i[1])

    result_list=[]
    for i in median_dict:
        values=median_dict[i]
        system_dict={}
        for j in values:
            if j[0] not in system_dict:
                system_dict[j[0]]=j[1]
            else:
                system_dict[j[0]].extend(j[1])

        for m in system_dict:
            result=system_dict[m]
            system_dict[m]=round(sum(result)/len(result), 2)

        system_dict["地区"]=i[0]
        system_dict["时点"]=i[1]
        system_dict["时间"]=i[2]

        result_list.append(system_dict)

    return result_list
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
                "indicator":["indicator1", "indicator2", ...]
            }, 
            "system2":{}
        }
    """
    
    with open("./data.json", "r") as f:
        arg_dict=json.load(f)
    #print(arg_dict) 

    weight=[20, 80]

    data=arg_dict.get("data")
    request=arg_dict.get("request")

    """
    result_list=[]
    for i in request.keys():
        indicators=request.get(i).get("indicator")
        result_dict=mode_a(data, indicators, weight, i)
        result_dict=mode_a(data, indicators, weight, i)
        result_list.append(result_dict)

    print(result_list)
    exit()
    """
    #result_list=[]
    result_dict=mode_a(data, request, weight)
    #result_list.append(result_dict)

    print(json.dumps(result_dict, ensure_ascii=False))
    
if __name__ == "__main__":
    main()
