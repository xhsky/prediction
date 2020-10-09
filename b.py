import numpy as np
def data_polyfit(data_list, forecasted_length, polyfit_times):
    x=range(1, len(data_list)+1)
    #x=range(0, len(data_list))
    fx=np.polyfit(x, data_list, polyfit_times)
    p=np.poly1d(fx)
    new_x=range(len(data_list)+forecasted_length)
    new_y=[]
    for y in p(new_x):
        new_y.append(round(y, 4))
    return new_y

data_list=[86.78,  90.67,  91.47,  91.45,  91.14,  91.23,  91.13,  91.18,  91.3,  91.19,  91.01,  83.8,  92.17,  92.44,  93.1,  93.22,  93.81,  94.38,  94.78,  94.87,  94.62,  94.45,  95.66,  84.37 ,  88.87,  90.02,  89.91,  90.54,  91.68,  91.43]
y=data_polyfit(data_list, 10, 4)
print(f"{data_list=}")
print(f"{y}")
