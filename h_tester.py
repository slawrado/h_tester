"""Okna aplikacji"""
import errno
import os
#import shelve
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

selftest = False #Pomijamy sprawdzenie modulów

operators = ['A.Salamon', 'M.Dżygun', 'W.Sławiński', 'Z.Batogowski', 'W.Tomczyk', 'K.Hamann']
test_keys = ('-UKB', '-OUTPUT-Q1', '-OUTPUT-MWY', '-INPUTS', '-STYCZNIK', '-BOCZNIK', '-CZUJNIK-TEMP', '-BAT-FUSE',
             '-PROSTOWNIK', '-MZK', '-RS485', '-ASYM', '-BAT-FUSE-MOD', '-CZUJNIK-MZK')
test_clasess = (testy.TestUkb, testy.TestOutputQ1, testy.TestOutputMWY, testy.TestInput,
                testy.TestStycznika, testy.TestBocznika, testy.TestCzujnikowTemp,
                testy.TestBaterryFuses, testy.TestRectifier, testy.TestMZK, testy.TestRs485,
                testy.TestAsymBat, testy.TestBezpiecznikaBat, testy.TestCzujnikowMZK)
tests = dict(zip(test_keys, test_clasess))

config = dict(zip(test_keys, tuple(len(test_keys) * [0])))
rezult = dict(zip(test_keys, tuple(len(test_keys) * [False])))
config_range = {'-OUTPUT-Q1': [i for i in range(5)], '-OUTPUT-MWY': [i for i in range(9)],
                '-INPUTS': [i for i in range(0, 17, 8)], '-STYCZNIK': [i for i in range(4)],
                '-BOCZNIK': [i for i in range(2)], '-CZUJNIK-TEMP': [i for i in range(4)],
                '-BAT-FUSE': [i for i in range(5)], '-MZK': [i for i in range(2)], '-RS485': [i for i in range(2)],
                '-ASYM': [i for i in range(2)], '-BAT-FUSE-MOD': [i for i in range(2)], '-CZUJNIK-MZK': [i for i in range(2)]}
ident = {'Nazwa:  ': '', 'Indeks:  ': '', 'Nr seryjny:  ': '', 'Nr seryjny Q1:  ': '',
         'Wersja programu Q1:  ': '', 'Wersja konfiguracji Q1:  ': '', 'Operator:  ':  '', 'Data:  ':  ''}

indeks_nazwa = {'0-000-0': ('xxx xxx', 'OS-000000-0000'),
                 '9070-00696-22': ('Modernizacja Benning', 'OS-000310-002E'), 
                 '9070-00696-28': ('Modernizacja Benning', 'OS-000310-002E'),
                 '9030-00328': ('H-system', 'OS-000311-002A')}
indeks_config = {'9070-00696-22': {'-UKB': 1, '-OUTPUT-Q1': 0, '-OUTPUT-MWY': 7, '-INPUTS': 0, '-STYCZNIK': 2, '-BOCZNIK': 1,
                             '-CZUJNIK-TEMP': 1, '-BAT-FUSE': 0, '-PROSTOWNIK': 4, '-MZK': 0, '-RS485': 0,
                             '-ASYM': 1, '-BAT-FUSE-MOD': 1, '-CZUJNIK-MZK': 0},
                 '9070-00696-28': {'-UKB': 1, '-OUTPUT-Q1': 0, '-OUTPUT-MWY': 7, '-INPUTS': 0, '-STYCZNIK': 2, '-BOCZNIK': 1,
                             '-CZUJNIK-TEMP': 1, '-BAT-FUSE': 0, '-PROSTOWNIK': 4, '-MZK': 0, '-RS485': 0,
                             '-ASYM': 1, '-BAT-FUSE-MOD': 1, '-CZUJNIK-MZK': 0},
                 '9030-00328': {'-UKB': 0, '-OUTPUT-Q1': 0, '-OUTPUT-MWY': 0, '-INPUTS': 0, '-STYCZNIK': 0, '-BOCZNIK': 0,
                             '-CZUJNIK-TEMP': 0, '-BAT-FUSE': 0, '-PROSTOWNIK': 0, '-MZK': 1, '-RS485': 0,
                             '-ASYM': 0, '-BAT-FUSE-MOD': 0, '-CZUJNIK-MZK': 1}          }

json_file = {}
json_file.update(ident)
stop_test, non_edit = False, False


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
text_p = dict(zip(test_keys, tip))


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
    """Uruchamia wszystkie skonfigurowane testy."""

    for i in test_keys:
        w[i + 'R'].update('')  # zerowanie wników testów
    liczba_testow = len(config) - list(config.values()).count(0)
    print('Liczba zaplanowanych testów: ', liczba_testow)
    if stop_test:
        print('Zatrzymanie testów po pierwszym negatywnym !')
    start = datetime.now()
    for i in test_keys:
        if config[i]:  # jeśli test został skonfigurowny tzn != 0
            print('Test numer: {}'.format(test_keys.index(i)+1))
            w[i + 'R'].update('In progress', text_color='yellow')
            w.refresh()
            ti = tests[i](config[i], w)
            if ti.test():  # jeśli wykonał się poprawnie: zwrócił True
                w[i + 'R'].update('Ok', text_color='white')
                rezult[i] = True
            else:
                w[i + 'R'].update('Fail', text_color='red')
                if stop_test:
                    return
            time.sleep(2)
        else:
            print('Test nr:  {} pominięty w konfiguracji.'.format(test_keys.index(i) + 1))
            w[i + 'R'].update('Not configured', text_color='grey')
            w.refresh()
        w.refresh()
    # dane do raportu
    for i in ident:
        json_file[i] = ident[i]
    wynik = []
    for i in test_keys:
        if config[i]:
            wynik.append(rezult[i])
            json_file[tests[i].test_name] = rezult[i], config[i]
        else:
            if tests[i].test_name in json_file:
                del json_file[tests[i].test_name]

    #if config['-PROSTOWNIK']:
        #json_file['prostowniki'] = q1.get_rectifier_serial()#numery seryjne prostowników
    
    if all(wynik):
        q1 = modules.Q1()
        q1.set_dufault_ip()
        del q1
        print('Adres 192.168.5.120 , dhcp off')
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
    col1, col2, col3 = [], [], []
    for i in test_keys:
        col1.append([sg.Text('{:>2}. {}'.format(test_keys.index(i) + 1, tests[i].test_name), key=i + 'P', tooltip=text_p[i])])
        col2.append([sg.Text(size=(12, 1), key=i + 'R')])
    for i in ident:
        col3.append([sg.Text(' ' + i + ident[i], size=(34, 1), key=i)])
    col3.append([sg.Text(size=(34, 1), key='-3')])  # , visible=False
    layout = [[sg.Text('Stan przekaźników: '),

               sg.Checkbox('Faza1', enable_events=True, key='f1'),
               sg.Checkbox('Faza2', enable_events=True, key='f2'),
               sg.Checkbox('Faza3', enable_events=True, key='f3'),
               sg.Checkbox('Bat1', enable_events=True, key='b1'),
               sg.Checkbox('Bat2', enable_events=True, key='b2'),
               sg.Checkbox('Bat3', enable_events=True, key='b3'),
               sg.Checkbox('Bat4', enable_events=True, key='b4'),
               # sg.Text('| Self test: ', size=(18, 1)),
               ],

              [sg.HSep()],
              [sg.Button('Self test & power ON', key='-SF-', expand_x=True),
               sg.Button('Konfiguracja testów', key='-KT-', disabled=True, expand_x=True)],  #
              [sg.HSep()],
              [sg.Column(col1), sg.Column(col2), sg.Frame(' Identyfikacja ', col3)],
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
                                  enable_events=True, text_color='gray', key='-OUTPUT-', auto_size_text=True)]]
    layout.append([sg.Frame(" Work preview  ", frame_layout, element_justification='center')])

    return sg.Window('H tester', layout, finalize=True)


# 'alice blue'
def make_conf_window():
    """Tworzy okno konfiguracji testów"""
    col1, col2 = [], []
    
    for i in test_keys:
        
        col1.append([sg.Text(' {:>2}. {}: '.format(test_keys.index(i) + 1, tests[i].config_name))])
        if i in ('-UKB', '-PROSTOWNIK'):
            col2.append([sg.Input(size=(5, 1), default_text=config[i], enable_events=True, justification='right',
                      expand_x=True, key=i, disabled=non_edit)])          
        else:
            col2.append([sg.Combo(config_range[i], size=(4, 1), default_value=config[i], enable_events=True,
                      expand_x=True, key=i, disabled=non_edit)])
    layout = [

        [sg.Text('Konfiguracja testów: ')],

        [sg.Checkbox('Zakończ po pierwszym negatywnym.', key='test_break', enable_events=True, )],
        [sg.Column(col1), sg.Column(col2, element_justification='right', expand_x=True)],
        [sg.HSep()],
        [sg.Button('Zapisz', tooltip='')]]
    return sg.Window('Konfiguracja', layout, location=(0, 50), finalize=True).make_modal()


# main_window['-ST-'].set_focus()
def self_test():
    """Sprawdza komunikację z modułami testera."""
    # ip['-MWW-'], ip['-MZF-'], ip['-LOAD-'] , ip['-MZB-']= '192.168.1.102', '192.168.1.101',
    # '192.168.1.103', '192.168.1.105' # MWW 102
    # result = False
    if not selftest:
        return True
        
    if modules.ping('192.168.1.1'):
        print('Dostęp do sieci 192.168.1.xxx OK')
        # w.refresh()
    else:
        print('Nie masz dostępu do sieci 192.168.1.xxx')
        # w.refresh()
        return False
    required = set()  # wymagane moduły dla danej konfiguracji testów.
    for i in test_keys:
        if config[i]:
            for j in tests[i].required_modules:
                required.add(j)
    if ident['Indeks:  '] == '0-000-0':
        required = {modules.MZF, modules.LOAD, modules.MWW, modules.Q1}  # modules.RS485 modules.MZB,
   
    #required.remove(modules.Q1)
    for k in required:
        """if k == modules.Q1:
            if k(ip_q1).self_test():
                print(f'Komunikacja z {k.__name__} OK.')
                # w.refresh()
            else:
                print(f'Brak komunikacji z {k.__name__}.')
                # w.refresh()
                return False
        else:"""
        if k().self_test():
            print(f'Komunikacja z {k.__name__} OK.')
            # w.refresh()
        else:
            print(f'Brak komunikacji z {k.__name__}.')
            # w.refresh()
            return False
    # w.refresh()

    return True


def buttons_availability(w, stan):
    """Aktywuje lub dezaktywuje przyciski"""
    for i in ('-SF-', '-ST-', '-RT-', 'f1', 'f2', 'f3', 'b1', 'b2', 'b3', 'b4'):
        if stan:
            w[i].update(disabled=False)
        else:
            w[i].update(disabled=True)
    if ident['Indeks:  '] == '0-000-0':
        if stan:
            w['-KT-'].update(disabled=False)
        else:
            w['-KT-'].update(disabled=True)

# Utworzenie katalogu do zapisu raportów z testów


try:
    os.makedirs('raporty')
except OSError as e:
    if e.errno != errno.EEXIST:
        raise
"""if exists('gfg.dat'):
    shelve_file = shelve.open("gfg")
    ident['Operator:  '] = shelve_file['ident']['Operator:  ']
    shelve_file.close()"""
# Okno do wpisania indeksu i numeru serejnego testowanej siłowni
event, values = sg.Window('Indeksy',
                          [[sg.Text('Indeks: ', size=(15, 1)),
                            sg.Combo(values=list(indeks_nazwa.keys()), size=(15, 1),
                                     key='Indeks:  ', default_value=list(indeks_nazwa.keys())[1])],
                           [sg.Text('Numer seryjny: ', size=(15, 1)),
                            sg.Input(size=(15, 1), justification='right',
                                     expand_x=True, key='Nr seryjny:  ')],
                           [sg.Text('Operator: ', size=(15, 1)),
                            sg.Combo(operators, size=(15, 1), default_value=operators[2],  # ident['Operator:  ']
                                     key='Operator:  ')],
                            [sg.Text('Operator2: ', size=(15, 1)),         
                            sg.Combo(operators, size=(15, 1), default_value=operators[2],  # ident['Operator:  ']
                                     key='Operator2:  ')],                                     

                           [sg.Button('OK'), ]]).read(close=True)
# 'Indeks:  ': '', 'Nr seryjny:  '
if event == sg.WINDOW_CLOSED:
    sys.exit()
if values['Indeks:  '] and values['Indeks:  '] != '0-000-0':
    config = indeks_config[values['Indeks:  ']]
    non_edit = True
    ident['Indeks:  '], ident['Nr seryjny:  '], ident['Operator:  '] = values['Indeks:  '], values['Nr seryjny:  '], values['Operator:  ']
    ident['Operator2:  '] = values['Operator2:  ']

else:
    ident['Indeks:  '], ident['Nr seryjny:  '], ident['Operator:  '] = values['Indeks:  '], values['Nr seryjny:  '], values['Operator:  ']
    ident['Operator2:  '] = values['Operator2:  ']

main_window, conf_window = make_main_window(), None
# Główna pętla aplikacji.
try:
    while True:
        window, event, values = sg.read_all_windows()
        if event == sg.WIN_CLOSED or event == 'Exit':
            if window == conf_window:
                conf_window = None
            elif window == main_window:
                sf = modules.MZF()
                if sf.self_test():
                    sf.realy_switching('000')
                del sf
                """sb = modules.MZB()
                if sb.self_test():
                    sb.realy_switching('0000')
                del sb"""
                break
            if window:
                window.close()
        elif event == '-KT-' and not conf_window:
            """if exists('gfg.dat'):
                shelve_file = shelve.open("gfg")
                ident = shelve_file['ident']
                shelve_file.close()"""
            conf_window = make_conf_window()
        elif event == '-SF-':
            buttons_availability(window, False)
            window.perform_long_operation(self_test, '-RETURN_TRIGGER-')
        elif event == '-RETURN_TRIGGER-':
            # if self_test(window):
            if values['-RETURN_TRIGGER-']:
                print('Self test OK.')
                print('Power ON ...')
                window.refresh()

                if selftest:
                    sf = modules.MZF(w=main_window)
                    sf.realy_switching('111')
                    for i in range(3):
                        time.sleep(1)
                        window.refresh()
                    del sf

                    for i in range(6):
                        time.sleep(1)
                        window.refresh()
                #q1ip = modules.search_q1_ip()
                #if q1ip:
                    
                    #print('Komunikacja z Q1 OK')

                q1 = modules.Q1() 
                ident['Nr seryjny Q1:  '], ident['Wersja programu Q1:  '], \
                    ident['Wersja konfiguracji Q1:  '] = q1.ident_inf()

                ident['Data:  '] = datetime.now().strftime("%d/%m/%Y")
                if ident['Indeks:  '] in indeks_nazwa.keys():
                    ident['Nazwa:  '] = indeks_nazwa[ident['Indeks:  ']][0]
                for i in ident:
                    main_window[i].update(i + ident[i])
                if int(ident['Wersja programu Q1:  '].split('b')[1]) >= 30:
                    pass
                else:
                    main_window['Wersja programu Q1:  '].update(text_color='red')
                    print('Tester wymaga Q1 z wersją 1.0b30 lub wyższą.')                
                if ident['Wersja konfiguracji Q1:  '] != indeks_nazwa[ident['Indeks:  ']][1] and ident['Indeks:  '] != '0-000-0':
                    main_window['Wersja konfiguracji Q1:  '].update(text_color='red')
                    print(f"Nieprawidłowa wersja konfiguracji -> {ident['Wersja konfiguracji Q1:  ']}")
                    print(f"Prawidłowa wersja konfiguracji    -> {indeks_nazwa[ident['Indeks:  ']][1]}")
                    test_button_disable = True
                else:
                    print(f"Wersja konfiguracji Q1 -> {indeks_nazwa[ident['Indeks:  ']][1]} OK")
                    
                del q1
                #else:
                    #print('Brak komunikacjia z Q1')
                    #window['-OUTPUT-'].update('Self test error.\n', text_color_for_value='red', append=True)
            else:
                window['-OUTPUT-'].update('Self test error.\n', text_color_for_value='red', append=True)
            for j in test_keys:
                if not config[j]:
                    window[j + 'P'].update(text_color='gray')
                else:
                    window[j + 'P'].update(text_color='white')
            buttons_availability(window, True)
        elif event == 'Zapisz':
            test_button_disable = False
            # window.refresh()
            for i in config:
                if i == '-UKB' or i == '-PROSTOWNIK':
                    config[i] = check_number(values[i], i)
                else:
                    config[i] = int(values[i])
            if values['test_break']:
                stop_test = True
            else:
                stop_test = False

            q1 = modules.Q1()
            ident['Nr seryjny Q1:  '], ident['Wersja programu Q1:  '],\
                ident['Wersja konfiguracji Q1:  '] = q1.ident_inf()

            ident['Data:  '] = datetime.now().strftime("%d/%m/%Y")
            if int(ident['Wersja programu Q1:  '].split('b')[1]) >= 30:
                pass
            else:
                main_window['Wersja programu Q1:  '].update(text_color='red')
                # ident_value['-DATA'] = ''
                print('Tester wymaga Q1 z wersją 1.0b30 lub wyższą.')
                test_button_disable = True
                window.close()
 
            """if len(values['Nr seryjny:  ']) > 0 and ' ' in values['Nr seryjny:  ']:
                ident['Indeks:  '], ident['Nr seryjny:  '] = values['Nr seryjny:  '].strip().split(' ')"""
            if ident['Indeks:  '] in indeks_nazwa.keys():
                ident['Nazwa:  '] = indeks_nazwa[ident['Indeks:  ']][0]
                main_window['Indeks:  '].update(text_color='white')
                if ident['Wersja konfiguracji Q1:  '] != indeks_nazwa[ident['Indeks:  ']][1] and ident['Indeks:  '] != '0-000-0':
                    main_window['Wersja konfiguracji Q1:  '].update(text_color='red')
                    print(f"Nieprawidłowa wersja konfiguracji -> {ident['Wersja konfiguracji Q1:  ']}")
                    print(f"Prawidłowa wersja konfiguracji    -> {indeks_nazwa[ident['Indeks:  ']][1]}")
                    test_button_disable = True
                    window.close()
                    # main_window['-ST-'].update(disabled=False)
            else:
                main_window['Indeks:  '].update(text_color='red')
                ident['Nazwa:  '] = 'Unidentified'
                print(f"Tester nie obsługuje wyrobu o indeksie:  {ident['Indeks:  ']}")
                test_button_disable = True
                window.close()
            """else:
                window['Nr seryjny:  '].update(text_color='red')
                print('Nieprawidłowe format (oczekiwany:  indeks spacja numer seryjny)')"""
            del q1
            if all(ident.values()):
                # for i in ip:  print('{}{: 10}->{}'.format('Adres ip ', i.strip('-'), ip[i]))

                """shelve_file = shelve.open("gfg")
                shelve_file['ident'] = ident
                shelve_file.close()"""
                # for i in ident_name:  window[i].update(ident_name[i]+ident_value[i])
                for i in ident:
                    main_window[i].update(i + ident[i])
                for j in test_keys:
                    if not config[j]:
                        main_window[j + 'P'].update(text_color='gray')
                    else:
                        main_window[j + 'P'].update(text_color='white')
                window.close()
            main_window['-ST-'].update(disabled=test_button_disable)
            if not test_button_disable:
                print(f'Konfiguracja zapisana.')
        elif event == '-ST-':
            buttons_availability(window, False)
            test_all()
        elif event == '-THREAD DONE-':
            buttons_availability(window, True)
        elif event in ('f1', 'f2', 'f3'):
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
        elif event in ('b1', 'b2', 'b3', 'b4'):
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
            raport.save_pdf(json_file, tuple(ident.keys()), tuple(tests[i].test_name for i in test_keys),
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
