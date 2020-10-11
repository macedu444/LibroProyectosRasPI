import numpy as np
from tensorflow import keras
from sklearn.model_selection import train_test_split
import os
from numpy import save, load
from sklearn.preprocessing import StandardScaler

root_logdir = os.path.join(os.curdir, "rna_logs")
FILENAME = 'menus.csv'
etapa = '-400relu-300relu'


def get_run_logdir():
    import time
    run_id = time.strftime("run_%Y_%m_%d-%H_%M_%S"+etapa)
    return os.path.join(root_logdir, run_id)

def inttobin(v,nb):
    res = np.zeros(nb)
    for i in range(nb):
        res[i]=int(v%2)
        v=int(v/2)
    return np.flip(res)

def loadData(maxceros):
    contX=0
    contY=0
    dataset = np.loadtxt(FILENAME, delimiter=',')
    print(dataset)
    print("Menus cargados (",len(dataset),"):")
    print("Iniciando generación de datos para red neuronal...")
    n = (2 ** 14) - 1  # 14 unos en binario
    for f in range(0,len(dataset)):
        print("Creando datos a partir de menu ",f)
        v = dataset[f]
        r=np.array([v*inttobin(n,14)])
        for i in range(1,n):
            aux=inttobin(i,14)
            if ((14-np.count_nonzero(aux))<maxceros):
                r=np.append(r,[v*aux],axis=0)
        if f==0:
            X=r
            Y=np.tile(dataset[f],(len(r),1))
        else:
            X=np.append(X,r,axis=0)
            Y = np.append(Y,np.tile(dataset[f],(len(r),1)),axis=0)
        print("Agregadas ",len(X)-contX," filas en X (total ",len(X),") y ",len(Y)-contY," en Y (total ",len(Y),")")
        contX = len(X)
        contY = len(Y)
    return X,Y

def optimizeAndSplitData(X,Y,percent):
    total=np.append(X,Y,axis=1)
    train, val = train_test_split(total, test_size=(percent/100), random_state=42)
    X_train=train[:,:14]
    Y_train=train[:,14:]
    X_val=val[:,:14]
    Y_val=val[:,14:]
    return X_train, Y_train, X_val, Y_val

X,Y = loadData(7)
X_train, Y_train, X_val, Y_val = optimizeAndSplitData(X,Y,30)

print("Datos cargados.")
print("Escalando datos")
scalerX=StandardScaler()
X_train = scalerX.fit_transform(X_train)
X_val = scalerX.transform(X_val)
print("Datos escalados")
np.save('ScalerX.npy',[scalerX.mean_, scalerX.var_ ** 0.5])

model=keras.models.Sequential()
model.add(keras.layers.Dense(400, activation="relu" , input_shape=[14]))
model.add(keras.layers.Dense(300, activation="relu"))
model.add(keras.layers.Dense(14, activation="relu"))

model.compile(loss="mean_squared_error", optimizer="sgd", metrics=["accuracy"])

run_logdir = get_run_logdir()
tensorboard_cb = keras.callbacks.TensorBoard(run_logdir)
checkpoint_cb = keras.callbacks.ModelCheckpoint("rnaMenu_model"+etapa+".h5", save_best_only=True)
model.fit(X_train,Y_train,epochs=200,validation_data=(X_val,Y_val),callbacks=[checkpoint_cb,tensorboard_cb])

model=keras.models.load_model("rnaMenu_model"+etapa+".h5")

X_new=[[1,2,3,0,0,0,7,8,9,10,11,12,13,0]]
X_new = scalerX.transform(X_new)
Y_new = model.predict(X_new)
print('Con X_new=',X_new,'\nLa predicción es: ',Y_new)
X_new=[[1,15,0,17,0,19,7,0,20,12,0,3,22,23]]
X_new = scalerX.transform(X_new)
Y_new = model.predict(X_new)
print('Con X_new=',X_new,'\nLa predicción es: ',Y_new)
