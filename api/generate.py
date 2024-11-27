from flask import Flask, request, jsonify, send_file
import tempfile
from draw import draw_structure

app = Flask(__name__)

@app.route('/api/generate', methods=['POST'])
def handle():
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
        with tempfile.NamedTemporaryFile(suffix='.dxf', delete=False, dir='/tmp') as tmp_file:
            output_path = tmp_file.name
            
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
            
            return send_file(
                output_path,
                as_attachment=True,
                download_name='estructura_generada.dxf',
                mimetype='application/dxf'
            )
    except Exception as e:
        print(f"Error en generate: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Para desarrollo local
if __name__ == '__main__':
    app.run() 