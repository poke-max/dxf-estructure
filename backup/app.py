import ezdxf
import tkinter as tk
from tkinter import filedialog

# Definir dimensions como una variable global
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

def browse_file():
    global output_file, filename  # Agregamos filename como global
    filename = filedialog.askopenfilename(filetypes=[("DXF files", "*.dxf")])
    if filename:
        analyze_dxf(filename)
        show_results_button.config(state='normal')

def show_results():
    # Crear nueva ventana para mostrar resultados
    results_display = tk.Toplevel(root)
    results_display.title("Resultados")
    center_window(results_display, 400, 300)
    
    # Mostrar resultados en la ventana
    text_widget = tk.Text(results_display, height=15, width=45)
    text_widget.pack(pady=10)
    text_widget.insert(tk.END, f"Cotas Verticales:\n{cotas_vertical}\n\n")
    text_widget.insert(tk.END, f"Cotas Horizontales:\n{cotas_horizontal}\n\n")
    text_widget.config(state='disabled')
    
    # Frame para los botones
    button_frame = tk.Frame(results_display)
    button_frame.pack(pady=10)
    
    # Botón para guardar archivo
    save_button = tk.Button(
        button_frame,
        text="Guardar Archivo",
        command=lambda: save_and_update_text(text_widget, filename)
    )
    save_button.pack(side=tk.LEFT, padx=5)
    
    # Botón para abrir ubicación del archivo (se habilitará después de guardar)
    location_button = tk.Button(
        button_frame,
        text="Abrir ubicación del archivo",
        state='disabled'
    )
    location_button.pack(side=tk.LEFT, padx=5)

def save_and_update_text(text_widget, filename):
    global output_file
    output_file = save_results_to_file(filename)
    
    # Habilitar y actualizar el botón de ubicación en el frame de botones
    for widget in text_widget.master.winfo_children():
        if isinstance(widget, tk.Frame):
            for button in widget.winfo_children():
                if "ubicación" in button['text'].lower():
                    button.config(
                        state='normal',
                        command=lambda: open_file_location(output_file)
                    )
    
    # Actualizar el texto para mostrar la ubicación del archivo
    text_widget.config(state='normal')
    text_widget.insert(tk.END, f"\n\nArchivo guardado en:\n{output_file}")
    text_widget.config(state='disabled')

def analyze_dxf(filename):
    # Abre el archivo DXF
    drawing = ezdxf.readfile(filename)

    # Encuentra las cotas y sus valores
    find_dimensions(drawing)

def main():
    global root, show_results_button, output_file, filename
    root = tk.Tk()
    root.title("Explorador de archivos DXF")
    center_window(root, 300, 150)

    browse_button = tk.Button(root, text="Seleccionar archivo DXF", command=browse_file)
    browse_button.pack(pady=20)

    show_results_button = tk.Button(root, text="Mostrar Resultados", command=show_results, state='disabled')
    show_results_button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
