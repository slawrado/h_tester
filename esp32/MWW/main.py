from machine import Pin, I2C #SoftI2C, 
import sys, pcf8574, time
import usocket as socket

#p22 = Pin(22, Pin.IN, Pin.PULL_UP)
#p21 = Pin(21, Pin.IN, Pin.PULL_UP)

i2c = I2C(0, scl=Pin(22), sda=Pin(21),freq=50000)
#i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=100000)

pcf_list = []
adres_list = i2c.scan()
print(adres_list)
adres_list.reverse()
print(adres_list)
#argumenty: nr MWY, nr PIN (opcja), wartość do zapisu 0,1 dla konkretnego pinu lub bajt dla portu
def set_realy(value):
    if len(value) == 3:
        pcf_list[value[0]].pin(value[1], value[2])
    elif len(value) == 2:
        pcf_list[value[0]].port = value[1]
    elif len(value) == 1:
        pass
    return  pcf_list[value[0]].port

for i in adres_list:
    o = pcf8574.PCF8574(i2c, i)
    pcf_list.append(o)
    o.port = 0xff


           
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
        print('Waiting for connection ... ',end='')    
        conn, addr = s.accept()
        conn.settimeout(5.0)
        print('Received connection from %s' % str(addr),end='')        
        request = conn.recv(8)
        conn.settimeout(None)
        if request:
            
            print('request ->',request.decode())        
            conn.settimeout(None)
            r = [int(i) for i in request.decode().split(',')]
            read = set_realy(r)
            if len(r) == 3:
                print('MW*',hex(adres_list[r[0]]),'| pin nr',r[1],'write',r[2],'| stan {:08b}'.format(read),'| mem free',gc.mem_free())
            elif len(r) == 2:
                print('MW*',hex(adres_list[r[0]]),'write',r[1],'| stan {:08b}'.format(read),'| mem free',gc.mem_free())
            elif len(r) == 1:
                print('MW*',hex(adres_list[r[0]]),'| stan {:08b}'.format(read),'| mem free',gc.mem_free())    
            
            conn.send(str(read))
        else:
            pass
        conn.close()
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