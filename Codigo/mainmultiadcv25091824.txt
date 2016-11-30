import beaglebone_pru_adc as adc
import time
import smbus
import Adafruit_BBIO.GPIO as GPIO
from flask import Flask, render_template, request, jsonify
import threading

class captureThread(threading.Thread):
    def __init__(self, numSamples_ = 10000, numSamplesExternal_ = 100, delayCapture_ = 10, delayADC_ = 0, captureWindow_ = 100, oneTime_ = False, offset_ = 10, interface_refreshTime_ = 100, interface_refreshType_ = 0, ymin_ = 0, ymax_ = 4095, ytype_ = 1,ymin_external_ = 0, ymax_external_ = 65535):
        threading.Thread.__init__(self)
        self.numSamples = numSamples_
        self.numSamplesExternal = numSamplesExternal_
        self.delayCapture = delayCapture_
        self.delayADC  = delayADC_
        self.oneTime = oneTime_
        self.offset = offset_
        self.ytype = ytype_
        self.ymin = ymin_
        self.ymax = ymax_
        self.yminExternal = ymin_external_
        self.ymaxExternal = ymax_external_
        self.captureWindow = captureWindow_
        self.interface_refreshTime = interface_refreshTime_
        self.interface_refreshType = interface_refreshType_ #0 - continuo / 1 - uma vez
        self.captureSamples = ()
        self.captureSamplesExternal = ()
        print("ADC inicializado")
        print("Samples: ", self.numSamples, "Capture delay: ", self.delayCapture, "ADC speed: ", self.delayADC,"Offset: ", self.offset, "Interface refresh: ", self.interface_refreshTime, "interface_refreshType", self.interface_refreshType)
    def run(self):
        print("Iniciando captura do ADC interno...")
        print("Iniciando captura do ADC externo...")
        while(self.oneTime == False):
            self.captureData()
        print("Processo terminado.")
    def captureData(self):
        capture = adc.Capture()
        bus = smbus.SMBus(1)
        data = [0x84, 0x83]
        bus.write_i2c_block_data(0x48, 0x01, data)
        i = 0
        time.sleep(0.5)
        actual_time = time.clock()
        if self.delayADC != 0:
            capture.cap_delay = self.delayADC
    
        capture.oscilloscope_init(adc.OFF_VALUES, self.numSamples) # captures AIN0 - the first elt in AIN array
        capture.start()
        captureSamplesBuffer = []
        internalADC_complete = False
        externalADC_complete = False
        while(True):
            if (externalADC_complete == False):
                data = bus.read_i2c_block_data(0x48, 0x00, 2)
                raw_adc = data[0]*256 + data[1]
                if(i < self.numSamplesExternal):
                    captureSamplesBuffer.append(raw_adc)
                else:
                    self.captureSamplesExternal = tuple(captureSamplesBuffer)
                    del captureSamplesBuffer[:]
                    captureSamplesBuffer = []
                    i = 0
                    externalADC_complete = True
            if (capture.oscilloscope_is_complete() and internalADC_complete == False):
                internalADC_complete = True
            if (externalADC_complete and internalADC_complete):
                break;
            time.sleep(self.delayCapture/1000)
        
        capture.stop()
        capture.wait()
        print("Buffer atualizado com %d amostras."%(self.numSamples,))
        self.captureSamples = capture.oscilloscope_data(self.numSamples)
        capture.close()

thread1 = captureThread()
thread1.start()
print("Thread criado.")
        
app = Flask(__name__)
@app.route('/')
def toolbox():
    internal_adc = []
    for x in thread1.captureSamples[thread1.offset:len(thread1.captureSamples)]:
        internal_adc.append(int(x))
    external_adc = thread1.captureSamplesExternal
    web_data = {"internal" : internal_adc, "external": list(external_adc)}
    return render_template('toolbox.html', web_data = web_data, noSamples = thread1.numSamples, delayADC = thread1.delayCapture, offsetADC = thread1.offset, speedADC = thread1.delayADC, interface_refreshType = thread1.interface_refreshType, interface_frameRate = thread1.interface_refreshTime, windowSamples = thread1.captureWindow, ytype = thread1.ytype, ymin = thread1.ymin, ymax = thread1.ymax)

"""@app.route('/config')
def toolbox_config():
    pass"""

@app.route('/config', methods=['POST'])
def toolbox_config():
    thread1.numSamples =  int(request.form['adc_captureSamples'])
    thread1.delayCapture = int(request.form['adc_captureDelay'])
    thread1.offset = int(request.form['adc_captureOffset'])
    thread1.delayADC = int(request.form['adc_captureSpeed'])
    thread1.interface_refreshType = int(request.form['interface_refreshType'])
    thread1.ytype = int(request.form['ytype'])
    if thread1.ytype == 1:
        thread1.ymin = int(request.form['ymin'])
        thread1.ymax = int(request.form['ymax'])
    if thread1.interface_refreshType == 0:
        thread1.interface_refreshTime = int(request.form['interface_frameRate'])
    thread1.captureWindow = int(request.form['adc_windowSize'])
    print("Samples: ", thread1.numSamples, "Capture delay: ", thread1.delayCapture, "ADC speed: ", thread1.delayADC,"Offset: ", thread1.offset, "Interface refresh: ", thread1.interface_refreshTime, "interface_refreshType", thread1.interface_refreshType)
    return ''
    
@app.route('/senddata', methods=['POST'])
def send_data():
    web_data = []
    for x in thread1.captureSamples[thread1.offset:len(thread1.captureSamples)]:
        web_data.append(int(x))
    return jsonify(web_data)
    
    
if __name__ == '__main__':
    app.run('0.0.0.0')
