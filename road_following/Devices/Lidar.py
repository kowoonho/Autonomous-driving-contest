import serial
import logging
import time
import sys
from pathlib import Path
import os
sys.path.append(os.path.dirname(__file__))
# sys.path.append("")

from Lidar_utility import _b2i, _showhex, _process_scan, lidar_initialize
import struct

SYNC_BYTE = b'\xA5'
SYNC_BYTE2 = b'\x5A'

GET_INFO_BYTE = b'\x50'
GET_HEALTH_BYTE = b'\x52'

STOP_BYTE = b'\x25'
RESET_BYTE = b'\x40'

_SCAN_TYPE = {
    'normal': {'byte': b'\x20', 'response': 129, 'size': 5},
    'force': {'byte': b'\x21', 'response': 129, 'size': 5},
    'express': {'byte': b'\x82', 'response': 130, 'size': 84},
}

DESCRIPTOR_LEN = 7
INFO_LEN = 20
HEALTH_LEN = 3

INFO_TYPE = 4
HEALTH_TYPE = 6

# Constants & Command to start A2 motor
MAX_MOTOR_PWM = 1023
DEFAULT_MOTOR_PWM = 660
SET_PWM_BYTE = b'\xF0'

_HEALTH_STATUSES = {
    0: 'Good',
    1: 'Warning',
    2: 'Error',
}


class RPLidarException(Exception):
    '''Basic exception class for RPLidar'''

class LidarModule(): # baudrate = 115200
    def __init__(self, lidar_port = '/dev/ttyUSB1', baudrate=115200, timeout=1, logger=None):
        self.lidar_port = lidar_port
        self._serial = None
        self.baudrate = baudrate
        self.timeout = timeout
        self._motor_speed = DEFAULT_MOTOR_PWM
        self.scanning = [False, 0, 'normal']
        self.express_trame = 32
        self.express_data = False
        self.motor_running = None
        if logger is None:
            logger = logging.getLogger('rplidar')
        self.logger = logger
        self.connect()
    
    def connect(self):
        '''Connects to the serial port with the name `self.port`. If it was
        connected to another serial port disconnects from it first.'''
        if self._serial is not None:
            self.disconnect()
        try:
            self._serial = serial.Serial(
                self.lidar_port, self.baudrate,
                parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                timeout=self.timeout)
        except serial.SerialException as err:
            raise RPLidarException('Failed to connect to the sensor '
                                   'due to: %s' % err)
    
    def _set_pwm(self, pwm):
        payload = struct.pack("<H", pwm)
        self._send_payload_cmd(SET_PWM_BYTE, payload)
    
    def _send_payload_cmd(self, cmd, payload):
        '''Sends `cmd` command with `payload` to the sensor'''
        size = struct.pack('B', len(payload))
        req = SYNC_BYTE + cmd + size + payload
        checksum = 0
        for v in struct.unpack('B'*len(req), req):
            checksum ^= v
        req += struct.pack('B', checksum)
        self._serial.write(req)
        self.logger.debug('Command sent: %s' % _showhex(req))
    
    def start_motor(self):
        '''Starts sensor motor'''
        self.logger.info('Starting motor')
        # For A1
        self._serial.setDTR(False)

        # For A2
        self._set_pwm(self._motor_speed)
        self.motor_running = True
    
    def stop_motor(self):
        '''Stops sensor motor'''
        self.logger.info('Stoping motor')
        # For A2
        self._set_pwm(0)
        time.sleep(.001)
        # For A1
        self._serial.setDTR(True)
        self.motor_running = False
    
    def _send_cmd(self, cmd):
        '''Sends `cmd` command to the sensor'''
        req = SYNC_BYTE + cmd
        self._serial.write(req)
        self.logger.debug('Command sent: %s' % _showhex(req))
    
    def _read_descriptor(self):
        '''Reads descriptor packet'''
        descriptor = self._serial.read(DESCRIPTOR_LEN)
        self.logger.debug('Received descriptor: %s', _showhex(descriptor))
        if len(descriptor) != DESCRIPTOR_LEN:
            raise RPLidarException('Descriptor length mismatch')
        elif not descriptor.startswith(SYNC_BYTE + SYNC_BYTE2):
            raise RPLidarException('Incorrect descriptor starting bytes')
        is_single = _b2i(descriptor[-2]) == 0
        return _b2i(descriptor[2]), is_single, _b2i(descriptor[-1])
    
    def _read_response(self, dsize):
        '''Reads response packet with length of `dsize` bytes'''
        self.logger.debug('Trying to read response: %d bytes', dsize)
        while self._serial.inWaiting() < dsize:
            time.sleep(0.001)
        data = self._serial.read(dsize)
        self.logger.debug('Received data: %s', _showhex(data))
        return data
    
    def scanning_start(self, scan_type = 'normal'):
        if self.scanning[0]:
            return "Scanning already running!"
        
        cmd = _SCAN_TYPE[scan_type]['byte']
        
        self._send_cmd(cmd)
        dsize, is_single, dtype = self._read_descriptor()
        
        if dsize != _SCAN_TYPE[scan_type]['size']:
            raise RPLidarException('Wrong get_info reply length')
        if is_single:
            raise RPLidarException('Not a multiple response mode')
        if dtype != _SCAN_TYPE[scan_type]['response']:
            raise RPLidarException('Wrong response data type')
        
        self.scanning = [True, dsize, scan_type]
        
    def scanning_stop(self):
        '''Stops scanning process, disables laser diode and the measurement
        system, moves sensor to the idle state.'''
        self.logger.info('Stopping scanning')
        self._send_cmd(STOP_BYTE)
        time.sleep(.1)
        self.scanning[0] = False
        
        # Flush
        if self.scanning[0]:
            return 'Cleaning not allowed during scanning process active!'
        self._serial.flushInput()
    
    
    def iter_measures(self, max_buf_meas= 3000):
        self.start_motor()
        if not self.scanning[0]:
            self.scanning_start()
        while True:
            dsize = self.scanning[1]
            if max_buf_meas:
                data_in_buf = self._serial.inWaiting()
                if data_in_buf > max_buf_meas:
                    self.logger.warning(
                        'Too many bytes in the input buffer: %d/%d. '
                        'Cleaning buffer...',
                        data_in_buf, max_buf_meas)
                    self.scanning_stop()
                    self.scanning_start()

            
            raw = self._read_response(dsize)
            yield _process_scan(raw)
            
    
    def iter_scans(self, max_buf_meas=3000, min_len=5):
        scan_list = []
        iterator = self.iter_measures(max_buf_meas)
        for new_scan, quality, angle, distance in iterator:
            if new_scan:
                if len(scan_list) > min_len:
                    return scan_list
                scan_list = []
            if distance > 0:
                scan_list.append((lidar_initialize(int(angle)), int(distance)))
    
    
    def disconnect(self):
        '''Disconnects from the serial port'''
        if self._serial is None:
            return
        self._serial.close()
        
    def lidar_finish(self):
        self.scanning_stop()
        self.stop_motor()
        self.disconnect()
        pass