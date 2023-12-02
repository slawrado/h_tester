#import usocket as socket
import sys, time, errno,socket
#12-D6,13-D7,14-D5
nr_pin = (12, 13, 14)
name = {12:'faza1',13:'faza2',14:'faza3'}

def odczyt():
    r = ''
    for j in [(machine.Pin(i).value()) for i in nr_pin]:
        r += str(j)
    return r
    
def setPin(p,v):
    machine.Pin(p).value(v)
def check_request(r):
    r = r.decode()
    if ',' in r:
        r = r.split(',')

    else:
        return False
    if r[0].isdigit() and r[1].isdigit():
        p, v  = int(r[0]), int(r[1])
        
        if p in nr_pin and v in (0,1):        
            return (p,v)
        else:
            return False
    else:
        return False
print(odczyt())    
for i in nr_pin: machine.Pin(i, machine.Pin.OUT)
print(odczyt())

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(5.0)
s.setblocking(True)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', 9090))
s.listen(1)
print('mem free',gc.mem_free())
while True:
    conn = None
    if gc.mem_free() < 30000:
        print('mem free beafore',gc.mem_free())
        gc.collect()
        print('mem free after',gc.mem_free())    
    try:        
        #print("Waiting for connection...")                  
        conn, addr = s.accept()        
        conn.settimeout(5.0)
        print('Received connection from %s' % str(addr),end=' ')        
        request = conn.recv(4)
        print(request)
        conn.settimeout(None)
        if request and check_request(request) :
            p,v = check_request(request)
            setPin(p,v)        
            conn.settimeout(None)            
            conn.send(str(odczyt()).encode())
        else:
            conn.send(str(odczyt()).encode())
            #conn.sendall('Allowed pin:'+str(nr_pin)+',alowed value 0 or 1')
            continue
            print('continue')
        conn.close()
    except OSError as exc:
        if exc.args[0] == errno.ETIMEDOUT:    #case for ESP8266
            print("Caught OSError: ETIMEDOUT")
            time.sleep(1)
        elif exc.args[0] == errno.EAGAIN:     #case for ESP32
            print("Caught OSError: EAGAIN")
        else:
            print(exc.args[0])
            time.sleep(2)
    except KeyboardInterrupt:
        if conn:
            conn.close()
        print('Ctr C done')
        sys.exit()
    finally:
        if conn:
            conn.close()        