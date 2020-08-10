#!/usr/bin/env python
# *-* coding:utf8 *-*
# Date: 2020年 08月 04日 星期二 11:19:16 CST
# sky

from statsmodels.tsa.holtwinters import ExponentialSmoothing, SimpleExpSmoothing, Holt
from dateutil.relativedelta import relativedelta
import pandas as pd
import sys, json, datetime, io

def prediction(original_data, raw_data, forecasted_date_length, algorithm_name, periods, return_type):
    # tran data(int, str) to float
    for index, item in enumerate(original_data):
        if item=="":
            pass
        else:
            original_data[index]=float(item)

    forecasted_length=forecasted_date_length

    if algorithm_name=="ses":
        fit=ses(original_data)
    elif algorithm_name=="halt":
        fit=halt(original_data)
    elif algorithm_name=="halt_winters":
        fit=halt_winters(original_data, periods)

    if return_type == 0:
        indicator_value=list(fit.forecast(forecasted_length))
    elif return_type == 1:
        indicator_value=raw_data+list(fit.forecast(forecasted_length))
    #print("预测后的数据:\n", indicator_value)

    # tran data(%.Nf) to %.2f
    for index, item in enumerate(indicator_value):
        if item is None:
            indicator_value[index]=item
        else:
            indicator_value[index]=float("%.2f" % item)

    return indicator_value

def data_sorting(data_dict, data_type):
    sorted_data_dict={}
    if data_type=="Q":
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

"""
def trans_time_cap(time_list):
    for index, item in enumerate(time_list):
        quarter_map={
                "03": "一", 
                "06": "二", 
                "09": "三", 
                "12": "四"
                }
        quarter=item[5:7]
        quarter=quarter_map[quarter]

        time_list[index]=f"{item[0:5]}{quarter}{item[7:]}"

    return time_list
"""
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
    #quarter_map={
    #        "一": "01", 
    #        "二": "04", 
    #        "三": "07", 
    #        "四": "10"
    #        }
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

    if date_format=="Y":
        begin_date=datetime.datetime.strptime(begin_date_str, "%Y年")
        end_date=datetime.datetime.strptime(begin_date_str, "%Y年")+relativedelta(years=forecasted_length)
        date_list = [x.strftime('%Y年') for x in list(pd.date_range(start=begin_date, end=end_date, freq='Y'))]
    elif date_format=="Q":
        begin_date_str=trans_time_low(begin_date_str)
        begin_date=datetime.datetime.strptime(begin_date_str, "%Y年%m季度")
        end_date=datetime.datetime.strptime(begin_date_str, "%Y年%m季度")+relativedelta(months=3*forecasted_length)
        low_date_list = [x.strftime('%Y年%m季度') for x in list(pd.date_range(start="%s" % begin_date, end="%s" % end_date, freq='Q'))]
        date_list=[]
        for i in low_date_list:
            date_list.append(trans_time_cap(i))
    elif date_format=="M":
        begin_date=datetime.datetime.strptime(begin_date_str, "%Y年%m月")
        end_date=datetime.datetime.strptime(begin_date_str, "%Y年%m月")+relativedelta(months=forecasted_length)
        date_list = [x.strftime('%Y年%m月') for x in list(pd.date_range(start="%s" % begin_date, end="%s" % end_date, freq='M'))]
    date_list.remove(date_list[0])          # 去掉第一个时间(list中已有)
    return date_list, len(date_list)

def ses(data):
    """ ses(简单指数平滑)预测算法, 用于没有明显趋势或季节规律的数据 """

    fit=SimpleExpSmoothing(data).fit(optimized=True)
    #fit=SimpleExpSmoothing(data).fit(smoothing_level=0.6, optimized=False)
    return fit

def halt(data):
    """ halt(二次指数平滑)预测算法, 用于有明显趋势的数据 """

    data_src=pd.Series(data)
    fit=Holt(data, damped=True).fit(smoothing_level=0.8, smoothing_slope=0.2)
    return fit

def halt_winters(data, periods):
    """ halt_winters(三次指数平滑)预测算法, 用于具有趋势和季节性的数据 """

    data_src=pd.Series(data)
    fit=ExponentialSmoothing(data_src, seasonal_periods=periods, trend='add', seasonal='add', damped=True).fit()
    return fit

def get_data(data, request):
    """
        从接口中获取原始数据
    """
    original_data_list=[]
    for region in data:
        for indicator in data.get(region):
            for timepoint in data[region][indicator]:
                tag={"地区": region, "指标": indicator, "时点": timepoint} 
                original_data_dict=data[region][indicator][timepoint]
                original_data_list.append({"tag": tag, "original_data_dict": original_data_dict})

    return original_data_list

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
            "name": "halt",                  # 指定算法: "halt_winters"|"halt"|"ses"
            "periods": N                               # 仅当指定为halt_winters时使用, 预测周期
            "forecasted_length": N                     # 预测长度
            "time_unit": "Y"                           # 预测时间的单位. M: 月, Q: 季度 Y: 年
            "return_type": 0                           # 0: 仅返回未来预测值, 1: 返回原始值和未来预测值
        }
    """
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    data_json=sys.argv[1]
    arg_dict=json.loads(data_json)
    #with open("./data_pre_year.json",  "r", encoding="utf8") as f:
    #    arg_dict=json.load(f)
    
    data=arg_dict.get("data")
    request=arg_dict.get("request")
    original_data_list=get_data(data, request)

    result=[]
    for i in original_data_list:
        tag=i.get("tag")
        original_data_dict=i.get("original_data_dict")
        #original_data_all=sorted(original_data_dict.items(), key=lambda item:item[0])
        original_data_all=data_sorting(original_data_dict, request.get("time_unit"))

        original_date, original_data, raw_data=[], [], []
        for index, item in enumerate(original_data_all):
            raw_data.append(item[1])
            # 若值为空, 则将其前一个值赋给当前值
            if item[1]==None:
                number=original_data_all[index-1][1]
            else:
                number=item[1]

            original_date.append(item[0])
            original_data.append(number)

        algorithm=request
        forecasted_date, forecasted_date_length=forecasted_date_fun(algorithm.get("time_unit"), original_date[-1], algorithm.get("forecasted_length")+1)
        forecasted_data=prediction(original_data, raw_data, forecasted_date_length, algorithm.get("name"), algorithm.get("periods"), algorithm.get("return_type"))

        # 获取预测时间值
        if algorithm.get("return_type")==1:
            original_date.extend(forecasted_date)
            forecasted_date=original_date

        # 合并为字典
        prediction_data_all=dict(zip(forecasted_date, forecasted_data))
        
        # 加入预测的时间和值
        single_list=[]
        for j in prediction_data_all:
            single_tag=tag.copy()
            single_tag["时间"]=j
            #single_tag["值"]=prediction_data_all[j]
            single_tag[tag.get("指标")]=prediction_data_all[j]
            single_tag.pop("指标")
            single_list.append(single_tag)
        result.extend(single_list)

    # 合并相同的 地区, 时间, 时点的值
    temp_dict={}
    for i in result:
        key=f"{i['地区']}{i['时间']}{i['时点']}"
        if key not in temp_dict:
            temp_dict[key]=i
        else:
            temp_dict[key].update(i)

    result=[]
    for i in temp_dict:
        result.append(temp_dict[i])
    
    print(json.dumps({"result":result}, ensure_ascii=False))

if __name__ == "__main__":
    #print(datetime.datetime.now().strftime('%Y_%m_%d_%H:%M:%S.%f'))
    main()
    #print(datetime.datetime.now().strftime('%Y_%m_%d_%H:%M:%S.%f'))
   
