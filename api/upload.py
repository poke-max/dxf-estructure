from flask import Flask, request, jsonify
import ezdxf
import os
from http.server import BaseHTTPRequestHandler
from datetime import datetime

app = Flask(__name__)

def find_dimensions(drawing):
    cotas_vertical = []
    cotas_horizontal = []

    for entity in drawing.entities:
        if entity.dxftype() == 'DIMENSION':
            actual_measurement = entity.dxf.actual_measurement
            text_midpoint_y = entity.dxf.text_midpoint[1]

            if entity.dxf.angle == 90:
                cotas_vertical.append((actual_measurement, text_midpoint_y))
            else:
                cotas_horizontal.append((actual_measurement, text_midpoint_y))

    cotas_vertical.sort(key=lambda x: x[1])
    cotas_horizontal.sort(key=lambda x: x[1])

    cotas_vertical = [cota[0] for cota in cotas_vertical]
    cotas_horizontal = [cota[0] for cota in cotas_horizontal]

    cotas_vertical.insert(0, 0)
    
    return cotas_vertical, cotas_horizontal

@app.route('/api/upload', methods=['POST'])
def handle():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.dxf'):
            return jsonify({'error': 'Invalid file type'}), 400

        # Usar /tmp para archivos temporales
        temp_path = os.path.join('/tmp', f"upload_{datetime.now().timestamp()}.dxf")
        file.save(temp_path)

        # Leer el archivo DXF
        drawing = ezdxf.readfile(temp_path)
        
        # Encontrar las dimensiones
        cotas_vertical, cotas_horizontal = find_dimensions(drawing)
        
        # Eliminar el archivo temporal
        os.remove(temp_path)
        
        return jsonify({
            'cotas_vertical': cotas_vertical,
            'cotas_horizontal': cotas_horizontal
        })

    except Exception as e:
        print(f"Error processing DXF: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Para desarrollo local
if __name__ == '__main__':
    app.run() 