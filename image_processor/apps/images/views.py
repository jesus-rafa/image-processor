import os
import extcolors
from PIL import Image
from rembg import remove
from dotenv import load_dotenv
from supabase import create_client, Client
from django.conf import settings
from rest_framework.response import Response
from rest_framework import generics, status

load_dotenv()

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

class Remove_Background(generics.GenericAPIView):

    def get(self, request, *args, **kwargs):
        url: str = os.getenv('SUPABASE_URL')
        key: str = os.getenv('SUPABASE_KEY')

        try:
            supabase: Client = create_client(url, key)
        except Exception as e:
            status_resp = 'error'
            code = status.HTTP_404_NOT_FOUND
            message = str(e)
            data = False

        image_url = self.kwargs['image_url'].replace('*', '/')
        bucket = self.kwargs['bucket']

        # image_url = UserId / TeamId / ImageId
        image_id = image_url.split('/')[-1]

        folder = bucket
        folder_bg = bucket + '-bg'

        if not os.path.exists(os.path.join(settings.MEDIA_ROOT,folder)):
            os.makedirs(os.path.join(settings.MEDIA_ROOT,folder))
        if not os.path.exists(os.path.join(settings.MEDIA_ROOT,folder_bg)):
            os.makedirs(os.path.join(settings.MEDIA_ROOT,folder_bg))

        path_input = os.path.join(settings.MEDIA_ROOT, folder +  '/' + image_id + '.png')
        path_output = os.path.join(settings.MEDIA_ROOT, folder_bg + '/' + image_id+ '.png')

        try:
            # Descargar imagen actual del bucket
            with open(path_input, 'wb+') as file_name:
                response = supabase.storage.from_('/public/' + bucket).download(image_url)
                file_name.write(response)

            # Tamaña Maximo 5MB
            image_size = os.path.getsize(path_input)
            if image_size > MAX_FILE_SIZE:
                status_resp = 'error'
                code = status.HTTP_404_NOT_FOUND
                message = 'Imagen mayor a 5MB' 
                data = False
                return

            try:
                # Quitar fondo a la imagen
                image = Image.open(path_input)
                fixed = remove(image)    
                fixed.save(path_output, format="PNG")
                
            except Exception as e:
                status_resp = 'error'
                code = status.HTTP_404_NOT_FOUND
                message = str(e)
                data = False
                
            # Borrar imagen del bucket
            supabase.storage.from_(bucket).remove(image_url)

            # Actualizar imagen sin fondo en el bucket
            with open(path_output, 'rb') as file_name:
                supabase.storage.from_(bucket).upload(
                    path=image_url,
                    file=file_name,
                    file_options={"content-type": "image/png"}
                )

            # Borrar imagenes de la api
            os.remove(path_input)
            os.remove(path_output)

            # Generar Response
            status_resp = 'success'
            code = status.HTTP_200_OK
            message = 'Imagen procesada correctamente!'
            data = True

        except Exception as e:
            status_resp = 'error'
            code = status.HTTP_404_NOT_FOUND
            message = str(e)
            data = False

        return Response({
            'status': status_resp,
            'code': code,
            'message': message,
            'data': data
        })
    

class Extract_Colors(generics.GenericAPIView):

    def get(self, request, *args, **kwargs):
        url: str = os.getenv('SUPABASE_URL')
        key: str = os.getenv('SUPABASE_KEY')

        try:
            supabase: Client = create_client(url, key)
        except Exception as e:
            status_resp = 'error'
            code = status.HTTP_404_NOT_FOUND
            message = str(e)
            data = False

        image_url = self.kwargs['image_url'].replace('*', '/')
        bucket = self.kwargs['bucket']

        # image_url = UserId / TeamId / ImageId
        image_id = image_url.split('/')[-1]
        folder = bucket

        if not os.path.exists(os.path.join(settings.MEDIA_ROOT,folder)):
            os.makedirs(os.path.join(settings.MEDIA_ROOT,folder))

        path_input = os.path.join(settings.MEDIA_ROOT, folder +  '/' + image_id + '.png')

        try:
            with open(path_input, 'wb+') as file_name:
                response = supabase.storage.from_('/public/' + bucket).download(image_url)
                file_name.write(response)

            # Tamaña Maximo 5MB
            image_size = os.path.getsize(path_input)
            if image_size > MAX_FILE_SIZE:
                status_resp = 'error'
                code = status.HTTP_404_NOT_FOUND
                message = 'Imagen mayor a 5MB' 
                data = []
                return

            colors, pixel_count = extcolors.extract_from_path(path_input)
            colors_rgba = []

            for color_rgb, value in colors:
                # Excluimos el color blanco y negro
                if color_rgb != (0, 0, 0) and color_rgb != (255, 255, 255):
                    rgba_string = f'rgba({color_rgb[0]}, {color_rgb[1]}, {color_rgb[2]}, 0.8)'
                    colors_rgba.append(rgba_string)

            # Borrar imagenes de la api
            os.remove(path_input)

            # Generar Response
            status_resp = 'success'
            code = status.HTTP_200_OK
            message = 'Imagen procesada correctamente!'
             # Retornar el color predominante
            data = colors_rgba[0]
        
        except Exception as e:
            status_resp = 'error'
            code = status.HTTP_404_NOT_FOUND
            message = str(e)
            data = []

        return Response({
            'status': status_resp,
            'code': code,
            'message': message,
            'data': data
        })