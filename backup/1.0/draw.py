import ezdxf
import math
import os

def draw_structure(cotas_horizontal, cotas_vertical, output_path=None, ht=2.60, pend=0.15, ac=0.35, sep=0.05, long_apoyo=0, h=0.6, t_chapa="Termoacústica", t_diag="Intercalado"):
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



    


# Solo ejecutar si se corre directamente
if __name__ == "__main__":
    draw_structure()


