import redpitaya_scpi as scpi
import numpy as np
import matplotlib.pyplot as plt

rp = scpi.scpi("192.168.128.1")

print("Connected to Device, Acquiring Data Now...")

while 1:
    rp.tx_txt("ACQ:DEC 64")
    rp.tx_txt("ACQ:TRIG EXT_PE")
    rp.tx_txt("ACQ:TRIG:DLY 8192")
    rp.tx_txt("ACQ:START")
    
    while 1:
        rp.tx_txt('ACQ:TRIG:STAT?')
        if rp.rx_txt() == 'TD':
            break
    
    rp.tx_txt("ACQ:SOUR1:DATA?")
    
    str_res = rp.rx_txt()
    
    res = str_res[1:-1]
    
    array = np.fromstring(res, dtype=float, sep=",")
    
    plt.plot(array)
    plt.pause(1)
    plt.close()