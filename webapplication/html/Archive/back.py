import random
import json


from flask import Flask, jsonify, make_response
from flask import request
from random import randint
import subprocess
import time
import os

app = Flask(__name__)

#  Entry level method for SMART analyzer.
#  It accpets aisle image path and product image path
#  as input and calls model pipeline to process
@app.route('/smart/analyze', methods = ['POST'])
def analyze_aisle_image():
   
   ais_audio_file = request.form.get('data', type=str)
   print(ais_audio_file)
   
   fil = open("testfile2.txt","wb") 
   fil.write(ais_audio_file) 
   fil.close() 


   resp = make_response(json.dumps(str(ais_audio_file)[2:-3]))
   resp.headers['Access-Control-Allow-Origin'] = '*'
   return resp


if __name__ == '__main__':
  app.run(host='0.0.0.0')

