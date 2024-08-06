import os
from PIL import Image
import pillow_heif
from concurrent.futures import ThreadPoolExecutor, as_completed

# Función para convertir un archivo HEIC a PNG
def convert_heic_to_png(filepath, png_directory):
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
        return f"Imagen guardada como: {new_filepath}"
    except Exception as e:
        return f"Error al convertir {filename}: {e}"

# Solicita la ruta del directorio que contiene las imágenes HEIC
directory = input("Introduce la ruta del directorio que contiene las imágenes HEIC: ").strip()

# Verifica que el directorio exista
if not os.path.isdir(directory):
    print("El directorio especificado no existe.")
    exit()

png_directory = os.path.join(directory, 'png_images')

# Crea el directorio para las imágenes PNG si no existe
if not os.path.exists(png_directory):
    os.makedirs(png_directory)

# Obtiene una lista de archivos HEIC en el directorio
heic_files = [os.path.join(directory, filename) for filename in os.listdir(directory) if filename.lower().endswith(".heic")]

# Usa ThreadPoolExecutor para procesar archivos en paralelo
with ThreadPoolExecutor() as executor:
    # Crea un diccionario de futuros
    future_to_file = {executor.submit(convert_heic_to_png, filepath, png_directory): filepath for filepath in heic_files}

    # Imprime los resultados a medida que se completan
    for future in as_completed(future_to_file):
        result = future.result()
        print(result)
