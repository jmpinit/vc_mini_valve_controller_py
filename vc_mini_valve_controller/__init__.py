# Implements serial control of the VC Mini Valve Controller according to the specification found here:
# https://downloads.fgyger.ch/vc-mini/Manual%20serial%20interface%20VC%20Mini%20rev%202.00%20en.pdf

import serial
import time

ADDRESS_VALVE = 0
ADDRESS_MASTER = 8


class Microvalve:
    def __init__(self, port_name, baud_rate=38400):
        self.port = serial.Serial(port_name, baud_rate, timeout=1)

        self.buffer = ''
        self.current_address = 0

    def read_line(self):
        """Blocking read of the next line received on the serial port"""
        while True:
            self.buffer += self.port.read().decode('utf8')

            if '\n' in self.buffer:
                lines = self.buffer.split('\n')
                line = lines[0]
                self.buffer = '\n'.join(lines[1:])
                return line

    def disconnect(self):
        self.port.close()

    def reset(self):
        # Send ^R to reset and then escape to enter terminal mode
        self.port.write(bytes([0x12, 0x1b]))

        # Wait for welcome/mode message to be printed
        while True:
            if self.read_line().strip() == 'TERMINAL-Mode':
                break

    def init(self):
        self.reset()

        self.command('0*')
        self.command('0n')

    def command(self, cmd):
        self.port.write(cmd.encode('utf8'))
        # print('tx:', cmd)
        reply = self.read_line()
        # print('rx:', reply)

        # TODO: validate reply
        # if not reply.startswith('>'):
        #     raise Exception('Unexpected reply to command')

        return reply

    def set_address(self, address):
        if address < 0 or address > 8:
            raise Exception('Address out of range')

        self.command(f'{address}*')
        self.current_address = address

    def get_address(self):
        return int(self.command('='))

    def set_plc_standard_mode(self):
        if not self.current_address == ADDRESS_MASTER:
            self.set_address(ADDRESS_MASTER)

        self.command('00F')

    def set_plc_last_state_restore_mode(self):
        if not self.current_address == ADDRESS_MASTER:
            self.set_address(ADDRESS_MASTER)

        self.command('01F')

    def set_param_selection_type(self, sel_type):
        # TODO
        raise Exception('Unimplemented')

    def get_param_selection_type(self):
        # TODO
        raise Exception('Unimplemented')

    def set_baud_rate(self, baud_rate):
        if not self.current_address == ADDRESS_MASTER:
            self.set_address(ADDRESS_MASTER)

        if baud_rate == 9600:
            self.command('0%')
        elif baud_rate == 19200:
            self.command('1%')
        elif baud_rate == 38400:
            self.command('2%')
        elif baud_rate == 57600:
            self.command('3%')
        elif baud_rate == 115200:
            self.command('4%')
        elif baud_rate == 230400:
            self.command('5%')
        else:
            raise Exception('Cannot set specified baud rate')

    def set_shot_trigger_mode(self):
        """Sets single shot trigger mode.
        The valve is opened according to the shot settings at a positive edge
        of the external hardware input"""
        if not self.current_address == ADDRESS_VALVE:
            self.set_address(ADDRESS_VALVE)

        self.command('X')

    def set_continuous_trigger_mode(self):
        """Sets continuous trigger mode.
        The valve is opened as long as the hardware input is high"""
        if not self.current_address == ADDRESS_VALVE:
            self.set_address(ADDRESS_VALVE)

        self.command('T')

    def set_series_trigger_mode(self):
        """Sets series trigger mode.
        The valve is opened according to the shot settings, including the number
        of shots configured via the G parameter, at a positive edge on the
        external hardware input"""
        if not self.current_address == ADDRESS_VALVE:
            self.set_address(ADDRESS_VALVE)

        self.command('P')

    def set_endless_trigger_mode(self):
        """Sets series trigger mode.
        Valve shots are fired according to the configured shot settings as long
        as the external hardware input is high"""
        if not self.current_address == ADDRESS_VALVE:
            self.set_address(ADDRESS_VALVE)

        self.command('L')

    def stop_triggering(self):
        if not self.current_address == ADDRESS_VALVE:
            self.set_address(ADDRESS_VALVE)

        self.command('S')

    def single_shot(self, v1, v2):
        if not self.current_address == ADDRESS_VALVE:
            self.set_address(ADDRESS_VALVE)

        if v1 and v2:
            self.command('V')
        else:
            if v1:
                self.command('Y')
            else:
                self.command('Z')

    def series_shot(self, v1, v2):
        if not self.current_address == ADDRESS_VALVE:
            self.set_address(ADDRESS_VALVE)

        if v1 and v2:
            self.command('U')
        else:
            if v1:
                self.command('Q')
            else:
                self.command('R')

    def series_shot_stop(self):
        if not self.current_address == ADDRESS_VALVE:
            self.set_address(ADDRESS_VALVE)

        self.command('S')

    def load_parameters(self, valve, set_index):
        assert valve == 0 or valve == 1
        assert 0 <= set_index <= 3

        if not self.current_address == ADDRESS_VALVE:
            self.set_address(ADDRESS_VALVE)

        if valve == 0:
            self.command(f'{set_index}n')
        else:
            self.command(f'{set_index + 4}n')

    def store_parameters(self, valve, set_index):
        assert valve == 0 or valve == 1

        if not self.current_address == ADDRESS_VALVE:
            self.set_address(ADDRESS_VALVE)

        if valve == 0:
            self.command(f'{set_index}N')
        else:
            self.command(f'{set_index + 4}N')
            
    def set_peak_time(self, value):
        assert 10 <= value <= 65535

        if not self.current_address == ADDRESS_VALVE:
            self.set_address(ADDRESS_VALVE)

        self.command(f'{value}A')
            
    def set_open_time(self, value):
        assert 10 <= value <= 9999999

        if not self.current_address == ADDRESS_VALVE:
            self.set_address(ADDRESS_VALVE)

        self.command(f'{value}B')
            
    def set_cycle_time(self, value):
        assert 10 <= value <= 9999999

        if not self.current_address == ADDRESS_VALVE:
            self.set_address(ADDRESS_VALVE)

        self.command(f'{value}C')
            
    def set_peak_current(self, value):
        assert 0 <= value <= 15

        if not self.current_address == ADDRESS_VALVE:
            self.set_address(ADDRESS_VALVE)

        # TODO: input current instead of index
        # Ip = 450mA + (D * 50mA)
        self.command(f'{value}D')
            
    def set_shot_count(self, value):
        assert 0 <= value <= 65535

        if not self.current_address == ADDRESS_VALVE:
            self.set_address(ADDRESS_VALVE)

        self.command(f'{value}G')
    
    def zero_shot_counter(self, valve):
        raise Exception('Unimplemented')

    # TODO: implement parameter reading
