import numpy as np
import tensorflow as tf

def scale_data(array, means, stds):
    return (array-means)/stds

# Load TFLite model and allocate tensors.
interpreter = tf.lite.Interpreter(model_path="rnaMenu_model-400relu-300relu.tflite")
interpreter.allocate_tensors()

# Get input and output tensors.
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Test model on random input data.
X_new=[[1,2,3,0,0,0,7,8,9,10,11,12,13,0]]
[means, stds] = np.load('ScalerX.npy')
X_new = scale_data(X_new,means,stds)
input_data = np.array(X_new, dtype=np.float32)
interpreter.set_tensor(input_details[0]['index'], input_data)

interpreter.invoke()

# The function `get_tensor()` returns a copy of the tensor data.
# Use `tensor()` in order to get a pointer to the tensor.
output_data = interpreter.get_tensor(output_details[0]['index'])
print(output_data)
