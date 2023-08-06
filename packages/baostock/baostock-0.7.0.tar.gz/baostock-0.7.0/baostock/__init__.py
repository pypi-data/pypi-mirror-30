# -*- coding:utf-8 -*-
"""
发布方法
@author: baostock.com
@group : baostock.com
@contact: baostock@163.com
"""
import baostock.common.contants as cons
__version__ = cons.BAOSTOCK_CLIENT_VERSION
__author__ = cons.BAOSTOCK_AUTHOR

# login/logout
from baostock.login.loginout import (login, logout)

# history data
from baostock.security.history import (query_history_k_data)

# evaluation data
from baostock.evaluation.season_index import (query_dividend_data, query_adjust_factor,
                                              query_profit_data, query_operation_data,
                                              query_growth_data, query_dupont_data,
                                              query_balance_data, query_cash_flow_data)

# corporate performance
from baostock.corpreport.corp_performance import (query_performance_express_report, query_forecast_report)
