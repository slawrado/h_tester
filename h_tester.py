"""Okna aplikacji"""
import errno
import os
from collections import namedtuple
import sys
import time
from datetime import datetime
#from os.path import exists
import PySimpleGUI as sg
import raport.raport as raport
import modules
import testy
import threading
# 192.168.1.122
 #('-UKB', '-OUTPUT-Q1', '-OUTPUT-MWY', '-INPUTS', '-STYCZNIK', '-BOCZNIK', '-CZUJNIK-TEMP', '-BAT-FUSE','-PROSTOWNIK', '-MZK', '-RS485', '-ASYM', '-BAT-FUSE-MOD', '-CZUJNIK-MZK')
 #Pomijamy sprawdzenie modułów
selftest, stop_test, default_ip, bez_izolacji, bez_prostowników = False, False, False, False, False
# operators = ['A.Salamon', 'M.Dżygun', 'W.Sławiński', 'Z.Batogowski', 'W.Tomczyk', 'K.Hamann']
operators = {'A.Salamon':'', 'M.Dżygun':'', 'W.Sławiński':'177/E/0832/19', 'Z.Batogowski':'177/E/0709/23', 'W.Tomczyk':'177/E/0708/23', 'K.Hamann':'177/E/0706/23'}    
Test_data = namedtuple('Test_data', ['test_class','test_name', 'config_name', 'config_range', 'required_modules', 'config', 'result'])
test_classes = tuple(testy.test_classes) 


tests = {}
for i in test_classes:
    tests[i.test_key] = Test_data(i, i.test_name, i.config_name, i.config_range, i.required_modules, [0], [False])

ident = {'Nazwa:  ': '', 'Indeks:  ': '', 'Nr seryjny:  ': '', 'Nr seryjny Q1:  ': '',
         'Wersja programu Q1:  ': '', 'Wersja konfiguracji Q1:  ': '', 'Operator (test izolacji):  ':  '', 'Operator (test systemu):  ':  '', 'Data:  ':  ''}

indeks_nazwa = {'0000-00000-00': ('Custom test', 'OS-000309-001E'),
                 '9070-00696-22': ('Modernizacja Benning', 'OS-000310-002E'), 
                 '9070-00696-28': ('Modernizacja Benning', 'OS-000310-002E'),
                 '9030-00328': ('H-system', 'OS-000311-002A'),
                 }
indeks_config = {
                 '9070-00696-28': {'-UKB': 1, '-OUTPUT-Q1': 0, '-OUTPUT-MWY': 7, '-INPUTS': 0, '-STYCZNIK': 2, '-BOCZNIK': 1,
                             '-CZUJNIK-TEMP': 1, '-BAT-FUSE': 0, '-PROSTOWNIK': 4, '-MZK': 0, '-RS485': 0,
                             '-ASYM': 1, '-BAT-FUSE-MOD': 1, '-CZUJNIK-MZK': 0},
                 '9070-00696-22': {'-UKB': 1, '-OUTPUT-Q1': 0, '-OUTPUT-MWY': 7, '-INPUTS': 0, '-STYCZNIK': 2, '-BOCZNIK': 1,
                             '-CZUJNIK-TEMP': 1, '-BAT-FUSE': 0, '-PROSTOWNIK': 4, '-MZK': 0, '-RS485': 0,
                             '-ASYM': 1, '-BAT-FUSE-MOD': 1, '-CZUJNIK-MZK': 0},                             
                 '9030-00328': {'-UKB': 0, '-OUTPUT-Q1': 0, '-OUTPUT-MWY': 0, '-INPUTS': 0, '-STYCZNIK': 0, '-BOCZNIK': 0,
                             '-CZUJNIK-TEMP': 0, '-BAT-FUSE': 0, '-PROSTOWNIK': 0, '-MZK': 1, '-RS485': 0,
                             '-ASYM': 0, '-BAT-FUSE-MOD': 0, '-CZUJNIK-MZK': 1},         
                 '0000-00000-00': {'-UKB': 0, '-OUTPUT-Q1': 0, '-OUTPUT-MWY': 0, '-INPUTS': 0, '-STYCZNIK': 0, '-BOCZNIK': 0,
                             '-CZUJNIK-TEMP': 0, '-BAT-FUSE': 0, '-PROSTOWNIK': 0, '-MZK': 0, '-RS485': 0,
                             '-ASYM': 0, '-BAT-FUSE-MOD': 0, '-CZUJNIK-MZK': 0},             }

def set_config(indeks, debug=False):
    if debug:
        print('indeks config')
        for j in indeks_config[indeks]:
            print(j, indeks_config[indeks][j], end='')
        print('tests config')    
        for i in tests:
            print(i, tests[i].config[0], end='')
    for i in indeks_config[indeks]:
        if indeks_config[indeks][i] == 0:
            del tests[i]
        else:
            tests[i].config[0] = indeks_config[indeks][i]
    if debug:        
        for j in indeks_config[indeks]:
            print(j, indeks_config[indeks][j], end='')            
        for i in tests:
            print(i, tests[i].config[0], end='')   

json_file = {}
json_file.update(ident)



tip = ('\"Podaje plusa\" na kolejne zabezpieczenia i weryfikuje wejście i zejście alarmu bezpiecznika odbioru.',
       'Steruje stanem wyjść Q1 i weyfikuje zmiany.',
       'Steruje stanem wyjść MWY i weyfikuje zmiany.',
       'Zwiera wejścia MWE i sprawdza reakcję Q1.',
       'Wykonuje rozwarcie i zwarcie styczników i weryfikuje odpowiednie alarmy sterownika.',
       'Odcina zasilanie AC, sprawdza kierunek i wartość pradu baterii.',
       'Sprawdza komunikację Q1 z czujnikami temperatury.',
       'Wymusza i sprawdza pojawienie się i zejście kolejnych alarmów bezpiecznika baterii.',
       'Wykonuje przydział faz, odcina kolejne fazy, sprawdza poprawność alrmów zaniku faz i awarii prostownika.',
       'Sprawdza działanie wyjść i wejść MZK',
       'Odczytuje rejestr 281 po modbus RTU i over TCP i porównuje odczyty',
       'Podaje minus na wej alarmu asymetrii sterownika',
       'Podaje minus na wej alarmu bezpiecznika baterii sterownika',
       'Sprawdza komunikację MZK z czujnikami temperatury.',)
text_p = dict(zip(tuple(tests.keys()), tip))


def check_number(number, key):
    """ Waliduje dane wprowadzone przez uzytkownika
    (liczbę zabezpieczeń odbioru i prostowników)."""
    max_number = {'-UKB': 33, '-PROSTOWNIK': 61}
    if number.isdigit() and int(number) in range(0, max_number[key]):
        return int(number)
    else:
        print(key, 'zakres wartości konfiguracji:  0 ->', max_number[key])
        return False


def test_all_thread(w):
    """Uruchamia wszystkie testy danej konfiguracji."""

    for i in tests:
        w[i + 'R'].update('')  # zerowanie wników testów
    liczba_testow = len(tests) # - len([tests[i].config[0] for i in tests if tests[i].config[0] == 0])                                    
    print('Liczba zaplanowanych testów: ', liczba_testow)
    if stop_test:
        print('Zatrzymanie testów po pierwszym negatywnym !')
    start = datetime.now()
    for i in tests:
        print('Test numer: {}'.format(tuple(tests.keys()).index(i)+1))
        w[i + 'R'].update('In progress', text_color='yellow')
        w.refresh()
        ti = tests[i].test_class(tests[i].config[0], w) #instancja obiektu testu
        if ti.test():  # wywołanie metody test, jeśli wykona się poprawnie: zwróci True
            w[i + 'R'].update('Ok', text_color='white')
            tests[i].result[0] = True
        else:
            w[i + 'R'].update('Fail', text_color='red')
            if stop_test:
                return
        time.sleep(2)

        w.refresh()
    # dane do raportu
    for i in ident:
        json_file[i] = ident[i]
    wynik = []
    for i in tests:
        wynik.append(tests[i].result[0])
        json_file[tests[i].test_name] = tests[i].result[0], tests[i].config[0]

    q1 = modules.Q1()
    if '-PROSTOWNIK' in tuple(tests.keys()) and not bez_prostowników:
        json_file['prostowniki'] = q1.get_rectifier_serial(tests['-PROSTOWNIK'].config[0])#numery seryjne prostowników
    json_file['ip'], json_file['izolacja'], json_file['noserial'] = default_ip, bez_izolacji, bez_prostowników   
    if all(wynik) and default_ip:        
        q1.set_dufault_ip()
        print('Adres 192.168.5.120 , dhcp off')
    del q1    
    stop = datetime.now()
    print('Czas wykonania testów:  {}, ilość wykonanych testów:  {}'.format(testy.sec2min((stop - start).total_seconds()),
                                                                            liczba_testow))
    window.write_event_value('-THREAD DONE-', '')


def test_all():
    threading.Thread(target=test_all_thread, args=(window,), daemon=True).start()


sg.theme('DarkTeal12')  # Add a touch of color
text_size = 60


def make_main_window():
    """Tworzy zawartość głównego okna aplikacji."""
    col1, col2, col3, col4 = [], [], [], []
    for i in tests:
        col1.append([sg.Text('{:>2}. {}'.format(tuple(tests.keys()).index(i) + 1, tests[i].test_name), key=i + 'P', tooltip=text_p[i])])
        col2.append([sg.Text(size=(12, 1), key=i + 'R')])
    
    for i in ident: 
        col3.append([sg.Text(f' {i}', size=(20, 1))])
        col4.append([sg.Text(f' {ident[i]}', size=(15, 1), key=i)])
    #col3.append([sg.Text(size=(34, 1), key='-3')])  # , visible=False 
    layout = [[sg.Text('Stan przekaźników: '),

               sg.Checkbox('Faza1', enable_events=True, key='f1'),
               sg.Checkbox('Faza2', enable_events=True, key='f2'),
               sg.Checkbox('Faza3', enable_events=True, key='f3'),
               sg.Push(),
               sg.Checkbox('Bat1', enable_events=True, key='b1'),
               sg.Checkbox('Bat2', enable_events=True, key='b2'),
               sg.Checkbox('Bat3', enable_events=True, key='b3'),
               sg.Checkbox('Bat4', enable_events=True, key='b4'),
               # sg.Text('| Self test: ', size=(18, 1)),
               ],

              [sg.HSep()],
              [sg.Button('Self test & power on', key='-SF-', expand_x=True),
               sg.Button('Help', key='-KT-', disabled=True, expand_x=True)],  #
              [sg.HSep()],
              [sg.Column(col1), sg.Column(col2), sg.Frame(' Identyfikacja ', [[sg.Column(col3), sg.Column(col4)]], expand_x=True)],
              # , element_justification='right', expand_x=True
              [sg.HSep()],
              [sg.Text('Wykonanie testu: '),
               sg.ProgressBar(max_value=0, orientation='h', expand_x=True, bar_color=('light blue', 'white'),
                              size=(28, 20), key='progress'),  # ,
               sg.Button('Wykonaj testy', key='-ST-', disabled=True),
               sg.Button('Zapisz raport', key='-RT-', disabled=True)]

              ]

    frame_layout = [[sg.Multiline(font=('Consolas', 10, 'normal'), size=(text_size + 21, 20),
                                  background_color='alice blue',
                                  autoscroll=True, reroute_stdout=True, reroute_stderr=True,
                                  enable_events=True, text_color='gray', key='-OUTPUT-', auto_size_text=True, expand_x=True)]]
    layout.append([sg.Frame(" Work preview  ", frame_layout, element_justification='center',expand_x=True)])

    return sg.Window('H tester', layout, finalize=True)


# 'alice blue'
def make_conf_window():
    """Tworzy okno konfiguracji testów"""
    col1, col2 = [], []
    
    for i in tests:
        col1.append([sg.Text(' {:>2}. {}: '.format(tuple(tests.keys()).index(i) + 1, tests[i].config_name))])
        if i in ('-UKB', '-PROSTOWNIK'):
            col2.append([sg.Input(size=(5, 1), default_text=tests[i].config[0], enable_events=False, justification='right',
                      expand_x=True, key=i, disabled=False)])          
        else:
            col2.append([sg.Combo(tests[i].config_range, size=(4, 1), default_value=0, enable_events=False,
                      expand_x=True, key=i, disabled=False)])               
    layout = [

        [sg.Text('Konfiguracja testów: ')],

        
        [sg.Column(col1), sg.Column(col2, element_justification='right', expand_x=True)],
        [sg.HSep()],
        [sg.Push(), sg.Button('Zapisz', tooltip='')]]
    return sg.Window('Konfiguracja uzytkownika', layout).read(close=True)# , finalize=True .make_modal() location=(0, 50)


# main_window['-ST-'].set_focus()
def self_test():
    """Sprawdza komunikację z modułami testera."""
        
    if modules.ping('192.168.1.1'):
        print('Dostęp do sieci 192.168.1.xxx OK')
        # w.refresh()
    else:
        print('Nie masz dostępu do sieci 192.168.1.xxx')
        # w.refresh()
        return False
    required = set()  # wymagane moduły dla danej konfiguracji testów.
    for i in tests:
        for j in tests[i].required_modules:
            required.add(j)
    if ident['Indeks:  '] == '0000-00000-00':
        required = {modules.MZF, modules.MWW, modules.Q1}  # modules.RS485 modules.MZB, modules.LOAD, 
   
    #required.remove(modules.Q1)
    for k in required:
        if k().self_test():
            print(f'Komunikacja z {k.__name__} OK.')
        else:
            print(f'Brak komunikacji z {k.__name__}.')
            return False
    return True


def buttons_availability(w, stan):
    """Aktywuje lub dezaktywuje przyciski"""
    for i in ('-SF-', '-ST-', '-RT-', 'f1', 'f2', 'f3', 'b1', 'b2', 'b3', 'b4'):
        if stan:
            w[i].update(disabled=False)
        else:
            w[i].update(disabled=True)
    w.refresh()
# Utworzenie katalogu do zapisu raportów z testów


try:
    os.makedirs('raporty')
except OSError as e:
    if e.errno != errno.EEXIST:
        raise

# Okno do wpisania indeksu i numeru serejnego testowanej siłowni
event, values = sg.Window('Wybór szablonu',
                          [[sg.Text('Indeks wyrobu: ', size=(20, 1)),
                            sg.Combo(values=list(indeks_nazwa.keys()), size=(15, 1),
                                     key='Indeks:  ', default_value=list(indeks_nazwa.keys())[3])],
                           [sg.Text('Numer seryjny: ', size=(20, 1)),
                            sg.Input(size=(15, 1), justification='right',
                                     expand_x=True, key='Nr seryjny:  ')],
                           [sg.Text('Operator (test izolacji): ', size=(20, 1)),
                            sg.Combo(list(operators.keys()), size=(15, 1), default_value='W.Sławiński',  # ident['Operator:  ']
                                     key='Operator (test izolacji):  ')],
                            [sg.Text('Operator (test systemu): ', size=(20, 1)),         
                            sg.Combo(list(operators.keys()), size=(15, 1), default_value='W.Sławiński',  # ident['Operator:  ']
                                     key='Operator (test systemu):  ')],
                            [sg.HSep()],                                              
                            [sg.Checkbox('Zatrzymaj po pierwszym negatywnym.', key='test_break', )],
                            [sg.Checkbox('Ustaw ip Q1 na 192.168.5.120', key='ip', )],
                            [sg.Checkbox('Raport sprawdzenia izolacji.', key='izolacja', )],
                            [sg.Checkbox('Raport bez numerów prostowników.', key='no_serial', )],
                            [sg.Push(),sg.Button('OK'), ]]).read(close=True)
# 'Indeks:  ': '', 'Nr seryjny:  '
if event == sg.WINDOW_CLOSED:
    sys.exit()
if values['test_break']:
    stop_test = True
else:
    stop_test = False    
if values['Indeks:  ']:
    if values['Indeks:  '] != '0000-00000-00':
        set_config(values['Indeks:  '])
    ident['Indeks:  '], ident['Nr seryjny:  '], ident['Operator (test izolacji):  '] = values['Indeks:  '], values['Nr seryjny:  '], values['Operator (test izolacji):  ']
    ident['Operator (test systemu):  '] = values['Operator (test systemu):  ']
    stop_test, default_ip, bez_izolacji, bez_prostowników = values['test_break'], values['ip'], values['izolacja'], values['no_serial']

if ident['Indeks:  '] == '0000-00000-00':
    event, values = make_conf_window()

    if event == 'Zapisz':

        # window.refresh()
        for i in indeks_config['0000-00000-00']:
            if i == '-UKB' or i == '-PROSTOWNIK':
                indeks_config['0000-00000-00'][i] = check_number(values[i], i)
            else:
                indeks_config['0000-00000-00'][i] = int(values[i])
        set_config('0000-00000-00')

                # main_window['-ST-'].update(disabled=False)
        
        print(f'Konfiguracja zapisana.') 

window = make_main_window()
# Główna pętla aplikacji.
try:
    while True:
        window, event, values = sg.read_all_windows()
        if event == sg.WIN_CLOSED or event == 'Exit':
            sf = modules.MZF()
            if sf.self_test():
                sf.realy_switching('000')
            del sf
            """sb = modules.MZB()
            if sb.self_test():
                sb.realy_switching('0000')
            del sb"""
            break
        elif event == '-SF-': # selftest
            buttons_availability(window, False)
            window.perform_long_operation(self_test, '-RETURN_TRIGGER-')
        elif event == '-RETURN_TRIGGER-':
            # if self_test(window):
            if values['-RETURN_TRIGGER-']:
                print('Self test OK.')
                print('Power ON ...')
                window.refresh()

                if selftest:
                    sf = modules.MZF(w=window)
                    sf.realy_switching('111')
                    for i in range(3):
                        time.sleep(1)
                        window.refresh()
                    del sf

                    for i in range(6):
                        time.sleep(1)
                        window.refresh()

                q1 = modules.Q1() 
                ident['Nr seryjny Q1:  '], ident['Wersja programu Q1:  '], \
                    ident['Wersja konfiguracji Q1:  '] = q1.ident_inf()

                ident['Data:  '] = datetime.now().strftime("%d/%m/%Y")
                if ident['Indeks:  '] in indeks_nazwa.keys():
                    ident['Nazwa:  '] = indeks_nazwa[ident['Indeks:  ']][0]
                for i in ident:
                    window[i].update(ident[i])
                if int(ident['Wersja programu Q1:  '].split('b')[1]) >= 30:
                    pass
                else:
                    window['Wersja programu Q1:  '].update(text_color='red')
                    print('Tester wymaga Q1 z wersją 1.0b30 lub wyższą.')
                    continue                
                if ident['Wersja konfiguracji Q1:  '] != indeks_nazwa[ident['Indeks:  ']][1] and ident['Indeks:  '] != '0000-00000-00':
                    window['Wersja konfiguracji Q1:  '].update(text_color='red')
                    print(f"Nieprawidłowa wersja konfiguracji -> {ident['Wersja konfiguracji Q1:  ']}")
                    print(f"Prawidłowa wersja konfiguracji    -> {indeks_nazwa[ident['Indeks:  ']][1]}")
                    test_button_disable = True
                    continue
                    #buttons_availability(window, False)
                    #window.refresh()
                    
                else:
                    print(f"Wersja konfiguracji Q1 -> {indeks_nazwa[ident['Indeks:  ']][1]} OK")
                    
                del q1
                #else:
                    #print('Brak komunikacjia z Q1')
                    #window['-OUTPUT-'].update('Self test error.\n', text_color_for_value='red', append=True)
            else:
                window['-OUTPUT-'].update('Self test error.\n', text_color_for_value='red', append=True)

            buttons_availability(window, True)

        elif event == '-ST-': #wykonanie testów
            buttons_availability(window, False)
            test_all()
        elif event == '-THREAD DONE-':
            buttons_availability(window, True)
        elif event in ('f1', 'f2', 'f3'): #fazy on off
            command = ['x', 'x', 'x']
            if values[event]:
                command[int(event[1]) - 1] = '1'
            else:
                command[int(event[1]) - 1] = '0'
            command = ''.join(command)
            sf = modules.MZF(w=window)
            if sf.self_test():
                sf.realy_switching(command)
            else:
                window[event].update(value=False)
            del sf
        elif event in ('b1', 'b2', 'b3', 'b4'): #baterie odłaczanie podłączanie
            pass
            """command = ['x', 'x', 'x', 'x']
            if values[event]:
                command[int(event[1]) - 1] = '1'
            else:
                command[int(event[1]) - 1] = '0'
            command = ''.join(command)
            sb = modules.MZB(w=window)
            if sb.self_test():
                sb.realy_switching(command)
            else:
                window[event].update(value=False)
            del sb"""
            # print('Brak ip MZF')
        elif event == '-RT-':
            raport.save_pdf(json_file, tuple(ident.keys()), tuple(tests[i].test_name for i in tuple(tests.keys())),
                            name='raporty\\' + ident['Nazwa:  '])
            print('Raport zapisany')
except Exception as e:
    sg.Print('Exception in my event loop for the program: ', sg.__file__, e, keep_on_top=True, wait=True)
    sg.popup_error_with_traceback('Problem in my event loop!', e)
finally:
    # Rozwarcie przekaźników faz i baterii
    sf = modules.MZF()
    if sf.self_test():
        sf.realy_switching('000')
    del sf
    #sb = modules.MZB()
    #if sb.self_test():
    #    sb.realy_switching('0000')
    #del sb
