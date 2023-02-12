import sys


class RPLidarException(Exception):
    '''Basic exception class for RPLidar'''

def _b2i(byte):
    '''Converts byte to integer (for Python 2 compatability)'''
    return byte if int(sys.version[0]) == 3 else ord(byte)


def _showhex(signal):
    '''Converts string bytes to hex representation (useful for debugging)'''
    return [format(_b2i(b), '#02x') for b in signal]


def _process_scan(raw):
    '''Processes input raw data and returns measurement data'''
    new_scan = bool(_b2i(raw[0]) & 0b1)
    inversed_new_scan = bool((_b2i(raw[0]) >> 1) & 0b1)
    quality = _b2i(raw[0]) >> 2
    if new_scan == inversed_new_scan:
        raise RPLidarException('New scan flags mismatch')
    check_bit = _b2i(raw[1]) & 0b1
    if check_bit != 1:
        raise RPLidarException('Check bit not equal to 1')
    angle = ((_b2i(raw[1]) >> 1) + (_b2i(raw[2]) << 7)) / 64.
    distance = (_b2i(raw[3]) + (_b2i(raw[4]) << 8)) / 4.
    return new_scan, quality, angle, distance

# def lidar_initialize(value, mid = 47):
#     if abs(value - mid) >= 180:
#         return value - mid - 360
#     else:
#         return value - mid

def lidar_initialize(value, mid = 296):
    if abs(value - mid) >= 180:
        return 360 - (mid - value)
    else:
        return value - mid
