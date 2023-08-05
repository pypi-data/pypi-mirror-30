import baostock as bs
import pandas as pd

#### 登陆系统 ####
lg = bs.login(user_id="anonymous", password="123456")
# 显示登陆返回信息
print('login respond error_code:'+lg.error_code)
print('login respond  error_msg:'+lg.error_msg)

#### 获取公司业绩快报 ####
rs = bs.query_performance_express_report("sh.600000", start_date="2015-01-01", end_date="2017-12-31")
print('query_performance_express_report respond error_code:'+rs.error_code)
print('query_performance_express_report respond  error_msg:'+rs.error_msg)

result_list = []
while (rs.error_code == '0') & rs.next():
    result_list.append(rs.get_row_data())
    # 分页查询，将每页信息合并在一起
result = pd.DataFrame(result_list, columns=rs.fields)
#### 结果集输出到csv文件 ####
result.to_csv("D:\\performance_express_report.csv", index=False)
print(result)


#### 获取公司业绩快报 ####
rs_forecast = bs.query_forecast_report("sh.600000", start_date="2015-01-01", end_date="2017-12-31")
print('query_forecast_reprot respond error_code:'+rs.error_code)
print('query_forecast_reprot respond  error_msg:'+rs.error_msg)
rs_forecast_list = []
while (rs.error_code == '0') & rs_forecast.next():
    # 分页查询，将每页信息合并在一起
    rs_forecast_list.append(rs_forecast.get_row_data())
result_forecast = pd.DataFrame(rs_forecast_list, columns=rs_forecast.fields)
#### 结果集输出到csv文件 ####
result_forecast.to_csv("D:\\forecast_report.csv", index=False)
print(result_forecast)


#### 登出系统 ####
bs.logout()
