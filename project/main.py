from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    # Updated the response message to be more informative and user-friendly
    # Updated the response to be "something cool"
    return 'Behold! This is the home page. Flask is pretty awesome!'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)