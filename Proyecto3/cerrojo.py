from flask import Flask, jsonify, request, make_response
import numpy as np
from scipy.stats import multivariate_normal

app = Flask(__name__) 

#Metemos estos campos para que no de error de AllowAccessControl por venir la peticion desde localhost
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

rv=0 #Distribucion gaussiana
rvmax=0 #Probabilidad de la media
password='' #Password
tol=5 #Tolerancia en % de precision al introducir la clave

@app.route('/train', methods=['POST']) 
def train(): 
    global rv, rvmax, password
    tt=np.array([])
    c23=np.array([])
    print('Llamada a Train.\n')
    print(request.form)
    password=request.form['pass']
    N=request.form['N']
    print('N=',N)
    for i in range(0,int(N)):
        tt=np.append(tt,int(request.form['t'+str(i)]))
        c23=np.append(c23,int(request.form['c'+str(i)]))
    print("Totales: ",tt)
    print("C23s: ",c23)

    #Vector de medias y matriz de covarianzas
    media=np.array([tt.mean(),c23.mean()])
    aux=np.array([tt,c23]);
    covar=np.cov(aux)
    #Y ahora calculemos la probabilidad de los valores de entrenamiento suponiendo distribucion gaussiana
    print("Media calculada: ",media)
    print("Covarianza calculada: ",covar)
    rv =multivariate_normal(media, covar, allow_singular=True)
    rvmax=rv.pdf(media)
    res='Entrenamiento finalizado:<br><table border CELLPADDING=10 CELLSPACING=0><tr><th>Muestra</th><th>Tiempo total</th><th>Cadencia 2-3</th><th>Probabilidad con Gaussiana</th></tr>';
    res+='<tr><td>Prototipo</td><td>'+str(media[0])+'</td><td>'+str(media[1])+'</td><td>'+str((rv.pdf(media)/rv.pdf(media))*100)+'%</td></tr>';
    for i in range(0,int(N)):
        aux1=rv.pdf(np.array([int(request.form['t'+str(i)]),int(request.form['c'+str(i)])]))
        aux2=(aux1/rvmax)*100
        res+='<tr><td>Muestra '+str(i)+'</td><td>'+request.form['t'+str(i)]+'</td><td>'+request.form['c'+str(i)]+'</td><td>'+str(aux2)+'%</td></tr>'
    res+='</table>'
    print('\n\n',res,'\n\n')
    return res
@app.route('/test', methods=['POST'])
def test():
    global rv, rvmax, password, tol
    print('Llamada a Test.\n')
    print(request.form)
    p=request.form['pass']
    tt=int(request.form['t0'])
    c23=int(request.form['c0'])
    print("Total: ",str(tt))
    print("C23: ",str(c23))
    aux1=rv.pdf(np.array([tt,c23]))
    prob=(aux1/rvmax)*100
    print("Probabilidad: ",str(prob))
    #He de comparar la clave, luego ver tt y c23, y en funcion de eso dar respuesta de clave correcta o incorrecta
    if(p!=password):
        res='NOK'
    else:
        if(prob<tol):
            res='NOK'
        else:
            res='OK'
    print('Resultado: '+res)
    return res

app.run(debug=True) 

