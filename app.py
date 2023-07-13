from flask import Flask,render_template,request,jsonify
import numpy as np
from prediction import get_prediction


app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/predict', methods=["post"])
def predict():
    data = [float(x) for x in request.form.values() ]
   
    result = get_prediction([data])
    print( 'Result', result[0])
    if result[0] == 0 :
        output = 'Not Noisy'
    else:
        output = 'Noisy'
    return render_template('index.html',result=output)




if '__main__' == __name__:
    app.run(debug=True)

