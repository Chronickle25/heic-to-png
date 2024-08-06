import os
from PIL import Image
import pillow_heif

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

# Recorre todos los archivos en el directorio
for filename in os.listdir(directory):
    # Verifica si el archivo está en formato HEIC
    if filename.lower().endswith(".heic"):
        # Crea la ruta completa del archivo
        filepath = os.path.join(directory, filename)
        print("Convirtiendo:", filepath)
        
        try:
            # Lee el archivo HEIC
            heif_file = pillow_heif.read_heif(filepath)
            image = Image.frombytes(
                heif_file.mode,
                heif_file.size,
                heif_file.data,
                "raw",
            )

            # Crea un nuevo nombre para el archivo PNG
            new_filename = os.path.splitext(filename)[0] + ".png"
            new_filepath = os.path.join(png_directory, new_filename)

            # Guarda la imagen como PNG
            image.save(new_filepath, format="png")
            print(f"Imagen guardada como: {new_filepath}")

        except Exception as e:
            print(f"Error al convertir {filename}: {e}")
