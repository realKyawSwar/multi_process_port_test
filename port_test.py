import serial
import os
import random
from time import sleep, perf_counter
from multiprocessing import Pool, Manager
from module import commands


LUT = {'C2': '0', 'P1': '1', 'P2': '2', 'P3': '3', 'P4': '4',
       'P5': '5', 'P6': '6', 'P7': '7', 'P8': '8', 'P9': '9',
       'P10': 'A', 'P11': 'B', 'P12': 'C', 'P13': 'D', 'P14': 'E',
       'P15': 'F', 'P16': 'G', 'P17': 'H', 'P18': 'I', 'P19': 'J',
       'P20': 'K', 'P21': 'L', 'P22': 'M', 'P23': 'N', 'P24': 'O',
       'P25': 'P', 'P26': 'Q', 'P27': 'R', 'P28': 'S', 'C3': 'V',
       'P0': '0', 'C1': '1', 'Load': '2', 'Unload': '3', 'C4': '4'}
port_dict = {
             201: '36', 202: '37', 203: '38',
             204: '39', 205: '40', 206: '41',
             207: '42', 208: '43', 209: '44',
             210: '45', 211: '46'
             }
socket = {'C2': '5047', 'P1': '5047', 'P2': '5047', 'P3': '5047',
          'P4': '5047', 'P5': '5047', 'P6': '5047', 'P7': '5047',
          'P8': '5047', 'P9': '5047', 'P10': '5047', 'P11': '5047',
          'P12': '5047', 'P13': '5047', 'P14': '5047', 'P15': '5047',
          'P16': '5047', 'P17': '5047', 'P18': '5047', 'P19': '5047',
          'P20': '5047', 'P21': '5047', 'P22': '5047', 'P23': '5047',
          'P24': '5047', 'P25': '5047', 'P26': '5047', 'P27': '5047',
          'P28': '5047', 'C3': '5047',
          'P0': '5048', 'C1': '5048', 'Load': '5048', 'Unload': '5048',
          'C4': '5048', 'VTC': '5048'}


def timer(func):
    def wrapper_timer(*args, **kwargs):
        start_time = perf_counter()
        ret_val = func(*args, **kwargs)
        timed = perf_counter() - start_time
        minu, sec = divmod(timed, 60)
        print("%02d:%02d" % (minu, sec))
        return ret_val
    return wrapper_timer


def create_serial(baud_rate, tout):
    return serial.Serial(baudrate=baud_rate, bytesize=serial.EIGHTBITS,
                         parity=serial.PARITY_EVEN, timeout=tout)


def serObj(_url_):
    return serial.serial_for_url(
        url=_url_,
        baudrate=19200,
        do_not_open=True,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_EVEN,
        stopbits=1, timeout=1)


def clean_serdata(inComing):
    clean_data = []
    for j in inComing:
        x = j[:-3]
        s = str(x[3:].lstrip('0'))
        if s == "":
            pass
        elif len(s) > 15:
            pass
        else:
            if len(s) < 9:
                a = int(s, 16)
            else:
                a = str(s[2:].lstrip('0'))
                a = int(s, 16)
            clean_data.append(str(a))
    return clean_data


def checkerCmd(stationNo):
    """command to detect zero speed"""
    return [commands.cmdStr(f'{stationNo}05', f'0{i}') for i in range(2)]


@timer
def line_check():
    # 'socket://128.53.66.36:5046'
    line_list = list(range(201, 212))
    ng_line = []
    ok_line = []
    for line in line_list:
        chambers_ = random.sample(list(LUT.keys()), 3)
        replies = []
        for chamber in chambers_:
            station = LUT[chamber]
            # main start; looping COM ports(devices) and run main code
            ser = serObj(f'socket://128.53.66.{port_dict[line]}:{socket[chamber]}')
            ser.open()
            for i in range(4):
                # print(ser.readline())
                ser.readline()
            ser.reset_input_buffer()
            # ser.write(bytearray(b'\x01302\x0270\x0301'))
            ser.write(commands.cmdStr(f'{station}02', '70'))
            # print(f"Processing {line} {chamber}")
            sleep(0.02)
            reply = ser.read(22)
            replies.append(reply)
        if replies == [b'', b'', b'']:
            ng_line.append(line)
        else:
            ok_line.append(line)
    return ng_line, ok_line


def check_chamber(line, chamber):
    # 'socket://128.53.66.36:5046'
    station = LUT[chamber]
    # main start; looping COM ports(devices) and run main code
    ser = serObj(f'socket://128.53.66.{port_dict[line]}:{socket[chamber]}')
    ser.open()
    for i in range(4):
        # print(ser.readline())
        ser.readline()
    ser.reset_input_buffer()
    # ser.write(bytearray(b'\x01302\x0270\x0301'))
    ser.write(commands.cmdStr(f'{station}02', '70'))
    # print(f"Processing {line} {chamber}")
    sleep(0.02)
    reply = ser.read(22)
    # print(reply)
    if reply != b'':
        # ser.write(bytearray(b'\x01385\x02000000\x03C5'))
        ser.write(commands.cmdStr(f'{station}85', '000000'))
        sleep(0.02)
        ser.read(6)
        # print(ser.read(6))
        # bytearray(b'\x01304\x0202\x03FE')
        ser.write(commands.cmdStr(f'{station}04', '02'))
        sleep(0.02)
        ser.read(10)
        # print(ser.read(10))
        # ser.write(bytearray(b'\x01385\x02000000\x03C5'))
        ser.write(commands.cmdStr(f'{station}85', '000000'))
        sleep(0.02)
        ser.read(6)
        for i in checkerCmd(station):
            ser.write(i)
            sleep(0.2)
            ser.read(14)
            # print(ser.read(14))
        ser.close()
    else:
        ser.close()
        return chamber


def main(line, d, lock):
    # all chamber
    listy = []
    for chamber in list(LUT.keys()):
        result = check_chamber(line, chamber)
        if result:
            listy.append(result)
    lock.acquire()
    d[line] = listy
    lock.release()
    # print(line, "locked release!")


@timer
def multi_run(listy):
    manager = Manager()
    dicty = manager.dict()
    lock = manager.Lock()
    processes = os.cpu_count() - 1
    pool = Pool(processes)
    for line in listy:
        pool.apply_async(main, args=(line, dicty, lock))
    pool.close()
    pool.join()
    return dicty


if __name__ == '__main__':
    ng_line, ok_line = line_check()
    print(ng_line)
    # print(ok_line)
    dicty = multi_run(ok_line)
    print(dicty)

    # for line in range(201, 212):
    #     print(line)
