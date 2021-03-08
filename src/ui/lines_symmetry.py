from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown 
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle, Line

import cv2
import imageio
import os

from src.ui.configs import DATA_DIR, ALL_DATABASES, ALL_LS_METHODS
from src.ui.base import ImgWidget, ImgBox
from src.core.lines_symmetry import search_lines


class SourceImgWidget(ImgWidget):
    def __init__(self, **kwargs):
        super(SourceImgWidget, self).__init__(**kwargs)
        self.lines = []

    def clear(self):
        for line in self.lines:
            self.canvas.remove(line)
        self.lines = []

    def set_line(self, x1, y1, x2, y2, color=(0, 1, 0, .5), width=4):
        with self.canvas:
            Color(*color)
            self.lines.append(Line(points = (x1, y1, x2, y2), width = width))

class MainBox(BoxLayout):

    def __init__(self, **kwargs):
        super(MainBox, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.spacing = 20

        self.method = 'express'
        default_database = 'ORL'

        with self.canvas:
            Color(.2, .3, .5, 1)
            self.bg = Rectangle(source = os.path.join(DATA_DIR, 'bg.jpg'), pos = self.pos, size = self.size)
            self.bind(pos = self.update_bg, size = self.update_bg)

        ''' ================ Source Img BOX ================ '''
        self.source = ImgBox(ImgWidget=SourceImgWidget, database=default_database)
        self.source.title.text = "'Source' изображение"

        ''' ================ Tool BOX ================ '''
        self.tools_box = BoxLayout(orientation='vertical', size_hint=(.8, .92), spacing = 250)

        # List of databases
        dropdown_databaces = DropDown()
        for database in ALL_DATABASES: 
            btn = Button(
                text = database, on_press=lambda instance: self.source.update_database(instance.text),
                size_hint_y = None, height = 30, 
                background_color = (.6, .9, 1, .5)) 
            btn.bind(on_release = lambda btn: dropdown_databaces.select(btn.text)) 
            dropdown_databaces.add_widget(btn) 
        self.list_databaces = Button(text ='База лиц', size_hint=(1, .1), background_color = (.6, .9, 1, 1))
        self.list_databaces.bind(on_release = dropdown_databaces.open)
        dropdown_databaces.bind(on_select = lambda instance, x: setattr(self.list_databaces, 'text', x))

        self.box_methods = BoxLayout(orientation='horizontal', size_hint=(1, .1), spacing = 10)
        # List of methods
        dropdown_methods = DropDown()
        for method in ALL_LS_METHODS: 
            btn = Button(
                text = method, on_press=self.set_method, 
                size_hint_y = None, height = 30, 
                background_color = (.6, .9, 1, .5)) 
            btn.bind(on_release = lambda btn: dropdown_methods.select(btn.text)) 
            dropdown_methods.add_widget(btn) 
        list_methods = Button(text ='Методы', size_hint=(.9, 1), background_color = (.6, .9, 1, 1))
        list_methods.bind(on_release = dropdown_methods.open)
        dropdown_methods.bind(on_select = lambda instance, x: setattr(list_methods, 'text', x))

        self.method_window_size = TextInput(text='10', disabled=True,
            size_hint=(.1, .6), pos_hint={"center_y":.5},
            multiline=False, input_type='number', input_filter='int')

        self.box_methods.add_widget(list_methods)
        self.box_methods.add_widget(self.method_window_size)

        # Run alg
        self.bth_run_alg = Button(text='ПОИСК', on_press=self.run_alg,
            background_normal = os.path.join(DATA_DIR, 'normal.png'), 
            background_down = os.path.join(DATA_DIR, 'down.png'),
            border = (30, 30, 30, 30),                    
            size_hint = (1, 0.2))

        self.tools_box.add_widget(self.list_databaces)
        self.tools_box.add_widget(self.box_methods)
        self.tools_box.add_widget(self.bth_run_alg)

        self.add_widget(self.source)
        self.add_widget(self.tools_box)

    def update_bg(self, *args): 
        self.bg.pos = self.pos ; self.bg.size = self.size

    def set_method(self, instance):
        self.method = instance.text
        if self.method == 'window': self.method_window_size.disabled = False
        else: self.method_window_size.disabled = True

    def _get_line_percentage(self, source_img, line):
        '''Get percentage line on source img'''
        # Get size of source img
        h_s, w_s = source_img.shape
        p1, p2 = line
        
        left_p1 = p1[0] / w_s ; top_p1 = (h_s-p1[1]) / h_s
        left_p2 = p2[0] / w_s ; top_p2 = (h_s-p2[1]) / h_s
        
        return left_p1, top_p1, left_p2, top_p2

    def _get_line_on_source(self, source_img, line):
        # Get percentage part of line
        left_p1, top_p1, left_p2, top_p2 = self._get_line_percentage(source_img, line)

        # Set line on source img
        x_s, y_s = self.source.img.rect.pos
        w_s, h_s = self.source.img.rect.size
        x_p1 = x_s + w_s * left_p1
        y_p1 = y_s + h_s * top_p1
        x_p2 = x_s + w_s * left_p2
        y_p2 = y_s + h_s * top_p2

        return x_p1, y_p1, x_p2, y_p2


    def run_alg(self, instance):
        self.source.img.clear()
        params = {}
        if self.method == 'window':
            win_size = int(self.method_window_size.text)
            if win_size <= 0: return
            params['win_size'] = win_size
        
        ''' ============== INPUT ============== '''
        # Load orig images
        if self.source.database == 'ORL':
            source_img = cv2.imread(self.source.img_path, -1)
        else:
            source_img = imageio.imread(self.source.img_path)

        ''' ============== RUN detection ============== '''
        lines = search_lines(source_img, self.method, **params)
        if lines is None: return
        *lines, centers = lines

        ''' ============== OUTPUT ============== '''
        for line in lines:
            self.source.img.set_line(*self._get_line_on_source(source_img, line))

        # Additional information
        x1_c, y1_c, x2_c, y2_c = self._get_line_on_source(source_img, centers)
        self.source.img.set_line(x1_c, y1_c, x2_c, y2_c, color=(.8, .4, .0, .5), width=2)
        s=10
        self.source.img.set_line(x1_c-s, y1_c, x1_c+s, y1_c, color=(.8, .4, .0, 1), width=3)
        self.source.img.set_line(x1_c, y1_c-s, x1_c, y1_c+s, color=(.8, .4, .0, 1), width=3)
        self.source.img.set_line(x2_c-s, y2_c, x2_c+s, y2_c, color=(.8, .4, .0, 1), width=3)
        self.source.img.set_line(x2_c, y2_c-s, x2_c, y2_c+s, color=(.8, .4, .0, 1), width=3)
