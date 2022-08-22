import binascii


def LUT(chamber):
    '''Look up table for station numbers corresponding to chambers in Dictionary
     format.'''
    LUT = {'C2': '0', 'P1': '1', 'P2': '2', 'P3': '3', 'P4': '4',
           'P5': '5', 'P6': '6', 'P7': '7', 'P8': '8', 'P9': '9',
           'P10': 'A', 'P11': 'B', 'P12': 'C', 'P13': 'D', 'P14': 'E',
           'P15': 'F', 'P16': 'G', 'P17': 'H', 'P18': 'I', 'P19': 'J',
           'P20': 'K', 'P21': 'L', 'P22': 'M', 'P23': 'N', 'P24': 'O',
           'P25': 'P', 'P26': 'Q', 'P27': 'R', 'P28': 'S', 'C3': 'V',
           'P0': '0', 'C1': '1', 'Load': '2', 'Unload': '3', 'C4': '4',
           'VTC': '5'}
    return LUT[chamber]


def firstPort(line):
    """ Port #37"""
    if line == "201":
        return [f'P{i}' for i in range(1, 23)] + ['C2', 'C3']
    elif line == "202":
        return [f'P{i}' for i in range(1, 22)] + ['C2', 'C3']
    else:
        return [f'P{i}' for i in range(1, 29)] + ['C2', 'C3']


def secondPort(line):
    """ Port #38"""
    if line == "202":
        return ['P0-1', 'P0-2', 'C1', 'Load', 'Unload', 'C4']
    else:
        return ['P0', 'C1', 'Load', 'Unload', 'C4']


def convertAscii_Hex(cd):
    """ ASCII to HEX conversion"""
    x = bytes(cd, 'utf-8')
    y = str(binascii.hexlify(x), 'ascii')
    cd = ' '.join(a+b for a, b in zip(y[::2], y[1::2]))
    return(cd)


def cmdStr(inputC, inputD):
    """Create command string from command input and data input,
    Checksum is added. Return bytearray"""
    SOH = '01 '
    STX = ' 02 '
    ETX = ' 03'
    a = convertAscii_Hex(inputC).split()
    b = convertAscii_Hex(inputD).split()
    for i in range(0, len(a)):
        a[i] = int(a[i], 16)
    for i in range(0, len(b)):
        b[i] = int(b[i], 16)
    total = int(STX, 16)+int(ETX, 16) + sum(a) + sum(b)
    dummy = str(hex(total))
    checksum = convertAscii_Hex(''.join((dummy[-2:]).split()).upper())
    return bytearray.fromhex(SOH+convertAscii_Hex(inputC)+STX +
                             convertAscii_Hex(inputD)+ETX+" "+checksum)


def dataLen(command):
    """Look up table for data length of corresponding commands"""
    dataLenDict = {'85': 6, 'B6': 6, '04': 10, '36': 10,
                   '02': 14, '05': 14, '37': 22}
    return dataLenDict[command]


def selection_TorS(stationNo, selection):
    cmdLst = ['02', '02', '02',
              '36', 'B6', '36', 'B6',
              '36', 'B6', '36', '36',
              '36', 'B6', 'B6', 'B6',
              'B6', 'B6', 'B6', '36',
              'B6', '36', 'B6', '36',
              'B6', '36', '36', 'B6',
              'B6', 'B6']
    newCmdLst = [f'{stationNo}' + i for i in cmdLst]
    if selection == 'speed':
        dataLst = ['70', '13', '11',
                   '10', '00FFFFFFFF00FFFFFF', '10', '00FFFFFFFF0001FFFF',
                   '10', '00FFFFFFFF0001FFFF', '03', '02',
                   '02', '111EA5', '0281F0', '00FFFFFFFF0001FFFF',
                   '00FFFFFFFF0001FFFF', '00FFFFFFFF0001FFFF',
                   '00FFFFFFFF0001FFFF', '10',
                   '00FFFFFFFF0001FFFF', '10', '00FFFFFFFF0001FFFF', '10',
                   '00FFFFFFFF0001FFFF', '01', '02', '010002',
                   '028182', '101EA5']
    elif selection == 'torque':
        dataLst = ['70', '13', '11',
                   '10', '00FFFFFFFF01FFFFFF', '10', '00FFFFFFFF0100FFFF',
                   '10', '00FFFFFFFF0100FFFF', '03', '02',
                   '02', '111EA5', '0281F0', '00FFFFFFFF0100FFFF',
                   '00FFFFFFFF0100FFFF', '00FFFFFFFF0100FFFF',
                   '00FFFFFFFF0100FFFF', '10',
                   '00FFFFFFFF0100FFFF', '10', '00FFFFFFFF0100FFFF', '10',
                   '00FFFFFFFF0100FFFF', '01', '02', '010001',
                   '028182', '101EA5']
    else:
        dataLst = []
    return [cmdStr(x, y) for x, y in zip(newCmdLst, dataLst)]


def checkerCmd(stationNo):
    """command to detect zero speed"""
    return cmdStr(f'{stationNo}36', '00')


def midCmd(stationNo):
    return [cmdStr(f'{stationNo}36', i) for i in ['00', '03', '03', '00']]


def fetchCmd(stationNo):
    new_str = []
    for x in range(4):
        for i in [hex(a)[2:].zfill(2).upper() for a in range(0, 256)]:
            i = i + f"000{x}"
            new_str.append(i)
    return [cmdStr(f"{stationNo}37", i) for i in new_str]


def endCmd(stationNo):
    initDatalst = ["05", "02", "01", "03"]
    initCmdlst = [f'{stationNo}' + "36" for i in range(5)]
    return [cmdStr(x, y) for x, y in zip(initCmdlst, initDatalst)]


# def initCmd(stationNo):
#     initDatalst = ["70", "13", "000000", "11", "02", "000000"]
#     initCmdlst = [f'{stationNo}' + i for i in
#                   ["02", "02", "85", "02", "04", "85"]]
#     return [cmdStr(x, y) for x, y in zip(initCmdlst, initDatalst)]


# def fetchCmd(stationNo, num):
#     fetchCmdLst = [cmdStr(f"{stationNo}05", x) for x in
#                    [hex(i)[2:].zfill(2).upper() for i in range(1, num)]]
#     return fetchCmdLst


# def midCmd1(stationNo):
#     initDatalst = ["000001", "02", "000001"]
#     initCmdlst = [f'{stationNo}' + i for i in ["85", "04", "85"]]
#     return [cmdStr(x, y) for x, y in zip(initCmdlst, initDatalst)]

# stationNo = '5'
# # # lol = (selection_TorS(stationNo, 'speed'))
# # # print(len(lol))
# # # print(midCmd(stationNo))
# fetchy = fetchCmd(stationNo)
# print(fetchy.pop(0))
# # print(endCmd(stationNo))
# print(len(fetchy))
