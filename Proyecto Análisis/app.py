import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import pydicom
import numpy as np
import pydicom.encoders.gdcm
import pylibjpeg

bundle_dir = os.path.abspath(os.path.dirname(__file__))
image_path = os.path.join(bundle_dir, '1.png')

def limpiar_resultado():
    entrada_busqueda.delete(0, tk.END)
    mostrar_todos_los_datos()

def mostrar_todos_los_datos():
    texto_info.config(state=tk.NORMAL)
    texto_info.delete("1.0", tk.END)
    for elem in ds:
        texto_info.insert(tk.END, f"{elem}\n")
    texto_info.config(state=tk.DISABLED)

def buscar_palabra():
    palabra = entrada_busqueda.get()
    if not palabra:
        mostrar_todos_los_datos()
        return

    texto_info.config(state=tk.NORMAL)
    texto_info.delete("1.0", tk.END)
    
    for elem in ds:
        linea = str(elem)
        if palabra.lower() in linea.lower():  # Buscar de manera insensible a mayúsculas/minúsculas
            texto_info.insert(tk.END, linea + "\n")
            idx = texto_info.search(palabra, tk.END+"-1c linestart", nocase=1)
            end_idx = f"{idx}+{len(palabra)}c"
            texto_info.tag_add("resultado", idx, end_idx)
    texto_info.tag_config("resultado", background="yellow", foreground="black")
    texto_info.config(state=tk.DISABLED)

def abrir_archivo():
    global ds
    ruta_archivo = filedialog.askopenfilename(filetypes=[("DICOM files", "*.dcm"), ("All files", "*.*")])
    if ruta_archivo:
        mostrar_informacion_imagen(ruta_archivo)

def mostrar_informacion_imagen(ruta_archivo):
    try:
        global ds
        ds = pydicom.dcmread(ruta_archivo)
        
        global ventana_info, texto_info, entrada_busqueda
        
        if 'ventana_info' in globals():
            texto_info.config(state=tk.NORMAL)
            texto_info.delete('1.0', tk.END)
            limpiar_resultado()
        
        if 'ventana_info' not in globals():
            ventana_info = tk.Toplevel()
            ventana_info.title("Información DICOM")
            ventana_info.geometry("1000x650")
            ventana_info.configure(bg="#1d1a1e")

            texto_frame = tk.Frame(ventana_info)
            texto_frame.pack(fill=tk.BOTH, expand=True)

            texto_info = tk.Text(texto_frame, wrap='word', bg="#2d2a2e", fg="#ffffff")
            texto_info.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            scrollbar = tk.Scrollbar(texto_frame, command=texto_info.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            texto_info.config(yscrollcommand=scrollbar.set)
            
            frame_busqueda = tk.Frame(ventana_info, bg="#1d1a1e")
            frame_busqueda.pack(fill=tk.X)
            entrada_busqueda = tk.Entry(frame_busqueda, bg="#2d2a2e", fg="#ffffff")
            entrada_busqueda.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.X, expand=True)
            boton_buscar = tk.Button(frame_busqueda, text="Buscar", command=buscar_palabra, bg='#1d1a1e', fg="#e0e0e0")
            boton_buscar.pack(side=tk.LEFT, padx=5, pady=5)
            boton_limpiar = tk.Button(frame_busqueda, text="Limpiar", command=limpiar_resultado, bg='#1d1a1e', fg="#e0e0e0")
            boton_limpiar.pack(side=tk.LEFT, padx=5, pady=5)
        
        mostrar_todos_los_datos()
        
        if 'PixelData' in ds:
            imagen = ds.pixel_array
            if ds.PhotometricInterpretation == "MONOCHROME1":
                imagen = np.amax(imagen) - imagen
            imagen = (imagen / np.max(imagen) * 255).astype(np.uint8)
            imagen = Image.fromarray(imagen)
            
            nuevo_ancho = 600  
            nuevo_alto = 600 
            imagen = imagen.resize((nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS)
            
            imagen_tk = ImageTk.PhotoImage(imagen)

            etiqueta_imagen_arriba.config(image=imagen_tk)
            etiqueta_imagen_arriba.image = imagen_tk
            etiqueta_imagen_arriba.pack(expand=1)
            boton_abrir.pack_forget()  
            boton_cambiar.pack(pady=20)
            
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo leer el archivo DICOM: {str(e)}")

ventana = tk.Tk()
ventana.title("ANALYTICS DREAM APP")
ventana.configure(bg="#2d2a2e") 
ventana.geometry("600x700") 

frame_central = tk.Frame(ventana, bg="#2d2a2e")
frame_central.pack(expand=True)

imagen = Image.open(image_path)
imagen = imagen.resize((150, 150), Image.Resampling.LANCZOS) 
imagen_tk = ImageTk.PhotoImage(imagen)

etiqueta_imagen_arriba = tk.Label(frame_central, image=imagen_tk, bg="#2d2a2e")
etiqueta_imagen_arriba.pack(pady=0)

boton_abrir = tk.Button(frame_central,
                        text="Abrir Archivo",
                        command=abrir_archivo,
                        compound="center",
                        bd=0,
                        highlightthickness=0,
                        cursor="hand2",
                        fg="#e0e0e0",
                        border=10
                        )
boton_abrir.config(bg='#1d1a1e', activebackground='#4d4a4e', font=("Helvetica", 21))
boton_abrir.pack(pady=0)

boton_cambiar = tk.Button(
    frame_central,
    text="Cambiar Archivo",
    command=abrir_archivo,
    compound="top",
    bd=0,
    highlightthickness=0,
    fg="black",
    padx=20,
    pady=20,
    cursor="hand2",
    border=10
    )
boton_cambiar.config(fg="#e0e0e0" ,bg='#1d1a1e', activebackground='#4d4a4e', font=("Helvetica", 21))

ventana.mainloop()
