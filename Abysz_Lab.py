import gradio as gr
import subprocess
import os
import imageio
from gradio.outputs import Image
from PIL import Image
import sys
import cv2
import shutil
import time

def procesar_imagenes_gradio(ruta_entrada_1, ruta_entrada_2, ruta_salida, frames_limit, dfi_strength, frame_refresh_frequency, refresh_strength, smooth, dfi_deghost):
    # Definir las rutas de las carpetas
        maskD = os.path.basename('MaskD')
        maskS = os.path.basename('MaskS')
        output = os.path.basename(ruta_salida)
        source = os.path.basename('Source')
        #gen = os.path.basename(ruta_entrada_2)

        
        os.makedirs(source, exist_ok=True)
        os.makedirs(maskS, exist_ok=True)
        os.makedirs(output, exist_ok=True)
        os.makedirs(maskD, exist_ok=True)
        #os.makedirs(gen, exist_ok=True)
        
        # Copy the images from Ruta1 to Source folder in JPEG quality 100
        #for file in os.listdir(ruta_entrada_1):
        #    if file.endswith(".jpg") or file.endswith(".jpeg") or file.endswith(".png"):
        #        img = Image.open(os.path.join(ruta_entrada_1, file))
        #        img.save(os.path.join("Source", file), "jpeg", quality=100)
        def copy_images(ruta_entrada_1, ruta_entrada_2, frames_limit=0):
            # Copiar todas las imágenes de la carpeta ruta_entrada_1 a la carpeta Source
            count = 0
            for file in os.listdir(ruta_entrada_1):
                if file.endswith(".jpg") or file.endswith(".jpeg") or file.endswith(".png"):
                    img = Image.open(os.path.join(ruta_entrada_1, file))
                    img.save(os.path.join("Source", file), "jpeg", quality=100)
                    count += 1
                    if frames_limit > 0 and count >= frames_limit:
                        break
        
        # Llamar a la función copy_images para copiar las imágenes
        copy_images(ruta_entrada_1,ruta_salida, frames_limit)
        
        #for file in os.listdir(ruta_entrada_2):
        #    if file.endswith(".jpg") or file.endswith(".jpeg") or file.endswith(".png"):
        #        img = Image.open(os.path.join(ruta_entrada_2, file))
        #        img.save(os.path.join(ruta_entrada_2, file))
        #        
        # Carpeta donde se encuentran las imágenes de Gen
        gen_folder = ruta_entrada_2
        
        # Carpeta donde se encuentran las imágenes de FULL
        full_folder = "Source"
        
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
        

        source_dir = "Source" # ruta de la carpeta "Source"
        
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
            
        gen_dir = ruta_entrada_2 # ruta de la carpeta "Source"
        
        # Obtener una lista de los nombres de archivo en la carpeta ruta_entrada_2
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

        # Obtener el primer archivo de la carpeta ruta_entrada_2
        gen_files = os.listdir(ruta_entrada_2)
        if gen_files:
            first_gen_file = gen_files[0]

            # Copiar el archivo a la carpeta "Output" y reemplazar si ya existe
            #output_file = "Output" + first_gen_file
            #shutil.copyfile(ruta_entrada_2 + first_gen_file, output_file)
            output_file = os.path.join(ruta_salida, first_gen_file)
            shutil.copyfile(os.path.join(ruta_entrada_2, first_gen_file), output_file)
        #subprocess call
        
        # Definir la carpeta donde están los archivos
        carpeta = 'Source'
        
        # Crear la carpeta MaskD si no existe
        os.makedirs('MaskD', exist_ok=True)
        
        # Inicializar contador
        contador = 1
        
        umbral_size = dfi_strength
        # Iterar a través de los archivos de imagen en la carpeta Source
        for filename in sorted(os.listdir(carpeta)):
            # Cargar la imagen actual y la siguiente en escala de grises
            if contador > 1:
                siguiente = cv2.imread(os.path.join(carpeta, filename), cv2.IMREAD_GRAYSCALE)
                diff = cv2.absdiff(anterior, siguiente)
        
                # Aplicar un umbral y guardar la imagen resultante en la carpeta MaskD. Menos es más.
                umbral = umbral_size
                umbralizado = cv2.threshold(diff, umbral, 255, cv2.THRESH_BINARY_INV)[1] # Invertir los colores
                cv2.imwrite(os.path.join('MaskD', f'{contador-1:03d}.png'), umbralizado)
        
            anterior = cv2.imread(os.path.join(carpeta, filename), cv2.IMREAD_GRAYSCALE)
            contador += 1
            
            #Actualmente, el tipo de umbralización es cv2.THRESH_BINARY_INV, que invierte los colores de la imagen umbralizada. 
            #Puedes cambiarlo a otro tipo de umbralización, 
            #como cv2.THRESH_BINARY, cv2.THRESH_TRUNC, cv2.THRESH_TOZERO o cv2.THRESH_TOZERO_INV.
        
        
        # Obtener la lista de los nombres de los archivos en la carpeta MaskD
        files = os.listdir("MaskD")
        # Definir la carpeta donde están los archivos
        carpeta = "MaskD"
        blur_kernel = smooth
        
        # Iterar sobre cada archivo
        for file in files:
            if dfi_deghost == 0:
                
                continue
            # Leer la imagen de la carpeta MaskD
            #img = cv2.imread("MaskD" + file)
            img = cv2.imread(os.path.join("MaskD", file))
            
            # Invertir la imagen usando la función bitwise_not()
            img_inv = cv2.bitwise_not(img)
            
            kernel_size = dfi_deghost
            
            # Dilatar la imagen usando la función dilate()
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size)) # Puedes cambiar el tamaño y la forma del kernel según tus preferencias
            img_dil = cv2.dilate(img_inv, kernel)
            
            # Volver a invertir la imagen usando la función bitwise_not()
            img_out = cv2.bitwise_not(img_dil)
            
             # Sobrescribir la imagen en la carpeta MaskD con el mismo nombre que el original
            #cv2.imwrite("MaskD" + file, img_out)
            #cv2.imwrite(os.path.join("MaskD", file, img_out))
            filename = os.path.join("MaskD", file)
            cv2.imwrite(filename, img_out)
       
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
                print(f"No se encontraron archivos para componer")
                # Eliminar las carpetas Source, MaskS y MaskD si no hay más archivos para procesar
                shutil.rmtree(maskD)
                shutil.rmtree(maskS)
                shutil.rmtree(source)
                break
                
            mask = mask_files[0]
            maskname = os.path.splitext(mask)[0]
            
            # Obtener la ruta de la imagen en la subcarpeta de output que tiene el mismo nombre que la imagen en MaskD
            output_files = [f for f in os.listdir(ruta_salida) if os.path.splitext(f)[0] == maskname]
            if not output_files:
                print(f"No se encontró en {ruta_salida} una imagen con el mismo nombre que {maskname}.")
                exit(1)
            
            output_file = os.path.join(ruta_salida, output_files[0])
            
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
            dissolve = 100 if loop_count % frame_refresh_frequency != 0 else refresh_strength
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
            gen_files = [f for f in os.listdir(ruta_entrada_2) if os.path.isfile(os.path.join(ruta_entrada_2, f)) and f.startswith(filename)]
            if gen_files:
                ext = os.path.splitext(gen_files[0])[1]
            else:
                print(f"No se encontró ningún archivo con el nombre '{filename}' en la carpeta '{ruta_entrada_2}'")
                ext = ''
                                  
            # Componer la imagen de MaskS y Gen con disolución (si está definido) y guardarla en la carpeta de salida
            os.system(f"magick composite {'-dissolve ' + str(dissolve) + '%' if dissolve is not None else ''} {maskS}/{filename}.png {ruta_entrada_2}/{filename}{ext} {output}/{filename}{ext}")
            
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
                                
            # Aumentar el contador de bucles
            loop_count += 1
            
        #def show_gif():
        #    # Cargando el GIF
        #    with open("animation.gif", "rb") as f:
        #        gif = f.read()
        #    
        #    # Retornando el GIF como resultado
        #    return gif    

inputs = [
    gr.inputs.Textbox(label="Original frames folder", placeholder="Unless you have used --just resize-- with different aspect ratios, any source will work."),
    gr.inputs.Textbox(label="Generated frames folder", placeholder="The frames of you generated video"),
    gr.inputs.Textbox(label="Output folder", placeholder="Remember that each generation overwrites previous frames in the same folder."),
    gr.inputs.Number(label="Frames to render. 0:ALL")
]

sliders = [
    gr.Slider(minimum=1, maximum=10, value=5, step=0.5, label="DFI Strength"),
    gr.Slider(minimum=1, maximum=30, value=5, step=1, label="Frame Refresh Frequency"),
    gr.Slider(minimum=0, maximum=100, value=50, step=5, label="Refresh Strength 0=MAX 100=OFF"),
    gr.Slider(minimum=1, maximum=99, value=25, step=2, label="Smooth"),
    gr.Slider(minimum=0, maximum=10, value=4, step=1, label="DFI Deghost")
]

output_placeholder = gr.outputs.Textbox(label="Status")

# Agregando el componente gr.outputs.Image a la lista de salidas
#outputs = [output_placeholder, gr.outputs.Image(label="GIF")]

gr.Interface(fn=procesar_imagenes_gradio,
             inputs=inputs+sliders,
             outputs=output_placeholder,
             title="Abysz Lab 0.0.2",
             description=" Full instructions: https://github.com/AbyszOne/Abysz_lab. Temporal coherence lab, version alpha 0.0.2. Updates incoming: Polar render (Front/back), Lumen deflicker, Mixed deflicker, visual references, and much more.").launch()
#outputs = [
#    gr.outputs.Image
#]
#gr.Interface(fn=procesar_imagenes_gradio, inputs=inputs+sliders, interpretation="Ejecutar").launch()
#gr.Interface(fn=procesar_imagenes_gradio, inputs=inputs+sliders, outputs=outputs, interpretation="Ejecutar").launch()
