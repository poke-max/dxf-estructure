from flask import Flask, request, jsonify, send_file
import ezdxf
import io
import traceback
import sys
from draw import draw_structure

app = Flask(__name__)

# Variables globales
cotas_vertical = []
cotas_horizontal = []

def find_dimensions(drawing):
    try:
        global cotas_vertical, cotas_horizontal
        cotas_vertical = []
        cotas_horizontal = []
        
        # Iterar sobre todas las entidades del modelspace
        msp = drawing.modelspace()
        for entity in msp:
            # Verificar si es una dimensión
            if entity.dxftype() == 'DIMENSION':
                # Obtener puntos de la dimensión
                defpoint = entity.dxf.defpoint
                text_midpoint = entity.dxf.text_midpoint
                
                # Calcular la diferencia en X e Y
                dx = abs(text_midpoint[0] - defpoint[0])
                dy = abs(text_midpoint[1] - defpoint[1])
                
                # Si la diferencia en Y es mayor, es una cota vertical
                if dy > dx:
                    cotas_vertical.append(entity.dxf.actual_measurement)
                else:
                    cotas_horizontal.append(entity.dxf.actual_measurement)
        
        # Ordenar las listas
        cotas_vertical.sort()
        cotas_horizontal.sort()
        
        return {
            'cotas_vertical': cotas_vertical,
            'cotas_horizontal': cotas_horizontal
        }
    except Exception as e:
        print(f"Error en find_dimensions: {str(e)}\n{traceback.format_exc()}", file=sys.stderr)
        raise

@app.route('/api/upload', methods=['POST'])
def upload_file():
    try:
        print("Iniciando upload_file", file=sys.stderr)
        
        if 'file' not in request.files:
            print("No file in request", file=sys.stderr)
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            print("Empty filename", file=sys.stderr)
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.dxf'):
            print("Invalid file type", file=sys.stderr)
            return jsonify({'error': 'Invalid file type'}), 400

        print(f"Procesando archivo: {file.filename}", file=sys.stderr)
        
        # Usar BytesIO en lugar de archivos temporales
        file_content = file.read()
        file_stream = io.BytesIO(file_content)
        
        # Leer el archivo DXF desde memoria
        print("Leyendo archivo DXF", file=sys.stderr)
        drawing = ezdxf.readfile(file_stream)
        
        # Encontrar las dimensiones
        print("Buscando dimensiones", file=sys.stderr)
        dimensions = find_dimensions(drawing)
        
        print(f"Dimensiones encontradas: {dimensions}", file=sys.stderr)
        return jsonify(dimensions)
        
    except Exception as e:
        error_msg = f"Error processing DXF: {str(e)}\n{traceback.format_exc()}"
        print(error_msg, file=sys.stderr)
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate', methods=['POST'])
def generate():
    try:
        print("Iniciando generate", file=sys.stderr)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        required_fields = ['cotas_horizontal', 'cotas_vertical', 'alturaCanaleta', 
                         'pendienteTecho', 'anchoCanaleta', 'separacionVigas', 
                         'longitudApoyo', 'alturaMontante', 'tipoChapa', 'tipoDiagonal']
        
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400

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

        print("Parámetros extraídos correctamente", file=sys.stderr)

        # Usar BytesIO para el archivo de salida
        output_stream = io.BytesIO()
            
        # Llamar a draw_structure con el stream en memoria
        print("Llamando a draw_structure", file=sys.stderr)
        draw_structure(
            cotas_horizontal=cotas_horizontal,
            cotas_vertical=cotas_vertical,
            output_path=output_stream,
            ht=ht,
            pend=pend,
            ac=ac,
            sep=sep,
            long_apoyo=long_apoyo,
            h=h,
            t_chapa=t_chapa,
            t_diag=t_diag
        )
        
        print("Estructura dibujada correctamente", file=sys.stderr)
        
        # Preparar el stream para lectura
        output_stream.seek(0)
            
        # Enviar el archivo generado
        return send_file(
            output_stream,
            as_attachment=True,
            download_name='estructura_generada.dxf',
            mimetype='application/dxf'
        )
    except Exception as e:
        error_msg = f"Error en generate: {str(e)}\n{traceback.format_exc()}"
        print(error_msg, file=sys.stderr)
        return jsonify({'error': str(e)}), 500

# Manejador de errores global
@app.errorhandler(Exception)
def handle_exception(e):
    error_msg = f"Error no manejado: {str(e)}\n{traceback.format_exc()}"
    print(error_msg, file=sys.stderr)
    return jsonify({'error': str(e)}), 500