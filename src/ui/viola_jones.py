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
        self.detections = []

    def clear(self):
        for detection in self.detections:
            self.canvas.remove(detection)
        self.detections = []

    def set_detection(self, x, y, w, h):
        with self.canvas:
            Color(0, 1, 0, .5)
            self.detections.append(Line(rectangle = (x, y, w, h), width = 4))

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

    def _get_detection_percentage(self, source_img, detection):
        '''Get percentage detection on source img'''
        # Get size of source img
        h_s, w_s = source_img.shape
        x_f, y_f, w_f, h_f = detection

        # Count percentage part of detection on source img
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
        detections = detected(source_img)

        ''' ============== OUTPUT ============== '''
        for detection in detections:
            # Get percentage part of match
            left_d, rigth_d, bottom_d, top_d = self._get_detection_percentage(source_img, detection)

            # Set detection on source img
            x_s, y_s = self.source.img.rect.pos
            w_s, h_s = self.source.img.rect.size
            x_d = x_s + w_s * left_d
            y_d = y_s + h_s * bottom_d
            w_d = w_s - w_s * rigth_d - w_s * left_d
            h_d = h_s - h_s * top_d - h_s * bottom_d
            self.source.img.set_detection(x_d, y_d, w_d, h_d)
