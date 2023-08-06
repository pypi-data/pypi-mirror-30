import time
import zlib
import ctypes
import inspect
import baostock.data.resultset as rs
import baostock.common.contants as cons
import baostock.util.stringutil as strUtil
import baostock.common.context as conx
import baostock.util.socketutil as sock
import baostock.data.messageheader as msgheader


def subscribe_by_code(code_list, subscribe_type=0, fncallback=None, options="", user_params=None):
    """订阅实时行情
    @param subscribe_type: 订阅方式 0：按证券代码订阅， 1：按行情数据类型订阅。0.7.5版本只支持按证券代码订阅；
    @param code_list: 每只证券代码之间用“英文逗号分隔符”，结尾不存在“英文逗号分隔符”；证券代码格式：sh.600000，前两位为证券市场：“sz”深圳、“sh”上海
    @param fncallback: 自定义回调方法
    @param options: 预留参数
    @param user_params: 用户参数，回调时原样返回
    """
    data = rs.SubscibeData()
    data.method = "subscribe_by_code"
    data.options = options
    data.user_params = user_params

    # 设置订阅方式 默认为0
    if subscribe_type == 0 or subscribe_type == 1:
        pass
    else:
        subscribe_type = 0
    data.subscribe_type = subscribe_type

    data.code_list = code_list

    if not callable(fncallback):
        fncallback = DemoCallback
    data.fncallback = fncallback
    user_id = ""
    try:
        user_id = getattr(conx, "user_id")
    except Exception:
        print("you don't login.")
        data.error_code = cons.BSERR_NO_LOGIN
        data.error_msg = "you don't login."
        return data

    data.user_id = user_id
    param = "%s\1%s\1%s\1%s\1%s\1%s\1%s" % (
        "subscribe_by_code", user_id, subscribe_type,
        code_list, fncallback, options, user_params)
    msg_body = strUtil.organize_realtime_msg_body(param)
    msg_header = msgheader.to_message_header(
        cons.MESSAGE_TYPE_SUBSCRIPTIONS_BY_SECURITYID_REQUEST, len(msg_body))
    data.msg_type = cons.MESSAGE_TYPE_SUBSCRIPTIONS_BY_SECURITYID_REQUEST
    data.msg_body = msg_body

    head_body = msg_header + msg_body
    crc32str = zlib.crc32(bytes(head_body, encoding='utf-8'))

    sock.send_real_time_subscibe(head_body + cons.MESSAGE_SPLIT + str(crc32str), data)

    return data


def cancel_subscribe(thread):
    """取消实时行情
    @param thread: 实时行情的线程；
    """
    data = rs.SubscibeData()
    thread._tstate_lock = None
    thread._stop()
    data.error_code = cons.BSERR_SUCCESS
    data.error_msg = "success"
    return data


def DemoCallback(quantdata):
    """
    DemoCallback 是订阅时提供的回调函数模板。该函数只有一个为ResultData类型的参数quantdata
    :param quantdata:ResultData
    :return:
    """
    print("BaostockCallback,", quantdata)
