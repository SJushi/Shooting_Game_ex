from email.mime import image
from operator import pos
from pydoc import text
from random import Random
import random
import tkinter
from tkinter.font import BOLD
import turtle
import pygame
import time
from pygame import color
import math

#장면전환
class SceneChange:
    def __init__(self):
        self.window = tkinter.Tk() #윈도우 형성
        self.window.title("슈팅게임")
        self.window.geometry("1024x768")
        self.window.resizable(0,0)
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.scene_idx = 0

        #게임과 메뉴 생성
        self.game = MainGame(self.window)
        self.menu = Menu(self.window)
        self.menu.pack() #메뉴를 먼저 호출함

        self.canvas_list = [] #캔버스리스트에 게임과 메뉴 추가
        self.canvas_list.append(self.game)
        self.canvas_list.append(self.menu)
        
        self.window.bind("<KeyPress>", self.keyPressHandler) #키바인딩도 해주고
        self.window.bind("<KeyRelease>", self.keyReleaseHandler)

        #슴슴하니까 음악도 삽입하기
        pygame.mixer.init()
        self.Menu_music_list = [
            pygame.mixer.Sound("../Songs/Main.mp3"),
            pygame.mixer.Sound("../Songs/Main2.mp3"),
            pygame.mixer.Sound("../Songs/Main3.mp3")
        ]
        for music in self.Menu_music_list:
            music.set_volume(0.4)

        self.Game_music = pygame.mixer.Sound("../Songs/Battle.mp3")
        self.Game_music.set_volume(0.4)

        self.now_music = None

        self.Loop() # 게임 루프 걸어주기
        self.window.mainloop() #TKinter 이벤트루프 걸어주기


    def Menu_music(self):
        if self.now_music:
            self.now_music.stop()
        self.now_music = random.choice(self.Menu_music_list)
        self.now_music.play(loops=-1)

    def Loop(self):

        if self.scene_idx == 0: #메뉴
            self.menu.display()
            if getattr(self, "game_music_playing", False): 
                self.Game_music.stop()
                self.game_music_playing = False
            if not getattr(self, "menu_music_playing", False):
                self.Menu_music()
                self.menu_music_playing = True

        elif self.scene_idx == 1: #게임
            self.game.display()
            if self.now_music:
                self.now_music.stop()
                self.now_music = None
                self.menu_music_playing = False
            if not getattr(self, "game_music_playing", False):
                self.Game_music.play(loops=-1)
                self.game_music_playing = True

        self.window.after(33, self.Loop)

    
    def on_closing(self):
        for canvas in self.canvas_list:
            canvas.destroy()

        if self.now_music:
            self.now_music.stop()
        if hasattr(self, 'Game_music'):
            self.Game_music.stop()

        self.window.destroy()

    def keyReleaseHandler(self, event):

        result = -1

        if self.scene_idx == 0: #0일때 메뉴
            result = self.menu.keyReleaseHandler(event)

            if result == 1:
                self.on_closing()
                return()    

        elif self.scene_idx == 1: #1일때 게임
            result = self.game.keyReleaseHandler(event)

        if self.scene_idx == 0 and result == 0:
            self.scene_idx = 1 #0일때 1받으면 게임오픈
            self.menu.unpack()
            self.game.GameOver = False
            self.game.reset()
            self.game.start_time = time.time()
            self.game.pack()

        elif self.scene_idx == 1 and result == 0:
            self.game.reset() #게임은 초기화시킴
            self.game.unpack()
            self.scene_idx = 0 #1일때 0받으면 메뉴오픈
            self.menu.pack()

    def keyPressHandler(self,event):
        if self.scene_idx == 0:  # 메뉴씬이면 메뉴에서 처리
            if event.keycode == 27:
                self.on_closing()    # 메뉴에서 ESC키 누르면 종료
        elif self.scene_idx == 1:  # 게임씬
            result = self.game.keyPressHandler(event)
            if result == 0:  # ESC 키 누름
                self.game.reset()
                self.game.keys.clear() # 누르고 있는 키 초기화
                self.scene_idx = 0
                self.menu.pack()
                self.game.unpack()
                self.game.canvas.update()


#메뉴
class Menu:
    def __init__(self,window):
        self.window = window
        self.menu_idx = 0
        self.is_packed = False

        self.canvas = tkinter.Canvas(self.window, bg = "black")
        self.canvas.create_text(512,320, fill="white", text="Start")
        self.canvas.create_text(512,448, fill="white", text="Exit")
        self.canvas.create_text(512,640, fill="white", text="Z키 확인 및 발사, 화살표키로 움직이기")

        self.arrowsss = tkinter.PhotoImage(file="../image/arrow.png").subsample(15)
        self.arrow = self.canvas.create_image(320,320, image = self.arrowsss, tags = "arrow")

    def display(self):
        pass

    def pack(self):
        if not self.is_packed:
            self.canvas.pack(expand=True, fill=tkinter.BOTH)
            self.is_packed = True

    def unpack(self):
        if self.is_packed:
            self.canvas.pack_forget()
            self.is_packed = False

    def keyReleaseHandler(self, event):
        if event.keycode == 38 and self.menu_idx > 0: # 윗키
            self.menu_idx = self.menu_idx - 1
            self.canvas.move(self.arrow, 0, -128)
            return -1
        elif event.keycode == 40 and self.menu_idx < 1: # 아래키
            self.menu_idx = self.menu_idx + 1
            self.canvas.move(self.arrow, 0, 128)
            return -1
        elif event.keycode == 90: # Z키
            return self.menu_idx

    def destroy(self):
        self.canvas.destroy()

#적
class Enemy:
    def __init__(self, canvas, images, id, enemy_type, enemy_HP):
        self.__frame = 0
        self.id = 'en' + str(id)
        self.canvas = canvas
        self.enemy_type = enemy_type
        self.dir = 1
        self.enemy_HP = enemy_HP
        self.images = images[enemy_type]
        self.this = self.canvas.create_image(random.randint(40,980), 20, image = self.images, tags = self.id)

        #적 3 전용 변수
        self.E3_speed = 0.1

      
    def Update(self, player_x = None): #일단 none으로 해서 못받아올때 안터지게 만들기

        #적 3 전용 변수
        E3_x, E3_y =  self.canvas.coords(self.this)

        if self.enemy_type == 0:
            self.canvas.move(self.this, 0, random.randint(10, 20))

        elif self.enemy_type == 1:
            dir_t = time.time()
            self.canvas.move(self.this, math.sin(dir_t) * 8, random.randint(8, 16))

        elif self.enemy_type == 2:
            if player_x is None:
                dx = 0
            else:
                dx = (player_x - E3_x) * self.E3_speed
                self.canvas.move(self.this, dx, random.randint(3,8))
            
       
    def getPosition(self):
        return self.canvas.coords(self.this)

    def getID(self):
        return self.this

#게임
class MainGame:
    def __init__(self,window):
        self.window = window
        self.keys=set()
        self.is_packed = False
        self.lastTime = time.time()
        self.start_time = 0
        self.end_time = 0
        self.Level = 1  
        self.hp = 3
        self.GameOver = False
        
        #화면 생성  
        self.canvas = tkinter.Canvas(self.window, bg="black")

        
        #이미지 파일 가져오기
        self.ship0000 = tkinter.PhotoImage(file="../image/Ships/ship_0000.png").zoom(2)
        self.pov_ship = self.canvas.create_image(512,614, image = self.ship0000, tags = "pov_ship")

        self.fire = tkinter.PhotoImage(file="../image/Assets/PNG/Lasers/laserBlue05.png")

        self.BGimg = tkinter.PhotoImage(file="../image/BG/BG.png") # 화면크기는 1024,768임
        self.bg_h = self.BGimg.height() #배경 루프준비
        self.bg1 = self.canvas.create_image(512, self.bg_h//2, image=self.BGimg)
        self.bg2 = self.canvas.create_image(512, self.bg_h//2 - self.bg_h, image=self.BGimg)
        self.canvas.lower(self.bg1)
        self.canvas.lower(self.bg2) #레이어 가장 밑으로 보내야됨
        self.bgSpeed = 3


        #적
        self.enemy_img_num = 0
        self.enemy_images = [tkinter.PhotoImage(file="../image/Ships/ship_0018.png"), tkinter.PhotoImage(file="../image/Ships/ship_0017.png"),
                             tkinter.PhotoImage(file="../image/Ships/ship_0014.png")]

        self.enemy_list = []
        self.enemy_id = 0

        self.hp_text = self.canvas.create_text(80, 80, fill="white", text=f"HP = {self.hp}", font="Arial")
    
    def enemyManage(self):
        
        self.Level_update()

        en_HP = 1

        #적 아이디 할당해주기
        if (random.randint(0,5) == 0): #적 생성량 조절
            self.enemy_list.append(Enemy(self.canvas, self.enemy_images, self.enemy_id, 0, en_HP))
            self.enemy_id = self.enemy_id + 1

        if self.Level >= 2:
            en_HP = 2
            if (random.randint(0,10) == 0):
                self.enemy_list.append(Enemy(self.canvas, self.enemy_images, self.enemy_id, 1, en_HP))
                self.enemy_id = self.enemy_id + 1

        if self.Level >= 3:
            en_HP = 3

        if self.Level >= 4:
            if (random.randint(0,20) == 0):
                self.enemy_list.append(Enemy(self.canvas, self.enemy_images, self.enemy_id, 2, en_HP))

        if self.Level >= 5:
            en_HP = 4

        if self.Level >= 6:
            en_HP = 5

        if self.Level >= 7:
            if (random.randint(0,10) == 0):
                self.enemy_list.append(Enemy(self.canvas, self.enemy_images, self.enemy_id, 0, en_HP))
                self.enemy_id = self.enemy_id + 1

        if self.Level >= 8:
            en_HP = 6

        if self.Level >= 9:
            if (random.randint(0,10) == 0):
                self.enemy_list.append(Enemy(self.canvas, self.enemy_images, self.enemy_id, 1, en_HP))
                self.enemy_id = self.enemy_id + 1


        for en in self.enemy_list:
            player_pos = self.canvas.coords(self.pov_ship)
            player_x = player_pos[0]
            en.Update(player_x)

            if en.getPosition()[1] > 768 : # 아래로 가면 혼자 제거
                self.canvas.delete(en.getID())
                self.enemy_list.pop(self.enemy_list.index(en))

        
        #총알과 충돌 시 제거시키기
        fires = self.canvas.find_withtag("fire") 
        area = 20

        enemies_delete = [] #루프 끝나고 없애야되니까 리스트 깔아두기
        fires_delete = []

        for fire in fires:
            f_pos = self.canvas.coords(fire)
            if not f_pos:
                continue
            for en in self.enemy_list:
                en_pos = en.getPosition()
                if not en_pos:
                    continue
                if ((en_pos[0] - area < f_pos[0]) and (en_pos[0] + area > f_pos[0]) and (en_pos[1] - area < f_pos[1]) and (en_pos[1] + area > f_pos[1])):
                    en.enemy_HP -= 1
                    fires_delete.append(fire)
                    if en.enemy_HP <= 0:
                        enemies_delete.append(en)
                    break

        for fire in fires_delete:
            self.canvas.delete(fire)

        for en in enemies_delete:
            self.canvas.delete(en.getID())
            if en in self.enemy_list:
                self.enemy_list.remove(en)

        #키 누름
    def keyPressHandler(self,event):
        if event.keycode == 27: #esc키로 메뉴로 돌아감
            return 0
        elif event.keycode not in self.keys:
            self.keys.add(event.keycode)
        else: 
            self.keys.add(event.keycode) #esc 키가 아니면 세트에 추가함

        #키 땜
    def keyReleaseHandler(self,event):
        if self.GameOver:
            if event.keycode == 27:
                self.GameOver = False
                return 0
            return

        if event.keycode in self.keys:
            self.keys.remove(event.keycode)

    def display(self): #여기에 게임시스템 구현
        if self.GameOver: #게임오버 상태일 땐 화면정지
            return

        if not self.GameOver:
            time_recode = int(time.time() - self.start_time)
            minute = time_recode // 60
            second = time_recode % 60
        else:
            end_time = time_recode
        
        self.canvas.delete("timer")
        self.canvas.create_text(80,50, fill="white", text=f"Time : {minute}:{second}", font="Arial", tags="timer")

        pov_ship = self.canvas.find_withtag("pov_ship")
        for key in self.keys:
           if key == 39:
               self.canvas.move(self.pov_ship, 15, 0)
           if key == 37:
               self.canvas.move(self.pov_ship, -15, 0)
           if key == 90:
               now = time.time()
               if (now - self.lastTime) > 0.1: #연사제한 두기
                   self.lastTime = now
                   pos = self.canvas.coords(pov_ship)
                   self.canvas.create_image(pos[0],pos[1]-10, image = self.fire, tags="fire")

        player_pos = self.canvas.coords(self.pov_ship)
        if player_pos:
            area = 20
            for en in self.enemy_list:
                en_pos = en.getPosition()
                if ((en_pos[0] - area < player_pos[0]) and (en_pos[0] + area > player_pos[0]) and (en_pos[1] - area < player_pos[1]) and (en_pos[1] + area > player_pos[1])):
                    self.canvas.delete(en.getID())
                    self.enemy_list.pop(self.enemy_list.index(en)) 
                    self.hp -= 1
                    self.update_hp()
                    if self.hp <= 0:
                        self.GameOver = True
                        self.canvas.create_text(512,400, fill="white", text="Game Over", font=("Arial", 40, "bold"), tags="gameover_text")
                        self.keys.clear()

        #화면 밖으로 못나가게 막기
        ship_width = 16
        canvas_width = 1024

        if player_pos[0] < ship_width:
            self.canvas.coords(self.pov_ship, ship_width, player_pos[1]) #캔버스 끝자락에 닿으면 자리 고정
        elif player_pos[0] > canvas_width - ship_width:
            self.canvas.coords(self.pov_ship, canvas_width - ship_width, player_pos[1]) 

        #배경 루프시키기
        self.canvas.move(self.bg1, 0, self.bgSpeed) 
        self.canvas.move(self.bg2, 0, self.bgSpeed)

        bg1_pos = self.canvas.coords(self.bg1)
        bg2_pos = self.canvas.coords(self.bg2)

        if bg1_pos[1] >= self.bg_h + 384:
            self.canvas.coords(self.bg1, 512, bg2_pos[1] - self.bg_h)
        if bg2_pos[1] >= self.bg_h + 384:
            self.canvas.coords(self.bg2, 512, bg1_pos[1] - self.bg_h)


        #총알 움직임 설정
        fires = self.canvas.find_withtag("fire")

        for fire in fires:
            self.canvas.move(fire,0,-30)
            if self.canvas.coords(fire)[1] < 0:
                self.canvas.delete(fire)

        self.enemyManage()

    def update_hp(self):
        self.canvas.itemconfig(self.hp_text, text=f"HP : {self.hp}")

    def Level_update(self): #레벨 만들기
        time_recode = int(time.time() - self.start_time)
        self.Level = time_recode // 20 + 1 
         

    def pack(self):
        if not self.is_packed:
            self.canvas.pack(expand=True, fill=tkinter.BOTH)
            self.is_packed = True

    def unpack(self):
        if self.is_packed:
            self.canvas.pack_forget()
            self.is_packed = False

    def reset(self): # 게임 플레이 중 메뉴로 돌아왔을 때 초기화
        try:
            self.canvas.delete("gameover_text")
        except Exception:
            pass
        self.keys.clear()
        self.canvas.coords(self.pov_ship, 512, 614)
        self.canvas.update()
        for en in self.enemy_list:
            self.canvas.delete(en.getID())
        self.enemy_list.clear()
        self.enemy_id = 0
        self.hp = 3
        self.update_hp()
        self.Level = 1
        #나중에 추가될것도 까먹지 말고 초기화하기
        
    def destroy(self): # 종료 이벤트
        self.canvas.destroy()

if __name__=='__main__':
    SceneChange()