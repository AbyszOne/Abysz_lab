import modules.scripts as scripts
import gradio as gr
import subprocess
import os
from PIL import Image
import sys
import cv2
import shutil
import time
            
from modules import images
from modules.processing import process_images, Processed
from modules.processing import Processed
from modules.shared import opts, cmd_opts, state


class Script(scripts.Script):

    # The title of the script.
    def title(self):
        return "Abysz Lab"

    # Determines when the script should be shown in the dropdown menu via the 
    
    def show(self, is_img2img):
        return is_img2img
            
    def ui(self, is_img2img):
        source_folder = gr.Textbox(label="Source images folder", value="J:\FULL")
        source_folder_value = source_folder.value
        generated_folder = gr.Textbox(label="Generated images folder", value="d:/usuario/Documents/CONTROLNET/DEFLIKER/Maingradio/Gen")
        generated_folder_value = generated_folder.value
        out_folder = gr.Textbox(label="Out", value="d:/usuario/Documents/CONTROLNET/DEFLIKER/Maingradio/Gen/out")
        slider1 = gr.Slider(minimum=1, maximum=30, value=5, step=1, label="Frame refresh frecuency")
        slider2 = gr.Slider(minimum=0, maximum=100, value=50, step=5, label="Refresh Strength")
        slider3 = gr.Slider(minimum=1, maximum=10, value=5, step=0.5, label="DFI Strength")
        slider4 = gr.Slider(minimum=0, maximum=10, value=4, step=1, label="DFI Deghost")
        slider5 = gr.Slider(minimum=1, maximum=99, value=25, step=2, label="Smooth")
        render_button = gr.Button("Render", onclick=lambda: run_abysz_deflicker(slider1.value, slider2.value, slider3.value, slider4.value, slider5.value))
        
        # Definir las rutas de las carpetas
        maskD = os.path.join(os.getcwd(), 'extensions', 'Abysz-Deflicker', 'scripts', 'Run', 'MaskD')
        maskS = os.path.join(os.getcwd(), 'extensions', 'Abysz-Deflicker', 'scripts', 'Run', 'MaskS')
        output = os.path.join(os.getcwd(), 'extensions', 'Abysz-Deflicker', 'scripts', 'Run', 'Output')
        source = os.path.join(os.getcwd(), 'extensions', 'Abysz-Deflicker', 'scripts', 'Run', 'Source')
        gen = os.path.join(os.getcwd(), 'extensions', 'Abysz-Deflicker', 'scripts', 'Run', 'Gen')
        
        def run_abysz_deflicker(slider1, slider2, slider3, slider4, slider5):
            # Copy the images from source_folder to run folder in JPEG quality 100
            os.makedirs(source, exist_ok=True)
            os.makedirs(maskS, exist_ok=True)
            os.makedirs(output, exist_ok=True)
            os.makedirs(maskD, exist_ok=True)
            os.makedirs(gen, exist_ok=True)
            
            for file in os.listdir(source_folder_value):
                if file.endswith(".jpg") or file.endswith(".jpeg") or file.endswith(".png"):
                    img = Image.open(os.path.join(source_folder_value, file))
                    img.save(os.path.join("./extensions/Abysz-Deflicker/scripts/Run/Source", file), "jpeg", quality=100)
            for file in os.listdir(generated_folder_value):
                if file.endswith(".jpg") or file.endswith(".jpeg") or file.endswith(".png"):
                    img = Image.open(os.path.join(generated_folder_value, file))
                    img.save(os.path.join("./extensions/Abysz-Deflicker/scripts/Run/Gen", file))
                    
            # Carpeta donde se encuentran las imágenes de Gen
            gen_folder = generated_folder_value
            
            # Carpeta donde se encuentran las imágenes de FULL
            full_folder = "./extensions/Abysz-Deflicker/scripts/Run/Source/"
            
            # Obtener la primera imagen en la carpeta Gen
            gen_images = os.listdir(gen_folder)
            gen_image_path = os.path.join(gen_folder, gen_images[0])
            gen_image = cv2.imread(gen_image_path)
            gen_height, gen_width = gen_image.shape[:2]
            gen_aspect_ratio = gen_width / gen_height
            
            # Recorrer todas las imágenes en la carpeta FULL
            for image_name in os.listdir(full_folder):
                image_path = os.path.join(full_folder, image_name)
                image = cv2.imread(image_path)
                height, width = image.shape[:2]
                aspect_ratio = width / height
            
                if aspect_ratio != gen_aspect_ratio:
                    if aspect_ratio > gen_aspect_ratio:
                        # La imagen es más ancha que la imagen de Gen
                        crop_width = int(height * gen_aspect_ratio)
                        x = int((width - crop_width) / 2)
                        image = image[:, x:x+crop_width]
                    else:
                        # La imagen es más alta que la imagen de Gen
                        crop_height = int(width / gen_aspect_ratio)
                        y = int((height - crop_height) / 2)
                        image = image[y:y+crop_height, :]
            
                # Redimensionar la imagen de FULL a la resolución de la imagen de Gen
                image = cv2.resize(image, (gen_width, gen_height))
            
                # Guardar la imagen redimensionada en la carpeta FULL
                cv2.imwrite(os.path.join(full_folder, image_name), image)
            

            source_dir = "./extensions/Abysz-Deflicker/scripts/Run/Source" # ruta de la carpeta "Source"
            
            # Obtener una lista de los nombres de archivo en la carpeta "Source"
            files = os.listdir(source_dir)
            
            # Renombrar cada archivo
            for i, file_name in enumerate(files):
                old_path = os.path.join(source_dir, file_name) # ruta actual del archivo
                new_file_name = f"{i+1:03d}" # nuevo nombre de archivo con formato %03d
                new_path = os.path.join(source_dir, new_file_name + os.path.splitext(file_name)[1]) # nueva ruta del archivo
                try:
                    os.rename(old_path, new_path)
                except FileExistsError:
                    print(f"El archivo {new_file_name} ya existe. Se omite su renombre.")
                
            gen_dir = "./extensions/Abysz-Deflicker/scripts/Run/Gen" # ruta de la carpeta "Source"
            
            # Obtener una lista de los nombres de archivo en la carpeta "Gen"
            files = os.listdir(gen_dir)
            
            # Renombrar cada archivo
            for i, file_name in enumerate(files):
                old_path = os.path.join(gen_dir, file_name) # ruta actual del archivo
                new_file_name = f"{i+1:03d}" # nuevo nombre de archivo con formato %03d
                new_path = os.path.join(gen_dir, new_file_name + os.path.splitext(file_name)[1]) # nueva ruta del archivo
                try:
                    os.rename(old_path, new_path)
                except FileExistsError:
                    print(f"El archivo {new_file_name} ya existe. Se omite su renombre.")

            # Obtener el primer archivo de la carpeta "Gen"
            gen_files = os.listdir("./extensions/Abysz-Deflicker/scripts/Run/Gen")
            if gen_files:
                first_gen_file = gen_files[0]

                # Copiar el archivo a la carpeta "Output" y reemplazar si ya existe
                output_file = "./extensions/Abysz-Deflicker/scripts/Run/Output/" + first_gen_file
                shutil.copyfile("./extensions/Abysz-Deflicker/scripts/Run/Gen/" + first_gen_file, output_file)
            
            #subprocess call
            
            # Definir la carpeta donde están los archivos
            carpeta = './extensions/Abysz-Deflicker/scripts/Run/Source/'
            
            # Crear la carpeta MaskD si no existe
            os.makedirs('./extensions/Abysz-Deflicker/scripts/Run/MaskD', exist_ok=True)
            
            # Inicializar contador
            contador = 1
            
            umbral_size = slider3
            # Iterar a través de los archivos de imagen en la carpeta Source
            for filename in sorted(os.listdir(carpeta)):
                # Cargar la imagen actual y la siguiente en escala de grises
                if contador > 1:
                    siguiente = cv2.imread(os.path.join(carpeta, filename), cv2.IMREAD_GRAYSCALE)
                    diff = cv2.absdiff(anterior, siguiente)
            
                    # Aplicar un umbral y guardar la imagen resultante en la carpeta MaskD. Menos es más.
                    umbral = umbral_size
                    umbralizado = cv2.threshold(diff, umbral, 255, cv2.THRESH_BINARY_INV)[1] # Invertir los colores
                    cv2.imwrite(os.path.join('./extensions/Abysz-Deflicker/scripts/Run/MaskD', f'{contador-1:03d}.png'), umbralizado)
            
                anterior = cv2.imread(os.path.join(carpeta, filename), cv2.IMREAD_GRAYSCALE)
                contador += 1
                
                #Actualmente, el tipo de umbralización es cv2.THRESH_BINARY_INV, que invierte los colores de la imagen umbralizada. 
                #Puedes cambiarlo a otro tipo de umbralización, 
                #como cv2.THRESH_BINARY, cv2.THRESH_TRUNC, cv2.THRESH_TOZERO o cv2.THRESH_TOZERO_INV.
            
            
            # Obtener la lista de los nombres de los archivos en la carpeta MaskD
            files = os.listdir("./extensions/Abysz-Deflicker/scripts/Run/MaskD")
            
            # Iterar sobre cada archivo
            for file in files:
              # Leer la imagen de la carpeta MaskD
              img = cv2.imread("./extensions/Abysz-Deflicker/scripts/Run/MaskD/" + file)
            
              # Invertir la imagen usando la función bitwise_not()
              img_inv = cv2.bitwise_not(img)
              
              kernel_size = slider4

              # Dilatar la imagen usando la función dilate()
              kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size)) # Puedes cambiar el tamaño y la forma del kernel según tus preferencias
              img_dil = cv2.dilate(img_inv, kernel)
            
              # Volver a invertir la imagen usando la función bitwise_not()
              img_out = cv2.bitwise_not(img_dil)
            
               # Sobrescribir la imagen en la carpeta MaskD con el mismo nombre que el original
              cv2.imwrite("./extensions/Abysz-Deflicker/scripts/Run/MaskD/" + file, img_out)
              
            # Definir la carpeta donde están los archivos
            carpeta = "./extensions/Abysz-Deflicker/scripts/Run/MaskD"
            blur_kernel = slider5
            # Iterar a través de los archivos de imagen en la carpeta MaskD
            for imagen in os.listdir(carpeta):
                if imagen.endswith(".jpg") or imagen.endswith(".png") or imagen.endswith(".jpeg"):
                    # Leer la imagen
                    img = cv2.imread(os.path.join(carpeta, imagen))
                    # Aplicar el filtro
                    img = cv2.GaussianBlur(img, (blur_kernel,blur_kernel),0)
                    # Guardar la imagen con el mismo nombre
                    cv2.imwrite(os.path.join(carpeta, imagen), img)
            
            
            # INICIO DEL BATCH Obtener el nombre del archivo en MaskD sin ninguna extensión
            # Agregar una variable de contador de bucles
            loop_count = 0
            
            # Agregar un bucle while para ejecutar el código en bucle infinito
            while True:
            
                mask_files = sorted(os.listdir(maskD))
                if not mask_files:
                    print(f"No se encontraron archivos en {maskD}")
                    exit(1)
                
                mask = mask_files[0]
                maskname = os.path.splitext(mask)[0]
                
                # Obtener la ruta de la imagen en la subcarpeta de output que tiene el mismo nombre que la imagen en MaskD
                output_files = [f for f in os.listdir(output) if os.path.splitext(f)[0] == maskname]
                if not output_files:
                    print(f"No se encontró en {output} una imagen con el mismo nombre que {maskname}.")
                    exit(1)
                
                output_file = os.path.join(output, output_files[0])
                
                # Aplicar el comando magick composite con las opciones deseadas
                composite_command = f"magick composite -compose CopyOpacity {os.path.join(maskD, mask)} {output_file} {os.path.join(maskS, 'result.png')}"
                os.system(composite_command)
                
                # Obtener el nombre del archivo en output sin ninguna extensión
                name = os.path.splitext(os.path.basename(output_file))[0]
                
                # Renombrar el archivo result.png con el nombre del archivo en output y la extensión .png
                os.rename(os.path.join(maskS, 'result.png'), os.path.join(maskS, f"{name}.png"))
                
                #Guardar el directorio actual en una variable
                original_dir = os.getcwd()
                
                #Cambiar al directorio de la carpeta MaskS
                os.chdir(maskS)
                
                #Iterar a través de los archivos de imagen en la carpeta MaskS
                for imagen in sorted(os.listdir(".")):
                    # Obtener el nombre de la imagen sin la extensión
                    nombre, extension = os.path.splitext(imagen)
                    # Obtener solo el número de la imagen
                    numero = ''.join(filter(str.isdigit, nombre))
                    # Definir el nombre de la siguiente imagen
                    siguiente = f"{int(numero)+1:0{len(numero)}}{extension}"
                    # Renombrar la imagen
                    os.rename(imagen, siguiente)
                
                # Volver al directorio original
                os.chdir(original_dir)
                
                # Establecer un valor predeterminado para disolución
                dissolve = 100 if loop_count % slider1 != 0 else slider2
                #slider2 = gr.inputs.Slider(minimum=0, maximum=100, default=50, step=5, label="FPR Strength")
            
            
                # Obtener el nombre del archivo en MaskS sin la extensión
                maskS_files = [f for f in os.listdir(maskS) if os.path.isfile(os.path.join(maskS, f)) and f.endswith('.png')]
                if maskS_files:
                    filename = os.path.splitext(maskS_files[0])[0]
                else:
                    print(f"No se encontraron archivos de imagen en la carpeta '{maskS}'")
                    filename = ''[0]
                
                # Salir del bucle si no hay más imágenes que procesar
                if not filename:
                    break
                
                # Obtener la extensión del archivo en Gen con el mismo nombre
                gen_files = [f for f in os.listdir(gen) if os.path.isfile(os.path.join(gen, f)) and f.startswith(filename)]
                if gen_files:
                    ext = os.path.splitext(gen_files[0])[1]
                else:
                    print(f"No se encontró ningún archivo con el nombre '{filename}' en la carpeta '{gen}'")
                    ext = ''
                
                input("Presione una tecla para continuar...")
                
                # Componer la imagen de MaskS y Gen con disolución (si está definido) y guardarla en la carpeta de salida
                os.system(f"magick composite {'-dissolve ' + str(dissolve) + '%' if dissolve is not None else ''} {maskS}/{filename}.png {gen}/{filename}{ext} {output}/{filename}{ext}")
                
                # Obtener el nombre del archivo más bajo en la carpeta MaskD
                maskd_files = [f for f in os.listdir(maskD) if os.path.isfile(os.path.join(maskD, f)) and f.startswith('')]
                if maskd_files:
                    maskd_file = os.path.join(maskD, sorted(maskd_files)[0])
                    os.remove(maskd_file)
                
                # Obtener el nombre del archivo más bajo en la carpeta MaskS
                masks_files = [f for f in os.listdir(maskS) if os.path.isfile(os.path.join(maskS, f)) and f.startswith('')]
                if masks_files:
                    masks_file = os.path.join(maskS, sorted(masks_files)[0])
                    os.remove(masks_file)
                
                input("Presione una tecla para continuar...")
                
                # Aumentar el contador de bucles
                loop_count += 1
                
                
                    
            # FIN DEL BATCH
            
            # Return a message indicating success or failure
            try:
                # Insert your processing code here
                return f"Processing completed successfully! Images saved to {output_folder}."
            except:
                return "Error occurred during processing. Please check the input folders and try again."
                
        render_button.click(fn=run_abysz_deflicker)
        
        return [source_folder, generated_folder, out_folder, slider1, slider2, slider3, slider4, slider5, render_button]

    def run(self, source_folder, generated_folder, out_folder, slider1, slider2, slider3, slider4, slider5, render_button):
        return None
