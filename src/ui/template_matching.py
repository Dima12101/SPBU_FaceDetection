from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown 
from kivy.graphics import Color, Rectangle, Line

import cv2
import imageio
import os
from collections import namedtuple

from src.ui.configs import DATA_DIR, ALL_METHODS, ALL_DATABASES
from src.ui.base import ImgWidget, ImgBox
from src.core.template_matching import detected


RectParams = namedtuple('Rectangle' , 'x y w h')


class TemplateImgWidget(ImgWidget):
    def __init__(self, **kwargs):
        super(TemplateImgWidget, self).__init__(**kwargs)
        self.area_obj = None
        self.area_params = None

    def on_touch_down(self, touch):
        with self.canvas:
            if self.collide_point(*touch.pos):
                self.area_params = RectParams(x=touch.x, y=touch.y, w=0, h=0)
                if self.area_obj is None:
                    Color(1, 0, 0, .5)
                    self.area_obj = Line(rectangle = self.area_params, width = 4)
                else:
                    self.area_obj.rectangle = self.area_params

    def on_touch_move(self, touch):
        with self.canvas:
            if self.collide_point(*touch.pos):
                if self.area_obj is not None:
                    self.area_params = RectParams(
                        x = self.area_params.x, y = self.area_params.y,
                        w = touch.x - self.area_params.x, h = touch.y - self.area_params.y)
                    self.area_obj.rectangle = self.area_params

    def get_points_area(self):
        '''Get control points of rectangle
        
        (x,y) -------          ------- point (right-top) 
              |     |          |     |
              |     | -h  =>   |     |
              |     |          |     |
              -------          -------
                 w         point (left-bottom)
        '''
        x, y, w, h = self.area_params

        if w >= 0 and h >= 0: left_bottom = (x, y) ; right_top = (x + w, y + h)
        if w >= 0 and h < 0: left_bottom = (x, y + h) ; right_top = (x + w, y)
        if w < 0 and h >= 0: left_bottom = (x + w, y) ; right_top = (x, y + h)
        if w < 0 and h < 0: left_bottom = (x + w, y + h) ; right_top = (x, y)

        return left_bottom, right_top


class SourceImgWidget(ImgWidget):
    def __init__(self, **kwargs):
        super(SourceImgWidget, self).__init__(**kwargs)
        self.match_obj = None

    def set_match(self, x, y, w, h):
        with self.canvas:
            if self.match_obj is None:
                Color(0, 1, 0, .5)
                self.match_obj = Line(rectangle = (x, y, w, h), width = 4)
            else:
                self.match_obj.rectangle = (x, y, w, h)

    def clear(self):
        if self.match_obj is not None:
            self.canvas.remove(self.match_obj) ; self.match_obj = None


class MainBox(BoxLayout):

    def __init__(self, **kwargs):
        super(MainBox, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.spacing = 20

        self.method = 'TM_CCOEFF'
        database = 'ORL'

        with self.canvas:
            Color(.2, .3, .5, 1)
            self.bg = Rectangle(source = os.path.join(DATA_DIR, 'bg.jpg'), pos = self.pos, size = self.size)
            self.bind(pos = self.update_bg, size = self.update_bg)

        ''' ================ Template Img BOX ================ '''
        self.template = ImgBox(ImgWidget=TemplateImgWidget, database=database)
        self.template.title.text = "'Template' изображение"

        ''' ================ Tool BOX ================ '''
        self.tools_box = BoxLayout(orientation='vertical', size_hint=(.25, .92), spacing = 250)

        # List of databases
        dropdown_databaces = DropDown()
        for method in ALL_DATABASES: 
            btn = Button(
                text = method, on_press=self.update_database,
                size_hint_y = None, height = 30, 
                background_color = (.6, .9, 1, .5)) 
            btn.bind(on_release = lambda btn: dropdown_databaces.select(btn.text)) 
            dropdown_databaces.add_widget(btn) 
        self.list_databaces = Button(text ='Базы лиц', size_hint=(1, .1), background_color = (.6, .9, 1, 1))
        self.list_databaces.bind(on_release = dropdown_databaces.open)
        dropdown_databaces.bind(on_select = lambda instance, x: setattr(self.list_databaces, 'text', x))

        # List of methods
        dropdown_methods = DropDown()
        for method in ALL_METHODS: 
            btn = Button(
                text = method, on_press=lambda instance: setattr(self, 'method', instance.text), 
                size_hint_y = None, height = 30, 
                background_color = (.6, .9, 1, .5)) 
            btn.bind(on_release = lambda btn: dropdown_methods.select(btn.text)) 
            dropdown_methods.add_widget(btn) 
        self.list_methods = Button(text ='Методы', size_hint=(1, .1), background_color = (.6, .9, 1, 1))
        self.list_methods.bind(on_release = dropdown_methods.open)
        dropdown_methods.bind(on_select = lambda instance, x: setattr(self.list_methods, 'text', x))

        # Run alg
        self.bth_run_alg = Button(text='ДЕТЕКЦИЯ', on_press=self.run_alg,
            background_normal = os.path.join(DATA_DIR, 'normal.png'), 
            background_down = os.path.join(DATA_DIR, 'down.png'),
            border = (30, 30, 30, 30),                    
            size_hint = (1, 0.2))

        self.tools_box.add_widget(self.list_databaces)
        self.tools_box.add_widget(self.list_methods)
        self.tools_box.add_widget(self.bth_run_alg)

        ''' ================ Source Img BOX ================ '''
        self.source = ImgBox(ImgWidget=SourceImgWidget, database=database)
        self.source.title.text = "'Source' изображение"

        self.add_widget(self.template)
        self.add_widget(self.tools_box)
        self.add_widget(self.source)

    def update_bg(self, *args): 
        self.bg.pos = self.pos ; self.bg.size = self.size

    def update_database(self, instance):
        self.source.update_database(instance.text)
        self.template.update_database(instance.text)

    def _get_area_percentage(self):
        '''Get percentage part of area on template img
        
        ------------------
        |      top       |
        |    -------     |
        |    |     |     |
        |left|     |right|
        |    |     |     |
        |    -------     |
        |     bottom     |
        ------------------
        '''

        # Control points of template img
        size_rect = self.template.img.rect.size
        left_bottom_rect = self.template.img.rect.pos
        right_top_rect = (left_bottom_rect[0] + size_rect[0], left_bottom_rect[1] + size_rect[1])

        # Control points of area
        left_bottom_area, right_top_area = self.template.img.get_points_area()

        # Count percentage part of area on template img
        left = (left_bottom_area[0] - left_bottom_rect[0]) / size_rect[0]
        rigth = (right_top_rect[0] - right_top_area[0]) / size_rect[0]
        bottom = (left_bottom_area[1] - left_bottom_rect[1]) / size_rect[1]
        top = (right_top_rect[1] - right_top_area[1]) / size_rect[1]

        return left, rigth, bottom, top

    def _get_match_percentage(self, source_img, top_left, bottom_right):
        '''Get percentage part of match on source img'''
        # Get size of source img
        h_s, w_s = source_img.shape

        # Count percentage part of match on source img
        left = top_left[0] / w_s
        rigth = (w_s - bottom_right[0]) / w_s
        bottom = (h_s - bottom_right[1]) / h_s
        top = top_left[1] / h_s
        
        return left, rigth, bottom, top

    def run_alg(self, instance):
        if self.template.img.area_obj is None: return
        
        ''' ============== INPUT ============== '''
        # Load orig images
        if self.source.database == 'ORL':
            source_img = cv2.imread(self.source.img_path, -1)
        else:
            source_img = imageio.imread(self.source.img_path)
        
        if self.template.database == 'ORL':
            template_img = cv2.imread(self.template.img_path, -1)
        else:
            template_img = imageio.imread(self.template.img_path)

        # Get percentage part of area
        left_area, rigth_area, bottom_area, top_area = self._get_area_percentage()

        # Crop area from orig template img
        h_t, w_t = template_img.shape
        template_img_area = template_img[
            int(h_t*top_area):-int(h_t*bottom_area),
            int(w_t*left_area):-int(w_t*rigth_area)]

        ''' ============== RUN detection ============== '''
        top_left, bottom_right = detected(source_img, template_img_area, self.method)

        ''' ============== OUTPUT ============== '''
        # Get percentage part of match
        left_match, rigth_match, bottom_match, top_match = self._get_match_percentage(
            source_img, top_left, bottom_right)

        # Set match on source img
        x_s, y_s = self.source.img.rect.pos
        w_s, h_s = self.source.img.rect.size
        x_match = x_s + w_s * left_match
        y_match = y_s + h_s * bottom_match
        w_match = w_s - w_s * rigth_match - w_s * left_match
        h_match = h_s - h_s * top_match - h_s * bottom_match
        self.source.img.set_match(x_match, y_match, w_match, h_match)
