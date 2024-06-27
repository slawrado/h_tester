"""Klasy do wykonywania poszczególnych testów"""
import modules
import time
from datetime import datetime
import logging
import os, sys
import errno
from pathlib import Path

try:
    os.makedirs('log')
except OSError as e:
    if e.errno != errno.EEXIST:
        raise
fle = Path('log\\tester.log')
fle.touch()  # exist_ok=True
logger = logging.getLogger('')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(fle)
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

test_classes = []


def register(decorated):
    test_classes.append(decorated)   
    return decorated


def printr(napis, w, log, color=None):
    """Koloruje napisy w oknie komunikatów, przesyła info do pliku logowania"""
    if color and w:
        w['-OUTPUT-'].update(napis + '\n', text_color_for_value=color, append=True)
    else:
        print(napis)
    """if w:
    #    w.refresh()
    else:
        pass """
    log.info(napis)


def sec2min(total_seconds):
    """Zamienia sekundy na godziny minuty sekundy"""
    total_seconds = int(round(total_seconds))
    time_string = "{:02d}:{:02d}:{:02d}".format(total_seconds // 3600, total_seconds // 60, total_seconds % 60)
    return time_string

@register
class TestStycznika:

    """Wykonuje rozwarcie i zwarcie styczników i weryfikuje odpowiednie alarmy sterownika."""
    test_number = 5
    test_name = 'Test styczników'
    config_name = 'Styczniki'
    config_range = list(range(4))
    required_modules = (modules.Q1, )
    number_tests = 0
    test_result = False    

    def __init__(self, number=0, w=None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.q1 = None
        self.w = w
        self.number = number

    def get_modules(self):
        """Tworzy obiekty modułów używanych przy wykonywaniu testu"""
        if self.number:
            self.q1 = modules.Q1()


    def stycznik_open(self, i):
        """Otwiera stycznik"""
        if not self.q1:
            self.get_modules()
        if i == 0:
            tryb, stan = '.1.3.6.1.4.1.32038.2.2.14.31.0', '.1.3.6.1.4.1.32038.2.2.14.4.0'
        elif i == 1:
            tryb, stan = '.1.3.6.1.4.1.32038.2.2.14.30.0', '.1.3.6.1.4.1.32038.2.2.14.8.0'
        elif i == 2:
            tryb, stan = '.1.3.6.1.4.1.32038.2.2.14.30.0', '.1.3.6.1.4.1.32038.2.2.14.12.0'
        else:
            return 'Ilość styczników poza zakresem'
        if self.q1.snmp_querry(tryb, value=1) == '1':  # tryb pracy manual
            self.logger.info('Tryb stycznika manualny')
            time.sleep(1)
            if self.q1.snmp_querry(stan, value=0) == '0':  # rgr open
                self.logger.info('Stycznik open')
                time.sleep(5)
                return 0
            else:
                self.logger.warning('Q1 nie otwiera stycznika.')
                return False
        else:
            self.logger.warning('Q1 nie przełącza stycznika w tryb manualny.')
            return False

    def stycznik_close(self, i):
        """Zamyka stycznik"""
        if not self.q1:
            self.get_modules()
        if i == 0:
            tryb, stan = '.1.3.6.1.4.1.32038.2.2.14.31.0', '.1.3.6.1.4.1.32038.2.2.14.4.0'
        elif i == 1:
            tryb, stan = '.1.3.6.1.4.1.32038.2.2.14.30.0', '.1.3.6.1.4.1.32038.2.2.14.8.0'
        elif i == 2:
            tryb, stan = '.1.3.6.1.4.1.32038.2.2.14.30.0', '.1.3.6.1.4.1.32038.2.2.14.12.0'
        else:
            return 'Ilość styczników poza zakresem'
        if self.q1.snmp_querry(tryb) == '0':  # tryb auto
            if self.q1.snmp_querry(tryb, value=1) == '1':  # tryb manual
                pass
            else:
                self.logger.warning('Q1 nie przełącza stycznika w tryb manual')
                return False
        if self.q1.snmp_querry(stan, value=1) == '1':  # rgr close
            time.sleep(2)
            self.logger.info('Stycznik close')
            if self.q1.snmp_querry(tryb, value=0) == '0':  # tryb pracy auto
                self.logger.info('Stycznik tryb auto')
                return 1
            else:
                self.logger.warning('Q1 nie przełącza stycznika w tryb auto')
                return False
        else:
            self.logger.warning('Q1 nie zamyka stycznika.')
            return False

    def test(self):
        self.get_modules()
        start = datetime.now()
        oids_list, oids, ss = [], {0: '.1.3.6.1.4.1.32038.2.2.14.4.0', 1: '.1.3.6.1.4.1.32038.2.2.14.8.0',
                                   2: '.1.3.6.1.4.1.32038.2.2.14.12.0'}, ''
        for i in range(self.number):
            oids_list.append(oids[i])
            ss += '1'  # stan styczników gdy zamknięte (do porównania z odczytem z q1)
        stan_stycznikow = self.q1.snmp_querry(*tuple(oids_list))
        if stan_stycznikow == ss:
            pass
        else:
            printr('Przed rozpoczęciem testu styczników wykryto otwarty stycznik nr {}!'.format(
                stan_stycznikow.index('0')), self.w, self.logger, color='red')
            return False
        self.logger.info(
            'Test styczników rozwiera (i zwiera) kolejne styczniki i sprawdza wystąpienie (lub brak) alarmów w Q1')
        printr('Start testu styczników: {:02d}:{:02d}:{:02d}'.format(start.hour, start.minute, start.second), self.w,
               self.logger)
        printr(f'Liczba zadeklarowanych styczników: {self.number}', self.w, self.logger)
        styczniki = {0: 'RGR', 1: 'stycznika grupy nr 1', 2: 'stycznika grupy nr 2'}
        for i in range(self.number):
            stycznik = self.stycznik_open(i)
            time.sleep(1)
            self.q1.get_registers(start=8001, count=3)
            if i == 0:  # RGR
                alarm = self.q1.read_bit(8001, 7)
            else:  # grupy
                alarm = self.q1.read_bit(8003, i + 3)
            self.logger.info('Stan stycznika nr {}: {} alarm: {}'.format(i, stycznik, alarm))
            if alarm == 1 and stycznik == 0:
                printr('Test {} OK'.format(styczniki[i]), self.w, self.logger)
                self.stycznik_close(i)

            else:
                self.logger.warning('Error, test {} negatywny'.format(styczniki[i]))
                self.logger.info('Stan stycznika nr {}: {} alarm: {}'.format(i, stycznik, alarm))
                self.stycznik_close(i)
                return False
            if self.w:
                self.w['progress'].update_bar(i + 1, self.number)
                time.sleep(1)
        stop = datetime.now()
        printr('Koniec testu styczników: {:02d}:{:02d}:{:02d} Czas wykonania {}'.format(stop.hour, stop.minute,
                                                                                        stop.second, sec2min(
                (stop - start).total_seconds())), self.w, self.logger)
        if self.w:
            self.w['progress'].update_bar(0, 0)
        return True

@register
class TestBocznika:

    """Odcina zasilanie AC, sprawdza kierunek i wartość pradu baterii."""
    test_number = 6
    test_name = 'Test boczników'
    config_name = 'Boczniki'
    config_range = list(range(2))
    required_modules = (modules.Q1, modules.MZF, modules.LOAD)
    number_tests = 0
    test_result = False


    def __init__(self, number=0, w=None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.q1 = None
        self.w = w
        self.fazy = None
        self.load = None
        self.number = number

    def get_modules(self):
        """Tworzy obiekty modułów urzywanych przy wykonywaniu testu"""
        if self.number:
            self.q1 = modules.Q1()
            self.fazy = modules.MZF()
            self.load = modules.LOAD()
            self.load.connection()

    def test(self):
        self.get_modules()
        # load = opornica_dc.Opornica_dc(ip=self.opornica_ip)
        stycznik = TestStycznika()
        obc = 5.0
        start = datetime.now()
        self.logger.info('Test boczników: podaje obciążenie, odłącza zasilanie i sprawdza poprawność kierunku'
                         ' i wartości prądu baterii')
        printr('Start testu boczników: {:02d}:{:02d}:{:02d}'.format(start.hour, start.minute, start.second),
               self.w, self.logger)
        printr(f'Liczba zadeklarowanych boczników: {self.number}', self.w, self.logger)
        test = False
        if self.q1.snmp_querry('.1.3.6.1.4.1.32038.2.2.14.4.0') == '0':  # otwarty RGR
            self.logger.debug('Wykryto otwarty RGR')
            if not stycznik.stycznik_close(0):
                printr('RGR otwarty nie można wykonac testu', self.w, self.logger, color='red')
                del stycznik
                return test

        self.fazy.realy_switching('000')

        self.load.set_mode('CURR')
        time.sleep(2)
        self.load.set_value('CURR', obc)
        time.sleep(2)
        #  l = number

        buttery_current = self.q1.snmp_querry('.1.3.6.1.4.1.32038.2.2.2.14.0')

        if int(buttery_current) < 0:
            printr('Kierunek prądu OK', self.w, self.logger)
            if abs((int(buttery_current) + obc * 1000) / 1000) < 1:
                printr('Wartośc pradu OK', self.w, self.logger)
                test = True
            else:
                printr('Nieprawidłowe wskazanie wartości prądu', self.w, self.logger)
        else:
            printr('Nieprawidłowe wskazanie kieruneku prądu', self.w, self.logger)
        if self.w:
            self.w['progress'].update_bar(1, 1)
            time.sleep(1)
            self.w['progress'].update_bar(0, 0)
        self.load.set_value('CURR', 0)
        self.fazy.realy_switching('111')
        stop = datetime.now()
        printr('Koniec testu boczników: {:02d}:{:02d}:{:02d} Czas wykonania {}'.format(stop.hour, stop.minute,
                stop.second, sec2min((stop - start).total_seconds())), self.w, self.logger)
        del stycznik
        return test

@register
class TestRs485:
    """Odczytuje rejestr 281 po modbus RTU i over TCP i porównuje odczyty"""
    test_number = 11
    test_name = 'Test komunikacji rs485 modbus'
    config_name = 'RS485'
    config_range = list(range(2))
    required_modules = (modules.Q1, modules.RS485)
    number_tests = 0
    test_result = False

    def __init__(self, number=0, w=None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.q1 = None
        self.w = w
        self.rs485 = None
        self.number = number

    def get_modules(self):
        """Tworzy obiekty modułów używanych przy wykonywaniu testu"""
        if self.number:
            self.q1 = modules.Q1()
            self.rs485 = modules.RS485()

    def test(self):
        self.get_modules()
        start = datetime.now()
        print('Ustawienie w q1 modbus slave na RS485_2')
        self.q1.snmp_querry(self.q1.oids_name['modbusSlave_UartIdx'], value=3)
        time.sleep(2)
        self.logger.info('Test: poprawności komunikacji portu rs485')
        printr(
            'Start testu komunikacji portu rs485: {:02d}:{:02d}:{:02d}'.format(start.hour, start.minute, start.second),
            self.w, self.logger)
        printr(f'Liczba zadeklarowanych portów: {self.number}', self.w, self.logger)
        stan_pracy_rtu = self.rs485.send_packet('000')
        print('stan pracy (rtu):', stan_pracy_rtu)
        if self.q1.get_registers(start=281, count=1):
            time.sleep(1)
            stan_pracy_tcp = self.q1.get_register().registers[0]
            print('stan pracy (tcp):', stan_pracy_tcp)
        else:
            printr('Modbus error', self.w, self.logger, color='red')
            return False
        if int(stan_pracy_rtu) == stan_pracy_tcp:
            print('Komunikacja modbus RS485 OK')
            stop = datetime.now()
            printr('Koniec testu komunikacji portu rs485: {:02d}:{:02d}:{:02d} Czas wykonania {}'.format(stop.hour,
                                                                                                         stop.minute,
                                                                                                         stop.second,
                                                                                                         sec2min((
                                                                                                                             stop - start).total_seconds())),
                   self.w, self.logger)
            return True
        else:
            print('Komunikacja modbus RS485 Error')
            return False

@register
class TestBezpiecznikaBat:
    """Wymusza i sprawdza pojawienie się i zejście kolejnych alarmów bezpiecznika baterii."""
    test_number = 13
    test_name = 'Test alarmu bezpiecznika baterii'
    config_name = 'Alarm bezpiecznika baterii'
    config_range = list(range(2))
    required_modules = (modules.Q1, modules.MWW)
    number_tests = 0
    test_result = False

    def __init__(self, number=0, w=None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.q1 = None
        self.w = w
        self.mww = None
        self.number = number
    

    def get_modules(self):
        """Tworzy obiekty modułów używanych przy wykonywaniu testu"""
        if self.number:
            self.q1 = modules.Q1()
            self.mww = modules.MWW()

    def test(self):
        self.get_modules()
        adres = 2
        start = datetime.now()
        self.logger.info(
            'Test polega na podaniu minusa na wejscie alarmu bezpiecznika baterii w sterowniku')
        printr('Start testu alarmu bezpiecznika baterii: {:02d}:{:02d}:{:02d}'.format(start.hour, start.minute,
                                                                                   start.second), self.w,
               self.logger)
        printr(f'Liczba zadeklarowanych alarmów: {self.number}', self.w, self.logger)
        self.mww.send_packet(str(adres + 1) + ',255')
        time.sleep(2)

        alarm_bezpiecznika_baterii = self.q1.snmp_querry('.1.3.6.1.4.1.32038.2.2.5.22.1.4.0')
        
        if alarm_bezpiecznika_baterii == '0':
            self.logger.info('Stan alarmu bezpiecznika baterii {}'.format(alarm_bezpiecznika_baterii))
        else:
            self.logger.warning('Stan alarmu bezpiecznika baterii {}'.format(alarm_bezpiecznika_baterii))
            printr('Przed rozpoczeciem testu wykryto alarm bezpiecznika baterii!', self.w, self.logger, color='red')
            return False
        r = self.mww.send_packet(str(adres) + ',2,0')
        time.sleep(5)
        alarm_bezpiecznika_baterii = self.q1.snmp_querry('.1.3.6.1.4.1.32038.2.2.5.22.1.4.0')
        print('alarm_bezpiecznika_baterii:', alarm_bezpiecznika_baterii)
        if alarm_bezpiecznika_baterii == '1':
            self.logger.info(
                'Stan wysterowania przekaźników MWY testera: {:08b} | {: 2}'.format((int(r)), 1))
            printr('Alaram bezpiecznika baterii:  OK', self.w, self.logger)
        else:
            printr('Error, test alaramu bezpiecznika baterii negatywny {}'.format(alarm_bezpiecznika_baterii), self.w,
                   self.logger)
            return False

        r = self.mww.send_packet(str(adres) + ',2,1')
        time.sleep(6)

        alarm_bezpiecznika_baterii = self.q1.snmp_querry('.1.3.6.1.4.1.32038.2.2.5.22.1.4.0')
        if alarm_bezpiecznika_baterii == '0':
            self.logger.info(
                'Stan wysterowania przekażników MWY testera: {:08b} | {: 2}'.format((int(r)), 1))
            printr('Brak alarmu:          OK', self.w, self.logger)
        else:
            self.logger.warning(
                'Error test alaramu bezpiecznika baterii negatywny: 0 = {}'.format(alarm_bezpiecznika_baterii))
            return False
        if self.w:
            self.w['progress'].update_bar(1, self.number)
            time.sleep(1)

        stop = datetime.now()
        printr(
            'Koniec testu alaramu bezpiecznika baterii: {:02d}:{:02d}:{:02d} Czas wykonania {}'.format(stop.hour,
                                                                                                    stop.minute,
                                                                                                    stop.second,
                                                                                                    sec2min((
                                                                                                                        stop - start).total_seconds())),
            self.w, self.logger)
        if self.w:
            self.w['progress'].update_bar(0, 0)
        return True


    # .1.3.6.1.4.1.32038.2.2.5.22.1.4.0 bezpiecznik baterii
    # 1.3.6.1.4.1.32038.2.2.5.24.1.2.0   alarms.alarmsAsyTable.alarmsAsyEntry.alarmsBattAsyHi	  
@register
class TestAsymBat:
    """Sprawdzenie zadziałania alarmu asymetrii baterii modernizacja enetek, podaje minus na wej alarmu asymetrii sterownika"""
    test_number = 12
    test_name = 'Test asymetrii baterii'
    config_name = 'Asymetria baterii'
    config_range = list(range(2))
    required_modules = (modules.Q1, modules.MWW)
    number_tests = 0
    test_result = False

    def __init__(self, number=0, w=None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.q1 = None
        self.w = w
        self.mww = None
        self.number = number

    def get_modules(self):
        """Tworzy obiekty modułów używanych przy wykonywaniu testu"""
        if self.number:
            self.q1 = modules.Q1()
            self.mww = modules.MWW()

    def test(self):
        self.get_modules()
        adres = 2
        start = datetime.now()
        self.logger.info(
            'Test polega na podaniu minusa na wejscie alarmu asymetrii baterii w sterowniku')
        printr('Start testu alarmu asymetrii baterii: {:02d}:{:02d}:{:02d}'.format(start.hour, start.minute,
                start.second), self.w, self.logger)
        printr(f'Liczba zadeklarowanych alarmów: {self.number}', self.w, self.logger)
        self.mww.send_packet(str(adres + 1) + ',255')
        time.sleep(2)

        alarm_asymetrii_baterii = self.q1.snmp_querry('.1.3.6.1.4.1.32038.2.2.5.24.1.2.0')

        if alarm_asymetrii_baterii == '0':
            self.logger.info('Stan alarmu asymetrii baterii {}'.format(alarm_asymetrii_baterii))
        else:
            self.logger.warning('Stan alarmu asymetrii baterii {}'.format(alarm_asymetrii_baterii))
            printr('Przed rozpoczeciem testu wykryto alarm asymetrii baterii!', self.w, self.logger, color='red')
            return False



        r = self.mww.send_packet(str(adres) + ',1,0')
        time.sleep(5)
        alarm_asymetrii_baterii = self.q1.snmp_querry('.1.3.6.1.4.1.32038.2.2.5.24.1.2.0')
        if alarm_asymetrii_baterii == '1':
            self.logger.info('Stan wysterowania przekaźników MWY testera: {:08b} | {: 2}'.format((int(r)), 2))
            printr('Alaram asymetrii baterii: OK', self.w, self.logger)
        else:
            printr('Error, test alaramu asymetrii baterii negatywny {}'.format(alarm_asymetrii_baterii), self.w, self.logger)
            return False

        r = self.mww.send_packet(str(adres) + ',1,1')
        time.sleep(6)

        alarm_asymetrii_baterii = self.q1.snmp_querry('.1.3.6.1.4.1.32038.2.2.5.24.1.2.0')
        if alarm_asymetrii_baterii == '0':
            self.logger.info('Stan wysterowania przekażników MWY testera: {:08b} | {: 2}'.format((int(r)), 2))
            printr('Brak alarmu:          OK', self.w, self.logger)
        else:
            self.logger.warning(
                'Error test alaramu asymetrii baterii negatywny: 0 = {}'.format(alarm_asymetrii_baterii))
            return False
        if self.w:
            self.w['progress'].update_bar(1, self.number)
            time.sleep(1)

        stop = datetime.now()
        printr(
            'Koniec testu alaramu asymetrii baterii: {:02d}:{:02d}:{:02d} Czas wykonania {}'.format(stop.hour, stop.minute,
            stop.second, sec2min((stop - start).total_seconds())), self.w, self.logger)
        if self.w:
            self.w['progress'].update_bar(0, 0)
        return True

@register
class TestInput:
    """Zwiera wejścia MWE i sprawdza reakcję Q1."""
    test_number = 4
    test_name = 'Test wejść (MWE)'
    config_name = 'Wejscia (MWE)'
    config_range = list(range(0, 17, 8))
    required_modules = (modules.Q1, modules.MWW)
    number_tests = 0
    test_result = False

    def __init__(self, number=0, w=None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.q1 = None
        self.w = w
        self.mww = None
        self.number = number

    def get_modules(self):
        """Tworzy obiekty modułów urzywanych przy wykonywaniu testu"""
        if self.number:
            self.q1 = modules.Q1()
            self.mww = modules.MWW()

    def test(self):

        adres = 3  # przy pełnej obsadzie sprzętowej adres 6 (2 mwe, 4 + 2 mwy)
        self.get_modules()
        start = datetime.now()
        self.logger.info('Test wejść: zwiera kolejne wejścia MWE i weryfikuje poprzez odczyt stanu MWE w Q1')
        printr('Start {}: {:02d}:{:02d}:{:02d}'.format('Test wejść (MWE)', start.hour, start.minute, start.second), self.w, self.logger)
        printr(f'Liczba zadeklarowanych wejść: {self.number}', self.w, self.logger)

        for i in range(self.number // 8):
            oid = '.1.3.6.1.4.1.32038.2.2.10.18.1.2.0'
            if i == 1:
                adres += 1
                oid = '.1.3.6.1.4.1.32038.2.2.10.18.1.2.1'
            oid = '.1.3.6.1.4.1.32038.2.2.10.18.1.2.1' # tymczasowo dla drugiej mwe gsmr    
            #print('adres:',adres,'oid:',oid)    
            progress = 0
            d = str(adres) + ',255'
            r = self.mww.send_packet(d)  # reset wyjść MWW testera.
            time.sleep(2)
            mwe = self.q1.snmp_querry(oid)

            if mwe == '255':
                for j in (1, 2, 4, 8, 16, 32, 64, 128):
                    progress += 1
                    r = self.mww.send_packet(str(adres) + ',' + str(j))
                    time.sleep(2)
                    mwe = self.q1.snmp_querry(oid)

                    if r == mwe:
                        printr('MWE {} wej: {} OK'.format(i + 1, progress), self.w, self.logger)
                    else:
                        printr('MWE {} wej: {} error!'.format(i + 1, progress), self.w, self.logger)
                        if self.w:
                            self.w['progress'].update_bar(0, 0)
                        self.mww.send_packet(str(adres) + ',255')  # reset wyjść MWW testera
                        return False
                    if self.w:
                        self.w['progress'].update_bar(progress * (i + 1), self.number)
                    time.sleep(1)
            else:
                printr(f'MWE {i} error - nie można zresetować stanu wejść', self.w, self.logger, color='red')
                self.mww.send_packet(str(adres) + ',255')  # reset wyjść MWW testera
                return False
        self.mww.send_packet(str(adres) + ',255')  # reset wyjść MWW testera
        stop = datetime.now()
        printr(
            'Koniec {}: {:02d}:{:02d}:{:02d} Czas wykonania {}'.format(self.test_name, stop.hour, stop.minute, stop.second,
            sec2min((stop - start).total_seconds())), self.w, self.logger)
        if self.w:
            self.w['progress'].update_bar(0, 0)
        return True



class TestOutputQ1_old:
    """Sprawdza wyjscia Q1"""
    test_number = 2
    test_name = 'Test wyjść (Q1)'
    config_name = 'Wyjścia (Q1)'
    config_range = list(range(5))
    name, adres, offset = 'Q1', 0, 1
    required_modules = (modules.Q1, modules.MWW)
    number_tests = 0
    test_result = False

    def __init__(self, number=0, w=None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.q1 = None
        self.w = w
        self.mww = None
        self.number = number
        #self.offset = 0

    def get_modules(self):
        """Tworzy obiekty modułów używanych przy wykonywaniu testu"""
        if self.number:
            self.q1 = modules.Q1()
            self.mww = modules.MWW()

    def test(self):
        # popen('snmpset -v2c -Ovq -cprivate -r3 -t1 -Ln '+self.q1_ip+' .1.3.6.1.4.1.32038.2.2.17.2.0 i '+str(i))
        self.get_modules()
        """if key_gui == '-OUTPUT-MWY':
            name, adres, offset = 'MWY', 1, 9
        elif key_gui == '-OUTPUT-Q1':
            name, adres, offset = 'Q1', 0, 1
        else:
            print('Nieznany typ wyjść')
            return False"""

        start = datetime.now()
        self.logger.info(
            'Test wyjść załącza przekaźniki wyjściowe {} i sprawdza zwarcie kolejnych wyjść alarmowych'.format(
                self.name))
        printr('Start testu wyjść {}: {:02d}:{:02d}:{:02d}'.format(self.name, start.hour, start.minute, start.second), self.w, self.logger)
        printr(f'Liczba zadeklarowanych wyjść: {self.number}', self.w, self.logger)
        # print('{:08b}'.format(int(self.i2c.send_packet(str(nr)).decode())))
        set_realy = tuple([j + 2 if self.adres == 0 else j + 10 for j in range(self.number)])  # generuje klucze na podstawie liczby wyjśc alarmowych Q1 lub MWY
        print('set_realy',set_realy)
        realy_on = {17: 128, 16: 64, 15: 32, 14: 16, 13: 8, 12: 4, 11: 2, 10: 1, 5: 8, 4: 4, 3: 2,
                    2: 1}  # Klucz załączenie przekaźnika 10-17: MWY, 2-5: Q1
        mask = 0
        # if progress: self.w[progress].update(max_value=number_outputs)
        for i in set_realy:
            mask += realy_on[i]
        print('mask',mask)    
        self.q1.snmp_querry('.1.3.6.1.4.1.32038.2.2.17.2.0', value=0)  # wyzerowanie stanu przekaźników
        time.sleep(2)
        pb = 0  # progress bar
        for i in set_realy:
            pb += 1
            self.q1.snmp_querry('.1.3.6.1.4.1.32038.2.2.17.2.0', value=i)
            time.sleep(2)
            m = self.mww.send_packet(str(self.adres))
            print('m',m)
            r = int(m) & mask
            print('r',r, 'realy_on[i]', realy_on[i])
            if r == realy_on[i]:
                printr('Wyjście: {} OK'.format(i - self.offset), self.w, self.logger)
                self.logger.info('({}) Wyjście: {} OK {:08b}'.format(self.number, i - self.offset, r))
            else:
                printr('Wyjście: {} Error'.format(i - self.offset), self.w, self.logger)
                logger.warning('({}) Wyjście: {} Error  {:8b}'.format(self.number, i - self.offset, r))
                stop = datetime.now()
                printr(
                    'Koniec testu wyjść {}: {:02d}:{:02d}:{:02d} Czas testu {}'.format(self.name, stop.hour, stop.minute,
                                                                                       stop.second, sec2min(
                            (stop - start).total_seconds())), self.w, self.logger)
                return False
            if self.w:
                self.w['progress'].update_bar(pb, len(set_realy))
                time.sleep(1)

        stop = datetime.now()
        printr('Koniec testu wyjść {}: {:02d}:{:02d}:{:02d} Czas testu {}'.format(self.name, stop.hour, stop.minute,
                stop.second, sec2min((stop - start).total_seconds())), self.w, self.logger)
        if self.w:
            self.w['progress'].update_bar(0, 0)
        return True
@register        
class TestOutputQ1:
    """Steruje stanem wyjść Q1 i weyfikuje zmiany."""
    test_number = 2
    test_name = 'Test wyjść (Q1)'
    config_name = 'Wyjścia (Q1)'
    config_range = list(range(5))
    name, adres, offset = 'Q1', 0, 1
    required_modules = (modules.Q1, modules.MWW)
    number_tests = 0
    test_result = False

    def __init__(self, number=0, w=None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.q1 = None
        self.w = w
        self.mww = None
        self.number = number
        self.realy_on = {5: 247, 4: 251, 3: 253, 2: 254}  # Klucze załączenia przekaźników 2-5: Q1, warości stan mwe testera
        self.offset = 2

    def get_modules(self):
        """Tworzy obiekty modułów używanych przy wykonywaniu testu"""
        if self.number:
            self.q1 = modules.Q1()
            self.mww = modules.MWW()

    def test(self):
        # popen('snmpset -v2c -Ovq -cprivate -r3 -t1 -Ln '+self.q1_ip+' .1.3.6.1.4.1.32038.2.2.17.2.0 i '+str(i))
        self.get_modules()
        """if key_gui == '-OUTPUT-MWY':
            name, adres, offset = 'MWY', 1, 9
        elif key_gui == '-OUTPUT-Q1':
            name, adres, offset = 'Q1', 0, 1
        else:
            print('Nieznany typ wyjść')
            return False"""

        start = datetime.now()
        self.logger.info(
            'Test wyjść załącza przekaźniki wyjściowe {} i sprawdza zwarcie kolejnych wyjść alarmowych'.format(
                self.name))
        printr('Start testu wyjść {}: {:02d}:{:02d}:{:02d}'.format(self.name, start.hour, start.minute, start.second), self.w, self.logger)
        printr(f'Liczba zadeklarowanych wyjść: {self.number}', self.w, self.logger)
        # print('{:08b}'.format(int(self.i2c.send_packet(str(nr)).decode())))
        set_realy = tuple([j + self.offset for j in range(self.number)])  # generuje klucze na podstawie liczby wyjśc alarmowych Q1 lub MWY
        
        if self.mww.odczyt(self.adres) != '0':#'255':
            printr('Przed rozpoczęciem testu wyjścia powininy być stanie bezalarmowym', self.w, self.logger, color='red')
            return False

        pb = 0  # progress bar
        for i in set_realy:
            self.q1.snmp_querry('.1.3.6.1.4.1.32038.2.2.17.2.0', value=0)  # wyzerowanie stanu przekaźników
            time.sleep(2)            
            pb += 1
            self.q1.snmp_querry('.1.3.6.1.4.1.32038.2.2.17.2.0', value=i)
            time.sleep(2)
            key_values = self.realy_on[i]
            stan_mwe = self.mww.send_packet(str(self.adres))
            #print(i, key_values, stan_mwe)
            #if self.mww.send_packet(str(self.adres)) == str(self.realy_on[i]):
            if stan_mwe == str(key_values):
                printr('Wyjście: {} OK'.format(i - self.offset + 1), self.w, self.logger)
                self.logger.info('({}) Wyjście: {} OK {:08b}'.format(self.number, i - self.offset + 1, self.realy_on[i]))
            else:
                printr('Wyjście: {} Error'.format(i - self.offset), self.w, self.logger)
                logger.warning('({}) Wyjście: {} Error  {:8b}'.format(self.number, i - self.offset, self.realy_on[i]))
                stop = datetime.now()
                printr(
                    'Koniec testu wyjść {}: {:02d}:{:02d}:{:02d} Czas testu {}'.format(self.name, stop.hour, stop.minute,
                                                                                       stop.second, sec2min(
                            (stop - start).total_seconds())), self.w, self.logger)
                return False
            if self.w:
                self.w['progress'].update_bar(pb, len(set_realy))
                time.sleep(1)
        self.q1.snmp_querry('.1.3.6.1.4.1.32038.2.2.17.2.0', value=0)  # wyzerowanie stanu przekaźników
        time.sleep(2)
        stop = datetime.now()
        printr('Koniec testu wyjść {}: {:02d}:{:02d}:{:02d} Czas testu {}'.format(self.name, stop.hour, stop.minute,
                stop.second, sec2min((stop - start).total_seconds())), self.w, self.logger)
        if self.w:
            self.w['progress'].update_bar(0, 0)
        return True
@register
class TestOutputMWY(TestOutputQ1):
    """Steruje stanem wyjść MWY i weyfikuje zmiany."""
    test_number = 3
    test_name = 'Test wyjść (MWY)'
    config_name = 'Wyjścia (MWY)'
    config_range = list(range(9))
    name, adres, offset = 'MWY', 1, 9
    number_tests = 0
    test_result = False

    def __init__(self, number=0, w=None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.q1 = None
        self.w = w
        self.mww = None
        self.number = number
        #self.realy_on = {17: 127, 16: 191, 15: 223, 14: 239, 13: 247, 12: 251, 11: 253, 10: 254} # Klucze załączenie przekaźnika 10-17: MWY, wartości stan mwe testera
        self.realy_on = {17: 128, 16: 64, 15: 32, 14: 16, 13: 8, 12: 4, 11: 2, 10: 1}
        self.offset = 10
@register
class TestUkb:
    """Sprawdza działanie płytki UKB, Podaje plusa na kolejne zabezpieczenia i weryfikuje wejście i zejście alarmu bezpiecznika odbioru."""
    test_number = 9
    test_name = 'Test kontroli zabezpieczeń odbiorów'
    config_name = 'Zabezpieczenia odbiorów'
    config_range = None
    required_modules = (modules.Q1, modules.MWW)
    number_tests = 0
    test_result = False

    def __init__(self, number=0, w=None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.q1 = None
        self.w = w
        self.mww = None
        self.number = number

    def get_modules(self):
        """Tworzy obiekty modułów używanych przy wykonywaniu testu"""
        if self.number:
            self.q1 = modules.Q1()
            self.mww = modules.MWW()

    def test(self):
        self.get_modules()
        adres = 1
        start = datetime.now()
        self.logger.info(
            'Test polega na podaniu plusa na kolejne zabezpieczenia i sprawdzeniu wystapienia i zejścia alarmu bezpiecznika odbioru w sterowniku')
        printr('Start testu kontroli zabezpieczeń odbiorów: {:02d}:{:02d}:{:02d}'.format(start.hour, start.minute,
                start.second), self.w, self.logger)
        printr(f'Liczba zadeklarowanych zabezpieczeń: {self.number}', self.w, self.logger)
        self.mww.send_packet(str(adres + 1) + ',255')
        time.sleep(2)

        alarm_bezpiecznika_odbioru = self.q1.snmp_querry('.1.3.6.1.4.1.32038.2.2.5.8.0')

        if alarm_bezpiecznika_odbioru == '0':
            self.logger.info('Stan alarmu zbezpieczenia odbioru {}'.format(alarm_bezpiecznika_odbioru))
        else:
            self.logger.warning('Stan alarmu zbezpieczenia odbioru {}'.format(alarm_bezpiecznika_odbioru))
            printr('Przed rozpoczeciem testu wykryto alarm bezpiecznika odbioru!', self.w, self.logger, color='red')
            return False

        for i in range(self.number): # zwieksza adres po przejściu 0 , 8 ,16 (kolejna płytka MWY
            if i % 8 == 0:
                adres += 1

            r = self.mww.send_packet(str(adres) + ',' + str(i) + ',0')
            time.sleep(5)
            alarm_bezpiecznika_odbioru = self.q1.snmp_querry('.1.3.6.1.4.1.32038.2.2.5.8.0')
            if alarm_bezpiecznika_odbioru == '1':
                self.logger.info('Stan wysterowania przekaźników MWY testera: {:08b} | {: 2}'.format((int(r)), i + 1))
                printr('Alaram bezpiecznika: {: 2} OK'.format(i + 1), self.w, self.logger)
            else:
                printr('Error, test zabezpieczeń odbiorów negatywny {}'.format(alarm_bezpiecznika_odbioru), self.w, self.logger)
                return False

            r = self.mww.send_packet(str(adres) + ',' + str(i) + ',1')
            time.sleep(5)

            alarm_bezpiecznika_odbioru = self.q1.snmp_querry('.1.3.6.1.4.1.32038.2.2.5.8.0')
            if alarm_bezpiecznika_odbioru == '0':
                self.logger.info('Stan wysterowania przekażników MWY testera: {:08b} | {: 2}'.format((int(r)), i + 1))
                printr('Brak alarmu:         {: 2} OK'.format(i + 1), self.w, self.logger)
            else:
                self.logger.warning(
                    'Error test zabezpieczeń odbiorów negatywny: 0 = {}'.format(alarm_bezpiecznika_odbioru))
                return False
            if self.w:
                self.w['progress'].update_bar(i + 1, self.number)
                time.sleep(1)

        stop = datetime.now()
        printr(
            'Koniec testu zabezpieczeń odbiorów: {:02d}:{:02d}:{:02d} Czas wykonania {}'.format(stop.hour, stop.minute,
            stop.second, sec2min((stop - start).total_seconds())), self.w, self.logger)
        if self.w:
            self.w['progress'].update_bar(0, 0)
        return True

@register
class TestCzujnikowMZK:
    """Sprawdza komunikację MZK z czujnikami temperatury."""
    test_number = 14
    test_name = 'Test czujników (MZK)'
    config_name = 'Czujniki (MZK)'
    config_range = list(range(2))
    required_modules = (modules.Q1, )
    number_tests = 0
    test_result = False

    def __init__(self, number=0, w=None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.q1 = None
        self.w = w
        self.number = number

    def get_modules(self):
        """Tworzy obiekty modułów używanych przy wykonywaniu testu"""
        if self.number:
            self.q1 = modules.Q1(ip='192.168.5.202')

    def test(self):
        self.get_modules()
        start = datetime.now()
        self.logger.info('Test: sprawdza poprawnosc działania skonfigurowanych czujników')
        printr(
            'Start testu czujników: {:02d}:{:02d}:{:02d}'.
            format(start.hour, start.minute, start.second), self.w, self.logger)
        printr(f'Liczba zadeklarowanych czujników: {self.number}', self.w, self.logger)


        for i in range(self.number):

            if self.w:
                self.w['progress'].update_bar(i + 1, self.number)
   
            odczyt = self.q1.snmp_querry(self.q1.oids_name['environmentTempValue']+str(i)) #self.q1.oids_name['environmentTempValue']
              
            if  odczyt != '2147483647':
                printr(f'temperatura MZK.{i} {odczyt}: OK', self.w, self.logger)
            else:
                printr(f'temperatura MZK.{i}: brak odczytu Error', self.w, self.logger, color='red')
                if self.w:
                    self.w['progress'].update_bar(0, 0)
                return False
        for i in range(self.number):
            if self.w:
                self.w['progress'].update_bar(i + 1, self.number)
            odczyt = self.q1.snmp_querry(self.q1.oids_name['environmentHumValue']+str(i)) 

            if odczyt != '2147483647':
                printr(f'wilgotnosć.{i} {odczyt}:  OK', self.w, self.logger)
            else:
                printr(f'wilgotnosć.{i}: brak odczytu Error', self.w, self.logger, color='red')
                if self.w:
                    self.w['progress'].update_bar(0, 0)
                return False    
        stop = datetime.now()
        printr(
            'Koniec testu czujników MZK: {:02d}:{:02d}:{:02d} Czas wykonania {}'.format(stop.hour, stop.minute,
                                                                                                stop.second,
                                                                                                sec2min((stop - start).total_seconds())), self.w, self.logger)
        if self.w:
            self.w['progress'].update_bar(0, 0)
        return True

@register
class TestCzujnikowTemp:
    """Sprawdza komunikację Q1 z czujnikami temperatury."""
    test_number = 7
    test_name = 'Test czujników temperatury (Q1)'
    config_name = 'Czujniki temperatury (Q1)'
    config_range = list(range(4))
    required_modules = (modules.Q1, )
    number_tests = 0
    test_result = False

    def __init__(self, number=0, w=None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.q1 = None
        self.w = w
        self.number = number

    def get_modules(self):
        """Tworzy obiekty modułów używanych przy wykonywaniu testu"""
        if self.number:
            self.q1 = modules.Q1()

    def test(self):
        self.get_modules()
        start = datetime.now()
        self.logger.info('Test: sprawdza poprawnosc działania skonfigurowanych czyjników')
        printr(
            'Start testu czujników temperatury: {:02d}:{:02d}:{:02d}'.
            format(start.hour, start.minute, start.second), self.w, self.logger)
        printr(f'Liczba zadeklarowanych czujników: {self.number}', self.w, self.logger)
        if self.q1.snmp_querry(self.q1.oids_name['alarms.alarmTbatSensorFail']) == 1:
            printr('Przed rozpoczeciem testu wykryto alarm czujnika temperatury baterii',
                   self.w, self.logger, color='red')
            return False
        liczba_czujnikow_baterii = self.q1.snmp_querry(self.q1.oids_name['systemDC_nrOfBattTempSens'])
        conf_czujnik_temp_zew = self.q1.snmp_querry(self.q1.oids_name['tempSensorOutsideConfig'])
        conf_czujnik_temp_wew = self.q1.snmp_querry(self.q1.oids_name['tempSensorInsideConfig'])

        temperatura = {'systemDC.batteryTable.batteryEntry.battTemp1': False,
                       'systemDC.batteryTable.batteryEntry.battTemp2': False,
                       'environment.tempSensorOutside': False} # 'environment.tempSensorInside': False}

        if liczba_czujnikow_baterii == '2':
            temperatura['systemDC.batteryTable.batteryEntry.battTemp1'], temperatura[
                'systemDC.batteryTable.batteryEntry.battTemp2'] = True, True
        elif liczba_czujnikow_baterii == '1':
            temperatura['systemDC.batteryTable.batteryEntry.battTemp1'] = True

        if conf_czujnik_temp_zew != '0': temperatura['environment.tempSensorOutside'] = True
        #if conf_czujnik_temp_wew != '0': temperatura['environment.tempSensorInside'] = True
        if self.number == list(temperatura.values()).count(True):
            pass
        else:
            #print(temperatura)
            printr(
                f'Liczba zadeklarowanych czujników: {self.number} a liczba czujników do sprawdzenia w Q1 to'
                f' {list(temperatura.values()).count(True)}', self.w, self.logger, color='red')
            logger.warning('Zadeklarowana liczba czujników jest rózna od sprawdzanej')
            return False

        for j, i in enumerate(temperatura):
            if self.w:
                self.w['progress'].update_bar(j + 1, 4)
            if temperatura[i]:
                temperatura[i] = self.q1.snmp_querry(self.q1.oids_name[i])
                if temperatura[i] != '2147483647':
                    printr(f'{i.split(".")[-1]}: {temperatura[i]} OK', self.w, self.logger)
                else:
                    printr(f'{i.split(".")[-1]}: brak odczytu Error', self.w, self.logger, color='red')
                    if self.w:
                        self.w['progress'].update_bar(0, 0)
                    return False

        stop = datetime.now()
        printr(
            'Koniec testu czujników temperatury: {:02d}:{:02d}:{:02d} Czas wykonania {}'.format(stop.hour, stop.minute,
                                                                                                stop.second,
                                                                                                sec2min((stop - start).total_seconds())), self.w, self.logger)
        if self.w:
            self.w['progress'].update_bar(0, 0)
        return True

@register
class TestBaterryFuses:
    """Sprawdza zadziałanie alarmów przepalenia bezpieczników baterii"""
    test_number = 8
    test_name = 'Test kontroli zabezpieczeń baterii'
    config_name = 'Zabezpieczenia baterii'
    config_range = list(range(5))
    required_modules = (modules.Q1, modules.MZB)
    number_tests = 0
    test_result = False


    def __init__(self, number=0, w=None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.q1 = None
        self.w = w
        self.bat = None
        self.number = number

    def get_modules(self):
        """Tworzy obiekty modułów używanych przy wykonywaniu testu"""
        if self.number:
            self.q1 = modules.Q1()
            self.bat = modules.MZB()

    def test(self):
        self.get_modules()
        if self.bat.realy_switching('xxxx') != '1111':
            self.bat.realy_switching('1111')
        start = datetime.now()
        self.logger.info('Test: poprawność okablowania nadzoru przepalenia bezpieczników baterii')
        printr('Start testu bezpieczników baterii: {:02d}:{:02d}:{:02d}'.format(start.hour, start.minute, start.second), self.w, self.logger)
        printr(f'Liczba zadeklarowanych bezpieczników baterii: {self.number}', self.w, self.logger)
        printr('Zrzuć wszystkie zabezpieczenia bateryjne', self.w, self.logger, color='blue')

        oids_list, sb = [], ''
        for i in range(self.number):
            oids_list.append(self.q1.oids_name['alarms.alarmsBatteryTable.alarmsBatteryEntry.alarmsBattFuse'] + str(i))
            sb += '1'  # stan alarmu zabezpieczenia baterii (do porównania z odczytem z q1)
        to_long = 12

        while sb != self.q1.snmp_querry(*tuple(oids_list)):
            snmp = self.q1.snmp_querry(*tuple(oids_list))
            self.logger.info('Stan zabezpieczeń baterii: {}'.format(snmp))
            time.sleep(5)
            to_long -= 1
            if to_long < 0:
                printr('Zbyt długi czas oczekiwnia na zrzucenie zabezpieczeń baterii'
                       ' (lub brak alarmów bezpieczników baterii)',self.w, self.logger, color='red')
                return False

        command = ['x', 'x', 'x', 'x']
        for i in range(self.number):
            command[i] = '0'
            self.bat.realy_switching(''.join(command))
            time.sleep(5)
            alarm_bezpiecznika_baterii = self.q1.snmp_querry(
                self.q1.oids_name['alarms.alarmsBatteryTable.alarmsBatteryEntry.alarmsBattFuse'] + str(i))
            self.logger.info('Alarm bezpiecznika baterii{}: {}'.format(i + 1, alarm_bezpiecznika_baterii))
            if alarm_bezpiecznika_baterii == '0':
                printr(f'Bezpiecznik baterii: {i + 1} OK', self.w, self.logger)
            else:
                printr(f'Bezpiecznik baterii: {i + 1} Error', self.w, self.logger)

                return False

            if self.w:
                self.w['progress'].update_bar(i + 1, self.number + 1)
        self.bat.realy_switching('1111')
        printr('Podnieś wszystkie zabezpieczenia bateryjne', self.w, self.logger, color='blue')
        time.sleep(4)
        oids_list, sb = [], ''
        for i in range(self.number):
            oids_list.append(self.q1.oids_name['alarms.alarmsBatteryTable.alarmsBatteryEntry.alarmsBattFuse'] + str(i))
            sb += '0'  # stan alarmu zabezpieczenia baterii (do porównania z odczytem z q1)
        to_long = 12
        snmp = self.q1.snmp_querry(*tuple(oids_list))
        print(sb, 'snmp:',snmp)
        while sb != self.q1.snmp_querry(*tuple(oids_list)):
            snmp = self.q1.snmp_querry(*tuple(oids_list))
            self.logger.info('Stan zabezpieczeń baterii: {}'.format(snmp))
            time.sleep(4)
            to_long -= 1
            if to_long < 0:
                printr(
                    'Zbyt długi czas oczekiwnia na podniesienie zabezpieczeń baterii '
                    '(lub brak zejścia alarmów bezpiczników baterii)', self.w, self.logger, color='red')
                return False
        if self.w:
            self.w['progress'].update_bar(self.number + 1, self.number + 1)
        stop = datetime.now()
        printr(
            'Koniec testu bezpieczników baterii: {:02d}:{:02d}:{:02d} Czas wykonania {}'
            .format(stop.hour, stop.minute, stop.second, sec2min((stop - start).total_seconds())), self.w, self.logger)
        if self.w:
            self.w['progress'].update_bar(0, 0)
        return True

@register
class TestRectifier:

    """Wykonuje przydział faz, odcina kolejne fazy, sprawdza poprawność alrmów zaniku faz i awarii prostownika.Sprawdza pracę prostowników"""
    test_number = 1
    test_name = 'Test pracy prostowników'
    config_name = 'Prostowniki'
    config_range = None
    required_modules = (modules.Q1, modules.MZF)
    number_tests = 0
    test_result = False
    bez_prostownikow =False

    def __init__(self, number=0, w=None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.q1 = None
        self.fazy = None
        self.w = w
        self.number = number
        self.wynik = False
        
    def get_modules(self):
        """Tworzy obiekty modułów używanych przy wykonywaniu testu"""
        if self.number:
            self.q1 = modules.Q1()
            self.fazy = modules.MZF()
            if self.fazy.realy_switching('xxx') != '111':
                self.logger.info('Załączam wszystkie fazy')
                self.fazy.realy_switching('111')
                #time.sleep(6)
                self.wait_for_expected_value(self.q1.snmp_querry, ('.1.3.6.1.4.1.32038.2.2.2.12.0',),  30, str(self.number))

    def wait_for_expected_value(self, func, args, timeout, expected_value, interval=2):
        """
        Wysyła zapytanie co `interval` sekund, przez maksymalnie `timeout` sekund,
        aż zapytanie zwróci oczekiwaną wartość `expected_value`.
        
        Parameters:
        timeout (int): maksymalny czas oczekiwania w sekundach
        expected_value: oczekiwana wartość
        interval (int): odstęp czasu między kolejnymi zapytaniami w sekundach
        
        Returns:
        bool: True jeśli zapytanie zwróciło oczekiwaną wartość w czasie `timeout` sekund, w przeciwnym razie False
        """
        print('Oczekiwanie na ogarniecie się sterownika q1')
        last_result = None
        start_time = time.time()
        while time.time() - start_time < timeout:
            result = func(*args) #self.q1.snmp_querry('.1.3.6.1.4.1.32038.2.2.2.12.0')
            if last_result != result:
                print('q->', result)
            if result == expected_value:
                return True
            time.sleep(interval)
            last_result = result
        return False

    def make_phase_order(self):        
        printr('Wyjmij wszystkie prostowniki z siłowni', self.w, self.logger, color='blue')
        to_long = 12
        while self.q1.snmp_querry('.1.3.6.1.4.1.32038.2.2.2.12.0') != '0':
            self.logger.info('Liczba prostowników: {}'.format(self.q1.snmp_querry('.1.3.6.1.4.1.32038.2.2.2.12.0')))
            time.sleep(5)
            to_long -= 1
            if to_long < 0:
                printr('Zbyt długi czas oczekiwnia na wyjęcie prostowników (lub brak wykrycia braku)',
                       self.w, self.logger, color='red')
                return False
        if self.q1.snmp_querry('.1.3.6.1.4.1.32038.2.2.2.13.0') != '0':
            # odblokowanie zerowania liczby prostowników i ustawienia przydziału faz przez snmp
            self.q1.snmp_querry('.1.3.6.1.4.1.32038.2.2.13.1.0', value=3637)
            time.sleep(0.5)
            # zerowanie tablicy prostowników
            self.q1.snmp_querry('.1.3.6.1.4.1.32038.2.2.2.13.0', value=0)
            time.sleep(0.5)
            rectNrOfSet = self.q1.snmp_querry('.1.3.6.1.4.1.32038.2.2.2.13.0')
            if rectNrOfSet != '0':
                printr(f'Brak zerowania tablicy prostowników.  rectNrOfSet = {rectNrOfSet}',self.w, self.logger, color='red')
                return False
        for i in range(1, self.number + 1):
            if self.w:
                self.w['progress'].update_bar(i, self.number * 3)

            printr('Włóż prostownik na pozycję numer: {}'.format(i), self.w, self.logger,  color='blue')
            to_long = 12
            while self.q1.snmp_querry('.1.3.6.1.4.1.32038.2.2.2.12.0') != str(i):
                self.logger.info('Liczba prostowników: {}'.format(self.q1.snmp_querry('.1.3.6.1.4.1.32038.2.2.2.12.0')))
                time.sleep(5)
                to_long -= 1
                if to_long < 0:
                    printr('Zbyt długi czas oczekiwnia na włożenie prostownika (lub brak wykrycia prostownika)',
                           self.w, self.logger, color='red')
                    return False
        self.q1.snmp_querry('.1.3.6.1.4.1.32038.2.2.13.1.0', value=3637)
        for i in range(self.number):  # przydział faz
            faza = i % 3 + 1
            if self.q1.snmp_querry('.1.3.6.1.4.1.32038.2.2.2.2.1.23.' + str(i), value=faza) == str(faza):
                printr(f'Przydział prostownika {i + 1} do fazy {faza} OK', self.w, self.logger)
            else:
                printr(f'Przydział prostownika {i + 1} do fazy {faza} nieudany', self.w, self.logger, color='red')
                return False   
        printr('OK, przydział faz wykonany', self.w, self.logger)
        return True

    def check_phase(self):
        printr('Sprawdzenie przydziału faz.', self.w, self.logger)
        if self.fazy.realy_switching('xxx') != '111':
            self.logger.info('Załączam wszystkie fazy')
            self.fazy.realy_switching('111')
            #time.sleep(8)
            rect_on =  self.wait_for_expected_value(self.q1.snmp_querry, ('.1.3.6.1.4.1.32038.2.2.2.12.0',),  60, str(self.number))
            if not rect_on:
                return rect_on

        else:
            self.logger.info('Wszystkie fazy załaczone')
        if self.number == 1:
            liczba_faz = 1
        elif self.number == 2:
            liczba_faz = 2
        else:
            liczba_faz = 3
        oids = tuple(['.1.3.6.1.4.1.32038.2.2.16.2.1.' + str(15 + i) + '.0' for i in range(liczba_faz)])
        fazy = []
        for i in range(liczba_faz): fazy.append('1')
        self.logger.info(fazy)

        for i in range(liczba_faz):
            self.logger.info('Wyłączenie fazy {}'.format(i + 1))
            fazy[i] = '0'
            self.logger.info(fazy)
            # print('fazy',fazy)
            inverted_logic = ['0' if i == '1' else '1' for i in fazy]  # wcelu porównania z snmp
            inverted_logic = ''.join(inverted_logic)
            set_fazy = ''.join(fazy)
            for j in range(3 - liczba_faz): set_fazy += 'x'  # gdy liczba faz mniejsza niż trzy
            self.fazy.realy_switching(set_fazy)
            #print('inverted_logic:',inverted_logic)
            #time.sleep(10)
            stan_faz =  self.wait_for_expected_value(self.q1.snmp_querry, oids, 60, inverted_logic)
            #q1_stan_faz = self.q1.snmp_querry(*oids)
            #print('Alarm faz snmp:', q1_stan_faz, datetime.now())
            if stan_faz:#q1_stan_faz == inverted_logic:
                printr('Zanik i alarm fazy: {} OK'.format(i + 1), self.w, self.logger)
                if self.w:
                    self.w['progress'].update_bar(i + 1 + self.number * 2, self.number * 3)
                    time.sleep(1)
                fazy[i] = '1'    
            else:
                printr('Zanik i alarm fazy: {} Error'.format(i + 1), self.w, self.logger, color='red')
                import sys
                sys.exit()
                #return False 
            self.logger.info('Załączam wszystkie fazy')
            self.fazy.realy_switching('111')
            rect_on =  self.wait_for_expected_value(self.q1.snmp_querry, ('.1.3.6.1.4.1.32038.2.2.2.12.0',),  60, str(self.number))
        return True                   
    def alarm_prostownika(self):
        if self.bez_prostownikow: #nie sprawdzamy alarmu uszkodzenia prostownika
            return True
        for i in range(self.number):
            if self.w:
                self.w['progress'].update_bar(i + self.number + 1, self.number * 3)
            printr(f'Zablokuj wntylator prostownika na pozycji numer: {i + 1}', self.w, self.logger,  color='blue')
            to_long = 12
            while self.q1.snmp_querry('.1.3.6.1.4.1.32038.2.2.2.2.1.17.' + str(i)) != '1':
                time.sleep(5)
                to_long -= 1
                if to_long < 0:
                    printr('Zbyt długi czas oczekiwnia na zablokowanie prostownika (lub brak wykrycia blokady)',
                           self.w, self.logger, color='red')
                    if self.w:
                        self.w['progress'].update_bar(0, 0)
                    return False

        printr('Odblokuj wentylatory', self.w, self.logger, color='blue')

        oids = tuple(['.1.3.6.1.4.1.32038.2.2.2.2.1.17.' + str(i) for i in
                      range(self.number)])  # oidy alarmu wentylatora kolejnych prostowników
        w = self.q1.snmp_querry(*oids)
        to_long = 12
        while w != '0' * self.number:
            time.sleep(5)
            to_long -= 1
            if to_long < 0:
                printr('Zbyt długi czas oczekiwnia na odblokowanie prostowników (lub brak wykrycia odblokowania)',
                       self.w, self.logger, color='red')
                return False
            w = self.q1.snmp_querry(*oids)
        printr('OK, wentylatory odblokowane.', self.w, self.logger)
        return True
                                     
    def test(self):

        self.get_modules()
        start = datetime.now()
        self.logger.info(
            'Test: wyzerowuje tablicę prostowników, konfiguruje pozycję i przydział faz'
            ' i weryfikuje wprowadzone ustawienia')
        printr('Start testu prostowników: {:02d}:{:02d}:{:02d}'.
               format(start.hour, start.minute, start.second), self.w, self.logger)
        printr(f'Liczba zadeklarowanych prostowników: {self.number}', self.w, self.logger)        
        if self.make_phase_order() and self.alarm_prostownika() and self.check_phase():
            self.wynik = True
        self.logger.info('Załączam wszystkie fazy')
        self.fazy.realy_switching('111')
        time.sleep(5)         
        stop = datetime.now()
        printr('Koniec testu prostowników: {:02d}:{:02d}:{:02d} Czas wykonania {}'.
               format(stop.hour, stop.minute, stop.second, sec2min((stop - start).total_seconds())),
               self.w, self.logger)
        if self.w:
            self.w['progress'].update_bar(0, 0)
        return self.wynik

@register
class TestMZK:

    """Sprawdza działanie wyjść i wejść MZK"""
    test_number = 10
    test_name = 'Test MZK'
    config_name = 'MZK'
    config_range = list(range(2))
    required_modules = (modules.Q1, )
    number_tests = 0
    test_result = False

    def __init__(self, number=0, w=None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.q1 = None
        self.w = w
        self.number = number

    def get_modules(self):
        """Tworzy obiekty modułów używanych przy wykonywaniu testu"""
        if self.number:
            self.q1 = modules.Q1()   

    def test(self):
        self.get_modules()
        start = datetime.now()
        self.logger.info('Test: sprawdza okablowania i działanie MZK')

        printr('Start testu MZK: {:02d}:{:02d}:{:02d}'
               .format(start.hour,start.minute,start.second), self.w, self.logger)
        printr(f'Liczba zadeklarowanych mzk: {self.number}', self.w, self.logger)
        oids_name = ('alarmsEnvironmentDoorOpen', 'alarmsEnvironmentSmokeDet', 'alarmsEnvironmentHeaterZone2On', 'alarmsEnvironmentHeaterZone1On', 
                  'alarmsEnvironmentVentOn')
        oids_number = tuple([self.q1.oids_name[i] for i in oids_name])        
        result = self.q1.snmp_querry(*oids_number)
        # print('before',list(result))
        for c,j in enumerate(list(result)): # == '2':
            if j == '2':
                printr(f'Przed rozpoczeciem testu wykryto alarm:  {oids_name[c]}',self.w, self.logger, color='red')
                return False
        time.sleep(1)        
        self.q1.snmp_querry(self.q1.oids_name['environmentMode'], value=1)
        time.sleep(6)
        result = self.q1.snmp_querry(*oids_number)
        #print('after',list(result))
        for c,j in enumerate(list(result)):    
            if j != '2':
                printr(f'Brak alarmu:  {oids_name[c]}',self.w, self.logger, color='red')
                self.q1.snmp_querry(self.q1.oids_name['environmentMode'], value=0)
                time.sleep(2) 
                return False 
            else:
                printr(f'Alarm:  {oids_name[c]} OK.',self.w, self.logger)        
        printr(f'Oczekiwanie (80 s) na alarm wentylatora ...',self.w, self.logger, color='blue')
        time.sleep(80)
        if self.q1.snmp_querry(self.q1.oids_name['alarmsEnvironmentCoolingFail']) != '2':
            printr(f'Brak alarmu wentylatora',self.w, self.logger, color='red')
            self.q1.snmp_querry(self.q1.oids_name['environmentMode'], value=0) 
            time.sleep(2) 
            return False
        else:
            printr(f'Alarm wentylatora Ok',self.w, self.logger)
            printr(f'Podłącz wentylator testowy i czekaj na zejście alarmu wentylatora',self.w, self.logger, color='blue')
        to_long = 12
        while self.q1.snmp_querry(self.q1.oids_name['alarmsEnvironmentCoolingFail']) != '0':
            self.logger.info('Alarm wentylatora: {}'.format(self.q1.snmp_querry(self.q1.oids_name['alarmsEnvironmentCoolingFail'])))
            time.sleep(5)
            to_long -= 1
            if to_long < 0:
                printr('Zbyt długi czas oczekiwnia na zejście alarmu wentylatora',self.w, self.logger, color='red')
                self.q1.snmp_querry(self.q1.oids_name['environmentMode'], value=0)
                time.sleep(2)
                stop = datetime.now()
                printr('Koniec testu MZK: {:02d}:{:02d}:{:02d} Czas wykonania {}'
                    .format(stop.hour, stop.minute, stop.second, sec2min((stop-start).total_seconds())), self.w, self.logger)
                if self.w:
                    self.w['progress'].update_bar(0,0)
                return False
        self.q1.snmp_querry(self.q1.oids_name['environmentMode'], value=0)
        time.sleep(2)         
        stop = datetime.now()
        printr('Koniec testu MZK: {:02d}:{:02d}:{:02d} Czas wykonania {}'
               .format(stop.hour, stop.minute, stop.second, sec2min((stop-start).total_seconds())), self.w, self.logger)
        if self.w:
            self.w['progress'].update_bar(0,0)
        return True
class TestMWS:

    """Sprawdza zadziałanie odłaczanie i przyłaczanie styczników przez moduł MWS"""
    test_number = 11
    test_name = 'Test MWS'
    config_name = 'MWS'
    config_range = list(range(2))
    required_modules = (modules.LOAD, )
    number_tests = 0
    test_result = False

    def __init__(self, number=0, w=None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.load = None
        self.fluke = None
        self.w = w
        self.number = number
        self.rgr = (42.0, 48.0)
        self.grupa = (45.0, 49.0)

    def get_modules(self):
        """Tworzy obiekty modułów używanych przy wykonywaniu testu"""
        if self.number:
            self.load = modules.LOAD()
            self.fluke = modules.Fluke8845A()   

    def test(self):
        self.get_modules()
        start = datetime.now()
        self.logger.info('Test: sprawdza sprawność MWS')

        printr('Start testu MWS: {:02d}:{:02d}:{:02d}'
               .format(start.hour,start.minute,start.second), self.w, self.logger)
        printr(f'Liczba zadeklarowanych modułów MWS: {self.number}', self.w, self.logger)

        self.load.connection()

        print(f"Napiecie systemu przed testem: {self.load.get_value('VOLT')}")
        if self.load.get_value('VOLT') == 9.9e+37:
            print('RGR odłaczony przed rozpoczeciem testu!')
            return False
        self.load.set_mode('VOLT')    
        self.load.set_value('VOLT', self.rgr[0])
        print(f'Ustawienie obciążenia na {self.rgr[0]}')      
        time.sleep(20)
        print(f"Napiecie systemu po 20 sekundach: {self.load.get_value('VOLT')}")      
        if  self.load.get_value('VOLT') == 9.9e+37:
            print('MWS RGR: OK')
        else:
            print('MWS nie odłaczył RGR: Error')
            return False
        self.load.set_value('VOLT', 0)             
        print(f'Wyłączenie obciazenia')

        time.sleep(300)
        print(f"Napiecie systemu po 300 sekundach: {self.load.get_value('VOLT')}")
        if  self.load.get_value('VOLT') != 9.9e+37 and  self.load.get_value('VOLT') > self.rgr[1] -1:
            print('MWS podłaczył RGR: OK')
        else:
            print('MWS nie podłaczył RGR: Error')
            self.load.set_value('VOLT', 0)
            return False
        self.load.set_value('VOLT', 0) 
        print(f"Napiecie po wyłączeniu obciążenia: {self.load.get_value('VOLT')}") 

        """
        print(f'Napiecie grupy przed testem: {self.fluke.reading()}')
        if self.fluke.reading == 9.9e+37:
            print('Grupa odłaczona przed rozpoczeciem testu!')
            return False
        self.load.set_mode('VOLT')    
        self.load.set_value('VOLT', self.grupa[0])
        print(f'Ustawienie obciążenia na {self.grupa[0]}')      
        time.sleep(20)
        print(f'Napiecie grupy po 20 sekundach: {self.fluke.reading()}')      
        if  self.fluke.reading() == 9.9e+37:
            print('MWS odłaczył grupę: OK')
        else:
            print('MWS nie odłaczył grupy: Error')
            return False
        self.load.set_value('VOLT', 0)             
        print(f'Wyłączenie obciazenia')

        time.sleep(300)
        print(f'Napiecie grupy po 300 sekundach: {self.fluke.reading()}')
        if  self.fluke.reading() != 9.9e+37 and  self.fluke.reading() > self.grupa[1] -1:
            print('MWS podłaczył grupę: OK')
        else:
            print('MWS nie podłaczył grupy: Error')
            self.load.set_value('VOLT', 0)
            return False
        self.load.set_value('VOLT', 0) 
        print(f'Napiecie po wyłączeniu obciążenia: {self.fluke.reading()}')      
        """

                     

        stop = datetime.now()
        printr('Koniec testu MWS: {:02d}:{:02d}:{:02d} Czas wykonania {}'
               .format(stop.hour, stop.minute, stop.second, sec2min((stop-start).total_seconds())), self.w, self.logger)
        if self.w:
            self.w['progress'].update_bar(0,0)
        return True
# print(test_classes)
test_classes = sorted([x for  x in test_classes], key=lambda x: x.test_number)
# print(test_classes)
#for i in test_classes:
#    print(i.__name__, i.test_number, i.test_key, i.test_name, i.config_name)

if __name__ == "__main__":
    """t = TestRs485(1)
    print(t.test())
    del t
    t = TestRs485()
    print(t.get_modules())"""
    #lista_modulow = [TestRectifier, TestUkb, TestInput, TestOutputQ1, TestOutputMWY, TestBocznika, TestBaterryFuses,
    #                 TestCzujnikowTemp, TestStycznika, TestRs485, TestMZK]
    """modules.MZF(4).realy_switching('1111')
    time.sleep(2)
    modules.MZF(3).realy_switching('111')
    time.sleep(5)"""
    """bezpiecznik_odbioru = TestUkb(number=1)
    print(bezpiecznik_odbioru.test())
    time.sleep(1)
    asymetria = TestAsymBat(number=1)
    print(asymetria.test())
    time.sleep(1)
    bezpiecznik_baterii = TestBezpiecznikaBat(number=1)
    print(bezpiecznik_baterii.test())"""
    # print(dir(t))
    # print(t.get_modules())
    #for i in lista_modulow:
    #    print(i.__name__, '->', i.required_modules)

    #rs485 = TestRs485(1)
    #print(rs485.test())

    """mzk = TestMZK(number=1)
    mzk.get_modules()
    mzk.test()
    mzk_sensor = TestCzujnikowMZK(number=1)
    mzk_sensor.get_modules()
    mzk_sensor.test()"""
    TestRectifier.bez_prostownikow = True
    t = TestRectifier(number=3)
    t.get_modules()
    t.test()
    #print(type(t.q1.snmp_querry))
    #t.wait_for_expected_value(t.q1.snmp_querry, '.1.3.6.1.4.1.32038.2.2.2.12.0', 120, str(t.number))
    #t.test() 
    sys.exit()   
    bezbat = TestBezpiecznikaBat(1)
    bezbat.get_modules()
    bezbat.test()
    
    mwy = TestOutputMWY(number=8)
    mwy.get_modules()
    mwy.test()


    sys.exit()

    
    t_rs485 = TestRs485(number=1)
    t_rs485.get_modules()
    t_rs485.test()    


    t_mwy = TestOutputMWY(number=1)
    t_mwy.get_modules()
    t_mwy.test()
    
    test_stycznika = TestStycznika(number=2)
    test_stycznika.get_modules()
    test_stycznika.test()
    
    test_battery_fuses = TestBaterryFuses(number=1)
    test_battery_fuses.test()
    
    test_b = TestBocznika(number=1)
    test_b.get_modules()
    test_b.test()
    #time.sleep(40)
    #test.check_phase()
    #test = TestUkb(number=8)
    #test = TestBaterryFuses(number=4)
    #test = TestInput(number=8)
    #test.test()
    #for i in test_classes:
    #    print(i.__name__)

    """
    mws = TestMWS(number=1)
    mws.get_modules()
    mws.test()"""
    


 








