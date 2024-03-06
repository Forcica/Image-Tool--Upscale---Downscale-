import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
from functools import partial
from threading import Thread
from upscale_image_source.image_processing import ImageProcessor  # Import modifié

NUNITO_FONT = ("Nunito", 11)

class ImageToolApp:
   def __init__(self, master):
      self.master = master
      self.master.iconbitmap('D:/Code/Python/upscale_image/image-removebg-preview.ico')
      self.master.title("Outil d'Upscaling et de Réduction d'Images")
      self.master.geometry('1500x1200')

      self.apply_dark_theme()

      self.progress_label = ttk.Label(self.master, text="")
      self.progress_label.pack(fill=tk.X, padx=10, pady=5)

      self.selected_images = []
      self.image_previews = [] 
      self.create_new_version = tk.BooleanVar(value=False)
      self.upscale_value = tk.IntVar(value=2)
      self.scale_direction = tk.StringVar(value="Upscale")

      self.image_processor = ImageProcessor()

      self.create_widgets()
      self.setup_upscale_options()

   def apply_dark_theme(self):
      self.master.style = ttk.Style()
      self.master.style.theme_use("clam")
      self.master.style.configure('.', background='#333', foreground='white', font=NUNITO_FONT)
      self.master.style.configure('TFrame', background='#333')
      self.master.style.configure('TButton', background='#555', foreground='white', font=NUNITO_FONT, padding=(10, 5, 10, 5))

      self.master.style.configure('TLabel', background='#333', foreground='white', font=NUNITO_FONT)
      self.master.style.configure('TLabelFrame', background='#333', foreground='white', font=(NUNITO_FONT[0], 12, 'bold'))
      
      self.master.style.map('TButton', background=[('active', '#666666'), ('!disabled', 'black')], foreground=[('active', 'white'), ('!disabled', 'white')])

      self.master.style.configure('Hover.TButton', background='#555')
      self.master.style.configure('Black.TEntry', foreground='black')

   def on_enter(self, e):
      self.hover_id = self.master.after(100, lambda: e.widget.config(style='Hover.TButton'))

   def on_leave(self, e):
      if hasattr(self, 'hover_id'):
         self.master.after_cancel(self.hover_id)
      e.widget.config(style='TButton')

   def create_widgets(self):
      self.create_frame()
      self.create_image_selection_widgets()
      self.create_upscale_options()
      self.create_rename_images_widgets()

   def create_frame(self):
      padding = {'padx': 555, 'pady': 20}
      self.frame = ttk.Frame(self.master, padding="10")
      self.frame.pack(expand=True, fill=tk.BOTH)

   def create_image_selection_widgets(self):
      self.btn_select_images = ttk.Button(self.frame, text="[1] Sélectionner des Images", command=self.select_images, width=20)
      self.btn_select_images.pack(fill=tk.X, **padding)

      self.image_preview_frame = ttk.Frame(self.frame, height=300)
      self.image_preview_frame.pack(fill=tk.X, padx=5, pady=2)

      self.btn_remove_all_images = ttk.Button(self.frame, text="Supprimer toutes les images (Optionnel)", command=self.remove_all_images, width=20)
      self.btn_remove_all_images.pack(fill=tk.X, **padding)

      self.checkbutton_new_version = ttk.Checkbutton(
         self.frame, text="Créer une nouvelle version (Ne pas cocher l'option pour garder le nom d'origine)", variable=self.create_new_version, style=''
      )  
      self.checkbutton_new_version.pack(anchor='w', padx=5, pady=5)

   def create_upscale_options(self):
      upscale_frame = ttk.LabelFrame(self.frame, text="Options de redimensionnement :", padding="10")
      upscale_frame.pack(fill=tk.X, pady=10)

      ttk.Radiobutton(upscale_frame, text="Upscale (X2)", variable=self.scale_direction, value="Upscale").pack(side=tk.LEFT, padx=10)
      ttk.Radiobutton(upscale_frame, text="Downscale (/2)", variable=self.scale_direction, value="Downscale").pack(side=tk.LEFT, padx=10)

      padding = {'padx': 555, 'pady': 5}
      self.btn_scale_images = ttk.Button(self.frame, text="[2] Redimensionner les Images", command=self.scale_images_thread, width=20)
      self.btn_scale_images.pack(fill=tk.X, **padding)

   def create_rename_images_widgets(self):
      self.label_texture_name = ttk.Label(self.frame, text="(Optionnel) Entrez le nom initial pour renommer toutes les textures :")
      self.label_texture_name.pack(fill=tk.X, padx=5, pady=2)

      self.texture_name_entry = ttk.Entry(self.frame, style='Black.TEntry')
      self.texture_name_entry.pack(fill=tk.X, padx=5, pady=5)

      self.btn_rename_images = ttk.Button(self.frame, text="Renommer les Images (Optionnel)", command=self.rename_images_thread, width=20)
      self.btn_rename_images.pack(fill=tk.X, **padding)

   def select_images(self):
      file_paths = filedialog.askopenfilenames(
         title="Sélectionner des images", 
         filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
      )
      self.selected_images.extend(file_paths)
      self.display_image_previews()

   def remove_all_images(self):
      self.selected_images.clear()
      self.display_image_previews()

   def remove_image(self, index):
      try:
         del self.selected_images[index]
         self.display_image_previews()
      except IndexError:
         messagebox.showerror("Erreur", "Erreur lors de la suppression de l'image.")

   def display_image_previews(self):
      for widget in self.image_preview_frame.winfo_children():
         widget.destroy()
      self.image_previews.clear()

      num_columns = 11
      num_images = len(self.selected_images)
      num_rows = (num_images + num_columns - 1) // num_columns

      self.image_preview_frame.configure(height=num_rows * 150)

      for index, img_path in enumerate(self.selected_images):
         frame_row = index // num_columns
         frame_col = index % num_columns

         frame = ttk.Frame(self.image_preview_frame)
         frame.grid(row=frame_row, column=frame_col, padx=10, pady=5)

         try:
               img = Image.open(img_path)

               width, height = img.size

               img.thumbnail((123, 123))
               photo = ImageTk.PhotoImage(img)

               label = ttk.Label(frame, image=photo)
               label.image = photo
               label.pack(side=tk.TOP)

               size_label = ttk.Label(frame, text=f"{width}x{height}")
               size_label.pack(side=tk.TOP)

               btn_delete = ttk.Button(frame, text="✖", command=partial(self.remove_image, index))
               btn_delete.pack(side=tk.TOP)

               self.image_previews.append(photo)
         except Exception as e:
               messagebox.showerror("Erreur", f"Impossible de charger l'image : {e}")

   def scale_images_thread(self):
      Thread(target=self.scale_images, daemon=True).start()

   def scale_images(self):
      scale_factor = self.upscale_value.get()
      direction = self.scale_direction.get()

      total_images = len(self.selected_images)
      for index, img_path in enumerate(self.selected_images):
         self.image_processor.scale_image(img_path, scale_factor, direction)

         # Mise à jour de l'étiquette de progression avec le pourcentage
         percent_done = (index + 1) / total_images * 100
         self.progress_label['text'] = f"{percent_done:.2f}% accompli"

         self.master.update_idletasks()

      messagebox.showinfo("Succès", f"Images {'upscaled' if direction == 'Upscale' else 'downscaled'} avec succès.")
      self.display_image_previews()

   def rename_images_thread(self):
      Thread(target=self.rename_images).start()

   def rename_images(self):
      base_name = self.texture_name_entry.get()
      if not base_name:
         messagebox.showerror("Erreur", "Veuillez entrer un nom de base pour les images.")
         return

      total_images = len(self.selected_images)
      for index, img_path in enumerate(self.selected_images):
         new_name = f"{base_name}_{index}{os.path.splitext(img_path)[1]}"
         new_path = os.path.join(os.path.dirname(img_path), new_name)
         os.rename(img_path, new_path)
         self.selected_images[index] = new_path

         percent_done = (index + 1) / total_images * 100
         self.progress_label['text'] = f"{percent_done:.2f}% accompli"

         self.master.update_idletasks()

      messagebox.showinfo("Succès", "Images renommées avec succès.")
      self.display_image_previews()
