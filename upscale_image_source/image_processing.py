from PIL import Image
import os

class ImageProcessor:
   def __init__(self):
      pass

   def scale_image(self, img_path, scale_factor, direction):
      img = Image.open(img_path)
      if direction == "Upscale":
         new_size = (img.width * scale_factor, img.height * scale_factor)
         resized_img = img.resize(new_size, resample=Image.BICUBIC)
      else:  # Downscale
         new_size = (img.width // scale_factor, img.height // scale_factor)
         resized_img = img.resize(new_size, resample=Image.LANCZOS)  # Utiliser LANCZOS pour le downscale

      if self.create_new_version.get():
         base, ext = os.path.splitext(img_path)
         new_img_path = f"{base}_{'upscaled' if direction == 'Upscale' else 'downscaled'}{ext}"
      else:
         new_img_path = img_path

      resized_img.save(new_img_path)

      return new_img_path
