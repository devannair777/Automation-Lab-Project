from tensorflow.keras.models import load_model
import redpitaya_scpi as scpi
import numpy as np
import scipy
import time
from python_speech_features import mfcc

rp = scpi.scpi("192.168.128.1")
refBuffer = 3200
sampleRate = 16384
print("Connected to Device, Acquiring Data Now...")

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
    mfcc_feat = mfccRepresentation(sig)
    return mfcc_feat

def estimate(name):
    f= []
    for i in range(5):
        f.append(pollInstanceSample())
        time.sleep(1)
    features = np.vstack(f)
    features = np.reshape(features, (features.shape[0], 1, features.shape[1]))
    model = load_model(name)
    yhat = model.predict(features)
    print(yhat)
    indices = []
    for i in range(yhat.shape[0]):
        maxIndex = np.where(yhat[i] == np.amax(yhat[i]))[0]
        indices.append(maxIndex)

    t = np.vstack(indices)
    class1 = (np.count_nonzero(t == 0))
    class2 = (np.count_nonzero(t == 1))
    class3 = (np.count_nonzero(t == 2))

    prob = np.array([class1,class2,class3])
    detected = np.where(prob == np.amax(prob))[0][0]
    print('Class of Object Detected : '+str(detected))
    return detected

def enableIndication():
    index = estimate('lstm_model.h5')
    if index == 0:
        rp.tx_txt('DIG:PIN LED1' + ',' + str(1))  
        rp.tx_txt('DIG:PIN LED2' + ',' + str(0))  
        rp.tx_txt('DIG:PIN LED3' + ',' + str(0))   
    elif index == 1:
        rp.tx_txt('DIG:PIN LED1' + ',' + str(0))  
        rp.tx_txt('DIG:PIN LED2' + ',' + str(1))  
        rp.tx_txt('DIG:PIN LED3' + ',' + str(0))
    elif index == 2:
        rp.tx_txt('DIG:PIN LED1' + ',' + str(0))  
        rp.tx_txt('DIG:PIN LED2' + ',' + str(0))  
        rp.tx_txt('DIG:PIN LED3' + ',' + str(1))



if __name__=='__main__':
    while True:
        enableIndication()

