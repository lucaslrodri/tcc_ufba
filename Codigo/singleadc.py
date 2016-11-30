import beaglebone_pru_adc as adc
import time
from flask import Flask, render_template, request, jsonify
import threading

class captureThread(threading.Thread):
    def __init__(self, numSamples_ = 10000, delayCapture_ = 0, delayADC_ = 0, captureWindow_ = 100, oneTime_ = False, offset_ = 10, interface_refreshTime_ = 100, interface_refreshType_ = 0, ymin_ = 0, ymax_ = 4095, ytype_ = 1):
        threading.Thread.__init__(self)
        self.numSamples = numSamples_
        self.delayCapture = delayCapture_
        self.delayADC  = delayADC_
        self.oneTime = oneTime_
        self.offset = offset_
        self.ytype = ytype_
        self.ymin = ymin_
        self.ymax = ymax_
        self.captureWindow = captureWindow_
        self.interface_refreshTime = interface_refreshTime_
        self.interface_refreshType = interface_refreshType_ #0 - continuo / 1 - uma vez
        self.captureSamples = ()
        print("ADC inicializado")
        print("Samples: ", self.numSamples, "Capture delay: ", self.delayCapture, "ADC speed: ", self.delayADC,"Offset: ", self.offset, "Interface refresh: ", self.interface_refreshTime, "interface_refreshType", self.interface_refreshType)
    def run(self):
        print("Iniciando captura...")
        while(self.oneTime == False):
            self.captureData()
            time.sleep(self.delayCapture/1000)
        print("Processo terminado.")
    def captureData(self):
        capture = adc.Capture()
        
        if self.delayADC != 0:
            capture.cap_delay = self.delayADC

        capture.oscilloscope_init(adc.OFF_VALUES, self.numSamples) # captures AIN0 - the first elt in AIN array
        capture.start()
        
        while(True):
            if capture.oscilloscope_is_complete():
                break
        
        capture.stop()
        capture.wait()
        #print("Buffer atualizado com %d amostras."%(self.numSamples,))
        self.captureSamples = capture.oscilloscope_data(self.numSamples)
        capture.close()

"""while(True):
    try:
        thread1 = captureThread()
        thread1.start()
        print("Thread criado.")
        break
    except:
        print("Erro ao iniciar a captura de dados, tentando novamente...")
        time.sleep(1)"""
thread1 = captureThread()
thread1.start()
print("Thread criado.")
        
app = Flask(__name__)
@app.route('/')
def toolbox():
    web_data = []
    for x in thread1.captureSamples[thread1.offset:len(thread1.captureSamples)]:
        web_data.append(int(x))
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
