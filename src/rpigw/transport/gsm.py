# -*- coding: utf-8 -*-

"""
GSM
===

An implementation of a GSM communication.

:copyright: (c) 2017 Roman Ondráček.
:license: GNU GPLv3, see LICENSE for more details.
"""

import time
import serial


class Gsm(object):

    def __init__(self, config):
        """
        Initalize a serial connection with AT modem
        @param config Configuration in dictionary
        """
        self.enabled = config['gsm']['enabled']
        self.interface = config['gsm']['interface']
        self.interface_settings = config['gsm']['interfaces'][self.interface]
        self.port = self.interface_settings['port']
        self.baud_rate = self.interface_settings['baudRate']
        self.pin = config['gsm']['pin']
        self.serial = serial.Serial(self.port, self.baud_rate, timeout=0)
        self.reset()
        self.unlock()
        self.set_text_mode()

    def __exit__(self):
        self.close()

    def close(self):
        """
        Close a serial connection with the AT modem
        """
        self.serial.close()

    def read(self):
        """
        Read data form the AT modem
        @return Received data
        """
        bytes_to_read = self.serial.inWaiting()
        while bytes_to_read == 0:
            bytes_to_read = self.serial.inWaiting()
        data = self.serial.read(bytes_to_read)
        return data.decode('utf-8').strip()

    def write(self, data, ending='\r'):
        """
        Write data to the AT modem
        @param data Data to send
        """
        data += ending
        print(data)
        self.serial.write(data.encode('utf-8'))
        time.sleep(0.5)

    def reset(self):
        """
        Reset the AT modem
        """
        self.write('ATZ')

    def unlock(self):
        """
        Unlock SIM card
        """
        if self.pin is False:
            pass
        elif isinstance(self.pin, int):
            self.write('AT+CPIN=' + str(self.pin))
            self.write('AT+CPIN?')
            status = self.read()
            if status == '+CPIN: READY':
                print('Correct PIN')
            else:
                print('Incorrect PIN')
        else:
            print('PIN must be number with 4-8 digits.')

    def set_text_mode(self):
        """
        Set ASCII text mode communication
        """
        self.write('AT+CMGF=1')

    def read_sms(self, type):
        """
        Read a text messages
        @param type Type of messages (ALL, REC UNREAD, REC READ)
        @return Text message(s)
        """
        self.write('AT+CMGL="' + type + '"')
        return self.read()

    def send_sms(self, number, text):
        """
        Send a text message (SMS) to the telephone number
        @param number Telephone number
        @param text Text of message
        """
        self.write('AT+CMGS="' + str(number) + '"')
        time.sleep(1)
        self.write(text, chr(26))
