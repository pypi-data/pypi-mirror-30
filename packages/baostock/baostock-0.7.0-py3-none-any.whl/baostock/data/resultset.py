# -*- coding:utf-8 -*-
"""
返回数据接口
@author: baostock.com
@group : baostock.com
@contact: baostock@163.com
"""
import baostock.common.contants as cons
import pandas as pd
import json
import zlib
import baostock.data.messageheader as msgheader
import baostock.util.socketutil as sock


class ResultData(object):
    def __init__(self):
        """初始化方法"""

        # 消息头
        self.version = cons.BAOSTOCK_CLIENT_VERSION
        self.msg_type = 0  # 消息类型
        self.msg_body_length = 0

        # 消息体
        self.method = ""  # 方法名
        self.user_id = ""  # 用户账号
        self.error_code = cons.BSERR_NO_LOGIN  # 错误代码
        self.error_msg = ""  # 错误代码

        self.cur_page_num = 1  # 当前页码
        self.per_page_count = cons.BAOSTOCK_PER_PAGE_COUNT  # 当前页条数
        self.cur_row_num = 0  # 当前页面遍历条数 V0.5.5

        self.code = ""  # 股票代码
        self.fields = []  # 指示简称 list
        self.start_date = ""  # 开始日期
        self.end_date = ""  # 结束日期
        self.frequency = ""  # 数据类型
        self.adjustflag = ""  # 复权类型
        self.data = []  # 数据值 list类型

        self.msg_body = ""  # 消息体
        self.year = ""  # 年份
        self.yearType = ""  # 年份类别
        self.quarter = ""  # 季度

        # self.request_id = 0
        # self.serial_id = 0

    def next(self):
        """ 判断是否还有后续数据
        :return: 有数据时返回True，当前页没有数据时向服务器请求下一页；没有数据时返回False
        """
        if len(self.data) == 0:
            return False

        if self.cur_row_num < len(self.data):
            # 当前页还有数据
            return True
        else:
            # 当前页没有数据，取下一页数据
            msg_body_split = self.msg_body.split(cons.MESSAGE_SPLIT)

            if self.cur_page_num.isdigit():
                next_page = int(self.cur_page_num) + 1
                msg_body_split[2] = str(next_page)
            else:
                print("当前页面编号不正确，请检查后再试")
                return False

            msg_body = cons.MESSAGE_SPLIT.join(msg_body_split)
            msg_header = msgheader.to_message_header(
                    self.msg_type, len(msg_body))

            head_body = msg_header + msg_body
            crc32str = zlib.crc32(bytes(head_body, encoding='utf-8'))
            receive_data = sock.send_msg(
                        head_body + cons.MESSAGE_SPLIT + str(crc32str))

            if receive_data is None or receive_data.strip() == "":
                return False

            msg_header = receive_data[0:cons.MESSAGE_HEADER_LENGTH]
            msg_body = receive_data[cons.MESSAGE_HEADER_LENGTH:-1]

            header_arr = msg_header.split(cons.MESSAGE_SPLIT)
            body_arr = msg_body.split(cons.MESSAGE_SPLIT)
            # data.version = header_arr[0]
            # self.msg_type = header_arr[1]
            self.msg_body_length = header_arr[2]

            self.error_code = body_arr[0]
            self.error_msg = body_arr[1]

            if cons.BSERR_SUCCESS == self.error_code:
                self.method = body_arr[2]
                self.user_id = body_arr[3]
                self.cur_page_num = body_arr[4]
                self.per_page_count = body_arr[5]
                self.setData(body_arr[6])
                self.cur_row_num = 0
                if len(self.data) == 0:
                    return False
                else:
                    return True
            else:
                return False

    def get_row_data(self):
        """返回当前获取的结果的某一行
        @return: 返回当前行数据
        """
        # 组织返回数据
        return_data = []
        if self.cur_row_num < len(self.data):
            return_data = self.data[self.cur_row_num]
            self.cur_row_num = self.cur_row_num + 1
        return return_data

    def get_data(self):
        """返回当前获取的全部结果
        @return:DataFrame类型
        """
        if len(self.data) == 0:
            return pd.DataFrame()

        # 组织返回数据
        df = pd.DataFrame(self.data, columns=self.fields)
        self.cur_row_num = len(self.data)
        return df

    def setData(self, receive_date):
        """对返回数据进行处理，将string转为list类型
        @return: 返回处理后的list类型数据
        """
        if receive_date.strip() != "":
            js_data = json.loads(receive_date)  # dict
            self.data = js_data['record']  # list
        else:
            self.data = []

    def setFields(self, receive_fields):
        """对返回数据的指标参数进行处理，将string中的空格去除
        @return: 返回去除空格后的指标参数
        """
        field_arr = receive_fields.split(cons.ATTRIBUTE_SPLIT)
        i = 0
        while i < len(field_arr):
            # 去除空格
            field_arr[i] = field_arr[i].strip()
            i += 1
        self.fields = field_arr
