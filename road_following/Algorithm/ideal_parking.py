import sys
import os
from pathlib import Path
PATH = str(Path(os.path.dirname(os.path.abspath(__file__))).parent)
sys.path.append(PATH)
from Algorithm.Control import moving_log

class idealparking():
    def __init__(self, serial, parking_log):
        self.serial = serial
        self.parking_log = parking_log
        pass
    def action(self, parking_location):
        try:
            log = self.parking_log + str(parking_location) # parking1, parking2, parking3, parking4
            messages = moving_log(log)
            for message in messages:
                self.serial.write(message.encode())
                
                if True:
                    """
                    선을 밟거나 부딪히려 하면 위치 조정
                    """
                    pass
                
                print(message)
            return True
            pass
        except Exception as e:
            _, _, tb = sys.exc_info()
            print("Trying parking error = {}, error line = {}".format(e, tb.tb_lineno))
            return False
            pass
