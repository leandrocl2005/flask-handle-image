import os
import imghdr
from flask import Flask, render_template, request, redirect, url_for, abort
from werkzeug.utils import secure_filename
from flask import send_from_directory
import cv2

from PIL import Image
from io import BytesIO
import numpy as np
import base64

import time


app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
app.config['UPLOAD_PATH'] = 'uploads'


def validate_image(stream):
    header = stream.read(512)  # 512 bytes should be enough for a header check
    stream.seek(0)  # reset stream pointer
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')


@app.route('/uploads/<filename>')
def upload(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)


def convert2gray_from_filename(filename):
    image_from_upload = cv2.imread(filename)
    gray_image = cv2.cvtColor(image_from_upload, cv2.COLOR_BGR2GRAY)
    return gray_image

def convert2gray_from_image(image):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    time.sleep(5)
    return gray_image

def create_uri_image_from_numpy_image(image):
    img = Image.fromarray(image.astype("uint8"))
    rawBytes = BytesIO()
    img.save(rawBytes, "JPEG")
    rawBytes.seek(0)
    img_base64 = base64.b64encode(rawBytes.getvalue()).decode('ascii')
    mime = "image/jpeg"
    uri = "data:%s;base64,%s"%(mime, img_base64)
    return uri


@app.route('/')
def index():
    files = os.listdir(app.config['UPLOAD_PATH'])
    files_in_gray = filter(lambda x: 'gray' in x, files)
    return render_template('index.html', files=files_in_gray)


@app.route('/', methods=['POST'])
def upload_files():
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)

    byte_image = uploaded_file.stream.read()
    numpy_image = np.array(Image.open(BytesIO(byte_image)))

    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            abort(400)
        # uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        
        gray_image = convert2gray_from_image(numpy_image)
        uri_image = create_uri_image_from_numpy_image(gray_image)

        return render_template('index.html', image=uri_image)      
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
