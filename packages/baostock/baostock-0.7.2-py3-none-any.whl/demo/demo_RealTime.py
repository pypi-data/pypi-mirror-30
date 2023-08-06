import baostock as bs


def callbackFunc(data):
    print("demo_RealTime", data.data)


if __name__ == '__main__':
    login_result = bs.login_real_time()
    # print(login_result.error_msg)
    rs = bs.subscribe_by_code("sh.600067", 0, callbackFunc, "", "test")
    if rs.error_code != '0':
        print("request real time error, ", rs.error_msg)
    else:
        text = input("press any key to cancel real time \r\n")
        cancel_rs = bs.cancel_subscribe(rs.serial_id)

