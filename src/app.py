from flask import Flask, render_template, Response
from picamera2 import Picamera2
from io import BytesIO
from PIL import Image

app = Flask(__name__)

# Initialize the camera
picam2 = Picamera2()
# Configure the camera to stream in a suitable format
picam2.configure(picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)}))
picam2.start()

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')

def gen():
    """Video streaming generator function using picamera2."""
    while True:
        # Capture an image from the camera
        frame = picam2.capture_array()

        # Convert the frame to JPEG using PIL
        image = Image.fromarray(frame)
        buffer = BytesIO()
        image.save(buffer, 'JPEG')
        frame = buffer.getvalue()

        # Yield the frame as part of an HTTP multipart response
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    """Video streaming route."""
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True, threaded=True)
