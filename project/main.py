from flask import Flask, request, jsonify
import math
import functools  # Import functools for wrapping functions

app = Flask(__name__)

# In-memory store for API keys (replace with a more secure solution for production)
API_KEYS = {'mysecretkey': True, 'anotherkey': True}

# Authentication decorator
def authenticate(f):
    @functools.wraps(f)  # Preserve original function's metadata
    def wrapper(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key and API_KEYS.get(api_key):
            return f(*args, **kwargs)  # Call the original function if authenticated
        else:
            return jsonify({'error': 'Unauthorized'}), 401
    return wrapper


@app.route('/')
@authenticate  # Apply authentication to the home route
def home():
    # Updated the response message to be more informative and user-friendly
    # Updated the response to be "something cool"
    return 'Behold! This is the home page. Flask is pretty awesome!'

# New endpoint to calculate the area of a circle
@app.route('/area', methods=['POST'])
@authenticate  # Apply authentication to the area calculation route
def calculate_area():
    """
    Calculates the area of a circle based on the radius provided in the request.
    The radius should be a numerical value passed as a JSON payload.
    Returns the calculated area as a JSON response. Handles potential errors, 
    such as missing radius or invalid radius values.
    """
    try:
        # Attempt to get the radius from the JSON request body
        data = request.get_json()
        radius = float(data.get('radius'))

        # Validate the radius value
        if radius <= 0:
            return jsonify({'error': 'Radius must be a positive number'}), 400

        # Calculate the area of the circle
        area = math.pi * (radius ** 2)
        
        # Return the result as a JSON response
        return jsonify({'area': area})

    except (TypeError, ValueError):
        # Handle cases where the radius is missing or not a valid number
        return jsonify({'error': 'Invalid request. Please provide a valid radius in the request body.'}), 400
    except Exception as e:
        # Handle any other unexpected errors
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)