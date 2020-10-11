import tensorflow as tf
model=tf.keras.models.load_model("./rnaMenu_model-400relu-300relu.h5")
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()
open("rnaMenu_model-400relu-300relu.tflite", "wb").write(tflite_model)
