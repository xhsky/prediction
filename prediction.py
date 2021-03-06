#!/usr/bin/env python
# *-* coding:utf8 *-*
# Date: 2020年 03月 19日 星期四 17:41:04 CST
# sky

from statsmodels.tsa.holtwinters import ExponentialSmoothing, SimpleExpSmoothing, Holt
from dateutil.relativedelta import relativedelta
import pandas as pd
import sys, json, datetime

def prediction(original_data, forecasted_date_length, algorithm_name, periods, return_type):

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
        indicator_value=list(fit.fittedvalues)+list(fit.forecast(forecasted_length))
    #print("预测后的数据:\n", indicator_value)

    # tran data(%.Nf) to %.2f
    for index, item in enumerate(indicator_value):
        indicator_value[index]=float("%.2f" % item)

    return indicator_value

def forecasted_date_fun(date_format, begin_date, end_date):
    """返回预测的时间列表, 不包含原始时间.
    """

    if date_format=="Y":
        begin_date=datetime.datetime.strptime(begin_date, "%Y")
        end_date=datetime.datetime.strptime(end_date, "%Y")+relativedelta(years=1)
        date_list = [x.strftime('%Y') for x in list(pd.date_range(start=begin_date, end=end_date, freq='Y'))]
    elif date_format=="Q":
        begin_date=datetime.datetime.strptime(begin_date, "%Y%m")
        end_date=datetime.datetime.strptime(end_date, "%Y%m")+relativedelta(months=3)
        date_list = [x.strftime('%Y%m') for x in list(pd.date_range(start="%s" % begin_date, end="%s" % end_date, freq='Q'))]
    elif date_format=="M":
        begin_date=datetime.datetime.strptime(begin_date, "%Y%m")
        end_date=datetime.datetime.strptime(end_date, "%Y%m")+relativedelta(months=1)
        date_list = [x.strftime('%Y%m') for x in list(pd.date_range(start="%s" % begin_date, end="%s" % end_date, freq='M'))]
    date_list.remove(date_list[0])          # 去掉第一个时间(list中已有)
    return date_list, len(date_list)

def ses(data):
    """ ses预测算法, 用于没有明显趋势或季节规律的数据 """

    fit=SimpleExpSmoothing(data).fit(optimized=True)
    #fit=SimpleExpSmoothing(data).fit(smoothing_level=0.6, optimized=False)
    return fit

def halt(data):
    """ halt预测算法, 用于有明显趋势的数据 """

    data_src=pd.Series(data)
    fit=Holt(data, damped=True).fit(smoothing_level=0.8, smoothing_slope=0.2)
    return fit

def halt_winters(data, periods):
    """ halt_winters预测算法, 用于具有趋势和季节性的数据 """

    data_src=pd.Series(data)
    fit=ExponentialSmoothing(data_src, seasonal_periods=periods, trend='add', seasonal='add', damped=True).fit()
    return fit

def main():
    """
    data_json={
        "data":{
            "201002":200,  
            "201003":130, 
            "201004":170, 
            "201005":800, 
            "201006":"", 
            "201007":800, 
            "201001":100
            }, 
        "algorithm": "halt",             # 指定算法: "halt_winters"|"halt"|"ses"
        "periods": N                     # 仅当指定为halt_winters时使用, 预测周期
        "forecasted_time": "201101"      # 预测时间
        "time_unit": "Y"                 # 预测时间的单位. M: 月, Q: 季度 Y: 年
        "return_type": 0                 # 0: 仅返回未来预测值, 1: 返回原始预测值和未来预测值
        }
    """
    #data_json='{\"params\":{\"data\":{\"201403\":\"1520.33\", \"201406\":\"1727.32\", \"201409\":\"1820.25\", \"201412\":\"2041.84\", \"201503\":\"1709.73\", \"201506\":\"1994.27\", \"201509\":\"1965.11\", \"201512\":\"2229.24\", \"201603\":\"1852.65\", \"201606\":\"2213.39\", \"201609\":\"2130.08\", \"201612\":\"2535.72\", \"201703\":\"2122.83\", \"201706\":\"2412.72\", \"201709\":\"2371.81\", \"201712\":\"2744.03\", \"201803\":\"2388.21\", \"201806\":\"2626.97\", \"201809\":\"2494.28\", \"201812\":\"2952.13\", \"201903\":\"2506.56\", \"201906\":\"2720.74\"}, \"format\":\"quarter\", \"goal_start_time\": \"201901\", \"algorithm\":\"all\", \"target_value\": 20000, \"forecasted_time\":\"201912\"}}'
    #data_json='{\"params\":{\"data\":{\"201402\":\"184.92\", \"201403\":\"226.76\", \"201404\":\"301.92\", \"201405\":\"385.47\", \"201406\":\"437.88\", \"201407\":\"500.07\", \"201408\":\"538.23\", \"201409\":\"572.33\", \"201410\":\"614.48\", \"201411\":\"647.38\", \"201412\":\"684.51\", \"201502\":\"182.47\", \"201503\":\"237.55\", \"201504\":\"340.9\", \"201505\":\"432.09\", \"201506\":\"492.13\", \"201507\":\"571.55\", \"201508\":\"614.48\", \"201509\":\"667.62\", \"201510\":\"702.55\", \"201511\":\"744.28\", \"201512\":\"788.19\", \"201602\":\"231.94\", \"201603\":\"348\", \"201604\":\"472.44\", \"201605\":\"584.31\", \"201606\":\"662.5\", \"201607\":\"750.03\", \"201608\":\"801.51\", \"201609\":\"845.57\", \"201610\":\"899.03\", \"201611\":\"942.23\", \"201612\":\"963.75\", \"201702\":\"232.74\", \"201703\":\"339.07\", \"201704\":\"444.87\", \"201705\":\"562.78\", \"201706\":\"679.58\", \"201707\":\"774.89\", \"201708\":\"823.66\", \"201709\":\"873.61\", \"201710\":\"926.94\", \"201711\":\"968.11\", \"201712\":\"996.26\", \"201802\":\"242.44\", \"201803\":\"344.81\", \"201804\":\"452.89\", \"201805\":\"586.3\", \"201806\":\"702.54\", \"201807\":\"809.73\", \"201808\":\"868.09\", \"201809\":\"919.89\", \"201810\":\"985.56\", \"201811\":\"1029.31\", \"201812\":\"1066.2\", \"201902\":\"253.28\", \"201903\":\"374.22\", \"201904\":\"480.99\", \"201905\":\"604.06\", \"201906\":\"709.68\"}, \"format\":\"month\", \"algorithm\":\"all\", \"special\":\"ljz\", \"target_value\":12000, \"forecasted_time\":\"201912\", \"goal_start_time\":\"201901\"}}'
    #data_json='{\"params\":{\"data\":{\"1990\":\"14.15\", \"1991\":\"28.95\", \"1992\":\"75\", \"1993\":\"164.56\", \"1994\":\"261.13\", \"1995\":\"285.07\", \"1996\":\"395.04\", \"1997\":\"504.36\", \"1998\":\"583.22\", \"1999\":\"438.2\", \"2000\":\"351.06\", \"2001\":\"416.18\", \"2002\":\"587.2\", \"2003\":\"602.16\", \"2004\":\"651.94\", \"2005\":\"693.61\", \"2006\":\"659.97\", \"2007\":\"784.1\", \"2008\":\"872.68\", \"2009\":\"1420.77\", \"2010\":\"1432.3\", \"2011\":\"1435.39\", \"2012\":\"1454.98\", \"2013\":\"1679.22\", \"2014\":\"1765.73\", \"2015\":\"1772.94\", \"2016\":\"1825.74\", \"2017\":\"1903.7\", \"2018\":\"2003.09\"}, \"format\":\"year\", \"algorithm\":\"all\", \"target_value\":16000, \"special\": \"gdzctz\", \"forecasted_time\":\"2025\"}}'
    #data_json='{\"params\":{\"data\":{\"1990\":\"60.24\", \"1991\":\"71.54\", \"1992\":\"101.49\", \"1993\":\"164\", \"1994\":\"291.2\", \"1995\":\"414.65\", \"1996\":\"496.47\", \"1997\":\"608.22\", \"1998\":\"704.27\", \"1999\":\"801.36\", \"2000\":\"923.51\", \"2001\":\"1087.53\", \"2002\":\"1244\", \"2003\":\"1510.32\", \"2004\":\"1850.13\", \"2005\":\"2108.79\", \"2006\":\"2365.33\", \"2007\":\"2793.39\", \"2008\":\"3150.99\", \"2009\":\"4001.39\", \"2010\":\"4707.52\", \"2011\":\"5484.35\", \"2012\":\"5929.91\", \"2013\":\"6448.68\", \"2014\":\"7109.74\", \"2015\":\"7898.35\", \"2016\":\"8731.84\", \"2017\":\"9651.39\", \"2018\":\"10461.59\"}, \"format\":\"year\", \"algorithm\":\"all\", \"special\":\"tb\", \"target_value\":20000, \"forecasted_time\":\"2025\"}}'
    #data_json='{\"params\":{\"data\":{\"1990\":\"60.24\", \"1991\":\"71.54\", \"1992\":\"101.49\", \"1993\":\"164\", \"1994\":\"291.2\", \"1995\":\"414.65\", \"1996\":\"496.47\", \"1997\":\"608.22\", \"1998\":\"704.27\", \"1999\":\"801.36\", \"2000\":\"923.51\", \"2001\":\"1087.53\", \"2002\":\"1244\", \"2003\":\"1510.32\", \"2004\":\"1850.13\", \"2005\":\"2108.79\", \"2006\":\"2365.33\", \"2007\":\"2793.39\", \"2008\":\"3150.99\", \"2009\":\"4001.39\", \"2010\":\"4707.52\", \"2011\":\"5484.35\", \"2012\":\"5929.91\", \"2013\":\"6448.68\", \"2014\":\"7109.74\", \"2015\":\"7898.35\", \"2016\":\"8731.84\", \"2017\":\"9651.39\", \"2018\":\"10461.59\"}, \"format\":\"year\", \"algorithm\":\"all\", \"special\":\"\", \"two_trillion\":\"1\", \"target_value\":20000, \"forecasted_time\":\"2025\"}}'
    #data_json='{\"params\":{\"data\":{\"2000\":\"923.51\", \"2001\":\"1087.53\", \"2002\":\"1244\", \"2003\":\"1510.32\", \"2004\":\"1850.13\", \"2005\":\"2108.79\", \"2006\":\"2365.33\", \"2007\":\"2793.39\", \"2008\":\"3150.99\", \"2009\":\"4001.39\", \"2010\":\"4707.52\", \"2011\":\"5484.35\", \"2012\":\"5929.91\", \"2013\":\"6448.68\", \"2014\":\"7109.74\", \"2015\":\"7898.35\", \"2016\":\"8731.84\", \"2017\":\"9651.39\", \"2018\":11767.749000000002}, \"format\":\"year\", \"algorithm\":\"all\", \"special\":\"", \"target_value\":20000, \"forecasted_time\":\"2025\", \"special\":\"gdzctz\", \"two_trillion\":{\"level_ratio\":\"0.6\", \"trend_ratio\":\"0.55\"}}}'
    #data_json='{\"params\":{\"data\":{\"201401\":\"727.21\", \"201402\":\"595.96\", \"201403\":\"803.94\", \"201404\":\"751.58\", \"201405\":\"752.73\", \"201406\":\"779.77\", \"201407\":\"751.15\", \"201408\":\"703.73\", \"201409\":\"807.94\", \"201410\":\"760.59\", \"201411\":\"800.36\", \"201412\":\"899.03\", \"201501\":\"815.97\", \"201502\":\"609.61\", \"201503\":\"751.56\", \"201504\":\"723.52\", \"201505\":\"752.56\", \"201506\":\"766.17\", \"201507\":\"736.22\", \"201508\":\"700.4\", \"201509\":\"854.28\", \"201510\":\"831.12\", \"201511\":\"795.52\", \"201512\":\"803.18\", \"201601\":\"740.07\", \"201602\":\"520.78\", \"201603\":\"724.78\", \"201604\":\"680.14\", \"201605\":\"675.27\", \"201606\":\"691.28\", \"201607\":\"685.51\", \"201608\":\"806.26\", \"201609\":\"903.86\", \"201610\":\"924.86\", \"201611\":\"929.82\", \"201612\":\"961.04\", \"201701\":\"766.6\", \"201702\":\"684.14\", \"201703\":\"825.75\", \"201704\":\"752.99\", \"201705\":\"803.83\", \"201706\":\"827.14\", \"201707\":\"849.32\", \"201708\":\"866.56\", \"201709\":\"970.49\", \"201710\":\"922.52\", \"201711\":\"928.04\", \"201712\":\"922.83\", \"201801\":\"957.56\", \"201802\":\"629.45\", \"201803\":\"838.99\", \"201804\":\"838.87\", \"201805\":\"811.81\", \"201806\":\"796.98\", \"201807\":\"831.13\", \"201808\":\"864.6\", \"201809\":\"889.76\", \"201810\":\"941.5\", \"201811\":\"955.26\", \"201812\":\"872.94\", \"201901\":\"847.69\", \"201902\":\"586.36\", \"201903\":\"785.49\", \"201904\":\"744.19\", \"201905\":\"737.28\", \"201906\":\"778.08\", \"201907\":\"727.27\"}, \"format\":\"month\", \"algorithm\":\"all\", \"target_value\":10000, \"forecasted_time\":\"201912\", \"goal_start_time\":\"201901\", \"special\":\"ljz\"}}'

    #data_json='{\"params\":{\"data\":{\"2000\":\"923.51\", \"2001\":\"1087.53\", \"2002\":\"1244\", \"2003\":\"1510.32\", \"2004\":\"1850.13\", \"2005\":\"2108.79\", \"2006\":\"2365.33\", \"2007\":\"2793.39\", \"2008\":\"3150.99\", \"2009\":\"4001.39\", \"2010\":\"4707.52\", \"2011\":\"5484.35\", \"2012\":\"5929.91\", \"2013\":\"6448.68\", \"2014\":\"7109.74\", \"2015\":\"7898.35\", \"2016\":\"8731.84\", \"2017\":\"9651.39\", \"2018\":11767.749000000002}, \"format\":\"year\", \"algorithm\":\"all\", \"target_value\":20000, \"forecasted_time\":\"2025\", \"two_trillion\":{\"level_ratio\":\"0.6\", \"trend_ratio\":\"0.55\"}}}'
    data_json=sys.argv[1]
    data_dict=json.loads(data_json)
    #with open("data.json",  "r") as f:
    #    data_dict=json.load(f)
    #data_json='{\"params\":{\"data\":{\"201403\":\"1520.33\", \"201406\":\"3247.65\", \"201409\":\"5067.9\", \"201412\":\"7109.74\", \"201503\":\"1709.73\", \"201506\":\"3704\", \"201509\":\"5669.11\", \"201512\":\"7898.35\", \"201603\":\"1852.65\", \"201606\":\"4066.04\", \"201609\":\"6196.12\", \"201612\":\"8731.84\", \"201703\":\"2122.83\", \"201706\":\"4535.55\", \"201709\":\"6907.36\", \"201712\":\"9651.39\", \"201803\":\"2388.21\", \"201806\":\"5015.18\", \"201809\":\"7509.46\", \"201812\":\"10461.59\", \"201903\":\"2506.56\", \"201906\":\"5227.3\"}, \"format\":\"quarter\", \"algorithm\":\"all\", \"target_value\":120, \"forecasted_time\":\"201912\", \"goal_start_time\":\"201903\", \"special\":\"ljz\"}}'
    #print(type(data_json))
    
    #print("初始参数", data_dict)

    original_data_all=sorted(data_dict["data"].items(), key=lambda item:item[0])
    #print("排序后的数据\n", original_data_all)

    original_date, original_data=[], []
    for i in original_data_all:
        original_date.append(i[0])
        original_data.append(i[1])
    #print("时间:", original_date)
    #print("数据:", original_data)
    print(data_dict)

    forecasted_date, forecasted_date_length=forecasted_date_fun(data_dict["time_unit"], original_date[-1], data_dict["forecasted_time"])

    forecasted_data=prediction(original_data, forecasted_date_length, data_dict["algorithm"], data_dict.get("periods"), data_dict["return_type"])

    if data_dict["return_type"]==1:
        original_date.extend(forecasted_date)
        forecasted_date=original_date


    # 合并为字典
    prediction_data_all={"predicted_data": dict(zip(forecasted_date, forecasted_data))}
    print(json.dumps(prediction_data_all))

if __name__ == "__main__":
    #print(datetime.datetime.now().strftime('%Y_%m_%d_%H:%M:%S.%f'))
    main()
    #print(datetime.datetime.now().strftime('%Y_%m_%d_%H:%M:%S.%f'))
   
