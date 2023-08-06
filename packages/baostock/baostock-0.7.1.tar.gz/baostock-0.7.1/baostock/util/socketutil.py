# -*- coding:utf-8 -*-
"""
获取默认socket
@author: baostock.com
@group : baostock.com
@contact: baostock@163.com
"""
import time
import socket
import threading
import baostock.common.contants as cons
import baostock.common.context as context


class SocketUtil(object):
    """Socket工具类"""
    # 记录第一个被创建对象的引用
    instance = None
    # 记录是否执行过初始化动作
    init_flag = False

    def __new__(cls, *args, **kwargs):
        # 1. 判断类属性是否是空对象
        if cls.instance is None:
            # 2. 调用父类的方法，为第一个对象分配空间
            cls.instance = super().__new__(cls)
        # 3. 返回类属性保存的对象引用
        return cls.instance

    def __init__(self):
        SocketUtil.init_flag = True

    def connect(self):
        """创建连接"""
        try:
            mySockect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            mySockect.connect((cons.BAOSTOCK_SERVER_IP, cons.BAOSTOCK_SERVER_PORT))
        except Exception:
            print("服务器连接失败，请稍后再试。")
        setattr(context, "default_socket", mySockect)


def get_default_socket():
    """获取默认连接"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((cons.BAOSTOCK_SERVER_IP, cons.BAOSTOCK_SERVER_PORT))
    except Exception:
        print("服务器连接失败，请稍后再试。")
        return None
    return sock


def send_msg(msg):
    """发送消息，并接受消息 """
    try:
        # default_socket = get_default_socket()
        if hasattr(context, "default_socket"):
            default_socket = getattr(context, "default_socket")
            if default_socket is not None:
                # str 类型 -> bytes 类型
                msg += "\n"  # 在消息结尾追加“消息之间的分隔符”
                default_socket.send(bytes(msg, encoding='utf-8'))
                receive = b""
                while True:
                    recv = default_socket.recv(1024)
                    receive += recv
                    # 判断是否读取完
                    if recv[-1:] == b"\n":
                        break
                return bytes.decode(receive)
            else:
                return None
        else:
            print("you don't login.")
    except Exception as ex:
        print(ex)
        print("接收数据异常，请稍后再试。")


class SocketRealTimeUtil(object):
    """Socket实时工具类"""
    # 记录第一个被创建对象的引用
    instance = None
    # 记录是否执行过初始化动作
    init_flag = False

    def __new__(cls, *args, **kwargs):
        # 1. 判断类属性是否是空对象
        if cls.instance is None:
            # 2. 调用父类的方法，为第一个对象分配空间
            cls.instance = super().__new__(cls)
        # 3. 返回类属性保存的对象引用
        return cls.instance

    def __init__(self):
        SocketRealTimeUtil.init_flag = True

    def connect(self):
        """创建实时行情连接"""
        try:
            mySockect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            mySockect.connect((cons.BAOSTOCK_SERVER_REAL_TIME_IP, cons.BAOSTOCK_SERVER_REAL_TIME_PORT))
        except Exception:
            print("服务器连接失败，请稍后再试。")
        setattr(context, "socket_real_time", mySockect)


def get_real_time_socket():
    """获取实时行情连接"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((cons.BAOSTOCK_SERVER_REAL_TIME_IP, cons.BAOSTOCK_SERVER_REAL_TIME_PORT))
    except Exception:
        print("服务器连接失败，请稍后再试。")
        return None
    return sock


def send_real_time_msg(msg):
    """发送实时行情消息，并接受消息 """
    try:
        # default_socket = get_default_socket()
        if hasattr(context, "socket_real_time"):
            default_socket = getattr(context, "socket_real_time")
            if default_socket is not None:
                # str 类型 -> bytes 类型
                msg += "\n"  # 在消息结尾追加“消息之间的分隔符”
                default_socket.send(bytes(msg, encoding='utf-8'))
                receive = b""
                while True:
                    recv = default_socket.recv(1024)
                    receive += recv
                    # 判断是否读取完
                    if recv[-1:] == b"\n":
                        break
                return bytes.decode(receive)
            else:
                return None
        else:
            print("you don't login.")
    except Exception as ex:
        print(ex)
        print("接收数据异常，请稍后再试。")


def real_time_subscibe_thread(socket_real_time, data):
    # time.sleep(2)
    receive = b""
    # data.fncallback(data)
    data.data = {}
    while True:
        recv = socket_real_time.recv(1024)
        receive += recv
        # 判断是否读取完
        if recv[-1:] == b"\n":
            receive_data = bytes.decode(receive)
            if receive_data is None or receive_data.strip() == "":
                data.error_code = cons.BSERR_RECVSOCK_FAIL
                data.error_msg = "网络接收错误。"
                return data

            # msg_header = receive_data[0:cons.MESSAGE_HEADER_LENGTH]
            msg_body = receive_data[cons.MESSAGE_HEADER_LENGTH:-1]

            # header_arr = msg_header.split(cons.MESSAGE_SPLIT)
            body_arr = msg_body.split(cons.MESSAGE_SPLIT)

            data.error_code = body_arr[0]
            data.error_msg = body_arr[1]

            if cons.BSERR_SUCCESS == data.error_code:
                real_time = body_arr[3]
                data.data[real_time.split(",")[0]] = real_time.split(',')
                data.error_code = data.error_code  # 错误代码
                data.error_msg = data.error_msg
                data.fncallback(data)
            # data.error_code = cons.BSERR_NO_LOGIN  # 错误代码
            # data.error_msg = ""
            data.data = {}
            receive = b""


def send_real_time_subscibe(msg, data):
    """发送实时行情消息，并接受消息 """
    try:
        # default_socket = get_default_socket()
        if hasattr(context, "socket_real_time"):
            socket_real_time = getattr(context, "socket_real_time")
            if socket_real_time is not None:
                # str 类型 -> bytes 类型
                msg += "\n"  # 在消息结尾追加“消息之间的分隔符”
                socket_real_time.send(bytes(msg, encoding='utf-8'))
                receive = b""
                while True:
                    recv = socket_real_time.recv(1024)
                    receive += recv
                    # 判断是否读取完
                    if recv[-1:] == b"\n":
                        receive_data = bytes.decode(receive)
                        if receive_data is None or receive_data.strip() == "":
                            data.error_code = cons.BSERR_RECVSOCK_FAIL
                            data.error_msg = "网络接收错误。"
                            return data

                        msg_header = receive_data[0:cons.MESSAGE_HEADER_LENGTH]
                        msg_body = receive_data[cons.MESSAGE_HEADER_LENGTH:-1]

                        header_arr = msg_header.split(cons.MESSAGE_SPLIT)
                        body_arr = msg_body.split(cons.MESSAGE_SPLIT)

                        data.error_code = body_arr[0]
                        data.error_msg = body_arr[1]

                        if cons.BSERR_SUCCESS == data.error_code:
                            # real_time = body_arr[3]
                            # data.data[real_time.split(",")[0]] = real_time.strip(',').split(',')
                            t = threading.Thread(target=real_time_subscibe_thread, args=(socket_real_time, data))
                            data.serial_id = t
                            t.start()
                        data.error_code = data.error_code  # 错误代码
                        data.error_msg = data.error_msg
                        break
                return data
            else:
                return None
        else:
            print("you don't login.")
    except Exception as ex:
        print(ex)
        print("接收数据异常，请稍后再试。")
