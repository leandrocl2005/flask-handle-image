import os
import imghdr
from flask import Flask, render_template, request, redirect, url_for, abort
from werkzeug.utils import secure_filename
from flask import send_from_directory
import cv2


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


def convert2gray(filename):
    image_from_upload = cv2.imread(filename)
    gray_image = cv2.cvtColor(image_from_upload, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(filename.split('.')[0] + "_gray.jpg", gray_image)


@app.route('/')
def index():
    files = os.listdir(app.config['UPLOAD_PATH'])
    files_in_gray = filter(lambda x: 'gray' in x, files)
    return render_template('index.html', files=files_in_gray)


@app.route('/', methods=['POST'])
def upload_files():
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            abort(400)
        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        convert2gray("uploads/" + filename)
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
