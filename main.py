import os
from PIL import Image
import pillow_heif
from concurrent.futures import ThreadPoolExecutor, as_completed
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar, Style

def convert_heic_to_png(filepath, png_directory):
    """Convert a HEIC file to PNG format."""
    filename = os.path.basename(filepath)
    new_filename = os.path.splitext(filename)[0] + ".png"
    new_filepath = os.path.join(png_directory, new_filename)
    
    try:
        heif_file = pillow_heif.read_heif(filepath)
        image = Image.frombytes(
            heif_file.mode,
            heif_file.size,
            heif_file.data,
            "raw",
        )
        image.save(new_filepath, format="png")
        return True, f"Imagen guardada como: {new_filepath}"
    except Exception as e:
        return False, f"Error al convertir {filename}: {e}"

def select_directory():
    """Open a dialog to select the directory containing HEIC images."""
    directory = filedialog.askdirectory()
    if directory:
        entry_directory.delete(0, tk.END)
        entry_directory.insert(0, directory)

def create_png_directory(directory):
    """Create a directory to store PNG images if it doesn't exist."""
    png_directory = os.path.join(directory, 'png_images')
    if not os.path.exists(png_directory):
        os.makedirs(png_directory)
    return png_directory

def get_heic_files(directory):
    """Get a list of HEIC files in the specified directory."""
    return [os.path.join(directory, filename) for filename in os.listdir(directory) if filename.lower().endswith(".heic")]

def process_files_in_parallel(directory, progressbar):
    """Process HEIC files in parallel and update the progress bar."""
    png_directory = create_png_directory(directory)
    heic_files = get_heic_files(directory)
    if not heic_files:
        messagebox.showinfo("Información", "No se encontraron archivos HEIC en el directorio especificado.")
        return

    progressbar["maximum"] = len(heic_files)
    progressbar["value"] = 0
    progressbar.pack(pady=10)

    with ThreadPoolExecutor() as executor:
        future_to_file = {executor.submit(convert_heic_to_png, filepath, png_directory): filepath for filepath in heic_files}
        for future in as_completed(future_to_file):
            success, message = future.result()
            progressbar["value"] += 1
            root.update_idletasks()
            if not success:
                messagebox.showerror("Error", message)
                return

    progressbar.pack_forget()
    messagebox.showinfo("Información", "Procesamiento completado.")

def start_conversion():
    """Start the conversion process."""
    directory = entry_directory.get().strip()
    if not os.path.isdir(directory):
        messagebox.showerror("Error", "El directorio especificado no existe.")
        return

    process_files_in_parallel(directory, progressbar)

# Configuración de la interfaz gráfica
root = tk.Tk()
root.title("Conversor de HEIC a PNG")
root.geometry("500x100")
root.resizable(False, False)

style = Style(root)
style.configure("TProgressbar", thickness=20)

frame = tk.Frame(root, pady=10, padx=10)
frame.pack(fill=tk.BOTH, expand=True)

label_directory = tk.Label(frame, text="Directorio de imágenes HEIC:")
label_directory.grid(row=0, column=0, padx=5, pady=5, sticky="e")

entry_directory = tk.Entry(frame, width=40)
entry_directory.grid(row=0, column=1, padx=5, pady=5)

button_browse = tk.Button(frame, text="Examinar", command=select_directory)
button_browse.grid(row=0, column=2, padx=5, pady=5)

button_convert = tk.Button(root, text="Convertir a PNG", command=start_conversion, height=2, width=20)
button_convert.pack(pady=10)

progressbar = Progressbar(root, orient=tk.HORIZONTAL, mode='determinate', length=400)

# Iniciar la aplicación
root.mainloop()
