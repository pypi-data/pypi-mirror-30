import baostock as bs
import pandas as pd

#### 登陆系统 ####
lg = bs.login(user_id="anonymous", password="123456")
# 显示登陆返回信息
print('login respond error_code:'+lg.error_code)
print('login respond  error_msg:'+lg.error_msg)

#### 查询除权除息信息####
# 查询2015年除权除息信息
rs_dividend_2015 = bs.query_dividend_data(code="sh.600000", year="2015", yearType="report")
result_dividend = pd.DataFrame(
    columns=["code", "dividPreNoticeDate", "dividAgmPumDate", "dividPlanAnnounceDate", "dividPlanDate",
             "dividRegistDate", "dividOperateDate", "dividPayDate", "dividStockMarketDate",
             "dividCashPsBeforeTax", "dividCashPsAfterTax", "dividStocksPs",
             "dividCashStock", "dividReserveToStockPs"])
while (rs_dividend_2015.error_code == '0') & rs_dividend_2015.next():
    result_dividend = result_dividend.append(rs_dividend_2015.get_row_data(), ignore_index=True)

# 查询2016年除权除息信息
rs_dividend_2016 = bs.query_dividend_data(code="sh.600000", year="2016", yearType="report")
while (rs_dividend_2016.error_code == '0') & rs_dividend_2016.next():
    result_dividend = result_dividend.append(rs_dividend_2016.get_row_data(), ignore_index=True)

# 查询2017年除权除息信息
rs_dividend_2017 = bs.query_dividend_data(code="sh.600000", year="2017", yearType="report")
while (rs_dividend_2017.error_code == '0') & rs_dividend_2017.next():
    result_dividend = result_dividend.append(rs_dividend_2017.get_row_data(), ignore_index=True)
    
# 打印输出
print(result_dividend)

#### 结果集输出到csv文件 ####   
result_dividend.to_csv("D:\\history_Dividend_data.csv", encoding="gbk",index=False)

#### 登出系统 ####
bs.logout()