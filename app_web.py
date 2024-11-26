from flask import Flask, render_template, request, jsonify, send_file
import ezdxf
import os
from datetime import datetime
import tempfile
from draw import draw_structure

app = Flask(__name__)

# Variables globales
cotas_vertical = []
cotas_horizontal = []

def find_dimensions(drawing):
    global cotas_vertical  # Declarar cotas_vertical como global
    global cotas_horizontal  # Declarar cotas_horizontal como global
    cotas_vertical = []
    cotas_horizontal = []

    for entity in drawing.entities:
        if entity.dxftype() == 'DIMENSION':
            actual_measurement = entity.dxf.actual_measurement
            text_midpoint_y = entity.dxf.text_midpoint[1]

            # Si el ángulo es 90 grados, se considera como cota vertical
            if entity.dxf.angle == 90:
                cotas_vertical.append((actual_measurement, text_midpoint_y))
            else:
                cotas_horizontal.append((actual_measurement, text_midpoint_y))

    # Ordenar cotas verticales de abajo hacia arriba
    cotas_vertical.sort(key=lambda x: x[1])

    # Ordenar cotas horizontales de izquierda a derecha
    cotas_horizontal.sort(key=lambda x: x[1])

    # Extraer solo los valores de las cotas ordenadas
    cotas_vertical = [cota[0] for cota in cotas_vertical]
    cotas_horizontal = [cota[0] for cota in cotas_horizontal]

    cotas_vertical.insert(0, 0)
    
@app.route('/')
def home():
    return send_file('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.endswith('.dxf'):
        return jsonify({'error': 'Invalid file type'}), 400

    try:
        # Guardar el archivo temporalmente
        temp_path = os.path.join('temp', file.filename)
        os.makedirs('temp', exist_ok=True)
        file.save(temp_path)

        # Leer el archivo DXF
        drawing = ezdxf.readfile(temp_path)
        
        # Encontrar las dimensiones
        find_dimensions(drawing)
        
        # Eliminar el archivo temporal
        os.remove(temp_path)
        
        return jsonify({
            'cotas_vertical': cotas_vertical,
            'cotas_horizontal': cotas_horizontal
        })
    except Exception as e:
        print(f"Error processing DXF: {str(e)}")  # Para debugging
        return jsonify({'error': str(e)}), 500

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        
        # Extraer los parámetros del JSON
        cotas_horizontal = data['cotas_horizontal']
        cotas_vertical = data['cotas_vertical']
        ht = float(data['alturaCanaleta'])
        pend = float(data['pendienteTecho'])
        ac = float(data['anchoCanaleta'])
        sep = float(data['separacionVigas'])
        long_apoyo = float(data['longitudApoyo'])
        h = float(data['alturaMontante'])
        t_chapa = data['tipoChapa']
        t_diag = data['tipoDiagonal']

        # Crear un archivo temporal para el output
        with tempfile.NamedTemporaryFile(suffix='.dxf', delete=False) as tmp_file:
            output_path = tmp_file.name
            
            # Llamar a draw_structure en lugar de generate_structure
            draw_structure(
                cotas_horizontal=cotas_horizontal,
                cotas_vertical=cotas_vertical,
                output_path=output_path,
                ht=ht,
                pend=pend,
                ac=ac,
                sep=sep,
                long_apoyo=long_apoyo,
                h=h,
                t_chapa=t_chapa,
                t_diag=t_diag
            )
            
            # Enviar el archivo generado
            return send_file(
                output_path,
                as_attachment=True,
                download_name='estructura_generada.dxf',
                mimetype='application/dxf'
            )
    except Exception as e:
        print(f"Error en generate: {str(e)}")  # Para debugging
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    os.makedirs('temp', exist_ok=True)
    app.run(debug=True)