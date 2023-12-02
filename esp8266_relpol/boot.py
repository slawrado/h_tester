# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()
import gc,network
#uos.dupterm(None, 1) # disable REPL on UART(0)
ap_if = network.WLAN(network.AP_IF)
print('ap_if ',ap_if.active())
print('Network config:',ap_if.ifconfig())
ap_if.active(False)
print('ap_if ',ap_if.active())
#import webrepl
#webrepl.start()
#machine.freq(160000000)
gc.collect()
def do_connect(essid,password):
    #import network
    sta_if  = network.WLAN(network.STA_IF)
    
    sta_if.active(True)
    
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.connect(essid,password)
        while not sta_if.isconnected():
            pass
    print('Network config:', sta_if.ifconfig())
    print('Dhcp_hostname:',sta_if.config('dhcp_hostname'))
do_connect('APtelzas2007', 'sdfkrew33478jeritkjdfskjkdsjfiwjerijwrektjc324324wqeas32')   
#do_connect('OnNetworks47', '58116142')