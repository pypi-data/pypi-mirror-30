# -*- coding: utf-8 -*-
from core import *
from api import *

import serial
import time
import inspect
import platform

if platform.system() == 'Windows':
    import serial.tools.list_ports_windows as list_ports
if platform.system() == 'Linux':
    import serial.tools.list_ports_linux as list_ports
if platform.system() == 'Darwin':
    import serial.tools.list_ports_osx as list_ports


class UF_PROTOCOL:
    UF_SINGLE_PROTOCOL = 0
    UF_NETWORK_PROTOCOL = 1


# class UF_COMMAND:
#     UF_COM_SW = 0x01
#     UF_COM_SR = 0x03
#     UF_COM_SI = 0x15


class _ResponseCommand(object):
    def __init__(self):
        self._received_packet = None
        self._start_code = 0x0
        self._command = 0x0
        self._module_id = 0x0
        self._size = 0x0
        self._param = 0x0
        self._error = 0x0
        self._flag = 0x0
        self._checksum = 0x0
        self._end_code = 0x0

    @property
    def received_packet(self):
        return self.received_packet

    @received_packet.setter
    def received_packet(self, value):
        self._received_packet = value

        # Single protocol
        if len(self._received_packet) == 13:
            self._start_code = self._received_packet[0]
            self._command = self._received_packet[1]
            self._param = self._received_packet[5] << 24 | self._received_packet[4] << 16 | self._received_packet[3] << 8 | self._received_packet[2]
            self._size = self._received_packet[9] << 24 | self._received_packet[8] << 16 | self._received_packet[7] << 8 | self._received_packet[6]
            self._error = self._flag = self._received_packet[10]
            self._checksum = self._received_packet[11]
            self._end_code = self._received_packet[12]
        # Network protocol
        elif len(self._received_packet) == 15:
            self._start_code = self._received_packet[0]
            self._module_id = self._received_packet[2] << 8 | self._received_packet[1]
            self._command = self._received_packet[3]
            self._param = self._received_packet[7] << 24 | self._received_packet[6] << 16 | self._received_packet[5] << 8 | self._received_packet[4]
            self._size = self._received_packet[11] << 24 | self._received_packet[10] << 16 | self._received_packet[9] << 8 | self._received_packet[8]
            self._error = self._flag = self._received_packet[12]
            self._checksum = self._received_packet[13]
            self._end_code = self._received_packet[14]

    @property
    def start_code(self):
        return self._start_code

    @property
    def command(self):
        return self._command

    @property
    def module_id(self):
        return self._module_id

    @property
    def param(self):
        return self._param

    @property
    def size(self):
        return self._size

    @property
    def error(self):
        return self._error

    @property
    def flag(self):
        return self._flag

    @property
    def checksum(self):
        return self._checksum

    @property
    def end_code(self):
        return self._end_code

    def clear(self):
        self._received_packet = None
        self._start_code = 0x0
        self._command = 0x0
        self._module_id = 0x0
        self._size = 0x0
        self._param = 0x0
        self._error = 0x0
        self._flag = 0x0
        self._checksum = 0x0
        self._end_code = 0x0

    def print_received_packet_info(self):
        print "Start Code : 0x%02X (int : %d)" % (self.start_code, self.start_code)
        print "ModuleID : 0x%04X (int : %d)" % (self.module_id, self.module_id)
        print "Command : 0x%02X (int : %d)" % (self.command, self.command)
        print "Param : 0x%08X (int : %d)" % (self.param, self.param)
        print "Size : 0x%08X (int : %d)" % (self.size, self.size)
        print "Error/Flag : 0x%02X (int : %d)" % (self.error, self.error)
        print "Checksum : 0x%02X (int : %d)" % (self.checksum, self.checksum)
        print "End Code: 0x%02X (int : %d)" % (self.end_code, self.end_code)

def get_port_list():
    ports = list_ports.comports()

    device = []
    for x in ports:
        device.append(x.device)
    return device

class ModuleBase:
    def __init__(self, port=None, baudrate=115200, protocol=UF_PROTOCOL.UF_SINGLE_PROTOCOL, ascii_mode=False, module_id=1):
        self.port = port
        self.list_port = None
        self.baudrate = baudrate
        self.protocol = protocol
        self.ascii_mode = ascii_mode
        self.commIsOpen = False
        self.hcomm = None
        self.generic_command_timeout = 10.00
        self.module_id = module_id
        self.response_command = _ResponseCommand()
        self.packet_trace_activation = True

    def __del__(self):
        pass

    def activate_packet_trace(self):
        self.packet_trace_activation = True

    def deactivate_packet_trace(self):
        self.packet_trace_activation = False

    def print_packet_trace(self, packet_trace):
        if self.packet_trace_activation == True:
            print(packet_trace)

    def system_status_check(self):
        packet = self.send_command(UF_COM_SS)

        received_packet = self.read_response_command()

        if self.protocol == UF_PROTOCOL.UF_SINGLE_PROTOCOL:
            status_code = self.response_command.param
        else:
            status_code = self.response_command.param

        if status_code == 0x30:
            return True
        else:
            return False

    def connect(self):

        if self.port == None:
            return False

        try:
            if self.commIsOpen is True:
                # print 'already opened'
                self.hcomm.close()
                self.commIsOpen = False

            self.hcomm = serial.Serial(self.port, self.baudrate)
            
        except serial.SerialException as e:
            print(e)
            self.commIsOpen = False
            return False

        self.commIsOpen = True

        try:
            if self.hcomm.isOpen() == False:
                return False
            if self.system_status_check() == False:
                return False
        except Exception as e:
            print(e)
            return False

        return True

    def initialize(self, port, baudrate, protocol=UF_PROTOCOL.UF_SINGLE_PROTOCOL, ascii_mode=False, module_id=1):
        self.port = port
        self.baudrate = baudrate
        self.protocol = protocol
        self.ascii_mode = ascii_mode
        self.module_id = module_id

    def disconnect(self):
        self.hcomm.close()
        self.commIsOpen = False
    
    def send_packet(self, packet): 
        self.response_command.clear()
        packet_trace = '[SEND] : ' + HexByteConversion.ByteToHex(packet)
        self.print_packet_trace(packet_trace)

        if self.ascii_mode == True:
            packet = HexByteConversion.ByteToHex(packet).replace(' ', '')

        # self.hcomm.timeout = self.generic_command_timeout
        self.hcomm.write(packet)

    def read_packet(self, timeout=0):
        packet_data = []

        current_timeout = self.generic_command_timeout

        if self.commIsOpen == False:
            return -1

        if timeout != 0:
            self.hcomm.timeout = timeout
        else:
            self.hcomm.timeout = current_timeout

        if self.protocol == UF_PROTOCOL.UF_NETWORK_PROTOCOL:
            num_of_packet = 15
        else:
            num_of_packet = 13

        if self.ascii_mode == True:
            num_of_packet *= 2
        # data = ""
        try:
            received_packet = self.hcomm.read(num_of_packet)
            if len(received_packet) < num_of_packet:
                raise Exception('Packet cannot be read.')
        except Exception as e:
            print '[EXCEPTION : {}]'.format(inspect.stack()[1][3]), e
            return ''

        if self.ascii_mode == True:
            received_packet = HexByteConversion.HexToByte(received_packet)

        packet_trace = '[RECV] : '

        for x in received_packet:
            packet_data.append(ord(x))

        self.response_command.received_packet = packet_data

        for x in packet_data:
            packet_trace = packet_trace + (hex(x)[2:]).zfill(2) + ' '

        packet_trace = packet_trace.upper()

        self.print_packet_trace(packet_trace)

        self.hcomm._timeout = current_timeout

        return packet_data

    def send_data(self, data, timeout=0):
        self.response_command.clear()
        if type(data) == list:
            temp = ""
            for x in data:
                temp += chr(x)
            data = temp

        packet_data = []

        # current_timeout = self.generic_command_timeout

        if self.commIsOpen == False:
            return -1

        # if timeout != 0:
        #     self.hcomm.timeout = timeout

        num_of_packet = len(data)

        packet_trace = '[DATA] : '

        for x in data:
            packet_data.append(ord(x))

        for x in packet_data:
            packet_trace = packet_trace + (hex(x)[2:]).zfill(2) + ' '

        packet_trace = packet_trace.upper()

        self.print_packet_trace(packet_trace)

        if self.ascii_mode == True:
            num_of_packet *= 2
            data = HexByteConversion.ByteToHex(data).replace(' ', '')

        # data = ""
        try:
            written_packet = self.hcomm.write(data)
            if written_packet < num_of_packet:
                raise Exception('Packet cannot be send.')
        except Exception as e:
            print '[EXCEPTION : {}]'.format(inspect.stack()[1][3]), e
            return ''

        # self.hcomm.timeout = current_timeout

    def send_end_packet(self, timeout = 0):
        return self.send_packet(chr(0x0A))

    def read_data(self, length, timeout=0):
        packet_data = []

        current_timeout = self.generic_command_timeout

        if self.commIsOpen == False:
            return -1

        if timeout != 0:
            self.hcomm.timeout = timeout

        num_of_packet = length

        if self.ascii_mode == True:
            num_of_packet *= 2
        # data = ""
        try:
            received_packet = self.hcomm.read(num_of_packet)
            if len(received_packet) < num_of_packet:
                raise Exception('Packet cannot be read.')
        except Exception as e:
            print '[EXCEPTION : {}]'.format(inspect.stack()[1][3]), e
            return ''

        if self.ascii_mode == True:
            received_packet = HexByteConversion.HexToByte(received_packet)

        packet_trace = '[DATA] : '

        for x in received_packet:
            packet_data.append(ord(x))

        self.response_command.received_packet = packet_data

        for x in packet_data:
            packet_trace = packet_trace + (hex(x)[2:]).zfill(2) + ' '

        packet_trace = packet_trace.upper()

        self.print_packet_trace(packet_trace)

        self.hcomm._timeout = current_timeout

        return packet_data

    def read_end_packet(self, timeout=0):
        return self.read_packet(timeout)

    def get_sys_parameter(self, parameter_id):
        if self.protocol == UF_PROTOCOL.UF_SINGLE_PROTOCOL:
            packet = make_packet(UF_COM_SR, 0, 0, parameter_id)
        else:
            packet = make_network_packet(UF_COM_SR, self.module_id, 0, 0, parameter_id)

        self.send_packet(packet)
        received_data = self.read_packet()
        if validate_checksum(received_data, self.protocol):
            return self.response_command.error
        else:
            return False

    def set_sys_parameter(self, parameter_id, parameter_value):
        if self.protocol == UF_PROTOCOL.UF_SINGLE_PROTOCOL:
            packet = make_packet(UF_COM_SW, 0, parameter_value, parameter_id)
        else:
            packet = make_network_packet(UF_COM_SR, self.module_id, 0, parameter_id, parameter_id)

        self.send_packet(packet)
        received_data = self.read_packet()
        if validate_checksum(received_data, self.protocol):

            return self.response_command.error
        else:
            return False

    def send_command(self, command, param=0, size=0, flag=0, timeout=0):
        self.hcomm.flush()
        packet_data = []
        current_timeout = self.generic_command_timeout

        if self.commIsOpen == False:
            return -1

        if timeout != 0:
            self.hcomm.timeout = timeout

        if self.protocol == UF_PROTOCOL.UF_SINGLE_PROTOCOL:
            packet = make_packet(command, param, size, flag)
        else:
            packet = make_network_packet(command, self.module_id, param, size, flag)

        num_of_packet = len(packet)

        packet_trace = '[SEND] : '

        for x in packet:
            packet_data.append(ord(x))

        for x in packet_data:
            packet_trace = packet_trace + (hex(x)[2:]).zfill(2) + ' '

        packet_trace = packet_trace.upper()

        self.print_packet_trace(packet_trace)

        if self.ascii_mode == True:
            num_of_packet *= 2
            packet = HexByteConversion.ByteToHex(packet).replace(' ', '')

        try:
            written_packet = self.hcomm.write(packet)
            if written_packet < num_of_packet:
                raise Exception('Packet cannot be send.')
        except Exception as e:
            print '[EXCEPTION : {}]'.format(inspect.stack()[1][3]), e
            return ''

        self.hcomm._timeout = current_timeout

    def read_response_command(self, timeout=0):
        self.hcomm.flush()
        return self.read_packet(timeout)

    def scan_image(self, image):
        if self.protocol == UF_PROTOCOL.UF_SINGLE_PROTOCOL:
            packet = make_packet(UF_COM_SI)
        else:
            packet = make_network_packet(UF_COM_SI, self.module_id)

        self.send_packet(packet)
        received_data = self.read_packet(timeout=10)

        if validate_checksum(received_data, self.protocol) == False:
            return False

        received_data = self.read_packet()

        if self.response_command.error != UF_PROTO_RET_SUCCESS:
            return False

        image_size = self.response_command.size

        received_data = self.read_data(image_size, timeout=20)

        image[0] = received_data # append(received_data)

        return True

    def uf_scan_image(self, image):
        return self.scan_image(image)

    def uf_enroll(self, userID=0, option=0x79): # return uf_ret_code, enrollID, imageQuality
        enrollID = 0
        imageQuality = 0

        self.get_sys_parameter(UF_SYS_ENROLL_MODE)
        ret = self.response_command.error

        if ret != UF_PROTO_RET_SUCCESS:
            return ret, enrollID, imageQuality

        enrollMode = self.response_command.size

        packet = make_packet(UF_COM_ES, param=userID, size=0, flag=option)
        self.send_packet(packet)

        if enrollMode == 0x41:
            iter = 0
            while(iter < 2):
                self.read_response_command(timeout=10)
                ret = self.response_command.error

                if ret == UF_PROTO_RET_SCAN_SUCCESS:
                    print "Scan Success"
                    continue
                elif ret == UF_PROTO_RET_SUCCESS:
                    print "Success"
                    enrollID = self.response_command.param
                    imageQuality = self.response_command.size
                    iter += 1
                else:
                    break


            if ret != UF_PROTO_RET_SUCCESS:
                print "ERROR"

            return UF_RET_SUCCESS, enrollID, imageQuality

    def uf_identify(self): #return userID, subID

        self.send_command(UF_COM_IS)
        self.read_response_command(10)
        self.read_response_command(10)

        if self.response_command.error != UF_PROTO_RET_SUCCESS:
            return 0, 0, 0

        userID = self.response_command.param
        subID = self.response_command.size

        return UF_RET_SUCCESS, userID, subID


    def uf_deleteall(self):

        current_timeout = self.generic_command_timeout
        self.generic_command_timeout = 10

        self.send_command(UF_COM_DA)
        self.read_response_command()
        self.generic_command_timeout = current_timeout
        return UF_RET_SUCCESS

class Module(ModuleBase):
    def __init__(self, port=None, baudrate=115200, protocol=UF_PROTOCOL.UF_SINGLE_PROTOCOL, ascii_mode=False, module_id=1):
        ModuleBase.__init__(self, port, baudrate, protocol, ascii_mode, module_id)