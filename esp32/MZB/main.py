import usocket as socket
import sys, time, machine
#4-D4,13-D13,12-D12
nr_pin = (23, 22, 21, 19)

def odczyt():
    r = ''
    for j in [(machine.Pin(i).value()) for i in nr_pin]:
        r += str(j)
    return r
    
def setPin(v):
    for i,j in enumerate(v):
        if j != 'x':
            machine.Pin(nr_pin[i]).value(int(j))
        else:
            pass
    return odczyt()        

print(odczyt())    
for i in nr_pin: machine.Pin(i, machine.Pin.OUT)
print(odczyt())

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.setblocking(True)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', 9090))
s.listen(2)
print('mem free',gc.mem_free())
while True:
    try:
        request = None
        if gc.mem_free() < 102000:
            print('mem free beafore',gc.mem_free())
            gc.collect()
            print('mem free after',gc.mem_free())    
            
        print("Waiting for connection...",end='')                  
        conn, addr = s.accept()        
        conn.settimeout(5.0)
        print('Received connection from %s' % str(addr),end=' ')        
        request = conn.recv(4)
        conn.settimeout(None)
        if request:
            print('request ->',request.decode()) 
            stan = setPin(request.decode())        
            conn.settimeout(None)           
            conn.send(stan.encode())
        else:
            pass
        conn.close()
        #print('Connection close')
    except OSError as e:
        #conn.close()
        print('OS error',e)
        print(gc.mem_free())
        time.sleep(1)
    except KeyboardInterrupt:
        if request:
            conn.close()
        print('Ctr C done')
        sys.exit()       

