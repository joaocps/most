import os
from os.path import expanduser, dirname

import cv2
import numpy as np
from kivy.app import App
from kivy.config import Config
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup, PopupException
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.utils import platform
import kivy.resources

import cv_func.fire_cv as fire_cv
import cv_func.image_transform as im_transform
import cv_func.watershed_automated as ws_auto
import cv_func.shapefile_creation_dao as shp_dao

Config.set('graphics', 'width', '500')
Config.set('graphics', 'height', '600')
Config.write()


# TODO (?)separar funcões auxiliares da classe original
class Menu(ScreenManager):

    def __init__(self, **kwargs):
        """ Create all the default gui elements  """
        super(Menu, self).__init__(**kwargs)
        self.fcv = fire_cv.FireCv()
        self.imT = im_transform.Image_Transform()
        self.wsA = ws_auto.watershed_automated()
        self.shpDAO = shp_dao.Shape_Creation_DAO()
        self.logo_file = kivy.resources.resource_find("static/logo.png")

        # main screen config
        self.main_screen = Screen(name='Most-g4')
        self.layout = BoxLayout(orientation='vertical')
        self.logo = Image(source=self.logo_file, allow_stretch=True, size_hint_y=1)
        self.layout_down = GridLayout(cols=2, rows=3, size_hint_y=0.2)
        self.layout.add_widget(self.logo)
        self.layout.add_widget(self.layout_down)
        self.main_screen.add_widget(self.layout)

        # define os and default path
        self.os = platform
        self.path = ""
        if self.os == 'win':
            self.path = dirname(expanduser("~"))
        else:
            self.path = expanduser("~")

        # Define and add buttons to main Screen
        self.vid = Button(text='Dividir Video', size_hint_y=0.1)
        self.vid.bind(on_press=lambda x: (self.browser('vid')))
        self.im = Button(text='Processar Frames', size_hint_y=0.1)
        self.im.bind(on_press=lambda x: (self.browser('frame')))
        self.seg_man = Button(text='Segmentação Personalizada', size_hint_y=0.1)
        self.seg_man.bind(on_press=self.seg_workflow)
        self.seg = Button(text='Segmentação Semi-Automizada', size_hint_y=0.1)
        self.seg.bind(on_press=self.seg_auto)
        self.shp_file = Button(text='Gerar Shapefiles', size_hint_y=0.1)
        self.shp_file.bind(on_press=self.dao_shp)
        self.image_transform = Button(text='Coordenadas Georeferenciadas', size_hint_y=0.1)
        self.image_transform.bind(on_press=self.image_transformation_workflow)

        self.layout_down.add_widget(self.vid)
        self.layout_down.add_widget(self.seg)
        self.layout_down.add_widget(self.im)
        self.layout_down.add_widget(self.seg_man)
        self.layout_down.add_widget(self.image_transform)
        self.layout_down.add_widget(self.shp_file)

        # init default popup
        self.popup = Popup()

        # Screen Manager
        self.s_open_file = Screen(name='Abrir Ficheiro')
        self.s_save_frame = Screen(name='Gravar Frames')
        self.s_save_area = Screen(name='Gravar Area')
        self.s_coords = Screen(name='Coords')
        self.s_wait = Screen(name='Wait')
        self.add_widget(self.main_screen)
        self.add_widget(self.s_open_file)
        self.add_widget(self.s_save_frame)
        self.add_widget(self.s_save_area)
        self.add_widget(self.s_wait)
        self.add_widget(self.s_coords)

        # filename
        self.text_input = TextInput()
        self.text = ""

        # watershed original fg and bg arrays
        self.ws_original = ""
        self.fg = []
        self.bg = []

        # watershed semi-automatic
        self.ws_auto = ""

        # Image transformation
        self.img_t_og = ""
        self.img_t_map = ""
        self.img_t_cntr = ""
        self.img_t_filename = ""

        self.georef_x_min_text = ""
        self.georef_x_max_text = ""
        self.georef_y_min_text = ""
        self.georef_y_max_text = ""

    def browser(self, op):
        """ This function creates the file chooser to select image"""
        # Create Layout for popup
        try:
            self.popup.dismiss()
        except PopupException:
            pass

        self.current = 'Abrir Ficheiro'
        b_main_lay = GridLayout(rows=2)
        action_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1)
        if op is 'seg_fg':
            file = FileChooserIconView(path=self.path, size_hint_y=0.9, multiselect=True)
        elif op is 'seg_bg':
            file = FileChooserIconView(path=self.path, size_hint_y=0.9, multiselect=True)
        else:
            file = FileChooserIconView(path=self.path, size_hint_y=0.9, multiselect=False)
        # this popup buttons and actions
        select = Button(text='Abrir')
        if op is "shp":
            self.popup.dismiss()
            select.bind(on_press=lambda x: self.create_shp(file.path))
        else:
            select.bind(on_press=lambda x: self.open(file.selection, op))

        cancel = Button(text='Cancelar')
        cancel.bind(on_press=self.cancel_callback)
        action_layout.add_widget(select)
        action_layout.add_widget(cancel)
        b_main_lay.add_widget(file)
        b_main_lay.add_widget(action_layout)

        self.s_open_file.add_widget(b_main_lay)

    def cancel_callback(self, instance):
        self.current = 'Most-g4'
        self.s_open_file.clear_widgets()
        self.s_save_frame.clear_widgets()
        self.s_save_area.clear_widgets()

    def open(self, filename, op):
        """ Selects the according action bases on operation type (op) and file size"""
        if len(filename) is 1:
            if op is 'frame':
                self.current = 'Most-g4'
                self.s_open_file.clear_widgets()
                try:
                    im = cv2.imread(filename[0])
                    if im is not None:
                        self.analize_frame(im)
                    else:
                        cv2.imshow('img', im)
                except cv2.error as e:
                    cv2.destroyAllWindows()
                    self.end_action(
                        "Oops! Algo correu mal!\nVerifique se selecionou o ficheiro correto")

            elif op is 'vid':
                self.current = 'Most-g4'
                self.s_open_file.clear_widgets()
                try:
                    vid = cv2.VideoCapture(filename[0])
                    print(vid)
                    self.save_frame(vid, str(os.path.basename(filename[0])).split(".")[0])
                except cv2.error as e:
                    self.end_action(
                        "Oops! Algo correu mal!\nVerifique se selecionou o ficheiro correto")

            elif op is 'seg_auto':
                self.current = 'Most-g4'
                self.s_open_file.clear_widgets()
                ws = ""
                cntr = ""
                try:
                    self.ws_auto = cv2.imread(filename[0])
                    ws, cntr = self.wsA.workflow(self.ws_auto, (os.path.basename(filename[0])).split(".")[0])
                except cv2.error as e:
                    self.end_action(
                        "Oops! Algo correu mal!\nVerifique se selecionou o ficheiro correto")
                finally:
                    self.save_builder(ws, cntr)

            elif op is 'original':
                self.current = 'Most-g4'
                self.s_open_file.clear_widgets()
                try:
                    self.ws_original = cv2.imread(filename[0])
                    cntr, ws = self.fcv.watershed(self.ws_original, self.fg, self.bg)
                except cv2.error as e:
                    self.end_action(
                        "Oops! Algo correu mal!\nVerifique se selecionou o ficheiro correto")
                finally:
                    self.save_builder(ws, cntr)

            elif op is 'img_t_og':
                self.current = 'Most-g4'
                self.s_open_file.clear_widgets()
                try:
                    self.img_t_og = cv2.imread(filename[0])
                    self.img_t_filename = os.path.basename(filename[0].split(".")[0])
                    self.image_transformation_workflow(instance="", it=1)
                except cv2.error as e:
                    self.end_action("Oops! Algo correu mal!\nVerifique se selecionou o ficheiro correto")

            elif op is 'img_t_map':
                self.current = 'Most-g4'
                self.s_open_file.clear_widgets()
                try:
                    self.img_t_map = cv2.imread(filename[0])
                    self.image_transformation_workflow(instance="", it=2)
                except cv2.error as e:
                    self.end_action("Oops! Algo correu mal!\nVerifique se selecionou o ficheiro correto")

            elif op is 'img_t_cntr':
                try:
                    self.img_t_cntr = np.load(filename[0], allow_pickle=True)
                    self.georef_coords()
                except IOError as e:
                    self.end_action("Oops! Algo correu mal!\nVerifique se selecionou o ficheiro correto")
        else:
            if op is 'seg_fg':
                self.fg = []
                self.current = 'Most-g4'
                self.s_open_file.clear_widgets()
                for i in filename:
                    try:
                        print(i)
                        aux = cv2.imread(i)
                        self.fg.append(aux)
                        self.seg_workflow(instance="", it=1)
                    except cv2.error as e:
                        self.end_action(
                            "Oops! Algo correu mal!\nVerifique se selecionou o ficheiro correto")

            elif op is 'seg_bg':
                self.current = 'Most-g4'
                self.s_open_file.clear_widgets()
                self.bg = []
                for i in filename:
                    try:
                        print(i)
                        aux = cv2.imread(i)
                        self.bg.append(aux)
                        self.seg_workflow(instance="", it=2)
                    except cv2.error as e:
                        self.end_action(
                            "Oops! Algo correu mal!\nVerifique se selecionou o ficheiro correto")

    def save_frame(self, video, folder):
        grid_s = GridLayout(rows=5)

        spinner = Spinner(
            # default value shown
            text='Tipo de ficheiro',
            text_autoupdate=True,
            # available values
            values=('.jpg', '.png'),
            # just for positioning in our example
            size_hint=(None, None),
            size=(100, 44),
            pos_hint={'center_x': .5, 'center_y': .5})

        spinner2 = Spinner(
            # default value shown
            text='intervalo(segundos)',
            text_autoupdate=True,
            # available values
            values=('10', '20', '30', '40', '50', '60', '90', '120', '240'),
            # just for positioning in our example
            size_hint=(None, None),
            size=(100, 44),
            pos_hint={'center_x': .5, 'center_y': .5})

        spinner.bind(text=self.show_selected_value)
        input_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1)
        input_label = Label(text="Timestamp base", size_hint=(None, None), size=(200, 44))
        self.text_input = TextInput(text="", hint_text="Ano Mês Dia Hora Minuto Segundo", multiline=False,
                                    size_hint=(None, None), size=(300, 44))
        self.text_input.bind(text=self.set_text)

        input_layout.add_widget(self.text_input)
        input_layout.add_widget(input_label)

        # save file
        save = Button(text="Selecionar", size_hint_y=None, size=(100, 44))
        file = FileChooserIconView(path=self.path)
        grid_s.add_widget(file)
        grid_s.add_widget(spinner2)
        grid_s.add_widget(spinner)
        grid_s.add_widget(input_layout)
        grid_s.add_widget(save)
        self.s_save_frame.add_widget(grid_s)
        self.current = 'Gravar Frames'
        save.bind(
            on_release=lambda x: self.video_helper(o=self.os, folder=folder, path=file.path, ext=spinner.text,
                                                   time=int(spinner2.text),
                                                   video=video, timestamp=self.text))

    def video_helper(self, o, folder, path, ext, time, video, timestamp):
        """ Call divide_video and report output to user """
        if timestamp is "":
            self.end_action("Timestamp vazio!\nPor favor insira um valor válido")
            self.s_save_frame.clear_widgets()
            return

        self.popup = Popup(title="Divisão de video", separator_height=0, content=Label(text="A processsar video"),
                           size_hint=(None, None), size=(300, 100))

        self.popup.bind(on_open=lambda x: self.vid_helper_cont(o=o, folder=folder, path=path, ext=ext,
                                                               time=time,
                                                               video=video, timestamp=timestamp))
        self.popup.open()

    def vid_helper_cont(self, o, folder, path, ext, time, video, timestamp):

        result = self.fcv.divide_video(o=o, folder=folder, path=path, ext=ext,
                                       time=time,
                                       video=video, timestamp=timestamp)
        if result is True:
            self.popup.bind(on_dismiss=lambda x: self.end_action("Video separado com sucesso!\nVer" + path))
        else:
            self.popup.bind(on_dismiss=lambda x: self.end_action(
                "Oops! Algo correu mal!\nVerifique se selecionou o ficheiro correto"))
        self.s_save_frame.clear_widgets()
        self.s_wait.clear_widgets()
        self.popup.dismiss()

    def end_action(self, text):
        """ sucess/error popup """
        self.current = 'Most-g4'
        grid = GridLayout(rows=2)
        label = Label(text=text)
        dismiss = Button(text='OK', size_hint_y=None, size=(50, 30))
        grid.add_widget(label)
        grid.add_widget(dismiss)
        self.popup = Popup(title="Most G4", separator_height=0, content=grid, size_hint=(None, None), size=(300, 200))
        self.popup.open()
        dismiss.bind(on_press=self.popup.dismiss)

    def analize_frame(self, frame):
        """ Auxiliary function to select foreground (relevate areas)
         and background(what to ignore on final segmentation) """

        img = self.fcv.analize_frame(frame=frame)
        self.save_builder(img)

    def save_builder(self, img="", cntr="", converted=""):
        grid_s = GridLayout(rows=3)
        action_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1)
        file_name_type_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1)

        # File extension
        spinner = Spinner(
            # default value shown
            text='Tipo de ficheiro',
            text_autoupdate=True,
            # available values
            values=('.jpg', '.png'),
            size_hint_x=0.3)

        spinner.bind(text=self.show_selected_value)

        # filename
        if converted is "":
            self.text_input = TextInput(text="", multiline=False)
            file_name_type_layout.add_widget(self.text_input)
            self.text_input.bind(text=self.set_text)

        # save file
        save = Button(text="Guardar")
        cancel = Button(text="Cancelar")
        action_layout.add_widget(save)
        action_layout.add_widget(cancel)
        file = FileChooserIconView(path=self.path, )
        grid_s.add_widget(file)

        if img is not "":
            file_name_type_layout.add_widget(spinner)

        grid_s.add_widget(file_name_type_layout)
        grid_s.add_widget(action_layout)
        cancel.bind(on_press=self.cancel_callback)
        self.s_save_area.add_widget(grid_s)
        self.current = 'Gravar Area'
        if cntr is not "":
            save.bind(on_press=lambda x: self.save_files(path=file.path, extension=spinner.text
                                                         , img=img, cntr=cntr))
        elif converted is not "":
            save.bind(on_press=lambda x: self.save_files(path=file.path, extension=spinner.text
                                                         , converted=converted))
        else:
            save.bind(on_press=lambda x: self.save_files(path=file.path, extension=spinner.text
                                                         , img=img))

    def seg_auto(self, instance):
        """ Workflow control for segmentação button """
        try:
            self.popup.clear_widgets()
            self.popup.dismiss()
        except PopupException:
            pass
        seg_layout = GridLayout(cols=1)
        info = Label(text="Selecionar Frame para obter\nzona de incêndio")
        confirm = Button(text="OK")

        # if it is 0:
        seg_layout.add_widget(info)
        confirm.bind(on_press=lambda x: self.browser('seg_auto'))
        seg_layout.add_widget(confirm)
        self.popup = Popup(title="Zona de Incêndio", separator_height=0, content=seg_layout,
                           size_hint=(None, None), size=(300, 150))
        self.popup.open()

    def seg_workflow(self, instance, it=0):
        """ Workflow control for segmentação button """
        try:
            self.popup.clear_widgets()
            self.popup.dismiss()
        except PopupException:
            pass
        seg_layout = GridLayout(cols=1)
        info = Label(text="Selecionar imagens áreas de interesse")
        info2 = Label(text="Selecionar imagens áreas a omitir")
        info3 = Label(text="Selecionar imagem original")
        confirm = Button(text="OK")

        if it is 0:
            seg_layout.add_widget(info)
            confirm.bind(on_press=lambda x: self.browser('seg_fg'))
        elif it is 1:
            seg_layout.add_widget(info2)
            confirm.bind(on_press=lambda x: self.browser('seg_bg'))
        elif it is 2:
            seg_layout.add_widget(info3)
            confirm.bind(on_press=lambda x: self.browser('original'))
        seg_layout.add_widget(confirm)
        self.popup = Popup(title="Segmentação", separator_height=0, content=seg_layout,
                           size_hint=(None, None), size=(300, 150))
        self.popup.open()

    def save_files(self, path, extension, img="", cntr="", converted=""):
        self.current = 'Most-g4'

        # print(converted)

        if self.os == 'win':
            # Create path with our without folder if saving multiple files
            if cntr is not "":
                path = path + "\\" + self.text
            if os.path.exists(os.path.normpath(path)) is False:
                os.mkdir(path)

            if img is not "":
                cv2.imwrite(path + "\\" + self.text + extension, img)
            if cntr is not "":
                np.save(path + "\\" + self.text, cntr)
            if converted is not "":
                np.save(path + "\\" + self.text, converted)

        else:
            # Create path with our without folder if saving multiple files
            if cntr is not "":
                path = path + "/" + self.text
            if os.path.exists(os.path.normpath(path)) is False:
                os.mkdir(path)

            if img is not "":
                cv2.imwrite(path + "/" + self.text + extension, img)
            if cntr is not "":
                np.save(path + "/" + self.text, cntr)
            if converted is not "":
                np.save(path + "/" + self.img_t_filename, converted)
        self.s_save_area.clear_widgets()

    def image_transformation_workflow(self, instance, it=0):
        """ Image transformation gui controller """
        try:
            self.popup.clear_widgets()
            self.popup.dismiss()
        except PopupException:
            pass

        imt_layout = GridLayout(cols=1)
        info = Label(text="Selecionar imagem original")
        info2 = Label(text="Selecionar mapa da área")
        info3 = Label(text="Selecionar ficheiro dos contorno\n(imagem_original.npy)")
        confirm = Button(text="OK")

        if it is 0:
            imt_layout.add_widget(info)
            confirm.bind(on_press=lambda x: self.browser('img_t_og'))
        elif it is 1:
            imt_layout.add_widget(info2)
            confirm.bind(on_press=lambda x: self.browser('img_t_map'))
        elif it is 2:
            imt_layout.add_widget(info3)
            confirm.bind(on_press=lambda x: self.browser('img_t_cntr'))
        imt_layout.add_widget(confirm)
        self.popup = Popup(title="Transformação", separator_height=0, content=imt_layout,
                           size_hint=(None, None), size=(300, 150))
        self.popup.open()

    def georef_coords(self):
        self.current = 'Coords'
        coods_layout = BoxLayout(orientation="vertical")

        main_in_layout = BoxLayout(orientation="vertical", size_hint_y=0.8)

        input_layout_x_min = BoxLayout(orientation='horizontal', size_hint_y=0.25)
        input_label_x_min = Label(text="X Mínimo", size_hint=(None, None), size=(200, 30))

        input_layout_x_max = BoxLayout(orientation='horizontal', size_hint_y=0.25)
        input_label_x_max = Label(text="X Máximo", size_hint=(None, None), size=(200, 30))

        input_layout_y_min = BoxLayout(orientation='horizontal', size_hint_y=0.25)
        input_label_y_min = Label(text="Y Mímino", size_hint=(None, None), size=(200, 30))

        input_layout_y_max = BoxLayout(orientation='horizontal', size_hint_y=0.25)
        input_label_y_max = Label(text="Y Máximo", size_hint=(None, None), size=(200, 30))

        georef_x_min = TextInput(text="615202.199", multiline=False, size_hint=(None, None), size=(300, 30))
        georef_x_max = TextInput(text="616268.574", multiline=False, size_hint=(None, None), size=(300, 30))
        georef_y_min = TextInput(text="4583991.175", multiline=False, size_hint=(None, None), size=(300, 30))
        georef_y_max = TextInput(text="4582453.191", multiline=False, size_hint=(None, None), size=(300, 30))
        confirm = Button(text="OK", size_hint_y=0.2)

        georef_y_min.bind(text=self.set_y_min)
        georef_y_max.bind(text=self.set_y_max)
        georef_x_min.bind(text=self.set_x_min)
        georef_x_max.bind(text=self.set_x_max)

        input_layout_x_min.add_widget(georef_x_min)
        input_layout_x_min.add_widget(input_label_x_min)

        input_layout_x_max.add_widget(georef_x_max)
        input_layout_x_max.add_widget(input_label_x_max)

        input_layout_y_min.add_widget(georef_y_min)
        input_layout_y_min.add_widget(input_label_y_min)

        input_layout_y_max.add_widget(georef_y_max)
        input_layout_y_max.add_widget(input_label_y_max)

        confirm.bind(
            on_press=self.coords_helper)

        main_in_layout.add_widget(input_layout_x_min)
        main_in_layout.add_widget(input_layout_x_max)
        main_in_layout.add_widget(input_layout_y_min)
        main_in_layout.add_widget(input_layout_y_max)
        coods_layout.add_widget(main_in_layout)
        coods_layout.add_widget(confirm)

        self.s_coords.add_widget(coods_layout)

    def coords_helper(self, instance):
        result = False
        self.current = 'Most-g4'
        self.s_coords.clear_widgets()
        self.s_open_file.clear_widgets()

        result, converted = self.imT.main(self.img_t_og, self.img_t_map, self.img_t_cntr, self.georef_x_min_text,
                                          self.georef_x_max_text, self.georef_y_min_text, self.georef_y_max_text)
        if result is True:
            self.save_builder(converted=converted)

    def dao_shp(self, instance):
        shp_layout = GridLayout(cols=1)

        info = Label(text="Selecionar diretório\ncom contornos convertidos")
        confirm = Button(text="OK")

        shp_layout.add_widget(info)
        shp_layout.add_widget(confirm)
        confirm.bind(on_press=lambda x: self.browser("shp"))
        self.popup = Popup(title="Gerar Shapefiles", separator_height=0, content=shp_layout,
                           size_hint=(None, None), size=(300, 150))
        self.popup.open()
        # self.browser("shp")

    def create_shp(self, path):
        self.shpDAO.main(path, self.os)
        self.current = 'Most-g4'
        self.s_open_file.clear_widgets()

        shp_layout = GridLayout(cols=1)

        info = Label(text="Shapefiles gerados com sucesso")
        confirm = Button(text="OK")

        shp_layout.add_widget(info)
        shp_layout.add_widget(confirm)
        confirm.bind(on_press=lambda x: self.popup.dismiss())
        self.popup = Popup(title="Gerar Shapefiles", separator_height=0, content=shp_layout,
                           size_hint=(None, None), size=(300, 150))
        self.popup.open()

    def show_selected_value(self, instance, text):
        """ Get current value from spinner """
        if text is not 'Tipo de ficheiro' and not '':
            return text
        else:
            print("Invalid file extension")

    def set_text(self, instance, input):
        """ Workaround to save input from textInput """
        self.text = input

    def set_x_min(self, instance, input):
        """ Workaround to save x min from textInput """
        self.georef_x_min_text = input

    def set_x_max(self, instance, input):
        """ Workaround to save x max from textInput """
        self.georef_x_max_text = input

    def set_y_min(self, instance, input):
        """ Workaround to save y min from textInput """
        self.georef_y_min_text = input

    def set_y_max(self, instance, input):
        """ Workaround to save x min from textInput """
        self.georef_y_max_text = input


class MostG4(App):

    def build(self):
        self.title = 'MostG4'
        return Menu()


if __name__ == '__main__':
    MostG4().run()
