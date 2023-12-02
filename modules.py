"""KOmunikacja ze sterownikiem Q1"""
import subprocess
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.transaction import ModbusRtuFramer
from datetime import datetime
from pymodbus.exceptions import ConnectionException
import socket
import logging
import sys
import time


# logger = logging.getLogger('q1  ')
"""def search_q1_ip():
    # Odnajduje ip sterownika q1
    ip = '192.168.1.'
    for i in (104, 108, 109, 110):
        if ping(ip + str(i)):
            try:
                if socket.gethostbyaddr(ip + str(i))[0] == 'MCHPBOARDxE':
                    return ip + str(i)
                else:
                    return False
            except socket.herror:
                print('No MCHPBOARDxE name found')
                return False"""
def search_q1_ip():
    """Odnajduje ip sterownika q1"""

    ip_list = ['192.168.1.100', '192.168.1.108']
    hostname = socket.gethostname()
    pc_ip = socket.gethostbyname(hostname)
    if pc_ip in ip_list:
        ip_list.remove(pc_ip)
        if len(ip_list) == 1 and ping(ip_list[0]):
            return ip_list[0]
        else:
            return False
    else:
        return False

def ping(ip):
    """Pinguje podany adres ip. Zwraca True lub False na podstawie otrzymanej odpowiedzi"""
    ping_reply = subprocess.run(['ping', '-n', '2', '-w', '100', ip], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    if ping_reply.returncode == 0:
        # ping will return 0 success if destination is unreachable so I have to check this
        if "Host docelowy jest" in str(ping_reply.stdout):
            return False
        else:
            return True
    elif ping_reply.returncode == 1:
        return False


class Q1:
    """Obsługa komunikacji z Q1"""
    oids_name = {
        'ident.identManufacturer': '.1.3.6.1.4.1.32038.2.2.1.1.0',
        'environment.tempSensorBattery': '.1.3.6.1.4.1.32038.2.2.4.2.0',
        'environment.tempSensorOutside': '.1.3.6.1.4.1.32038.2.2.4.3.0',
        'environment.tempSensorInside': '.1.3.6.1.4.1.32038.2.2.4.4.0',
        'tempSensorOutsideConfig': '.1.3.6.1.4.1.32038.2.2.4.6.0',
        'tempSensorInsideConfig': '.1.3.6.1.4.1.32038.2.2.4.7.0',
        'systemDC.batteryTable.batteryEntry.battTemp1': '.1.3.6.1.4.1.32038.2.2.2.87.1.5.0',
        'systemDC.batteryTable.batteryEntry.battTemp2': '.1.3.6.1.4.1.32038.2.2.2.87.1.5.1',
        'systemDC.batteryTable.batteryEntry.battTempConfig': '.1.3.6.1.4.1.32038.2.2.2.87.1.6.0',
        'systemDC_nrOfBattTempSens': '.1.3.6.1.4.1.32038.2.2.2.121.0',
        'environment.environmentTable.environmentEntry.environmentTempValue': '.1.3.6.1.4.1.32038.2.2.4.5.1.28.0',
        'alarms.alarmTbatSensorFail': '.1.3.6.1.4.1.32038.2.2.5.26.0',
        'alarms.alarmsEnvironment.alarmsEnvironmentTable.alarmsEnvironmentEntry.alarmsEnvironmentTempSensorFail':
            '.1.3.6.1.4.1.32038.2.2.5.1.2.1.6.0',
        'alarms.alarmsEnvironment.alarmsEnvironmentTable.alarmsEnvironmentEntry.alarmsEnvironmentTemp':
            '.1.3.6.1.4.1.32038.2.2.5.1.2.1.2.0',
        'alarmsEnvironmentDoorOpen': '.1.3.6.1.4.1.32038.2.2.5.1.2.1.5.0',
        'alarmsEnvironmentSmokeDet': '.1.3.6.1.4.1.32038.2.2.5.1.2.1.4.0',
        'alarmsEnvironmentHeaterZone2On': '.1.3.6.1.4.1.32038.2.2.5.1.2.1.7.0',
        'alarmsEnvironmentHeaterZone1On': '.1.3.6.1.4.1.32038.2.2.5.1.2.1.8.0',
        'alarmsEnvironmentVentOn': '.1.3.6.1.4.1.32038.2.2.5.1.2.1.13.0',
        'alarmsEnvironmentCoolingFail': '.1.3.6.1.4.1.32038.2.2.5.1.2.1.3.0',
        'environmentMode': '.1.3.6.1.4.1.32038.2.2.4.5.1.20.0',
        'environmentHumValue': '.1.3.6.1.4.1.32038.2.2.4.5.1.30.',
        'environmentTempValue': '.1.3.6.1.4.1.32038.2.2.4.5.1.28.',    
        'alarms.alarmsBatteryTable.alarmsBatteryEntry.alarmsBattFuse': '.1.3.6.1.4.1.32038.2.2.5.22.1.4.',
        'alarms.alarmsAsyTable.alarmsAsyEntry.alarmsBattAsyHi': '.1.3.6.1.4.1.32038.2.2.5.24.1.2', 
        'ident.identFirmwareVersion': '.1.3.6.1.4.1.32038.2.2.1.2.0',
        'ident.identSerialNumber': '.1.3.6.1.4.1.32038.2.2.1.4.0',
        'ident.identConfigurationVersion': '.1.3.6.1.4.1.32038.2.2.1.7.0',
        'systemDC.rectNrOfFound': '.1.3.6.1.4.1.32038.2.2.2.12.0'}

    q1_ip = 'start'

    def __init__(self, ip='192.168.1.108', w=None): # ip='192.168.1.108'
        self.ip = ip
        self.w = w
        self.registers_values = {}
        self.alarmy = []
        self.logger = logging.getLogger('q1')

    """def self_test(self):
        # Sprawdza czy moduł odpowiada
        if ping(self.ip):
            if self.snmp_querry(self.oids_name['ident.identManufacturer']) == '\"TELZAS\"':
                return True
            else:
                return False
        else:
            return False"""
    def self_test(self):
        """Sprawdza czy moduł odpowiada"""
        return ping(self.ip)
    def ident_inf(self):
        """Zwraca dane identyfikacyjne sterownika Q1"""
        resp = self.snmp_querry(self.oids_name['ident.identSerialNumber'], self.oids_name['ident.identFirmwareVersion'],
                                self.oids_name['ident.identConfigurationVersion'])
        resp = resp.strip('\"').split('\"\"')
        return resp

    def get_rectifier_serial(self, rect_number):
        """Odczytuje numery seryjne prostowników."""
        query = tuple(['.1.3.6.1.4.1.32038.2.2.2.2.1.20.'+str(i) for i in range(rect_number)])
        response = self.snmp_querry(*query).strip('\"').split('\"\"')
        return response
    def set_dufault_ip(self):
        """Ustawia fabryczne ip i wyłącza dhcp."""
        
        r = self.snmp_querry('.1.3.6.1.4.1.32038.2.2.6.3.1.0', value='192.168.5.120')
        self.snmp_querry('.1.3.6.1.4.1.32038.2.2.6.3.4.0', value=1)
        self.snmp_querry('.1.3.6.1.4.1.32038.2.2.6.3.5.0', value=1)

        print('Adres statyczny sterownika: 192.168.5.120, dhcp wyłączone')
        return r
        

    def alarm_bezpiecznika_odbioru(self):
        """Alar bezpiecznika odbioru"""
        if self.get_registers(start=8003,count=1):
            return self.read_bit(8003, 0)
        else:
            print('Modbus error')

    def snmp_querry(self, *oid, value='x'):
        """Odczyt i zapis po SNMP zmiennych w sterwniku Q1"""
        if value == 'x':
            command = ['snmpget', '-v', '2c', '-O', 'vq', '-c', 'public', '-r', '3', '-t', '1', '-L', 'n', self.ip, *oid]
        elif value == '192.168.5.120':
            command = ['snmpset', '-v', '2c', '-O', 'vq', '-c', 'public', '-r', '3', '-t', '1', '-L', 'n', self.ip,
                       *oid, 's', value]        
        else:
            command = ['snmpset', '-v', '2c', '-O', 'vq', '-c', 'public', '-r', '3', '-t', '1', '-L', 'n', self.ip,
                       *oid, 'i', str(value)]
               
        output = subprocess.run(command, capture_output=True, text=True)
        if output.returncode == 0:
            self.logger.info('Return Q1 snmp: {}'.format(''.join(output.stdout.split("\n"))))
            return ''.join(output.stdout.split('\n'))
        else:
            if self.w:
                self.w['-OUTPUT-'].update('Błąd komunikacji: SNMP!\n', text_color_for_value='red', append=True)
            self.logger.warning(f'Error snmp: {output.stderr}')
            return False

    def rtc(self):
        """Odczytuje aktualny czas sterownika"""
        client = ModbusTcpClient(self.ip, port=1234, framer=ModbusRtuFramer, timeout=1, debug=False)
        try:
            # c = self.conection()
            result = client.read_input_registers(2, 8, unit=0x01)

        except ConnectionException as e:
            # logger.exception(e)
            return e
        finally:
            client.close()
        data = czas = ''
        if not result.isError():
            for i in range(3):
                data += str(int(format(result.getRegister(i), '016b'), 2)) + '-'
            for i in range(3, 6):
                czas += str(int(format(result.getRegister(i), '016b'), 2)) + ':'
            czas = datetime.strptime(data[:-1] + ' ' + czas[:-1], '%Y-%m-%d %H:%M:%S')
            return czas
        else:
            print("error: {}".format(result))

    def check_alarms(self, rejestr, bits, name):
        """Sprawdza stan alarmów i dodaje do listy aktywnych"""
        for i in range(len(name)):
            if bits[i]:
                self.alarmy.append((rejestr, name[i]))

    def read_bit(self, rejestr, bit):
        """Odczyt bitu rejestru"""
        return self.registers_values[rejestr][bit]

    def read_reg(self, rejestr):
        """Odczyt rejestru"""
        return self.registers_values[rejestr]

    def get_registers(self, start=8001, count=75):
        """Odczyt rejestrów"""
        client = ModbusTcpClient(self.ip, port=1234, framer=ModbusRtuFramer, timeout=1, debug=False)
        try:
            # c = self.conection()
            result = client.read_input_registers(start, count, unit=0x01)
        except ConnectionException as e:
            # logger.exception(e)
            print(e)
            return False
        except Exception as e:
            print(e)
            return False
        finally:
            client.close()
        if not result.isError():
            for count, value in enumerate(result.registers):
                lista_bitow = [int(n) for n in bin(value)[2:].zfill(16)]
                lista_bitow.reverse()
                self.registers_values[start + count] = tuple(lista_bitow)
            return True
        else:
            print("Read registers error")
            return False

    def get_register(self, start=281, count=1):
        """Odczyt rejestru"""
        client = ModbusTcpClient(self.ip, port=1234, framer=ModbusRtuFramer, timeout=1, debug=False)
        try:
            # c = self.conection()
            result = client.read_input_registers(start, count, unit=0x01)
        except ConnectionException as e:
            # logger.exception(e)
            print(e)
            return False
        except Exception as e:
            print(e)
            return False
        finally:
            client.close()
        if not result.isError():
            return result
        else:
            print("Read registers error")
            return False


class LOAD:
    """Sterowanie oprnica DC"""
    def __init__(self, ip='192.168.1.103', port=1001):  # PLI-13460
        self.ip = ip
        self.port = port
        # self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.s.connect((self.ip, self.port))
        self.logger = logging.getLogger(self.__class__.__name__)

    def connection(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.ip, self.port))

    def self_test(self):
        """Sprawdza czy moduł odpowiada"""
        return ping(self.ip)

    def get_value(self, q):
        """Odczyt pomiarów z opornicy"""
        try:
            self.s.sendall(('MEAS:'+q+'?;\r\n').encode())
            c = float(self.s.recv(1024).decode()[:-1])
            return c
        except socket.error as e:
            self.logger.exception(e)
            time.sleep(1)
            return e

    def set_mode(self, q, value=0.0):
        """Ustawia tryb pracy opornicy"""
        try:
            self.s.sendall(('FUNC:MODE '+q+';:'+q+' '+str(value)+';\r\n').encode())
        except socket.error as e:
            self.logger.exception(e)
            time.sleep(1)
            return e

    def set_value(self, q, value):
        """Ustawia prąd obciążenia i załącza oprnicę, 0 wyłącza obciązenie"""
        try:
            value = ' '+str(value)
            if value == ' 0':
                self.s.sendall((q + value + ';:INP OFF;\r\n').encode())
            else:
                self.s.sendall((q + value + ';:INP ON;\r\n').encode())
            self.logger.info(f'Set load: {value}')
        except socket.error as e:
            self.logger.exception(e)
            time.sleep(1)
            return e


class MZF:
    """Sterowanie przekaźnikami relpol"""
    def __init__(self, ip='192.168.1.101', w=None):
        # 'espressif.telzas.local' 'ESP_9B6813.telzas.local' ESP_752B0E
        self.w = w
        self.ip = ip
        self.logger = logging.getLogger(self.__class__.__name__)

    def self_test(self):
        """Sprawdza czy moduł odpowiada"""
        return ping(self.ip)

    def check_data(self, v):
        """Sprawdza poprawność wysyłanych danych"""
        if len(v) == 3 and len([i for i in v if i in '01x']) == 3:
            return True
        else:
            print('Niepoprawne dane wejsciowe, (liczba znaków 3 pozycja 1 f1, pozycja 2 f2, pozycja 3 f3 ,'
                  ' 0 - faza off, 1 faza on, x bez zmiany')
            return False

    def realy_switching(self, v):
        """Zmienia stan przekażników"""
        if not self.check_data(v):
            self.logger.warning('Niepoprawne dane wejściowe')
            sys.exit()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # bufsize = s.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
        # print ("Buffer size [Before]:%d" %bufsize)
        s.settimeout(5.0)
        while True:  # [2]
            try:
                s.connect((self.ip, 9090))
            except (ConnectionRefusedError, ConnectionResetError):
                self.logger.exception("Nie można połączyć się z serwerem. Próba ponownego połączenia...")
                time.sleep(5)
            except socket.timeout as e:
                self.logger.exception(e)
                continue
            else:
                break
        resp = False
        try:
            s.send(v.encode())
            while True:
                resp = s.recv(3)
                if resp:
                    resp = resp.decode()
                    # self.logger.info('f1:{} f2:{} f3:{}'.format(*['OFF' if i == '0' else 'ON' for i in list(resp)]))
                    self.logger.info(resp)
                    # if len(sys.argv) == 2:
                    print('f ->', resp)
                    if self.w:
                        for j, i in enumerate(resp):
                            if i == '1':
                                self.w['f' + str(j + 1)].update(value=True)
                            elif i == '0':
                                self.w['f' + str(j + 1)].update(value=False)
                            else:
                                pass  # find_element()
                    break
                else:
                    break
        except socket.timeout as e:
            self.logger.exception('Upłynął czas oczekiwania na odpowiedź od serwera. {}'.format(e))
            s.close()
            time.sleep(2)
            self.realy_switching(v)
        except socket.error as e:
            self.logger.exception('Send: {} Socket.error: {}'.format(v, e))
            s.close()
            time.sleep(2)
            self.realy_switching(v)

        finally:
            s.close()
        s.close()
        return resp


class MZB:
    """Sterowanie przekaźnikami relpol"""
    def __init__(self, ip='192.168.1.105', w=None):
        # 'espressif.telzas.local' 'ESP_9B6813.telzas.local' ESP_752B0E
        self.ip = ip
        self.w = w
        self.logger = logging.getLogger(self.__class__.__name__)

    def self_test(self):
        """Sprawdza czy moduł odpowiada"""
        return ping(self.ip)

    def check_data(self, v):
        """Sprawdza poprawność wysyłanych danych"""
        if len(v) == 4 and len([i for i in v if i in '01x']) == 4:
            return True
        else:
            print('Niepoprawne dane wejsciowe, (liczba znaków 4 pozycja 1 b1, pozycja 2 b2, pozycja 3 b3 ,'
                  'pozycja 4 b4 , 0 - bat off, 1 bat on, x bez zmiany')
            return False

    def realy_switching(self, v):
        """Zmienia stan przekażników"""
        if not self.check_data(v):
            self.logger.warning('Niepoprawne dane wejściowe')
            sys.exit()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # bufsize = s.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
        # print ("Buffer size [Before]:%d" %bufsize)
        s.settimeout(5.0)
        while True:  # [2]
            try:
                s.connect((self.ip, 9090))
            except (ConnectionRefusedError, ConnectionResetError):
                self.logger.exception("Nie można połączyć się z serwerem. Próba ponownego połączenia...")
                time.sleep(5)
            except socket.timeout as e:
                self.logger.exception(e)
                continue
            else:
                break
        resp = False
        try:
            s.send(v.encode())
            while True:
                resp = s.recv(4)
                if resp:
                    resp = resp.decode()
                    # self.logger.info('f1:{} f2:{} f3:{}'.format(*['OFF' if i == '0' else 'ON' for i in list(resp)]))
                    self.logger.info(resp)
                    # if len(sys.argv) == 2:
                    print('b ->', resp)
                    if self.w:
                        for j, i in enumerate(resp):
                            if i == '1':
                                self.w['b' + str(j + 1)].update(value=True)
                            elif i == '0':
                                self.w['b' + str(j + 1)].update(value=False)
                            else:
                                pass  # find_element()
                    break
                else:
                    break
        except socket.timeout as e:
            self.logger.exception('Upłynął czas oczekiwania na odpowiedź od serwera. {}'.format(e))
            s.close()
            time.sleep(2)
            self.realy_switching(v)
        except socket.error as e:
            self.logger.exception('Send: {} Socket.error: {}'.format(v, e))
            s.close()
            time.sleep(2)
            self.realy_switching(v)

        finally:
            s.close()
        s.close()
        return resp


class MWW:
    """Moduł sterujacy płytkami mwy i mwe"""
    def __init__(self, ip='192.168.1.102', w=None):
        self.ip = ip
        self.w = w
        self.logger = logging.getLogger(self.__class__.__name__)

    def odczyt(self, adres):
        """Odczyt stanu płytek mww lub mwy"""
        # try:
        return self.send_packet(str(adres))

    def self_test(self):
        """Sprawdza komunikacje z modułem i poszczególnymi płytkami"""

        if ping(self.ip):
            for nr_m_mww in range(4):  # liczba płytek w module wejśc wyjśc testera docelowo 2 MWE 6 MWY , ip['-RS485-']
                m = self.odczyt(nr_m_mww)
                if m:
                    print(f'Komunikacja MWW testera z płytką o adresie:  {nr_m_mww} OK')

                else:
                    print(f'Brak komunikacji MWW testera z płytką o adresie:  {nr_m_mww}')
                    return False
            return True
        else:
            return False

    def send_packet(self, dane):
        """Komunikacja z modułem"""

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5.0)  # [2]
        while True:
            try:
                s.connect((self.ip, 9090))  # ESP_9B6813, espressif ESP_9C4AA6
            except (ConnectionRefusedError, ConnectionResetError):
                self.logger.exception("Nie można połączyć się z serwerem. Próba ponownego połączenia...")
                time.sleep(5)
            except socket.timeout as e:
                self.logger.exception(e)
                time.sleep(1)
                continue
            else:
                break
        resp = False
        try:
            s.send(dane.encode())
            resp = s.recv(8)
            if resp:
                # print(resp)
                resp = resp.decode()
                self.logger.info(f'Return from socket: {resp}')

            else:
                self.logger.warning('No response from socket')
                time.sleep(2)
                self.send_packet(dane)

        except socket.timeout:
            self.logger.warning("Upłynął czas oczekiwania na odpowiedź od serwera.")
            s.close()
            return False
            # time.sleep(2)
            # self.send_packet(data)
        except socket.error as e:
            self.logger.warning(f'Send: {dane}, Socket.error: {e}')
            s.close()
            return False
            # time.sleep(2)
            # self.send_packet(data)
        finally:
            s.close()
        s.close()
        return resp


class RS485:
    """Komunikacja rs_485"""

    def __init__(self, ip='192.168.1.106', w=None):
        self.ip = ip
        self.w = w
        self.logger = logging.getLogger(self.__class__.__name__)

    def self_test(self):
        """Sprawdza czy moduł odpowiada"""
        return ping(self.ip)

    def send_packet(self, data):
        """Komunikacja z modułem"""

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5.0)  # [2]
        while True:
            try:
                s.connect((self.ip, 9090))  # ESP_9B6813, espressif ESP_9C4AA6
            except (ConnectionRefusedError, ConnectionResetError):
                self.logger.exception("Nie można połączyć się z serwerem. Próba ponownego połączenia...")
                time.sleep(5)
            except socket.timeout as e:
                self.logger.exception(e)
                time.sleep(1)
                continue
            else:
                break
        resp = False
        try:
            s.send(data.encode())
            resp = s.recv(8)
            if resp:
                # print(resp)
                resp = resp.decode()
                self.logger.info(f'Return from socket: {resp}')

            else:
                self.logger.warning('No response from socket')
                time.sleep(2)
                self.send_packet(data)

        except socket.timeout:
            self.logger.warning("Upłynął czas oczekiwania na odpowiedź od serwera.")
            s.close()
            return False
            # time.sleep(2)
            # self.send_packet(data)
        except socket.error as e:
            self.logger.warning(f'Send: {data}, Socket.error: {e}')
            s.close()
            return False
            # time.sleep(2)
            # self.send_packet(data)
        finally:
            s.close()
        s.close()
        return resp


class Fluke8845A:
    """Komunikacja z Fluke 8845A"""

    def __init__(self, ip='192.168.7.91', port=3490):  # PLI-13460
        self.ip = ip
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.ip, self.port))
        self.logger = logging.getLogger(self.__class__.__name__)

    def self_test(self):
        """Sprawdza czy moduł odpowiada"""
        return ping(self.ip)

    def get_value(self):
        """Odczyt pomiarów z miernika"""
        try:
            self.s.sendall('FETCh3?\n'.encode())
            time.sleep(0.25)
            data = self.s.recv(1024)
            if len(data) > 1:
                self.s.close()
                return float(data.decode()[:-1])
            else:
                print('No respnse')
                self.s.close()
                return False
        except socket.error as e:
            self.logger.exception(e)
            time.sleep(1)
            self.s.close()
            return e


if __name__ == "__main__":

    # import q1_alarm_registers
    """m = Q1Unit('192.168.1.140')
    print(m.registers_values)
    print('Time: ', m.rtc())
    time.sleep(1)
    m.get_registers(start=281, count=1)
    print(m.registers_values)
    print(m.registers_values[281])
    time.sleep(1)
    # print(m.get_register())
    r = m.get_register().registers[0]
    print(m.registers_values)
    del m
    print(r)
    m = Q1Unit('192.168.1.122')
    print(m.snmp_querry(m.oids_name['environment.tempSensorBattery']))"""
    # m = RelpolOnOff(3)
    # m.self_test()
    # m.realy_switching('111')
    # print(dir(RS485))
    """fazy = MZF()
    fazy.realy_switching('111')
    fazy = MZF()
    fazy.realy_switching('1111')"""
    # fluke = Fluke8845A()
    # print(fluke.self_test())
    # print(fluke.get_value())
    """fazy = MZF()
    fazy.realy_switching('111')
    time.sleep(8)
    klasa = Q1
    print(klasa.q1_ip)
    klasa.q1_ip = search_q1_ip()
    print(klasa.q1_ip)
    obiekt = Q1()
    print(obiekt.self_test())
    fazy.realy_switching('000')
    load_ac = LOAD(ip='192.168.4.184', port=8000)
    print(load_ac.self_test())
    time.sleep(1)
    load_ac.set_value('CURR', 0.0)
    time.sleep(1)
    r = load_ac.get_value('CURR')
    print(r)
    mww = MWW()
    print(mww.odczyt(2))
    mww.send_packet('2,2,0')
    time.sleep(5)
    print(mww.odczyt(2))
    time.sleep(1)
    mww.send_packet('2,2,1')
    
    time.sleep(5)
    print(mww.odczyt(2))"""
    #mww = MWW()
    sterownik = Q1(ip='192.168.1.108')
    print(sterownik.get_rectifier_serial(5))
    #mww.send_packet('2,2,0')
    #time.sleep(5)
    #print('alarm')
    #print(sterownik.snmp_querry('.1.3.6.1.4.1.32038.2.2.5.24.1.2.0'))
    #mww.send_packet('2,2,1')
    #time.sleep(6)
    #print('brak')
    #print(sterownik.snmp_querry('.1.3.6.1.4.1.32038.2.2.5.24.1.2.0'))    
    #sterownik = Q1()
    #print(sterownik.snmp_querry('.1.3.6.1.4.1.32038.2.2.5.22.1.4.0'))
    #print(sterownik.snmp_querry('.1.3.6.1.4.1.32038.2.2.5.24.1.2.0')) .1.3.6.1.4.1.32038.2.2.5.24.1.2.0
    #r = tuple(['.1.3.6.1.4.1.32038.2.2.2.2.1.20.'+str(i) for i in range(4)])
    #print('zerowanie: ',sterownik.snmp_querry('.1.3.6.1.4.1.32038.2.2.2.13.0', value=0))
    #time.sleep(5)
    #print(sterownik.get_rectifier_serial())
    #print('Liczba prostowników: ',sterownik.snmp_querry('.1.3.6.1.4.1.32038.2.2.2.13.0'))
    #print('ip: ',sterownik.set_dufault_ip())
    #sterownik.snmp_querry('.1.3.6.1.4.1.32038.2.2.13.1.0', value=3637)
    #resp = sterownik.snmp_querry('.1.3.6.1.4.1.32038.2.2.2.2.1.23.' + str(2), value=3) 
    #print(sterownik.snmp_querry('.1.3.6.1.4.1.32038.2.2.5.1.2.1.5.0', '.1.3.6.1.4.1.32038.2.2.5.1.2.1.4.0', '.1.3.6.1.4.1.32038.2.2.5.1.2.1.7.0', '.1.3.6.1.4.1.32038.2.2.5.1.2.1.8.0', '.1.3.6.1.4.1.32038.2.2.5.1.2.1.13.0', '.1.3.6.1.4.1.32038.2.2.5.1.2.1.3.0'))

    











