# RTU Master setup
# act as host, get Modbus data via RTU from a client device
from umodbus.serial import Serial as ModbusRTUMaster
import time
import usocket as socket
#slave_addr = 1             # bus address of client

host = ModbusRTUMaster(
    #pins=(17,16),      # given as tuple (TX, RX), check MicroPython port specific syntax
    pins=(26,25),      # given as tuple (TX, RX), check MicroPython port specific syntax
    #baudrate=9600,    # optional, default 9600
    #data_bits=8,      # optional, default 8
    #stop_bits=1,      # optional, default 1
    parity=0,      # optional, default None
    ctrl_pin=27,      # optional, control DE/RE
    uart_id=1       # optional, see port specific documentation
)
# READ IREGS

def read_in_reg(slave_addr=1,starting_addr=281,register_qty=1,signed=False):
    try:
        register_value = host.read_input_registers(
                            slave_addr=slave_addr,
                            starting_addr=starting_addr,
                            register_qty=register_qty,
                            signed=signed)
        return register_value
    except OSError as error:
        print(error)
def read_coil(slave_addr=1,starting_addr=281,coil_qty=1):
    try:
        coil_status = host.read_coils(
            slave_addr=slave_addr,
            starting_addr=starting_addr,
            coil_qty=coil_qty)
        return coil_status
    except OSError as error:
        print(error)     
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
        request = conn.recv(3)
        conn.settimeout(None)
        if request:
            
            print('request ->',request.decode())
            if request.decode() == '000':
                tryb_pracy = str(read_in_reg()[0])

            else:
                tryb_pracy = request.decode()
            conn.settimeout(None)           
            conn.send(tryb_pracy.encode())
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


#print(read_in_reg()[0],type(read_in_reg()[0]))