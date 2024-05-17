import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.graphics.texture import Texture
from PIL import Image as PILImage
import numpy as np
import cv2

from plyer import filechooser, notification


class HistogramEqualizationApp(App):
    def build(self):
        # UI Layout
        layout = BoxLayout(orientation='vertical', spacing=10)

        # Button Layout for User Guidelines and About Us buttons
        top_button_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=60)
        user_guidelines_button = Button(text='User Guidelines', size_hint=(1, None), height=60)
        clear_button = Button(text='Clear', size_hint=(1, None), height=60)
        about_us_button = Button(text='About Us', size_hint=(1, None), height=60)

        top_button_layout.add_widget(user_guidelines_button)
        top_button_layout.add_widget(clear_button)
        top_button_layout.add_widget(about_us_button)

        layout.add_widget(top_button_layout)

        # Image Layout
        image_layout = BoxLayout(orientation='vertical')

        self.original_image_widget = Image()
        self.original_label = Label(text='Original Image', size_hint=(1, None), height=40)

        original_layout = BoxLayout(orientation='vertical')
        original_layout.add_widget(self.original_image_widget)
        original_layout.add_widget(self.original_label)

        self.eroded_image_widget = Image()
        self.eroded_label = Label(text='Result Image', size_hint=(1, None), height=40)

        eroded_layout = BoxLayout(orientation='vertical')
        eroded_layout.add_widget(self.eroded_image_widget)
        eroded_layout.add_widget(self.eroded_label)

        image_layout.add_widget(original_layout)
        image_layout.add_widget(eroded_layout)

        layout.add_widget(image_layout)

        # Button Layout for Open Image, Apply Erosion, and Save Image buttons
        bottom_button_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=60)
        bottom_button_layout.add_widget(Button(text='Open Image', on_release=self._open_image))
        bottom_button_layout.add_widget(Button(text='Equalize Histogram', on_release=self._apply_equalization))
        bottom_button_layout.add_widget(Button(text='Save Image', on_release=self._save_image))
        clear_button.bind(on_release=self.clear_images)
        user_guidelines_button.bind(on_release=self.show_user_guidelines)
        about_us_button.bind(on_release=self.show_aboutus)
        layout.add_widget(bottom_button_layout)

        return layout

    def show_user_guidelines(self, instance):
        content_layout = BoxLayout(orientation='vertical', spacing=5, size_hint=(1, None))
        content_scrollview = ScrollView(size_hint=(1, None), size=(Window.width, Window.height * 0.27))
        content_layout.add_widget(content_scrollview)

        user_guidelines = """\
        1. "Open Image" button helps to select an image from your device.
        2. After the desired image is selected, it will be displayed below.
        3. "Equalize Histogram" button helps to convert the original image to a 
            new output by applying the Equalization Histogram technique.
        4. The new output image will be shown below.
        5. "Save Image" button will save the output image to your local directory.
        6. "Clear" button helps users to clear the currently chosen image and 
            Equalize Histogram image for the purpose of selecting a new image."""
        user_guidelines_label = Label(text=user_guidelines, size_hint=(1, None), halign='center', valign='center')
        user_guidelines_label.bind(texture_size=user_guidelines_label.setter('size'))
        user_guidelines_label.text_size = (Window.width * 0.9, None)
        user_guidelines_label.height = user_guidelines_label.texture_size[1]
        content_layout.height = user_guidelines_label.texture_size[1]
        content_scrollview.add_widget(user_guidelines_label)

        popup = Popup(title='User Guidelines', content=content_layout, size_hint=(None, None),
                      size=(Window.width * 0.9, Window.height * 0.4))
        popup.open()

    def show_aboutus(self, instance):
        content_layout = BoxLayout(orientation='vertical', spacing=5, size_hint=(1, None))
        content_scrollview = ScrollView(size_hint=(1, None), size=(Window.width, Window.height * 0.45))
        content_layout.add_widget(content_scrollview)

        aboutus = """\
     "Welcome to our Morphological Image Processing App! We're passionate about unleashing 
     the power of advanced algorithms to transform your photos into stunning works of art. 
     With our app, you can explore the fascinating world of morphological image processing, 
     a technique that enhances and manipulates images in unique and creative ways.

     "Our Morphological Image Processing App is the brainchild of a talented team of 
     developers and designers who are passionate about pushing the boundaries of digital
     imaging. Developed by Muhammad Amirul Aiman Bin Abdul Aziz and Leong Chee Sum, students
     of UTHM has worked tirelessly to bring you a powerful and user-friendly tool for 
     morphological image processing. We are excited to share our Morphological Image Processing 
     App with you and invite you to join our community of passionate visual explorers. 
     Together, let's unleash the power of morphological image processing and transform 
     the way we perceive and interact with images." """
        aboutus_label = Label(text=aboutus, size_hint=(1, None), halign='center', valign='center')
        aboutus_label.bind(texture_size=aboutus_label.setter('size'))
        aboutus_label.text_size = (Window.width * 0.9, None)
        aboutus_label.height = aboutus_label.texture_size[1]
        content_layout.height = aboutus_label.texture_size[1]
        content_scrollview.add_widget(aboutus_label)

        popup = Popup(title='User Guidelines', content=content_layout, size_hint=(None, None),
                      size=(Window.width * 0.9, Window.height * 0.6))
        popup.open()

    def _open_image(self, instance):
        filechooser.open_file(on_selection=self._on_file_select)

    def _on_file_select(self, selection):
        if len(selection) > 0:
            self.image_path = selection[0]
            self._update_image()

    def _update_image(self):
        self.original_image_widget.source = self.image_path
        self.original_image_widget.reload()

        self.eroded_image_widget.source = ''
        self.eroded_image_widget.reload()

    def clear_images(self, instance):
        self.original_image_widget.source = ''
        self.original_image_widget.reload()
        self.eroded_image_widget.source = ''
        self.eroded_image_widget.reload()

    def _apply_equalization(self, instance):
        if not hasattr(self, 'image_path') or self.image_path is None:
            self._show_error_popup("No image selected.")
            return

        try:
            # Open the image with OpenCV
            img = cv2.imread(self.image_path, 0)
            
            # Apply histogram equalization
            equalized_img = cv2.equalizeHist(img)

            # Flip the image vertically (180 degrees)
            equalized_img = cv2.flip(equalized_img, 0)

            # Convert the equalized image to PIL format
            pil_image_equalized = PILImage.fromarray(equalized_img)
            # Convert the PIL image to Kivy texture
            texture_equalized = Texture.create(size=pil_image_equalized.size)
            texture_equalized.blit_buffer(pil_image_equalized.tobytes(), colorfmt='luminance', bufferfmt='ubyte')
            # Assign the texture to the equalized image widget
            self.eroded_image_widget.texture = texture_equalized

        except Exception as e:
            self._show_error_popup(f"Error applying histogram equalization: {str(e)}")

    def _save_image(self, instance):
        if not hasattr(self, 'image_path') or self.image_path is None:
            self._show_error_popup("No image selected.")
            return

        try:
            # Get the directory and filename from the selected image path
            directory, filename = os.path.split(self.image_path)
            # Generate the new filename for the eroded image
            new_filename = f"eroded_{filename}"
            # Get the file extension
            _, file_extension = os.path.splitext(filename)
            # Generate the new image path for the eroded image
            new_image_path = os.path.join(directory, new_filename)

            # Save the eroded image texture
            self.eroded_image_widget.texture.save(new_image_path)

            self._show_info_popup("Image saved successfully.")
        except Exception as e:
            self._show_error_popup(f"Error saving image: {str(e)}")

    def _show_error_popup(self, message):
        content = BoxLayout(orientation='vertical', padding=10)
        content.add_widget(Label(text=message))
        popup = Popup(title='Error', content=content, size_hint=(None, None), size=(400, 200))
        popup.open()

    def _show_info_popup(self, message):
        content = BoxLayout(orientation='vertical', padding=10)
        content.add_widget(Label(text=message))
        popup = Popup(title='Information', content=content, size_hint=(None, None), size=(400, 200))
        popup.open()


if __name__ == '__main__':
    HistogramEqualizationApp().run()
