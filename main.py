import time
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.window import Window
from plyer import filechooser
from kivy.core.audio import SoundLoader
from PIL import Image, ImageOps #Install pillow instead of PIL
import numpy as np
from kivymd.uix.selectioncontrol import MDCheckbox
from plyer import tts
import pdftotext
from gtts import gTTS
from kivymd.uix.filemanager import MDFileManager
import subprocess
from keras.models import load_model
from kivymd.toast import toast
from kivymd.uix.carousel import MDCarousel
from kivy.core.text import LabelBase
from kivymd.uix.dropdownitem import MDDropDownItem
from googletrans import Translator
from kivymd.uix.spinner import MDSpinner


LabelBase.register(name='main',fn_regular='Lobster-Regular.ttf')
import os.path
import os

Window.size = (400, 800)

class MainApp(MDApp):
    def build(self):
        global screen_manager
        screen_manager = ScreenManager()
        self.title='Dhvani'
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Purple"
        
        screen_manager.add_widget(Builder.load_file("home.kv"))
        screen_manager.add_widget(Builder.load_file("pdf.kv"))
        screen_manager.add_widget(Builder.load_file("braille.kv"))
        screen_manager.add_widget(Builder.load_file("currency.kv"))
        screen_manager.add_widget(Builder.load_file("donate_us.kv"))
        screen_manager.add_widget(Builder.load_file("braille2.kv"))
        
        return screen_manager

    def on_start(self):
        Clock.schedule_once(self.login, 5)   
        
        carousel1 = screen_manager.get_screen("home").ids['carousel']
        carousel1.loop = True
        Clock.schedule_interval(carousel1.load_next, 4.0)

        
    def current_slide(self, index):
        pass
        
    def capture(self):
        camera = screen_manager.get_screen("currency").ids['camera']
        camera.export_to_png("useimage.png")
        print("Captured")
        
        
        img = "useimage.png"
        
        np.set_printoptions(suppress=True)

        # Load the model
        model = load_model('keras_Model.h5', compile=False)

        # Load the labels
        class_names = open('labels.txt', 'r').readlines()

        # Create the array of the right shape to feed into the keras model
        # The 'length' or number of images you can put into the array is
        # determined by the first position in the shape tuple, in this case 1.
        data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

        # Replace this with the path to your image
        image = Image.open(img).convert('RGB')

        size = (224, 224)
        image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)

        #turn the image into a numpy array
        image_array = np.asarray(image) 

        # Normalize the image
        normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1

        # Load the image into the array
        data[0] = normalized_image_array

        # run the inference 
        prediction = model.predict(data)
        index = np.argmax(prediction)
        class_name = class_names[index]
        confidence_score = prediction[0][index]

        print('Confidence score:', confidence_score)
        print('Class:', class_name, end='')
        confidence_score = (confidence_score*100).round(3)
        class_name = class_name.split()

        if confidence_score> 99: 
            screen_manager.get_screen("currency").ids['curency'].text = "Currency is of " + class_name[1] + " Rupee"
            screen_manager.get_screen("currency").ids['Accuracy'].text = "Confidance is " +str(confidence_score) + "%"
            tts.speak(message = "Currency is " + class_name[1])
        else:
            screen_manager.get_screen("currency").ids['curency'].text = "Seems to be " + class_name[1] + " Rupee"
            screen_manager.get_screen("currency").ids['Accuracy'].text = "Confidance is " +str(confidence_score) + "%" 
            tts.speak(message = "Not sure")
        
    def btn_pressed(fuck_you, name):
        sound = SoundLoader.load(name)
        sound.play()
            
    def login(self, *args):
        screen_manager.current = "home"
        
    def spinner_clicked(self, value):
        self.ids.click_lable.text = value
    
    def file_chooser(self):
        try:
            filechooser.open_file(on_selection = self.selected)
        except(TypeError):
            toast("Please select a file")

        
    def selected(self, selection):
        global filename
        filename = os.path.basename(selection[0])
        screen_manager.get_screen("pdf").ids.filename.text = filename
        global file_loc
        file_loc = selection[0]
        global land
        land = "en"
        
    def pdf_lang(self, text):
        if text == "Select a Language":
            land = "en"
        if text == "Hindi":
            land = "hi"
        if text == "Gujrati":
            land = "gu"
        if text == "Marathi":
            land = "mr"
        if text == "Tamil":
            land = "ta"
        if text == "Telgu":
            land = "tl"
        if text == "Punjabi":
            land = "pa"
        if text == "Bengali":
            land = "bn"
        if text == "Urdu":
            land = "ur"
        if text == "Kannad":
            land = "kn"
        if text == "Odia":
            land = "or"
        if text == "English":
            land = "en"
        print(land)
        
    def pdf_audio(selection):
        screen_manager.get_screen("pdf").ids['hey'].active = True
        toast("Converting")
        audio_chunks = [] 
        try:
            with open(file_loc, "rb") as f:
                pdf = pdftotext.PDF(f)

            text_chunks = []
            for text in pdf:
                page_chunks = text.split(' ')  
                text_chunks.extend(page_chunks)
            
            MAX_CHARS = 15000
            current_chunk = ''
            for chunk in text_chunks:
                if len(current_chunk) + len(chunk) + 1 <= MAX_CHARS:  # check if adding the current chunk would exceed the limit
                    current_chunk += ' ' + chunk  # add the current chunk to the current string
                else:
                    # save the current string as a text chunk and start a new string with the current chunk
                    audio_chunks.append(current_chunk)
                    current_chunk = chunk
            audio_chunks.append(current_chunk)
        except:
            toast("Please Select a PDF File")
        screen_manager.get_screen("pdf").ids['hey'].active = False

        translator = Translator()
        for i, chunk in enumerate(audio_chunks):
            print(f"Translating and converting chunk {i + 1} of {len(audio_chunks)}")
            string_of_text = translator.translate(chunk, dest=land).text
            final_file = gTTS(text=str(string_of_text), lang=land) 
            name = f"converted/{filename}_chunk_{i + 1}_{land}.mp3"
            final_file.save(name)  
        
    def open_folder(self):
        # Create a file manager instance
        path='converted'
        file_manager = MDFileManager(
            exit_manager=self.exit_file_manager,
            select_path=self.select_path,
            # Set the initial directory
        )
        # Open the file manager
        file_manager.show(path)
    
    def exit_file_manager(self, *args):
        # Close the file manager
        self.manager_open = False
    
    def select_path(self, path):
        # Do something with the selected path
        subprocess.run(['open', path], check=True)
        print('Selected path:', path)

    global text
    text = [0,0,0,0,0,0]
    global line
    line = ""
    
    def text_braille(self, selection, isActive):
        if (selection == 1 and isActive == True): 
            text[0] = 1
        if (selection == 1 and isActive == False): 
            text[0] = 0
        if (selection == 2 and isActive == True): 
            text[1] = 1
        if (selection == 2 and isActive == False): 
            text[1] = 0
        if (selection == 3 and isActive == True): 
            text[2] = 1
        if (selection == 3 and isActive == False): 
            text[2] = 0
        if (selection == 4 and isActive == True): 
            text[3] = 1
        if (selection == 4 and isActive == False): 
            text[3] = 0
        if (selection == 5 and isActive == True): 
            text[4] = 1
        if (selection == 5 and isActive == False): 
            text[4] = 0
        if (selection == 6 and isActive == True): 
            text[5] = 1
        if (selection == 6 and isActive == False): 
            text[5] = 0
        if text == [1,0,0,0,0,0]:
            screen_manager.get_screen("braille").ids["char"].text = "a"
        if text == [1,1,0,0,0,0]:
            screen_manager.get_screen("braille").ids["char"].text = "b"
        if text == [1,0,0,1,0,0]:
            screen_manager.get_screen("braille").ids["char"].text = "c"
        if text == [1,0,0,1,1,0]:
            screen_manager.get_screen("braille").ids["char"].text = "d"
        if text == [1,0,0,0,1,0]:
            screen_manager.get_screen("braille").ids["char"].text = "e"
        if text == [1,1,0,1,0,0]:
            screen_manager.get_screen("braille").ids["char"].text = "f"
        if text == [1,1,0,1,1,0]:
            screen_manager.get_screen("braille").ids["char"].text = "g"
        if text == [1,1,0,0,1,0]:
            screen_manager.get_screen("braille").ids["char"].text = "h"
        if text == [0,1,0,1,0,0]:
            screen_manager.get_screen("braille").ids["char"].text = "i"
        if text == [0,1,0,1,1,0]:
            screen_manager.get_screen("braille").ids["char"].text = "j"
        if text == [1,0,1,0,0,0]:
            screen_manager.get_screen("braille").ids["char"].text = "k"
        if text == [1,1,1,0,0,0]:
            screen_manager.get_screen("braille").ids["char"].text = "l"
        if text == [1,0,1,1,0,0]:
            screen_manager.get_screen("braille").ids["char"].text = "m"
        if text == [1,0,1,1,1,0]:
            screen_manager.get_screen("braille").ids["char"].text = "n"
        if text == [1,0,1,0,1,0]:
            screen_manager.get_screen("braille").ids["char"].text = "o"
        if text == [1,1,1,1,0,0]:
            screen_manager.get_screen("braille").ids["char"].text = "p"
        if text == [1,1,1,1,1,0]:
            screen_manager.get_screen("braille").ids["char"].text = "q"
        if text == [1,1,1,0,1,0]:
            screen_manager.get_screen("braille").ids["char"].text = "r"
        if text == [0,1,1,1,0,0]:
            screen_manager.get_screen("braille").ids["char"].text = "s"
        if text == [0,1,1,1,1,0]:
            screen_manager.get_screen("braille").ids["char"].text = "t"
        if text == [1,0,1,0,0,1]:
            screen_manager.get_screen("braille").ids["char"].text = "u"
        if text == [1,1,1,0,0,1]:
            screen_manager.get_screen("braille").ids["char"].text = "v"
        if text == [0,1,0,1,1,1]:
            screen_manager.get_screen("braille").ids["char"].text = "w"
        if text == [1,0,1,1,0,1]:
            screen_manager.get_screen("braille").ids["char"].text = "x"
        if text == [1,0,1,1,1,1]:
            screen_manager.get_screen("braille").ids["char"].text = "y"
        if text == [1,0,1,0,1,1]:
            screen_manager.get_screen("braille").ids["char"].text = "z"
    def on_pres(self):
        character = screen_manager.get_screen("braille").ids["char"].text
        line = screen_manager.get_screen("braille").ids["textt"].text
        screen_manager.get_screen("braille").ids["textt"].text = line + character
        
    def backspace(self):
        line = screen_manager.get_screen("braille").ids["textt"].text
        screen_manager.get_screen("braille").ids["textt"].text = line[:-1]
        
    def speak(self,screen):
        if screen =="braille1":
            textt = screen_manager.get_screen("braille").ids["textt"].text
            tts.speak(message = textt)
        if screen == "braille2":
            textt = screen_manager.get_screen("braille2").ids["happy"].text
            tts.speak(message = textt)
        
    def textToBraille(text):
        txt = screen_manager.get_screen("braille2").ids["textt"].text
        screen_manager.get_screen("braille2").ids["happy"].text = txt
        if len(txt) > 10:
            i = 0
            result = ""
            for i in range(0, len(txt), 10):
                result += txt[i:i+10] + "\n"
            screen_manager.get_screen("braille2").ids["happy"].text = result
        if len(txt) > 20:
            screen_manager.get_screen("braille2").ids["happy"].size_hint= (0.8, 0.25)
            
        if len(txt) > 40:
            screen_manager.get_screen("braille2").ids["happy"].size_hint= (0.8, 0.35)
    def comming_soon(self):
        toast("Feature Comming Soon")
        
        
MainApp().run()