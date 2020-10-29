import redpitaya_scpi as scpi
import numpy as np
import matplotlib.pyplot as plt
import csv
from matplotlib.animation import FuncAnimation
from numpy.fft import fft,fftfreq
from python_speech_features import mfcc

rp = scpi.scpi("192.168.128.1")
refBuffer = 3200
sampleRate = 16384
print("Connected to Device, Acquiring Data Now...")
objClass = 'Demo'

def mfccRepresentation(signal):
    mfcc_feat = mfcc(signal,sampleRate)[0]
    return mfcc_feat

def pollInstanceSample():
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
    
    array = np.fromstring(res, dtype=float, sep=",") #Length of Sample is 16384
    array = array[refBuffer:-1]
    sig = np.array([array])
    with open('mfcc/'+objClass+'/TimeRepresentation.csv','ab') as persistObject:
        np.savetxt(persistObject,sig,fmt='%3.4f',delimiter=';')
      
    samples = np.linspace(0,len(array)-1,len(array))
    mfcc_feat = mfccRepresentation(sig)
    feat_sig = np.array([mfcc_feat])
    with open('mfcc/'+objClass+'/FeatureRepresentation.csv','ab') as persistObject2:
        np.savetxt(persistObject2,feat_sig,fmt='%3.4f',delimiter=';')

    plt.clf()
    plt.subplot(2,1,1)
    plt.plot(samples,array)
    plt.title('Time Domain representation')
    plt.xlabel('Samples')
    plt.ylabel('Amplitude')
    
    plt.subplot(2,1,2)
    plt.plot(mfcc_feat)
    plt.title('MFCC Coefficients')
    plt.xlabel('Index')
    plt.ylabel('Amplitude')
    

def animate(i):
    pollInstanceSample()

animation = FuncAnimation(plt.gcf(),animate,interval=500)   
plt.show() 
    