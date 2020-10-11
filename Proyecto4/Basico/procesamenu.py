from flask import Flask, jsonify, request, make_response
import numpy as np
import csv
import json
import tflite_runtime.interpreter as tflite

app = Flask(__name__)
interpreter = 0
input_details = 0
output_details = 0
means = 0
stds = 0

#Este apartado es para que no de error de AllowAccessControl por venir la peticion desde localhost
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

#Escala un array en funcion de las medias y desviaciones calculadas durante el entrenamiento
def scale_data(array):
    global means, stds
    return (array-means)/stds

#Inicializa el interprete de tensorflow lite y el escalador
def initTF():
    global interpreter, input_details, output_details, means, stds
    print("Iniciando reconocedor...")
    interpreter = tflite.Interpreter(model_path="rnaMenu_model-400relu-300relu.tflite")
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    print("Iniciando escalador...")
    [means, stds] = np.load('ScalerX.npy')
    print("Iniciacion completada.")

#Recibe un vector con menus y devuelve la prediccion
def predecir(X):
    global interpreter, input_details
    X_new = scale_data(X)
    input_data = np.array(X_new, dtype=np.float32)
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]['index'])
    return output_data

#Recibe el vector de selecciones del usuario y el vector predicho y genera un vector resultante
#mas o menos sensato. Para empezar, respeta todo lo seleccionado por el usuario
def postProcesado(X_orig,X_pred):
    X_res = X_orig
    for i in range(0,14):
        if (X_res[i]==0) and (X_pred[i]>=0):
            X_res[i]=int(round(X_pred[i]))
    return X_res

#Devuelve una respuesta con la lista de platos
@app.route('/platos', methods=['GET']) 
def platos(): 
    FILENAME = 'platos.csv'
    print('Llamada a platos.\n')
    #Cargo los platos en un dataset de numpy
    datafile = open(FILENAME,'r')
    myreader = csv.reader(datafile)
    dataset = [row for row in myreader]
    #Lo convierto a formato JSON
    dataset=np.array(dataset)
    json_str = json.dumps(dataset.tolist())
    res=json_str
    return res
#Devuelve una respuesta con la prediccion
@app.route('/prediccion', methods=['GET'])
def prediccion():
    print('Llamada a prediccion')
    v = json.loads(request.args.get('v'))
    X=[v.copy()]
    X_pred=predecir(X)
    dataset=[postProcesado(X[0],X_pred[0]),v]
    dataset=np.array(dataset)
    res=json.dumps(dataset.tolist())
    return res

#Inicializo el interprete de tensorflow y el escalador
initTF()

#Arranco el servidor
app.run(debug=True, port=5001) 

