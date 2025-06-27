from flask import Flask, request, render_template, send_file
import numpy as np
import cv2
from io import BytesIO

app = Flask(__name__)

# In-memory image storage (for this example only)
last_original_bytes = None
last_inverted_bytes = None

@app.route('/', methods=['GET', 'POST'])
def index():
    global last_original_bytes, last_inverted_bytes

    original_url = None
    inverted_url = None

    if request.method == 'POST':
        file = request.files.get('image')
        if file and file.filename:
            # Read raw image data from memory
            file_bytes = np.frombuffer(file.read(), np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            if img is None:
                return "Unsupported image format", 400

            # Store original image as PNG in memory
            _, buf1 = cv2.imencode('.png', img)
            last_original_bytes = BytesIO(buf1.tobytes())

            # Invert image
            inverted = cv2.bitwise_not(img)
            _, buf2 = cv2.imencode('.png', inverted)
            last_inverted_bytes = BytesIO(buf2.tobytes())

            original_url = "/view/original"
            inverted_url = "/view/inverted"

    return render_template('index.html', original=original_url, inverted=inverted_url)

@app.route('/view/<imgtype>')
def serve_image(imgtype):
    if imgtype == 'original' and last_original_bytes:
        last_original_bytes.seek(0)
        return send_file(last_original_bytes, mimetype='image/png')
    elif imgtype == 'inverted' and last_inverted_bytes:
        last_inverted_bytes.seek(0)
        return send_file(last_inverted_bytes, mimetype='image/png')
    else:
        return "Image not available", 404

if __name__ == '__main__':
    app.run(debug=True)
