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
    
def verify_program_validity():
    expiration_date = datetime(2024, 11, 30)
    # ... (lógica simplificada de verificación) ...
    return (expiration_date - datetime.now()).days

@app.route('/')
def home():
    days_remaining = verify_program_validity()
    return render_template('index.html', days_remaining=days_remaining)

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
@app.route('/generate', methods=['POST'])
def generate_structure(cotas_horizontal, cotas_vertical, output_path=None, ht=2.60, pend=0.15, ac=0.35, sep=0.05, long_apoyo=0, h=0.6, t_chapa="Termoacústica", t_diag="Intercalado"):
    D = cotas_horizontal[0]
    Le = sum(cotas_vertical)
    
    H = D*pend/2
    
    alpha = math.atan(2 * H / D)
    
    sen_alpha = math.sin(alpha)
    cos_alpha = math.cos(alpha)
    
    L = D/(2*cos_alpha)
    lm = h*cos_alpha
    
    if t_chapa == "Termoacústica":
        dc = 1.5
    if t_chapa == "Trapezoidal":
        dc = 1.2
    if t_chapa == "Zipada":
        dc = 1.1
        
    divcorr = math.ceil(dc/(h*math.tan(math.radians(60))))
    
    if ac != 0:
        di = (ac+lm*sen_alpha)/cos_alpha
        div = int(math.ceil((L-di-sep)/dc))
        dc = (L-di-sep)/div
    else:
        div = int(math.ceil((L-sep)/dc))
        dc = (L-sep)/div
        di = d
        
    divcorr = math.ceil(dc/(h*math.tan(math.radians(60)))) 
    d = dc/divcorr
    
    div = divcorr*div
    
    if di == d:
        cant_corr = int(round((L-sep)/dc,0)) #Cantidad de correas por caída
    else:
        cant_corr = int(round((L-di-sep)/dc,0)) #Cantidad de correas por caída
        
    if ac != 0:
        div = div
    else:
        div = div-1
        
    # Crear un nuevo DXF documento en formato R2010
    doc = ezdxf.new("R2010")
    
    # Obtener el modelspace del documento
    msp = doc.modelspace()
    
    # Crear un nuevo layer
    layer = doc.layers.new(name="Cordones")
    layer.rgb = (255, 0, 0)  
    layer = doc.layers.new(name="Montantes")
    layer.rgb = (255, 255, 0)  
    layer = doc.layers.new(name="Diagonales")
    layer.rgb = (0, 255, 0)  
    layer = doc.layers.new(name="Correas")
    layer.rgb = (0, 0, 255)  
    layer = doc.layers.new(name="Apoyos")
    layer.rgb = (255, 0, 255)  
    
    Cordones = []
    montantes = []
    diagonales = []
    Correas = []
    Apoyos = []
    Nudos = []
        
    for m in range (len(cotas_vertical)):
        # Puntos de origen
        Ox = 0  
        Oy = sum(cotas_vertical[0:m+1])
        Oz = long_apoyo+ht
        if cotas_vertical[m] !=cotas_vertical[-1]:
            Sep_port = cotas_vertical[m+1]
        
        cordones = [[(Ox, Oy, Oz), (Ox+D/2, Oy, Oz+D*pend/2)],[(Ox, Oy, Oz+h), (Ox+D/2, Oy, Oz+D*pend/2+h)] ,  
                    [(Ox+D/2, Oy, Oz+D*pend/2), (Ox+D, Oy, Oz)],[(Ox+D/2, Oy, Oz+D*pend/2+h), (Ox+D, Oy, Oz+h)] , 
                    [(Ox, Oy, Oz), (Ox, Oy, Oz+h)],[(Ox+D, Oy, Oz), (Ox+D, Oy, Oz+h)], 
                    [(Ox+(L-sep)*cos_alpha, Oy, Oz+(L-sep)*sen_alpha), (Ox+(L-sep)*cos_alpha, Oy, Oz+(L-sep)*sen_alpha+h)], 
                    [(Ox+(L-sep)*cos_alpha+2*sep*cos_alpha, Oy, Oz+(L-sep)*sen_alpha), (Ox+(L-sep)*cos_alpha+2*sep*cos_alpha, Oy, Oz+(L-sep)*sen_alpha+h)]] 
        
        for cordon in cordones:
            Cordones.append(cordon)
        
        cm = 0    
        for i in range (div):
            montantes.append([(Ox+(di+lm*sen_alpha)*cos_alpha+d*cos_alpha*cm, Oy, Oz+(di+lm*sen_alpha)*sen_alpha+d*sen_alpha*cm), (Ox+(di+lm*sen_alpha)*cos_alpha-lm*sen_alpha+d*cos_alpha*cm, Oy, Oz+(di+lm*sen_alpha)*sen_alpha+lm*cos_alpha+d*sen_alpha*cm)])
            montantes.append([(Ox+(D-(di+lm*sen_alpha)*cos_alpha-d*cos_alpha*cm), Oy, Oz+(di+lm*sen_alpha)*sen_alpha+d*sen_alpha*cm), (Ox+(D-(di+lm*sen_alpha)*cos_alpha+lm*sen_alpha-d*cos_alpha*cm), Oy, Oz+(di+lm*sen_alpha)*sen_alpha+lm*cos_alpha+d*sen_alpha*cm)])
            cm += 1
        
        if t_diag == "Intercalado":
            cm = 0
            for i in range (div):
                if cm != div-1:
                    if i % 2 != 0:
                        diagonales.append([(Ox+(di+lm*sen_alpha)*cos_alpha+d*cos_alpha*cm, Oy, Oz+(di+lm*sen_alpha)*sen_alpha+d*sen_alpha*cm), (Ox+(di+lm*sen_alpha)*cos_alpha-lm*sen_alpha+d*cos_alpha*(cm+1), Oy, Oz+(di+lm*sen_alpha)*sen_alpha+lm*cos_alpha+d*sen_alpha*(cm+1))])
                        diagonales.append([(Ox+(D-(di+lm*sen_alpha)*cos_alpha-d*cos_alpha*cm), Oy, Oz+(di+lm*sen_alpha)*sen_alpha+d*sen_alpha*cm), (Ox+(D-(di+lm*sen_alpha)*cos_alpha+lm*sen_alpha-d*cos_alpha*(cm+1)), Oy, Oz+(di+lm*sen_alpha)*sen_alpha+lm*cos_alpha+d*sen_alpha*(cm+1))])
                    else:
                        diagonales.append([(Ox+(di+lm*sen_alpha)*cos_alpha+d*cos_alpha*cm-lm*sen_alpha, Oy, Oz+(di+lm*sen_alpha)*sen_alpha+d*sen_alpha*cm+lm*cos_alpha), (Ox+(di+lm*sen_alpha)*cos_alpha+d*cos_alpha*(cm+1), Oy, Oz+(di+lm*sen_alpha)*sen_alpha+d*sen_alpha*(cm+1))])
                        diagonales.append([(Ox+(D-(di+lm*sen_alpha)*cos_alpha-d*cos_alpha*cm)+lm*sen_alpha, Oy, Oz+(di+lm*sen_alpha)*sen_alpha+d*sen_alpha*cm+lm*cos_alpha), (Ox+(D-(di+lm*sen_alpha)*cos_alpha-d*cos_alpha*(cm+1)), Oy, Oz+(di+lm*sen_alpha)*sen_alpha+d*sen_alpha*(cm+1))])
                else:
                    if i % 2 != 0:
                        diagonales.append([(Ox+(di+lm*sen_alpha)*cos_alpha+d*cos_alpha*cm, Oy, Oz+(di+lm*sen_alpha)*sen_alpha+d*sen_alpha*cm), (Ox+(L-sep)*cos_alpha, Oy, Oz+(L-sep)*sen_alpha+h)])
                        diagonales.append([(Ox+D-((di+lm*sen_alpha)*cos_alpha+d*cos_alpha*cm), Oy, Oz+(di+lm*sen_alpha)*sen_alpha+d*sen_alpha*cm), (Ox+D-(L-sep)*cos_alpha, Oy, Oz+(L-sep)*sen_alpha+h)])
                    else:
                        diagonales.append([(Ox+(di+lm*sen_alpha)*cos_alpha+d*cos_alpha*cm-lm*sen_alpha, Oy, Oz+(di+lm*sen_alpha+d*cm)*sen_alpha+lm*cos_alpha), (Ox+di*cos_alpha+d*cos_alpha*(cm+1), Oy, Oz+di*sen_alpha+d*sen_alpha*(cm+1))])
                        diagonales.append([(Ox+D-((di+lm*sen_alpha)*cos_alpha+d*cos_alpha*cm-lm*sen_alpha), Oy, Oz+(di+lm*sen_alpha+d*cm)*sen_alpha+lm*cos_alpha), (Ox+(D-(L-sep)*cos_alpha), Oy, Oz+(L-sep)*sen_alpha)])
                
                cm += 1
                
        if t_diag == "Igual":
            cm = 0
            for i in range (div):
                if cm != div-1:
                        diagonales.append([(Ox+(di+lm*sen_alpha)*cos_alpha+d*cos_alpha*cm, Oy, Oz+(di+lm*sen_alpha)*sen_alpha+d*sen_alpha*cm), (Ox+(di+lm*sen_alpha)*cos_alpha-lm*sen_alpha+d*cos_alpha*(cm+1), Oy, Oz+(di+lm*sen_alpha)*sen_alpha+lm*cos_alpha+d*sen_alpha*(cm+1))])
                        diagonales.append([(Ox+(D-(di+lm*sen_alpha)*cos_alpha-d*cos_alpha*cm), Oy, Oz+(di+lm*sen_alpha)*sen_alpha+d*sen_alpha*cm), (Ox+(D-(di+lm*sen_alpha)*cos_alpha+lm*sen_alpha-d*cos_alpha*(cm+1)), Oy, Oz+(di+lm*sen_alpha)*sen_alpha+lm*cos_alpha+d*sen_alpha*(cm+1))])
                else:
                    diagonales.append([(Ox+(di+lm*sen_alpha)*cos_alpha+d*cos_alpha*cm, Oy, Oz+(di+lm*sen_alpha)*sen_alpha+d*sen_alpha*cm), (Ox+(L-sep)*cos_alpha, Oy, Oz+(L-sep)*sen_alpha+h)])
                    diagonales.append([(Ox+D-((di+lm*sen_alpha)*cos_alpha+d*cos_alpha*cm), Oy, Oz+(di+lm*sen_alpha)*sen_alpha+d*sen_alpha*cm), (Ox+D-(L-sep)*cos_alpha, Oy, Oz+(L-sep)*sen_alpha+h)])
                
                cm += 1
        diagonales.append([(Ox, Oy, Oz), (Ox+(di+lm*sen_alpha)*cos_alpha-lm*sen_alpha, Oy, Oz+(di+lm*sen_alpha)*sen_alpha+lm*cos_alpha)])
        diagonales.append([(Ox+D, Oy, Oz), (Ox+(D-(di+lm*sen_alpha)*cos_alpha+lm*sen_alpha), Oy, Oz+(di+lm*sen_alpha)*sen_alpha+lm*cos_alpha)])
        
        if m != len(cotas_vertical)-1:
            if ac != 0:
                cm = 0
                for i in range (cant_corr):
                    Correas.append([(Ox+(di+lm*sen_alpha)*cos_alpha-lm*sen_alpha+dc*cos_alpha*cm, Oy, Oz+(di+lm*sen_alpha)*sen_alpha+lm*cos_alpha+dc*sen_alpha*cm), (Ox+(di+lm*sen_alpha)*cos_alpha-lm*sen_alpha+dc*cos_alpha*cm, Oy+Sep_port, Oz+(di+lm*sen_alpha)*sen_alpha+lm*cos_alpha+dc*sen_alpha*cm)])
                    Correas.append([(Ox+(D-(di+lm*sen_alpha)*cos_alpha+lm*sen_alpha-dc*cos_alpha*cm), Oy, Oz+(di+lm*sen_alpha)*sen_alpha+lm*cos_alpha+dc*sen_alpha*cm), (Ox+(D-(di+lm*sen_alpha)*cos_alpha+lm*sen_alpha-dc*cos_alpha*cm), Oy+Sep_port, Oz+(di+lm*sen_alpha)*sen_alpha+lm*cos_alpha+dc*sen_alpha*cm)])
                    cm += 1
            if ac == 0:
                cm = 0
                for i in range (cant_corr-1):
                    Correas.append([(Ox+(dc+lm*sen_alpha)*cos_alpha-lm*sen_alpha+dc*cos_alpha*cm, Oy, Oz+(dc+lm*sen_alpha)*sen_alpha+lm*cos_alpha+dc*sen_alpha*cm), (Ox+(dc+lm*sen_alpha)*cos_alpha-lm*sen_alpha+dc*cos_alpha*cm, Oy+Sep_port, Oz+(dc+lm*sen_alpha)*sen_alpha+lm*cos_alpha+dc*sen_alpha*cm)])
                    Correas.append([(Ox+(D-(dc+lm*sen_alpha)*cos_alpha+lm*sen_alpha-dc*cos_alpha*cm), Oy, Oz+(dc+lm*sen_alpha)*sen_alpha+lm*cos_alpha+dc*sen_alpha*cm), (Ox+(D-(dc+lm*sen_alpha)*cos_alpha+lm*sen_alpha-dc*cos_alpha*cm), Oy+Sep_port, Oz+(dc+lm*sen_alpha)*sen_alpha+lm*cos_alpha+dc*sen_alpha*cm)])
                    cm += 1
                        
                Correas.append([(Ox, Oy, Oz+h), (Ox, Oy+Sep_port, Oz+h)])
                Correas.append([(Ox+D, Oy, Oz+h), (Ox+D, Oy+Sep_port, Oz+h)])
            Correas.append([(Ox+(L-sep)*cos_alpha, Oy, Oz+(L-sep)*sen_alpha+h),(Ox+(L-sep)*cos_alpha, Oy+Sep_port, Oz+(L-sep)*sen_alpha+h)])
            Correas.append([(Ox+D-(L-sep)*cos_alpha, Oy, Oz+(L-sep)*sen_alpha+h),(Ox+D-(L-sep)*cos_alpha, Oy+Sep_port, Oz+(L-sep)*sen_alpha+h)])
                
        Apoyos.append([(Ox, Oy, Oz-long_apoyo), (Ox, Oy, Oz)])
        Apoyos.append([(Ox+D, Oy, Oz-long_apoyo), (Ox+D, Oy, Oz)])
    
    for i in range (len(Cordones)):
        Nudos.append(Cordones[i][0])
        Nudos.append(Cordones[i][1])
        
    for i in range(len(montantes)):
        Nudos.append(montantes[i][0])
        Nudos.append(montantes[i][1])
    
    # Proceso con diagonales
    for i in range(len(diagonales)):
        Nudos.append(diagonales[i][0])
        Nudos.append(diagonales[i][1])
    
    # Proceso con Correas
    for i in range(len(Correas)):
        Nudos.append(Correas[i][0])
        Nudos.append(Correas[i][1])
    
    Nudos = list(set(Nudos))
                
    for cordon in Cordones:
        # Añadir una línea al modelspace
        line = msp.add_line(cordon[0],cordon[1])
        # Asignar la línea al nuevo layer
        line.dxf.layer = "Cordones"
    
    for montante in montantes:    
        # Añadir una línea al modelspace
        line = msp.add_line(montante[0],montante[1])
        # Asignar la línea al nuevo layer
        line.dxf.layer = "Montantes"
        
    for diagonal in diagonales:    
        # Añadir una línea al modelspace
        line = msp.add_line(diagonal[0],diagonal[1])
        # Asignar la línea al nuevo layer
        line.dxf.layer = "Diagonales"
        
    for correa in Correas:    
        # Añadir una línea al modelspace
        line = msp.add_line(correa[0],correa[1])
        # Asignar la línea al nuevo layer
        line.dxf.layer = "Correas"
    
    for apoyo in Apoyos:    
        # Añadir una línea al modelspace
        line = msp.add_line(apoyo[0],apoyo[1])
        # Asignar la línea al nuevo layer
        line.dxf.layer = "Apoyos"
        
    # Guardar el documento DXF
    if output_path:
        doc.saveas(output_path)
    else:
        output_dir = os.path.dirname(os.path.abspath(__file__))
        doc.saveas(os.path.join(output_dir, "Galpon.dxf"))


if __name__ == '__main__':
    os.makedirs('temp', exist_ok=True)
    app.run(debug=True)