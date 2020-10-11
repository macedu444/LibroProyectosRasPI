from flask import Flask, jsonify, request, make_response
import numpy as np
import csv
import json
import tflite_runtime.interpreter as tflite
import mysql.connector
from decimal import Decimal

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
    X_new=X.copy()
    X_new[0]=X[0].copy() #De este modo no alteramos el vector original
    for i in range(0,len(X_new[0])):
        if(X_new[0][i]<0):
            X_new[0][i]=0
    X_new = scale_data(X_new)
    input_data = np.array(X_new, dtype=np.float32)
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    # The function `get_tensor()` returns a copy of the tensor data.
    # Use `tensor()` in order to get a pointer to the tensor.
    output_data = interpreter.get_tensor(output_details[0]['index'])
    return output_data

#Recibe el vector de selecciones del usuario y el vector predicho y genera un vector resultante
#mas o menos sensato. Para empezar, respeta todo lo seleccionado por el usuario
#Elimina aquellos platos seleccionados para comida siendo cena y viceversa. (los sustituye por cero)
#(a este respecto recuerda que comenzamos por la comida del lunes, es decir, las posiciones pares son
#comidas y las impares cenas)
def postProcesado(X_orig,X_pred):
    X_res = X_orig
#    print('X_orig:')
#    print(X_orig)
#    print('X_pred:')
#    print(X_pred)
    platos=getPlatos()
    for i in range(0,14):
        #Lo primero es encontrar el plato con id int(round(X_pred[i]))
        id=int(round(X_pred[i]))
        if(id>0): #Ya que de lo contrario no habra indices en la tabla
            #Me quedo con la primera columna para buscar en ella la posicion del id
            ids=(np.array(platos)[:,0])
# 
            print('ids={}, id={}'.format(ids,id))


            aux=np.where(ids == str(id))
            critico=np.shape(aux)[1]
            print('aux={}, len(aux)={}, critico={}'.format(aux,np.shape(aux),np.shape(aux)[1]))


            if(critico>0):
                pos=aux[0][0]
#               print('pos={}'.format(pos))
                plato=platos[pos]
            else:
                plato=[0,'','A']
        else:
            plato=[0,'','A']
#        print('Plato {} con id predicho {} es'.format(i,id))
#        print(plato)
        if (X_res[i]==0) and (X_pred[i]>=0):
            if(((i%2 == 0) and (plato[2] == 'E')) or ((i%2 !=0) and (plato[2] == 'O'))):
#                print('plato censurado')
                X_res[i]=0
            else:
#                print('plato admitido con i=',i,', uso=',platos[id][2])
                X_res[i]=id
    return X_res

#Obtiene la lista de platos de la base de datos.
def getPlatos():
    con = mysql.connector.connect( host='localhost', user='root', passwd='raspberry', db='menu' )
    cur = con.cursor()
    cur.execute( "SELECT * FROM Platos ORDER BY Descripcion" )
    dataset = cur.fetchall()
    con.close()
    return dataset

#Obtiene la lista de ingredientes de la base de datos
def getIngredientes(v):
    con = mysql.connector.connect( host='localhost', user='root', passwd='raspberry', db='menu' )
    cur = con.cursor()
    orden= 'SELECT Ingredientes.Descripcion, SUM(PlatosIngredientes.Cantidad) AS Cantidad FROM Ingredientes INNER JOIN PlatosIngredientes ON Ingredientes.ID=PlatosIngredientes.IDIngrediente WHERE PlatosIngredientes.IDPlato IN (';
    for p in v:
        if(p>0):
            orden = orden + '\'' + str(p) + '\','
    #Elimino la ultima coma
    orden=orden[:-1]
    orden = orden + ') GROUP BY Ingredientes.Descripcion ORDER BY Ingredientes.Seccion'
    cur.execute( orden )
    dataset = cur.fetchall()
    res=[]
    for row in dataset:
        for col in row:
            if type(col) is Decimal:
                res.append(int(col))
            else:
                res.append(col)
    con.close()
    return res

#Devuelve una respuesta con la lista de platos
@app.route('/platos', methods=['GET']) 
def platos(): 
    print('Llamada a platos.\n')
    #Cargo los datos desde la base de datos, pero me quedo solo con las dos primeras columnas, puesto que
    #el uso de cada plato (si es para comida o cena) es indiferente al usuario.
    dataset = np.array(getPlatos())[:,:2]
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

#Devuelve las listas de platos e ingredientes
@app.route('/all', methods=['GET'])
def all():
    v = json.loads(request.args.get('v'))
    dataset=[v,getIngredientes(v)]
    dataset=np.array(dataset)
    res=json.dumps(dataset.tolist())
    return res

#Inicializo el interprete de tensorflow y el escalador
initTF()

#Arranco el servidor
app.run(debug=True, port=5001) 

