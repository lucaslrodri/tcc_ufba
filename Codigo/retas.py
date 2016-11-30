import beaglebone_pru_adc as adc
import time
from flask import Flask, render_template, request, jsonify
import threading
from random import randint

class captureThread(threading.Thread):
    def __init__(self,range_,period):
        threading.Thread.__init__(self)
        self.range_ = range_
        self.period = period
        self.captureSample = [randint(0,period)+1000*x*period/range_ for x in range(self.range_)]
        print('Thread criado...')
    def run(self):
        while(True):
            self.captureData()
    def captureData(self):
        self.captureSample = [randint(0,self.period)+1000*x*self.period/self.range_ for x in range(self.range_)]
        
thread1 = captureThread(1000,1)
thread1.start()
thread2 = captureThread(1000,2)
thread2.start()
print("Thread criado.")
        
app = Flask(__name__)
@app.route('/')
def toolbox():
    web_data = {"internal" : thread1.captureSample, "external": thread2.captureSample}
    return render_template('toolbox.html', web_data = web_data)

@app.route('/config', methods=['POST'])
def toolbox_config():
    return ''
    
@app.route('/senddata', methods=['POST'])
def send_data():
    web_data = {"internal" : thread1.captureSample, "external": thread2.captureSample}
    return jsonify(web_data)
    
    
if __name__ == '__main__':
    app.run('0.0.0.0')
