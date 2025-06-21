from flask import Flask, request, jsonify, send_from_directory
import process
import base64

app = Flask(__name__, static_folder='.')

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

@app.route('/process/<type>', methods=['POST'])
def process_image_endpoint(type):
    if 'image' not in request.files:
        return 'No image file in request', 400
    
    file = request.files['image']
    image_bytes = file.read()

    result_b64 = None
    if type == 'portfolio':
        result_b64 = process.process_portfolio_image(image_bytes)
    elif type == 'order_o':
        result_b64 = process.order_o(image_bytes)
    elif type == 'order_c':
        result_b64 = process.order_c(image_bytes)
    elif type == 'order_op':
        result_b64 = process.order_op(image_bytes)
    elif type == 'order_oc':
        result_b64 = process.order_oc(image_bytes)
    elif type == 'order':
        result_b64 = process.process_order_image(image_bytes)
    else:
        return 'Invalid processing type', 400

    return jsonify({'image': result_b64})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)