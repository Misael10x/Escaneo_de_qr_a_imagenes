import os
from flask import Flask, request, jsonify, render_template
from pyzbar.pyzbar import decode
from PIL import Image
import cv2

app = Flask(__name__)

# Directorio donde se guardarán las imágenes
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
QR_IMAGES_DIR = os.path.join(BASE_DIR, "static", "qr_images")
os.makedirs(QR_IMAGES_DIR, exist_ok=True)  # Asegúrate de que la carpeta exista

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan_qr', methods=['POST'])
def scan_qr():
    # Verifica si el archivo está presente en la solicitud
    if 'image' not in request.files:
        return jsonify({"success": False, "message": "No file provided."})

    qr_image = request.files['image']

    # Verifica si el archivo tiene un nombre válido
    if qr_image.filename == '':
        return jsonify({"success": False, "message": "No file selected."})

    try:
        # Guardar imagen en el servidor
        image_path = os.path.join(QR_IMAGES_DIR, qr_image.filename)
        qr_image.save(image_path)

        # Verificar si la imagen es válida
        try:
            img = Image.open(image_path)
            img.verify()  # Verifica que sea una imagen válida
        except Exception as e:
            return jsonify({"success": False, "message": f"Invalid image: {e}"})

        # Procesar la imagen para detectar códigos QR
        decoded_objects = decode(cv2.imread(image_path))
        if not decoded_objects:
            return jsonify({"success": False, "message": "No QR code detected in the image."})

        # Extraer datos del código QR
        qr_data = [obj.data.decode('utf-8') for obj in decoded_objects]

        # Aquí puedes devolver el contenido AR basado en el QR
        return jsonify({"success": True, "data": qr_data[0]})

    except Exception as e:
        return jsonify({"success": False, "message": f"Error processing the image: {e}"})

if __name__ == '__main__':
    app.run(debug=True)
