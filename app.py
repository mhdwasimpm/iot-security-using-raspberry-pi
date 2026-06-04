from flask import Flask, Response, render_template_string, request, redirect, url_for
from picamera2 import Picamera2
import cv2

# Initialize Flask app
app = Flask(__name__)

# Camera configuration
camera = Picamera2()
camera.configure(camera.create_video_configuration(main={"size": (640, 480)}))
camera.start()

# Authentication credentials
USERNAME = "admin"
PASSWORD = "raspi"

# HTML template for login page
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>IoT Camera Login</title>
    <style>
        body {
            background: #1e1e2f;
            color: white;
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .login-box {
            background: #2d2d44;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 15px #000;
            width: 300px;
            text-align: center;
        }
        input[type="text"], input[type="password"] {
            width: 90%;
            padding: 10px;
            margin: 12px 0;
            border: none;
            border-radius: 5px;
        }
        input[type="submit"] {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin-top: 10px;
        }
        input[type="submit"]:hover {
            background: #45a049;
        }
        .error {
            color: red;
            margin-top: 10px;
            font-size: 0.9em;
        }
    </style>
    <script>
        document.addEventListener("DOMContentLoaded", function() {
            const inputs = document.querySelectorAll("input");
            inputs.forEach((input, index) => {
                input.addEventListener("keypress", function(e) {
                    if (e.key === "Enter") {
                        e.preventDefault();
                        if (index < inputs.length - 1) {
                            inputs[index + 1].focus();
                        } else {
                            document.getElementById("loginForm").submit();
                        }
                    }
                });
            });
        });
    </script>
</head>
<body>
    <div class="login-box">
        <h2>IoT Camera Login</h2>
        <form method="POST" id="loginForm">
            <input type="text" name="username" placeholder="Username" autofocus required><br>
            <input type="password" name="password" placeholder="Password" required><br>
            <input type="submit" value="Login">
        </form>
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
    </div>
</body>
</html>
"""

def generate_frames():
    """Video streaming generator function"""
    while True:
        frame = camera.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        _, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/', methods=['GET', 'POST'])
def login():
    """Login page handler"""
    error = None
    if request.method == 'POST':
        if request.form['username'] == USERNAME and request.form['password'] == PASSWORD:
            return redirect(url_for('video_feed'))
        else:
            error = "Invalid username or password"
    return render_template_string(LOGIN_TEMPLATE, error=error)

@app.route('/video')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
