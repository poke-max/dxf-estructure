from flask import Flask, request, jsonify, send_file
import ezdxf
import io

app = Flask(__name__, 
            static_folder='../static')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.dxf'):
            return jsonify({'error': 'Invalid file type'}), 400

        # Usar BytesIO en lugar de archivos temporales
        file_content = file.read()
        file_stream = io.BytesIO(file_content)
        
        # Leer el archivo DXF desde memoria
        drawing = ezdxf.readfile(file_stream)
        
        # Encontrar las dimensiones
        dimensions = find_dimensions(drawing)
        
        return jsonify(dimensions)
    except Exception as e:
        print(f"Error en upload_file: {str(e)}\nTraceback: {traceback.format_exc()}", file=sys.stderr)
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate', methods=['POST'])
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

        # Usar BytesIO para el archivo de salida
        output_stream = io.BytesIO()
            
        # Llamar a draw_structure con el stream en memoria
        draw_structure(
            cotas_horizontal=cotas_horizontal,
            cotas_vertical=cotas_vertical,
            output_path=output_stream,  # Pasar el stream en lugar de path
            ht=ht,
            pend=pend,
            ac=ac,
            sep=sep,
            long_apoyo=long_apoyo,
            h=h,
            t_chapa=t_chapa,
            t_diag=t_diag
        )
        
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
        print(f"Error en generate: {str(e)}")
        return jsonify({'error': str(e)}), 500 