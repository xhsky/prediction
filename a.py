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
    data=[86.78,  90.67,  91.47,  91.45,  91.14,  91.23,  91.13,  91.18,  91.3,  91.19,  91.01,  83.8,  92.17,  92.44,  93.1,  93.22,  93.81,  94.38,  94.78,  94.87,  94.62,  94.45,  95.66,  84.37 ,  88.87,  90.02,  89.91,  90.54,  91.68,  91.43]
    #fit=halt(data)
    fit=halt_winters(data, 10)
    indicator_value=list(fit.fittedvalues)+list(fit.forecast(5))
    print(f"{data=}")
    print(f"{indicator_value=}")



if __name__ == "__main__":
    #print(datetime.datetime.now().strftime('%Y_%m_%d_%H:%M:%S.%f'))
    main()
    #print(datetime.datetime.now().strftime('%Y_%m_%d_%H:%M:%S.%f'))
   
