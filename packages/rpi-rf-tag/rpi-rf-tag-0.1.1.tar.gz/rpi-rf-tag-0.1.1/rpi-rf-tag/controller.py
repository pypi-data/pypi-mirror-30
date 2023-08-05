# -*- coding: utf-8 -*-

from pirc522 import RFID
from rpi_rf import RFDevice
import time

class Tag(object):
    
    def __init__(self, func=None):
        #falta verificar se o usuário realmente passou uma função como parametro
        self.func = func
        self.tag_manager = RFID()
    
    def wait_for_tag(self):
        while true:
            self.tag_manager.wait_for_tag()
            error, tag_type = self.tag_manager.request()
            if not error:
                error, uid = self.tag_manager.anticoll()
                if not error:
                    self.tag_manager.stop_crypto()
                    self.func(str(uid))
        
        self.tag_manager.cleanup()

class RF(object):
    
    def __init__(self, func=None pin_gpio=27):
        #falta verificar se o usuário realmente passou uma função como parametro
        self.pin_gpio = pin_gpio
        self.func = func
        self.rf_manager = RFDevice(pin_gpio)
        self.rf_manager.enable_rx()
        self.timestamp = None

    def wait_for_rf(self):
        while true:
            if self.rf_manager.rx_code_timestamp != self.timestamp:
                self.timestamp = self.rx_code_timestamp
                self.func(str(self.rf_manager.rx_code))
            time.sleep(0.01)

    

