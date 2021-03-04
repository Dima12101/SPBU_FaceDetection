from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Rectangle, Line, Color

import os, glob

from src.ui.configs import DATA_DIR, DATABASE_CONF


class ImgWidget(Widget): 

    def __init__(self, **kwargs): 
        super(ImgWidget, self).__init__(**kwargs)

        # Arranging Canvas 
        with self.canvas: 
            self.rect = Rectangle(source = os.path.join(DATA_DIR, 'default-placeholder.png'), 
                                  pos = self.pos, size = self.size)

            Color(1, 1, 1, 1)
            self.borders = Line(rectangle = (self.x, self.y, self.width, self.height), width = 2)

            # Update the canvas as the screen size change 
            self.bind(pos = self._update, size = self._update)
            self.bind(x = self._update, y = self._update, width = self._update,  height = self._update)

    # update function which makes the canvas adjustable. 
    def _update(self, *args): 
        self.rect.pos = self.pos 
        self.rect.size = self.size
        self.borders.rectangle = (self.x, self.y, self.width, self.height)

    def clear(self):
        pass


class ImgBox(BoxLayout):

    def __init__(self, ImgWidget, database, **kwargs):
        super(ImgBox, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 0

        self.database = database

        self.index_group = 1
        self.index_img =  1

        self.title = Label(text="Img Box", size_hint=(1,.1))
        self.img = ImgWidget()
        self._update_img()
        
        self.box_bth_group = BoxLayout(orientation='horizontal', size_hint=(1,.1))
        self.bth_group_left = Button(text='<- группа', on_press=self.group_left, background_color = (.2, .5, 1, 1))
        self.bth_group_right = Button(text='группа ->', on_press=self.group_right, background_color = (.2, .5, 1, 1))
        self.box_bth_group.add_widget(self.bth_group_left)
        self.box_bth_group.add_widget(self.bth_group_right)

        self.box_bth_img = BoxLayout(orientation='horizontal', size_hint=(1,.1))
        self.bth_img_left = Button(text='<- изображение', on_press=self.img_left, background_color = (.2, .7, 1, 1))
        self.bth_img_right = Button(text='изображение ->', on_press=self.img_right, background_color = (.2, .7, 1, 1))
        self.box_bth_img.add_widget(self.bth_img_left)
        self.box_bth_img.add_widget(self.bth_img_right)

        self.add_widget(self.title)
        self.add_widget(self.img)
        self.add_widget(self.box_bth_group)
        self.add_widget(self.box_bth_img)

    def update_database(self, database):
        self.database = database
        self.index_group = 1
        self.index_img = 1
        self._update_img()

    def _update_img(self):
        if self.database == 'ORL':
            self.img_path = DATABASE_CONF['ORL']['img_path'].format(g=self.index_group, im=self.index_img)
        else:
            name_group = self.index_group if self.index_group >= 10 else f'0{self.index_group}'
            self.img_path = list(glob.glob(DATABASE_CONF['Yale_faces']['img_path'].format(g=name_group)))[self.index_img-1]
        self.img.rect.source = self.img_path
        self.img.clear()

    def group_left(self, instance):
        if self.index_group != 1:
            self.index_group -= 1 ; self.index_img = 1
            self._update_img()
            
    def group_right(self, instance):
        if self.index_group != DATABASE_CONF[self.database]['number_group']:
            self.index_group += 1 ; self.index_img = 1
            self._update_img()

    def img_left(self, instance):
        if self.index_img != 1:
            self.index_img -= 1 ; self._update_img()

    def img_right(self, instance):
        if self.index_img != DATABASE_CONF[self.database]['number_img']:
            self.index_img += 1 ; self._update_img()
