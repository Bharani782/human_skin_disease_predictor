

import cv2
import numpy as np
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
import tensorflow as tf 
import pickle # Assuming TensorFlow/Keras

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

# Ensure the upload directory exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

model = pickle.load(open('finalized_model.pkl','rb'))

def decode_prediction(prediction):
    mapping={0:"Actinic keratosis",1:"Atopic Dermatitis",2:"Benign keratosis",3:"Dermatofibroma",4:"Melanocytic nevus",5:"Melanoma",6:"Squamous cell carcinoma",7:" Tinea Ringworm Candidiasis",8:"Vascular lesion "}
    return mapping[np.argmax(prediction)]
def your_preprocessing_function(image_path, target_size=(224, 224)):
    image = cv2.imread(image_path)
    image = cv2.resize(image, target_size)
    image = image.astype(np.float32) / 255.0
    image = np.expand_dims(image, axis=0)  # Add batch dimension
    return image

@app.route('/')
def indexes():
    return render_template('indexes.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        print("No file part")
        return redirect(request.url)

    file = request.files['file']
    
    if file.filename == '':
        print("No selected file")
        return redirect(request.url)

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Make a prediction using the loaded model
        try:
            image = your_preprocessing_function(file_path)
            prediction = model.predict(image)
            prediction = decode_prediction(prediction)

            print(f"Prediction: {prediction}")

            return render_template('indexes.html', prediction=prediction)
        except Exception as e:
            print(e)
            print(f"Error making prediction: {e}")

    return redirect(url_for('indexes'))

if __name__ == '__main__':
    app.run(debug=True)
