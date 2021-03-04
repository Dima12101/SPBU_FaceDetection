from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown 
from kivy.graphics import Color, Rectangle, Line

import cv2
import imageio
import os

from src.ui.configs import DATA_DIR, ALL_DATABASES
from src.ui.base import ImgWidget, ImgBox
from src.core.viola_jones import detected


class SourceImgWidget(ImgWidget):
    def __init__(self, **kwargs):
        super(SourceImgWidget, self).__init__(**kwargs)
        self.faces = []

    def clear(self):
        for face in self.faces:
            self.canvas.remove(face)
        self.faces = []

    def set_face(self, x, y, w, h):
        with self.canvas:
            Color(0, 1, 0, .5)
            self.faces.append(Line(rectangle = (x, y, w, h), width = 4))

class MainBox(BoxLayout):

    def __init__(self, **kwargs):
        super(MainBox, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.spacing = 20

        database = 'ORL'

        with self.canvas:
            Color(.2, .3, .5, 1)
            self.bg = Rectangle(source = os.path.join(DATA_DIR, 'bg.jpg'), pos = self.pos, size = self.size)
            self.bind(pos = self.update_bg, size = self.update_bg)

        ''' ================ Source Img BOX ================ '''
        self.source = ImgBox(ImgWidget=SourceImgWidget, database=database)
        self.source.title.text = "'Source' изображение"

        ''' ================ Tool BOX ================ '''
        self.tools_box = BoxLayout(orientation='vertical', size_hint=(.8, .92), spacing = 550)

        # List of databases
        dropdown_databaces = DropDown()
        for method in ALL_DATABASES: 
            btn = Button(
                text = method, on_press=lambda instance: self.source.update_database(instance.text),
                size_hint_y = None, height = 30, 
                background_color = (.6, .9, 1, .5)) 
            btn.bind(on_release = lambda btn: dropdown_databaces.select(btn.text)) 
            dropdown_databaces.add_widget(btn) 
        self.list_databaces = Button(text ='Базы лиц', size_hint=(1, 0.05), background_color = (.6, .9, 1, 1))
        self.list_databaces.bind(on_release = dropdown_databaces.open)
        dropdown_databaces.bind(on_select = lambda instance, x: setattr(self.list_databaces, 'text', x))

        # Run alg
        self.bth_run_alg = Button(text='ДЕТЕКЦИЯ', on_press=self.run_alg,
            background_normal = os.path.join(DATA_DIR, 'normal.png'), 
            background_down = os.path.join(DATA_DIR, 'down.png'),
            border = (30, 30, 30, 30),                    
            size_hint = (1, 0.1))

        self.tools_box.add_widget(self.list_databaces)
        self.tools_box.add_widget(self.bth_run_alg)

        self.add_widget(self.source)
        self.add_widget(self.tools_box)

    def update_bg(self, *args): 
        self.bg.pos = self.pos ; self.bg.size = self.size

    def _get_face_percentage(self, source_img, face):
        '''Get percentage detection face on source img'''
        # Get size of source img
        h_s, w_s = source_img.shape
        x_f, y_f, w_f, h_f = face

        # Count percentage part of match on source img
        left = x_f / w_s
        rigth = (w_s - (x_f + w_f)) / w_s
        bottom = (h_s - (y_f + h_f)) / h_s
        top = y_f / h_s
        
        return left, rigth, bottom, top

    def run_alg(self, instance):
        self.source.img.clear()
        
        ''' ============== INPUT ============== '''
        # Load orig images
        if self.source.database == 'ORL':
            source_img = cv2.imread(self.source.img_path, -1)
        else:
            source_img = imageio.imread(self.source.img_path)

        ''' ============== RUN detection ============== '''
        faces = detected(source_img)

        ''' ============== OUTPUT ============== '''
        for face in faces:
            # Get percentage part of match
            left_face, rigth_face, bottom_face, top_face = self._get_face_percentage(source_img, face)

            # Set face on source img
            x_s, y_s = self.source.img.rect.pos
            w_s, h_s = self.source.img.rect.size
            x_face = x_s + w_s * left_face
            y_face = y_s + h_s * bottom_face
            w_face = w_s - w_s * rigth_face - w_s * left_face
            h_face = h_s - h_s * top_face - h_s * bottom_face
            self.source.img.set_face(x_face, y_face, w_face, h_face)
