import ezdxf
import tkinter as tk
from tkinter import filedialog
import os
import sys
from tkinter import ttk  # Necesario para Combobox
from tkinter import messagebox

# Definir dimensions como una variable global
cotas_vertical = []
cotas_horizontal = []
galpon_dxf_path = None  # Nueva variable global

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
    
def save_results_to_file(filename):
    output_file = filename.replace('.dxf', '_cotas.txt')
    with open(output_file, 'w') as f:
        f.write("Cotas Verticales:\n")
        f.write('\n'.join(map(str, cotas_vertical)))
        f.write("\n\nCotas Horizontales:\n")
        f.write('\n'.join(map(str, cotas_horizontal)))
    return output_file

def open_file_location(file_path):
    import os
    import subprocess
    file_path = os.path.normpath(file_path)  # Normaliza la ruta del archivo
    
    if os.name == 'nt':  # Windows
        # Usar 'explorer /select,' para seleccionar el archivo específico
        os.system(f'explorer /select,"{file_path}"')
    else:  # Linux/Mac
        folder_path = os.path.dirname(os.path.abspath(file_path))
        subprocess.Popen(['xdg-open', folder_path])

def center_window(window, width, height):
    # Obtener dimensiones de la pantalla
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    # Calcular posición x,y para centrar la ventana
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    
    # Establecer geometría de la ventana
    window.geometry(f'{width}x{height}+{x}+{y}')

def browse_file(filename_entry):
    global output_file, filename, galpon_dxf_path
    filename = filedialog.askopenfilename(filetypes=[("DXF files", "*.dxf")])
    if filename:
        # Actualizar el campo de nombre de archivo
        filename_entry.config(state='normal')
        filename_entry.delete(0, tk.END)
        filename_entry.insert(0, os.path.basename(filename))
        filename_entry.config(state='readonly')
        
        analyze_dxf(filename)
        update_text_display()

def update_text_display():
    # Buscar el widget Text en el contenedor principal
    text_widget = None
    for widget in root.winfo_children():
        for child in widget.winfo_children():
            if isinstance(child, tk.Text):
                text_widget = child
                break
    
    if text_widget:
        text_widget.config(state='normal')
        text_widget.delete(1.0, tk.END)
        text_widget.insert(tk.END, "Cotas Verticales:\n")
        text_widget.insert(tk.END, '\n'.join(map(str, cotas_vertical)))
        text_widget.insert(tk.END, "\n\nCotas Horizontales:\n")
        text_widget.insert(tk.END, '\n'.join(map(str, cotas_horizontal)))
        text_widget.config(state='disabled')

def analyze_dxf(filename):
    global galpon_dxf_path
    # Abre el archivo DXF
    drawing = ezdxf.readfile(filename)

    # Encuentra las cotas y sus valores
    find_dimensions(drawing)
    
    # Habilitar el botón de generar estructura
    for widget in root.winfo_children():
        for child in widget.winfo_children():
            if isinstance(child, tk.Button) and "Generar Estructura" in child['text']:
                child.config(state='normal')

def main():
    global root, galpon_dxf_path
    root = tk.Tk()
    root.title("Explorador de archivos DXF")
    root.resizable(False, False)  # Deshabilita el redimensionamiento horizontal y vertical
    center_window(root, 400, 600)

    # Contenedor principal con márgenes uniformes
    main_container = tk.Frame(root, padx=20, pady=20)
    main_container.pack(fill="both", expand=True)

    # Frame superior para nombre de archivo y botón - Centrado
    file_frame = tk.Frame(main_container)
    file_frame.pack(fill="x", pady=(0, 10), anchor="center")

    # Campo de nombre de archivo y botón de selección
    filename_entry = tk.Entry(file_frame, state='readonly', width=40)
    filename_entry.pack(side=tk.LEFT, padx=(0, 10), fill='x', expand=True)

    browse_button = tk.Button(file_frame, text="Seleccionar DXF", command=lambda: browse_file(filename_entry))
    browse_button.pack(side=tk.RIGHT)

    # Text widget para resultados - Centrado
    text_widget = tk.Text(main_container, height=10)
    text_widget.pack(fill="x", pady=(0, 10), anchor="center")
    text_widget.config(state='disabled')

    # Types frame - Centrado
    types_frame = tk.LabelFrame(main_container, text="Tipos", padx=10, pady=10)
    types_frame.pack(fill="x", pady=(0, 10))
    
    # Tipo de chapa - Centrado
    tchapa_frame = tk.Frame(types_frame)
    tchapa_frame.pack(fill="x", pady=2)
    
    # Crear un frame contenedor para centrar los elementos
    tchapa_container = tk.Frame(tchapa_frame)
    tchapa_container.pack(expand=True, padx=(0, 30))
    
    tk.Label(tchapa_container, text="Tipo de chapa", width=20, anchor="e").pack(side=tk.LEFT, padx=(0, 10))
    tchapa_combo = ttk.Combobox(tchapa_container, 
                               values=["Termoacústica", "Trapezoidal", "Zipada"],
                               state="readonly",
                               width=15,
                               justify="center")
    tchapa_combo.set("Termoacústica")
    tchapa_combo.pack(side=tk.LEFT, padx=(0, 40))

    # Tipo de diagonal - Centrado
    tdiag_frame = tk.Frame(types_frame)
    tdiag_frame.pack(fill="x", pady=2)
    
    # Crear un frame contenedor para centrar los elementos
    tdiag_container = tk.Frame(tdiag_frame)
    tdiag_container.pack(expand=True, padx=(0, 70))
    
    tk.Label(tdiag_container, text="Tipo de diagonal", width=20, anchor="e").pack(side=tk.LEFT, padx=(0, 10))
    tdiag_combo = ttk.Combobox(tdiag_container, 
                              values=["Intercalado", "Igual"],
                              state="readonly",
                              width=15,
                              justify="center")
    tdiag_combo.set("Intercalado")
    tdiag_combo.pack(side=tk.LEFT)

    # Params frame - Centrado
    params_frame = tk.LabelFrame(main_container, text="Parámetros", padx=10, pady=10)
    params_frame.pack(fill="x", pady=(0, 10))

    def create_param_entry(parent, label_text, default_value):
        frame = tk.Frame(parent)
        frame.pack(fill="x", pady=2)
        
        container = tk.Frame(frame)
        container.pack(expand=True, padx=(0, 30))
        
        
        label = tk.Label(container, text=label_text, width=30, anchor="e")
        label.pack(side=tk.LEFT, padx=(0, 10))
        entry = tk.Entry(container, width=10, justify="center")
        entry.insert(0, default_value)
        entry.pack(side=tk.LEFT, padx=(0, 20))
        return entry

    # Crear entradas de parámetros
    ht_entry = create_param_entry(params_frame, "Altura de canaleta techo", "2.60")
    pend_entry = create_param_entry(params_frame, "Pendiente del techo", "0.15")
    ac_entry = create_param_entry(params_frame, "Ancho de la canaleta embutida", "0.35")
    sep_entry = create_param_entry(params_frame, "Separación en union entre vigas", "0.05")
    long_entry = create_param_entry(params_frame, "Longitud de apoyo", "0")
    h_entry = create_param_entry(params_frame, "Altura de montante extrema", "0.60")

    # Botón para generar estructura - Centrado
    generate_button = tk.Button(
        main_container,
        text="Generar Estructura",
        command=lambda: generate_structure(
            float(ht_entry.get()),
            float(pend_entry.get()),
            float(ac_entry.get()),
            float(sep_entry.get()),
            float(long_entry.get()),
            float(h_entry.get()),
            tchapa_combo.get(),
            tdiag_combo.get()
        ),
        state='disabled'
    )
    generate_button.pack(pady=10, anchor="center")

    root.mainloop()

    return filename_entry, text_widget  # Retornamos las referencias

def generate_structure(ht, pend, ac, sep, long_apoyo, h, t_chapa, t_diag):
    try:
        import draw
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))
        
        # Obtener el nombre del archivo original sin extensión
        original_name = os.path.splitext(os.path.basename(filename))[0]
        
        # Crear el nuevo nombre: "Estructura - nombre_original.dxf"
        output_filename = f"Estructura - {original_name}.dxf"
        
        global galpon_dxf_path
        galpon_dxf_path = os.path.join(application_path, output_filename)
        
        draw.draw_structure(
            cotas_horizontal, 
            cotas_vertical, 
            output_path=galpon_dxf_path,
            ht=ht,
            pend=pend,
            ac=ac,
            sep=sep,
            long_apoyo=long_apoyo,
            h=h,
            t_chapa=t_chapa,
            t_diag=t_diag
        )
        
        # Abrir la ubicación del archivo inmediatamente después de generarlo
        open_file_location(galpon_dxf_path)
        
        # Mensaje de éxito con el nuevo nombre
        messagebox.showinfo("Éxito", f"Archivo generado correctamente como:\n{output_filename}")
        
    except Exception as e:
        messagebox.showerror("Error", f"Error al generar el dibujo: {str(e)}")

if __name__ == "__main__":
    main() 
