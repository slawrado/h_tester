# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()
import uos, gc, ubinascii 
#uos.dupterm(None, 1) # disable REPL on UART(0)

#import webrepl
#webrepl.start()
gc.collect()
def do_connect(essid,password):
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(essid,password)
        while not wlan.isconnected():
            pass
    print(ubinascii.hexlify(wlan.config('mac'), ':'))    
    print('Network config:', wlan.ifconfig())
    print('Dhcp_hostname:',wlan.config('dhcp_hostname'))
#do_connect('APtelzas2007', 'sdfkrew33478jeritkjdfskjkdsjfiwjerijwrektjc324324wqeas32')
do_connect('H-system', 'dnpsamntwlpl&6691')