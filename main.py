import os
from PIL import Image
import pillow_heif
from concurrent.futures import ThreadPoolExecutor, as_completed
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar, Style, Combobox

def convert_heic_to_format(filepath, output_directory, output_format):
    """Convert a HEIC file to the specified format."""
    filename = os.path.basename(filepath)
    new_filename = os.path.splitext(filename)[0] + f".{output_format.lower()}"
    new_filepath = os.path.join(output_directory, new_filename)
    
    try:
        heif_file = pillow_heif.read_heif(filepath)
        image = Image.frombytes(
            heif_file.mode,
            heif_file.size,
            heif_file.data,
            "raw",
        )
        image.save(new_filepath, format=output_format)
        return True, f"Imagen guardada como: {new_filepath}"
    except Exception as e:
        return False, f"Error al convertir {filename}: {e}"

def select_directory():
    """Open a dialog to select the directory containing HEIC images."""
    directory = filedialog.askdirectory()
    if directory:
        entry_directory.delete(0, tk.END)
        entry_directory.insert(0, directory)

def create_output_directory(directory):
    """Create a directory to store output images if it doesn't exist."""
    output_directory = os.path.join(directory, 'converted_images')
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    return output_directory

def get_heic_files(directory):
    """Get a list of HEIC files in the specified directory."""
    return [os.path.join(directory, filename) for filename in os.listdir(directory) if filename.lower().endswith(".heic")]

def process_files_in_parallel(directory, progressbar, output_format):
    """Process HEIC files in parallel and update the progress bar."""
    global running
    running = True
    output_directory = create_output_directory(directory)
    heic_files = get_heic_files(directory)
    if not heic_files:
        messagebox.showinfo("Información", "No se encontraron archivos HEIC en el directorio especificado.")
        return

    progressbar["maximum"] = len(heic_files)
    progressbar["value"] = 0
    progressbar.pack(pady=10)

    successful_conversions = 0
    failed_conversions = 0

    with ThreadPoolExecutor() as executor:
        future_to_file = {executor.submit(convert_heic_to_format, filepath, output_directory, output_format): filepath for filepath in heic_files}
        for future in as_completed(future_to_file):
            if not running:
                break
            success, message = future.result()
            progressbar["value"] += 1
            root.update_idletasks()
            if success:
                successful_conversions += 1
            else:
                failed_conversions += 1

    progressbar.pack_forget()
    summary = f"Procesamiento completado.\n\nÉxitos: {successful_conversions}\nFallos: {failed_conversions}"
    messagebox.showinfo("Resumen", summary)

def start_conversion():
    """Start the conversion process."""
    directory = entry_directory.get().strip()
    if not os.path.isdir(directory):
        messagebox.showerror("Error", "El directorio especificado no existe.")
        return
    
    output_format = format_combobox.get().strip().upper()
    if output_format not in ["PNG", "JPEG", "BMP", "GIF", "TIFF"]:
        messagebox.showerror("Error", "Formato de salida no válido.")
        return

    # Deshabilitar botones mientras se realiza la conversión
    button_convert.config(state=tk.DISABLED)
    button_cancel.config(state=tk.NORMAL)
    
    process_files_in_parallel(directory, progressbar, output_format)

    # Rehabilitar botones después de la conversión
    button_convert.config(state=tk.NORMAL)
    button_cancel.config(state=tk.DISABLED)

def cancel_conversion():
    """Cancel the ongoing conversion process."""
    global running
    running = False

# Configuración de la interfaz gráfica
root = tk.Tk()
root.title("Conversor de HEIC a Otros Formatos")
root.geometry("600x250")
root.resizable(False, False)

style = Style(root)
style.configure("TProgressbar", thickness=20)

frame = tk.Frame(root, pady=10, padx=10)
frame.pack(fill=tk.BOTH, expand=True)

label_directory = tk.Label(frame, text="Directorio de imágenes HEIC:")
label_directory.grid(row=0, column=0, padx=5, pady=5, sticky="e")

entry_directory = tk.Entry(frame, width=50)
entry_directory.grid(row=0, column=1, padx=5, pady=5)

button_browse = tk.Button(frame, text="Examinar", command=select_directory)
button_browse.grid(row=0, column=2, padx=5, pady=5)

label_format = tk.Label(frame, text="Formato de salida:")
label_format.grid(row=1, column=0, padx=5, pady=5, sticky="e")

format_combobox = Combobox(frame, values=["PNG", "JPEG", "BMP", "GIF", "TIFF"], state="readonly")
format_combobox.set("PNG")
format_combobox.grid(row=1, column=1, padx=5, pady=5)

button_convert = tk.Button(root, text="Convertir", command=start_conversion, height=2, width=20)
button_convert.pack(pady=10)

button_cancel = tk.Button(root, text="Cancelar", command=cancel_conversion, height=2, width=20, state=tk.DISABLED)
button_cancel.pack(pady=10)

progressbar = Progressbar(root, orient=tk.HORIZONTAL, mode='determinate', length=500)

# Inicializar variables globales
running = True

# Iniciar la aplicación
root.mainloop()
