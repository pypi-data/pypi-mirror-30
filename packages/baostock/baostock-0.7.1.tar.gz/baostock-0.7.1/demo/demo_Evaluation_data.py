import baostock as bs
import pandas as pd

# 登陆系统
lg = bs.login(user_id="anonymous", password="123456")
# 显示登陆返回信息
print('login respond error_code:'+lg.error_code)
print('login respond  error_msg:'+lg.error_msg)

# 查询季频估值指标盈利能力
profit_list = []
rs_profit = bs.query_profit_data(code="sh.600000", year=2017, quarter=2)
while (rs_profit.error_code == '0') & rs_profit.next():
    profit_list.append(rs_profit.get_row_data())
result_profit = pd.DataFrame(profit_list, columns=rs_profit.fields)
# 打印输出
print(result_profit)
# 结果集输出到csv文件
result_profit.to_csv("D:\\profit_data.csv", encoding="gbk", index=False)

# 营运能力
operation_list = []
rs_operation = bs.query_operation_data(code="sh.600000", year=2017, quarter=2)
while (rs_operation.error_code == '0') & rs_operation.next():
    operation_list.append(rs_operation.get_row_data())
result_operation = pd.DataFrame(operation_list, columns=rs_operation.fields)
# 打印输出
print(result_operation)
# 结果集输出到csv文件
result_operation.to_csv("D:\\operation_data.csv", encoding="gbk", index=False)

# 成长能力
growth_list = []
rs_growth = bs.query_growth_data(code="sh.600000", year=2017, quarter=2)
while (rs_growth.error_code == '0') & rs_growth.next():
    growth_list.append(rs_growth.get_row_data())
result_growth = pd.DataFrame(growth_list, columns=rs_growth.fields)
# 打印输出
print(result_growth)
# 结果集输出到csv文件
result_growth.to_csv("D:\\growth_data.csv", encoding="gbk", index=False)

# 偿债能力
balance_list = []
rs_balance = bs.query_balance_data(code="sh.600000", year=2017, quarter=2)
while (rs_balance.error_code == '0') & rs_balance.next():
    balance_list.append(rs_balance.get_row_data())
result_balance = pd.DataFrame(balance_list, columns=rs_balance.fields)
# 打印输出
print(result_balance)
# 结果集输出到csv文件
result_balance.to_csv("D:\\balance_data.csv", encoding="gbk", index=False)

# 季频现金流量
cash_flow_list = []
rs_cash_flow = bs.query_cash_flow_data(code="sh.600000", year=2017, quarter=2)
while (rs_cash_flow.error_code == '0') & rs_cash_flow.next():
    cash_flow_list.append(rs_cash_flow.get_row_data())
result_cash_flow = pd.DataFrame(cash_flow_list, columns=rs_cash_flow.fields)
# 打印输出
print(result_cash_flow)
# 结果集输出到csv文件
result_cash_flow.to_csv("D:\\cash_flow_data.csv", encoding="gbk", index=False)

# 登出系统
bs.logout()
