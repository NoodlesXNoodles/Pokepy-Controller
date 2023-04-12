import asyncio
import pyautogui
import cv2
import numpy as np
import os
import time

#définition des variables globales
dir_path = os.path.dirname(os.path.realpath(__file__))

#création de la classe game
class Game:
    def __init__(self,window_name,scal=4,see_analysis=True):
        global window, scale # remplacer par le chemin du dossier souhaité

        for filename in os.listdir(dir_path):
            if filename.startswith('Pokemon Red-') and filename.endswith('.png'):
                os.remove(os.path.join(dir_path, filename))
        self.callbacks = []
        self.window_name = window_name
        self.is_fighting = False
        self.see_analysis = see_analysis
        self.is_fighting = False
        self.json_info = {}
        scale = scal
        window = pyautogui.getWindowsWithTitle(window_name)[0]

    #initialisation du principe d'évenement
    def event(self, func):
        self.callbacks.append(func)
        return func
    
    async def trigger(self):
        coroutines = [callback() for callback in self.callbacks]
        await asyncio.gather(*coroutines)

    async def show_analysis(self,view):
        global analysis_img
        if view == True:
            while True:   
                #montre la vue de l'analyse si l'utilisateur le veut
                if view == True:
                    try:
                        cv2.imshow("Analysis",analysis_img)
                    except:
                        pass      
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                await asyncio.sleep(0.2)

    async def game_analysis(self):
        i = 0
        global img, analysis_img, scale
        while True:
            try:
                os.remove(fr"{dir_path}\Pokemon Red-0.png")
            except Exception as e:
                pass
            json = {}
            json["player"] = {}
            json["ennemy"] = {}
            #active la fenêtre
            window.activate()
            #prend une capture d'écran si mgba est la fenêtre active
            pyautogui.keyDown('f12')
            pyautogui.keyUp('f12')
            #intialise l'image exploité
            img = cv2.imread(fr"{dir_path}\Pokemon Red-0.png")
            #initialise l'image esthétique pour la vue de l'analyse
            height, width = img.shape[:2]
            new_height = height * scale
            new_width = width * scale
            analysis_img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_NEAREST)
            #détermine si l'utilisateur est en combat ou non en voyant si le mot fight est affiché
            self.is_fighting = self.is_fight()
            if self.is_fighting:
                #récupère le nom du pokemon de l'utilisateur
                pokemon_name = self.get_sprite_name()
                json["player"]["name"] = pokemon_name       
                if pokemon_name != "":
                    self.trace_rectangle(8*scale,40*scale,64*scale,56*scale,name=pokemon_name)
                #récupération et tracé du nombre de pv restant du joueur
                cropped = img[80:88, 87:112]
                remaining_HP = self.get_number(cropped)
                json["player"]['remaining_HP'] = remaining_HP
                self.trace_rectangle(87*scale,80*scale,25*scale,8*scale,name=str(remaining_HP))
                #récupération et tracé du nombre de pv total du jooueur
                cropped = img[80:88, 119:144]
                full_HP = self.get_number(cropped)
                json["player"]['full_HP'] = remaining_HP
                self.trace_rectangle(119*scale,80*scale,25*scale,8*scale,name=str(full_HP))
                #récupération et tracé du niveau du joueur
                cropped = img[64:72, 119:144]
                level = self.get_number(cropped)
                json["player"]['level'] = level
                self.trace_rectangle(119*scale,64*scale,25*scale,8*scale,name=str(level))
                #récupération du nom du pokemen adverse
                pokemon_name_ennmy = self.get_sprite_ennemy()
                json["ennemy"]["name"] = pokemon_name_ennmy
                if pokemon_name_ennmy != '':
                    self.trace_rectangle(96*scale,0*scale,56*scale,56*scale,custom_y=30,custom_x=10,name=pokemon_name_ennmy)
                #récupération du niveau du pokémon adverse:
                cropped = img[8:16, 39:64]
                adverselvl = self.get_number(cropped)
                json["ennemy"]["level"] = adverselvl
                self.trace_rectangle(39*scale,8*scale,25*scale,8*scale,name=str(adverselvl))
                self.json_info = json
                await self.trigger()
            else:
                pyautogui.keyDown('x')
                pyautogui.keyUp('x')
            #supprime la capture d'écran prise
            await asyncio.sleep(0.5)

    def get_sprite_ennemy(self):
        x,y,w,h = 96,0,152,56
        copied = img.copy()
        cropped = copied[y:h, x:w]
        cropped = cv2.resize(cropped, (56, 56), interpolation=cv2.INTER_NEAREST)
        gray_cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
        pokemon_name = ""
        for p in range(1,22):
            num = str(p).zfill(3)
            template = cv2.imread(fr"{dir_path}\assets\pokemon-sprites\front\spr_rb-gb_{num}.png")
            gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            res = cv2.matchTemplate(gray_cropped, gray_template, cv2.TM_CCOEFF_NORMED)
            max_similarity = np.max(res)
            if max_similarity > 0.95:
                with open(fr"{dir_path}\assets\pokedex.txt", "r") as f:
                    lines = f.readlines()
                    pokemon_name = lines[p-1].rstrip("\n")
                break
        return pokemon_name

    def get_ciffer(self,image):
        number = None
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        for p in range(10):
            template = cv2.imread(fr"{dir_path}\assets\numbers\{p}.png")
            template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            res = cv2.matchTemplate(image_gray, template, cv2.TM_CCOEFF_NORMED)
            max_similarity = np.max(res)
            if max_similarity > 0.995:
                number = p
                break
        return number

    def get_number(self,image):
        height, width = image.shape[:2]
        res = ""
        for p in range(int((width-1)/8)):
            cropped = image[0:height, (p*8):((1+p)*8)+1]
            num = self.get_ciffer(cropped)
            if num is None:
                pass
            else:
                res += str(num)
        return int(res)

    def trace_rectangle(self, x,y,w,h,color=(0, 255, 0),name="",custom_x=0,custom_y=-10):
        cv2.rectangle(analysis_img, (x, y), (x+w, y+h), color, 2)
        if name != "":
            cv2.putText(analysis_img, name, (x+custom_x, y+custom_y), cv2.FONT_HERSHEY_TRIPLEX, 1, color, 1)

    def get_sprite_name(self):
        x,y,w,h = 8,40,72,104
        copied = img.copy()
        cropped = copied[y:h, x:w]
        height, width = cropped.shape[:2]
        cv2.rectangle(cropped, (0, height-8), (width, height), (255, 255, 255), -1)
        cropped = cv2.resize(cropped, (32, 32), interpolation=cv2.INTER_NEAREST)
        gray_cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
        pokemon_name = ""
        for p in range(1,152):
            num = str(p).zfill(3)
            template = cv2.imread(fr"{dir_path}\assets\pokemon-sprites\back\b_rb-gb_{num}.png")
            gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            res = cv2.matchTemplate(gray_cropped, gray_template, cv2.TM_CCOEFF_NORMED)
            max_similarity = np.max(res)
            if max_similarity > 0.99:
                with open(fr"{dir_path}\assets\pokedex.txt", "r") as f:
                    lines = f.readlines()
                    pokemon_name = lines[p-1].rstrip("\n")
                break
        return pokemon_name

    def is_fight(self):
        resu = False
        image_gray = cv2.cvtColor(img[111:120, 79:120], cv2.COLOR_BGR2GRAY)
        template = cv2.imread(fr"{dir_path}\assets\others\fight.png")
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        res = cv2.matchTemplate(image_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        max_similarity = np.max(res)
        if max_similarity > 0.995:
            resu= True
        return resu
    
    def is_arrow(self,x,y,w,h):
        resu = False
        copied = img.copy()
        cropped = copied[y:h, x:w]
        gray_cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
        template = cv2.imread(fr"{dir_path}\assets\others\arrow.png")
        gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        res = cv2.matchTemplate(gray_cropped, gray_template, cv2.TM_CCOEFF_NORMED)
        max_similarity = np.max(res)
        if max_similarity > 0.9:
            resu = True
        return resu

    def escape(self):
        global img
        arrow_position = self.get_arrow_position_menu()
        window.activate()
        if arrow_position == "UL":
            pyautogui.keyDown('down')
            pyautogui.keyUp('down')
            pyautogui.keyDown('right')
            pyautogui.keyUp('right')
        elif arrow_position == "UR":
            pyautogui.keyDown('down')
            pyautogui.keyUp('down')
        elif arrow_position == "DL":
            pyautogui.keyDown('right')
            pyautogui.keyUp('right')
        pyautogui.keyDown('x')
        pyautogui.keyUp('x')
    
    def attack(self,num):
        global img
        arrow_position = self.get_arrow_position_menu()
        window.activate()
        if arrow_position == "DR":
            pyautogui.keyDown('left')
            pyautogui.keyUp('left')
            pyautogui.keyDown('up')
            pyautogui.keyUp('up')
        elif arrow_position == "UR":
            pyautogui.keyDown('left')
            pyautogui.keyUp('left')
        elif arrow_position == "DL":
            pyautogui.keyDown('up')
            pyautogui.keyUp('up')
        pyautogui.keyDown('x')
        pyautogui.keyUp('x')
        os.remove(fr"{dir_path}\Pokemon Red-0.png")
        time.sleep(1)
        pyautogui.keyDown('f12')
        pyautogui.keyUp('f12')
        time.sleep(1)
        img = cv2.imread(fr"{dir_path}\Pokemon Red-0.png")
        position = self.get_arrow_position_attack()
        resu = num - position
        if resu < 0:
            for p in range(-resu):
                pyautogui.keyDown('up')
                pyautogui.keyUp('up')
        elif resu > 0:
            for p in range(resu):
                pyautogui.keyDown('down')
                pyautogui.keyUp('down')
        pyautogui.keyDown('x')
        pyautogui.keyUp('x')

    def trace_arrow(self):
        self.get_arrow_position_attack()
        self.get_arrow_position_menu()

    def get_arrow_position_menu(self):
        if self.is_arrow(120,128,127,137) == True:
            self.trace_rectangle(120*scale,128*scale,7*scale,9*scale,name="arrow")
            resu = "DR"
        elif self.is_arrow(72,128,79,137) == True:
            self.trace_rectangle(72*scale,128*scale,7*scale,9*scale,name="arrow")
            resu="DL"
        elif self.is_arrow(72,112,79,121) == True:
            resu="UL"
            self.trace_rectangle(72*scale,112*scale,7*scale,9*scale,name="arrow")
        elif self.is_arrow(120,112,127,121) == True:
            resu="UR"
            self.trace_rectangle(120*scale,112*scale,7*scale,9*scale,name="arrow")
        else:
            resu=None
        return resu

    def get_arrow_position_attack(self):
        if self.is_arrow(40,104,47,113) == True:
            self.trace_rectangle(40*scale,104*scale,7*scale,9*scale,name="arrow")
            resu = 1
        elif self.is_arrow(40,112,47,121) == True:
            self.trace_rectangle(40*scale,112*scale,7*scale,9*scale,name="arrow")
            resu=2
        elif self.is_arrow(40,120,47,129) == True:
            resu=3
            self.trace_rectangle(40*scale,120*scale,7*scale,9*scale,name="arrow")
        elif self.is_arrow(40,128,47,137) == True:
            resu=4
            self.trace_rectangle(40*scale,128*scale,7*scale,9*scale,name="arrow")
        else:
            resu=None
        return resu

    async def main(self,view):
        task1 = asyncio.create_task(self.game_analysis())
        task2 = asyncio.create_task(self.show_analysis(view))
        await asyncio.gather(task1, task2)

    def run(self,view=True):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.main(view))

if __name__ == "__main__":
    game = Game("mGBA - 0.10.1")

    @game.event
    async def on_combat():
        print(game.json_info)
        user_input = await asyncio.wait_for(asyncio.get_event_loop().run_in_executor(None, input, 'What you do?'), timeout=None)
        try:
            await game.attack(int(user_input))
        except:
            print("error")
            game.escape()

    game.run()