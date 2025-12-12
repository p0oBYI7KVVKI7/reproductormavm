#librerias
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk
from pymkv import MKVFile
import tkinter as tk
import subprocess
import threading
import argparse
import pygame
import shutil
import time
import json
import vlc
import cv2
import os

#scripts para otros procesos
import menus
from mavm import MaVM

pygame.mixer.init()
try:
    shutil.rmtree(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp'))   #borra la carpeta completa
    os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp'))
except:
    os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp'))

try:
    shutil.rmtree(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp_frames'))   #borra la carpeta completa
    os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp_frames'))
except:
    os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp_frames'))

class ventana:
    def __init__(self, ventana_tk, file):
        #ventana
        self.ventana_tk = ventana_tk
        self.ventana_tk.title("reproductor MaVM")
        self.ventana_tk.geometry("800x450")
        self.ventana_tk.minsize(800,450)
        self.ventana_tk.config(bg='gray')
        self.ventana_tk.protocol("WM_DELETE_WINDOW", exit)


        #variables
        self.file = file
        self.raiz_proyecto = os.path.dirname(os.path.abspath(__file__))
        print(self.raiz_proyecto)
        self.carpeta_temporal = os.path.join(self.raiz_proyecto, 'temp')
        self.carpeta_temporal_frames = os.path.join(self.raiz_proyecto, 'temp_frames')
        self.resolution_menu = [False, None]
        self.detectar_botones = ""
        self.objetos_menu = []
        self.used_vid = {}


        #objetos
        #abrir un archivo
        archivos = tk.Button(self.ventana_tk, text="archivos", command=self.archivos_ventana)
        archivos.place(x=0,y=0,width=80,height=16)

        self.reproductor = tk.Frame(self.ventana_tk, bg='black')
        self.reproductor.place(x=0,y=20)

        self.atras_boton = tk.Button(self.ventana_tk, text="<-10s", command=self.detectar_botones_fun_atra)
        self.atras_boton.place(x=0,y=430,width=20,height=16)

        self.adelante_boton = tk.Button(self.ventana_tk, text="10s->", command=self.detectar_botones_fun_adel)
        self.adelante_boton.place(x=780,y=430,width=20,height=16)

        self.play_boton = tk.Button(self.ventana_tk, text="play/pause", command=self.detectar_botones_fun_stop)
        self.play_boton.place(x=780,y=430,width=20,height=16)

        self.ventana_tk.after(50, self.actalizar_medidas)


        #codigo
        if self.file:
            self.repdorucir()
    
    def detectar_botones_fun(self, boton):
        self.detectar_botones = ""
        self.ventana_tk.after(110, detectar_botones_fun)

    def detectar_botones_fun_atra(self):
        self.detectar_botones = "atras"
        self.ventana_tk.after(110, detectar_botones_fun)

    def detectar_botones_fun_adel(self):
        self.detectar_botones = "adelante"
        self.ventana_tk.after(110, detectar_botones_fun)

    def detectar_botones_fun_stop(self):
        self.detectar_botones = "stop-play"
        self.ventana_tk.after(110, detectar_botones_fun)

    def archivos_ventana(self):
        self.file = filedialog.askopenfilename(title='buscar video MaVM', filetypes=(('video MaVM', '*.mavm'),('todos los archivos', '*.*')))
        print(self.file)
        self.repdorucir()

    def actalizar_medidas(self):
        try:
            ancho_ventana = self.ventana_tk.winfo_width()
            alto_ventana = self.ventana_tk.winfo_height()
            
            interfaz_alto = max(self.ventana_tk.winfo_height()*.05,16)
            interfaz_ancho = max(self.ventana_tk.winfo_width()*.0625,50)
            play_ancho = max(self.ventana_tk.winfo_width()*.1875,150)

            self.reproductor.config(width=ancho_ventana,height=alto_ventana-(20+4+interfaz_alto))

            self.atras_boton.place(x=int(ancho_ventana/3)-interfaz_ancho/2,y=alto_ventana-interfaz_alto,width=interfaz_ancho,height=interfaz_alto)

            self.play_boton.place(x=int(ancho_ventana/2)-play_ancho/2,y=alto_ventana-interfaz_alto,width=play_ancho,height=interfaz_alto)

            self.adelante_boton.place(x=int(2*ancho_ventana/3)-interfaz_ancho/2,y=alto_ventana-interfaz_alto,width=interfaz_ancho,height=interfaz_alto)

            self.reproductor.update_idletasks()
        except:
            pass
        self.ventana_tk.after(10, self.actalizar_medidas)

    def start(self):
        for widget in self.reproductor.winfo_children():
            widget.destroy()  #elimina cada widget
        
        metadata_path   = self.contenido_dat['metadata.json']
        start_menu_path = self.contenido_dat['start.json']
        
        metadata_file = open(metadata_path, 'r')
        metadata_text = metadata_file.read()
        metadata_json = json.loads(metadata_text)
        metadata_file.close()

        start_menu_file = open(start_menu_path, 'r')
        start_menu_text = start_menu_file.read()
        start_menu_json = json.loads(start_menu_text)
        start_menu_file.close()

        self.video_mavm_version = metadata_json["mavm_version"]
        if not(self.video_mavm_version in ['v.2.1.0']):
            messagebox.showerror("error de version de archivo", "la version de archivo no es compatible. Este programa solo soporta la v.2.1.0")
            exit()
        print(self.video_mavm_version)

        version_compatible = menus.version_formato(self.video_mavm_version)[0]
        print(version_compatible)

        descripcion = tk.Label(self.reproductor,text=metadata_json["descripcion"]["text"],fg="#ffffff",background="black")
        descripcion.place(x=self.reproductor.winfo_width()//2-4*len(metadata_json["descripcion"]["text"]),y=self.reproductor.winfo_height()//2)
        self.reproductor.update_idletasks()
        print(metadata_json["descripcion"]["text"])

        for i in range(1,metadata_json["descripcion"]["duration"]*100):
            time.sleep(1/100)
        
        self.menu(start_menu_json)

    def menu(self, menu_json):
        self.loop_comandos_on = False
        self.objetos_menu = []
        self.used_vid = {}
        y = True
        for widget in self.reproductor.winfo_children():
            try:
                if widget is self.espacio_mv:
                    y = False
                else: 
                    widget.destroy()  #elimina cada widget
            except:
                widget.destroy()  #elimina cada widget
        
        #crear espacio para menu y video

        if y:
            self.espacio_mv = tk.Frame(self.reproductor, bg='white')
            self.espacio_mv.place()
        else:
            for widget_mv in self.espacio_mv.winfo_children():
                widget_mv.destroy()
        
        menu_dat = menus.version_formato(self.video_mavm_version)
        lista_comandos = menu_dat[1](menu_json).lista_comandos
        print("lc",lista_comandos)

        self.resolution_menu = [True, lista_comandos["resolucion"]]
        self.menu_resize()

        #self.objetos_menu = 
        #comando[1]["imagen"]
        print("start:",lista_comandos["start"])
        for comando in lista_comandos["start"]:
            print("lcc", comando)
            t = self.comnado_ejecutar(comando, self.espacio_mv)
            #time.sleep(t)
            time.sleep(16/1000)
        
        print(lista_comandos["loop"])
        if 0 == len(lista_comandos["loop"]):
            pass
        else:
            print("loop:",lista_comandos["loop"])
            self.loop_comandos_on = True
            self.menu_loop(lista_comandos["loop"])

    def menu_loop(self, lista_comandos):
        if self.loop_comandos_on:
            for comando in lista_comandos:
                if self.loop_comandos_on:
                    #print("lcc", comando)
                    t = self.comnado_ejecutar(comando, self.espacio_mv)
                    #time.sleep(t)
                    time.sleep(t)
                    if not(self.loop_comandos_on):
                        break
            time.sleep(10/1000)
            #threading.Thread(target=lambda: self.menu_loop(lista_comandos)).start()
            self.ventana_tk.after(10, lambda: self.menu_loop(lista_comandos))
        else:
            pass

    def comnado_ejecutar(self, comando, v):
            t = 16/1000
            #print("contenido comando:", comando)
            if comando[0] == "image":
                imagen_file = Image.open(self.contenido_dat[comando[1]["imagen"]])
                imagen = ImageTk.PhotoImage(imagen_file)
                if "create" in comando[1].keys():
                    self.objetos_menu.append({"id":comando[1]["create"],"objeto":tk.Label(v, image=imagen), "cordenadas":comando[1]["coordinates"], "imagen":imagen_file})
                    self.objetos_menu[len(self.objetos_menu)-1]["objeto"].image = imagen
                    self.objetos_menu[len(self.objetos_menu)-1]["objeto"].place(x=0,y=0)
                    print(self.objetos_menu[len(self.objetos_menu)-1])
                elif "edit" in comando[1].keys():
                    print("Buscando objeto con id:", comando[1]["edit"])
                    for i in range(len(self.objetos_menu)-1):
                        if "id" in self.objetos_menu[i].keys():
                            if self.objetos_menu[i]["id"] == comando[1]["edit"]:
                                print("Objeto encontrado:", self.objetos_menu[i])
                                self.objetos_menu[i]["cordenadas"] = comando[1]["coordinates"]
                                self.objetos_menu[i]["imagen"] = imagen_file
                                self.objetos_menu[i]["objeto"].place(x=0,y=0)
                                print(self.objetos_menu[i])
            elif comando[0] == "text":
                self.objetos_menu.append({"objeto": tk.Label(v,text=comando[1]["text"],fg="#808080"), "cordenadas":comando[1]["coordinates"]})
            elif comando[0] == "button":
                if "create" in comando[1].keys():
                    self.objetos_menu.append({"id":comando[1]["create"],"objeto":tk.Button(v, text=comando[1]["title"],bg=f'#{comando[1]["color"][0]:02x}{comando[1]["color"][1]:02x}{comando[1]["color"][2]:02x}'), "cordenadas":comando[1]["coordinates"]})
                    self.objetos_menu[len(self.objetos_menu)-1]["objeto"].place()
                    if "command" in comando[1].keys():
                        self.objetos_menu[len(self.objetos_menu)-1]["objeto"].config(command=lambda: self.ejecutar_boton(comando[1]["command"]))
                    if "command4selection" in comando[1].keys():
                        self.objetos_menu[len(self.objetos_menu)-1]["objeto"].bind("<Enter>", lambda e: self.ejecutar_boton(comando[1]["command4selection"]))
                    if "command4no_selection" in comando[1].keys():
                        self.objetos_menu[len(self.objetos_menu)-1]["objeto"].bind("<Leave>", lambda e: self.ejecutar_boton(comando[1]["command4no_selection"]))
                elif "edit" in comando[1].keys():
                    for i in range(len(self.objetos_menu)):
                        if "id" in self.objetos_menu[i].keys():
                            if self.objetos_menu[i]["id"] == comando[1]["edit"]:
                                self.objetos_menu[i] = {"id":comando[1]["edit"],"objeto":self.objetos_menu[i]["objeto"].config(text=comando[1]["title"]), "cordenadas":comando[1]["coordinates"]}
            elif comando[0] == "sound":
                print("TIPO:", type(comando[1]))
                print("VALOR:", comando[1])
                if "create" in comando[1].keys():
                    self.objetos_menu.append({"id":comando[1]["create"],"objeto":pygame.mixer.Sound(self.contenido_dat[comando[1]["sound"]])})
                    self.objetos_menu[len(self.objetos_menu)-1]["objeto"].play()
                    self.objetos_menu[len(self.objetos_menu)-1]["objeto"].set_volume(comando[1]["volume"]/100)
                    print("sonido play")
                elif "edit" in comando[1].keys():
                    for i in range(len(self.objetos_menu)-1):
                        if "id" in self.objetos_menu[i].keys():
                            if self.objetos_menu[i]["id"] == comando[1]["edit"]:
                                self.objetos_menu[i]["objeto"].set_volume(comando[1]["volume"]/100)
            elif comando[0] == "time":
                if "wait" in comando[1].keys():
                    tiempo = comando[1]["wait"][0]
                    unidad = comando[1]["wait"][1]
                    if unidad == "seconds":
                        t = tiempo
                    elif unidad == "minutes":
                        t = tiempo*60
                    elif unidad == "hours":
                        t = iempo*3600
            elif comando[0] == "teleport":
                self.teleport(comando[1]["ubicaciones"])
            elif comando[0] == "video":
                if not("restart" in comando[1].keys()):
                    file, extension = os.path.splitext(comando[1]["video"])

                    try:
                        os.makedirs(os.path.join(self.carpeta_temporal_frames,file))
                    except:
                        shutil.rmtree(os.path.join(self.carpeta_temporal_frames),file)
                        os.makedirs(os.path.join(self.carpeta_temporal_frames,file))
                    
                    subprocess.run(["ffmpeg","-i",self.contenido_dat[comando[1]["video"]],"frame_%04d.png"], cwd=f"{self.carpeta_temporal_frames}/{file}")
                    subprocess.run(["ffmpeg","-i",self.contenido_dat[comando[1]["video"]],"-vn","-c:a","liboups",f"{file}.opus"], cwd=f"{self.carpeta_temporal_frames}")
                
                if "create" in comando[1].keys():
                    self.objetos_menu.append({"id":comando[1]["create"],"objeto":tk.Label(v), "cordenadas":comando[1]["coordinates"], "video":file, "video_path":self.contenido_dat[comando[1]["video"]]})
                    self.objetos_menu[len(self.objetos_menu)-1]["objeto"].place(x=0,y=0)
                    print(self.objetos_menu[len(self.objetos_menu)-1])

                    fps = self.get_fps(self.objetos_menu[len(self.objetos_menu)-1]["video_path"])

                    self.video_r(len(self.objetos_menu)-1, file, fps, self.contenido_dat[comando[1]["video"]])
                elif "restart" in comando[1].keys():
                    for i in range(len(self.objetos_menu)):
                        if "id" in self.objetos_menu[i].keys():
                            if self.objetos_menu[i]["id"] == comando[1]["restart"]:
                                print('self.objetos_menu[i]["id"] == comando[1]["restart"]')
                                if not(self.used_vid[self.objetos_menu[i]["video"]][0]):
                                    print('not(self.used_vid[self.objetos_menu[i]["video"]][0])', not(self.used_vid[self.objetos_menu[i]["video"]][0]))
                                    self.used_vid[self.objetos_menu[i]["video"]] = [True,0]
                                    
                                    fps = self.get_fps(self.objetos_menu[i]["video_path"])

                                    self.video_r(i, self.objetos_menu[i]["video"], fps, self.objetos_menu[i]["video_path"])
                elif "edit" in comando[1].keys():
                    for i in range(len(self.objetos_menu)-1):
                        if "id" in self.objetos_menu[i].keys():
                            if self.objetos_menu[i]["id"] == comando[1]["edit"]:
                                self.objetos_menu[i].append({"id":comando[1]["create"],"objeto":tk.Label(v), "cordenadas":comando[1]["coordinates"], "video":file, "video_path":self.contenido_dat[comando[1]["video"]]})
                                elf.objetos_menu[len(self.objetos_menu)-1]["objeto"].place(x=0,y=0)
                                print(self.objetos_menu[len(self.objetos_menu)-1])
            return t

    def teleport(self, paths):
        print("h")
        print(paths)
        if type(paths) == type([]):
            for path in paths:
                self.teleport(path)
        else:
            self.loop_comandos_on = False
            nombre, extension = os.path.splitext(paths)
            if extension == ".mkv":
                self.video(self.contenido_dat[paths])
            elif extension == ".json":
                print("path_menu",self.contenido_dat[paths])
                menu_f = open(self.contenido_dat[paths])
                menu_t = menu_f.read()
                menu_j = json.loads(menu_t)
                menu_f.close()
                print("menu:",menu_j)
                time.sleep(16/1000)
                self.menu(menu_j)

    def video_r(self, vid, file_name, fps, video_path):
        print("video-r1")
        print(f"{self.carpeta_temporal_frames}/{file_name}")
        frames = sorted(os.listdir(f"{self.carpeta_temporal_frames}/{file_name}"))
        print("ff", frames)
        self.used_vid[file_name] = [False,0]
        try:
            self.used_vid[file_name][2] = pygame.mixer.Sound(f"{self.carpeta_temporal_frames}/{video_path}.opus")
            self.used_vid[file_name][2].play()
        except:
            pass
        print("vp", video_path)
        self.used_vid[file_name] = [True,0]
        video_hilo = threading.Thread(target=lambda: self.update_frame_vid(frames,fps,file_name,video_path,vid))
        video_hilo.start()

    def update_frame_vid(self, frames, fps, file_name, video_path, vid):
        print("video-r2")
        for frame in frames:
            if self.used_vid[file_name][0] and self.get_frames_num(video_path) > self.used_vid[file_name][1]:
                try:
                    frame_file = os.path.join(os.path.join(self.carpeta_temporal_frames,file_name),frame)
                    imagen_file = Image.open(frame_file)
                    imagen = ImageTk.PhotoImage(imagen_file)
                    self.objetos_menu[vid]["objeto"].image = imagen
                    self.objetos_menu[vid]["imagen"] = imagen_file
                    self.used_vid[file_name][1] += 1
                    time.sleep(1/fps)
                    print(frame)
                except:
                    pass
            else:
                try:
                    self.used_vid[file_name][2].stop()
                except:
                    pass
                self.used_vid[file_name][0] = False
        self.used_vid[file_name][0] = False
    
    def get_frames_num(self, filename):
        cmd = [
            "ffprobe", "-v", "error", "-count_frames",
            "-select_streams", "v:0",
            "-show_entries", "stream=nb_read_frames",
            "-of", "default=nokey=1:noprint_wrappers=1",
            filename
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return int(result.stdout.strip())

    def get_fps(self, filename):
        cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=r_frame_rate",
            "-of", "json", filename
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        data = json.loads(result.stdout)
        rate = data["streams"][0]["r_frame_rate"]
        num, den = map(int, rate.split('/'))
        fps = num / den

        print(f"FPS: {fps}")
        return fps
    
    def ejecutar_boton(self, comandos):
        if type(comandos[0]) == type([]):
            print("op")
            print(comandos)
            for comando in comandos:
                print("op2")
                print(comando)
                self.ejecutar_boton(comando)
        else:
            time.sleep(16/1000)
            self.comnado_ejecutar(comandos,self.espacio_mv)

    def menu_resize(self):
        try:
            if self.resolution_menu[0]:
                reproductor_ancho = self.reproductor.winfo_width()
                reproductor_alto = self.reproductor.winfo_height()


                escala_ancho = self.resolution_menu[1][0]
                escala_alto = self.resolution_menu[1][1]

                escala_relacion_de_aspecto = escala_ancho/escala_alto
                reproductor_relacion_de_aspecto = reproductor_ancho/reproductor_alto

                if escala_relacion_de_aspecto < reproductor_relacion_de_aspecto: #mas ancho que el menu
                    espacio_mv_ancho = reproductor_alto*escala_relacion_de_aspecto
                    espacio_mv_x     = (reproductor_ancho-espacio_mv_ancho)//2
                    espacio_mv_alto  = reproductor_alto
                    espacio_mv_y     = 0
                else: #mas alto que el menu
                    espacio_mv_alto  = reproductor_ancho/escala_relacion_de_aspecto
                    espacio_mv_y     = (reproductor_alto-espacio_mv_alto)//2
                    espacio_mv_ancho = reproductor_ancho
                    espacio_mv_x     = 0
                
                self.espacio_mv.place(x=espacio_mv_x,y=espacio_mv_y,width=espacio_mv_ancho,height=espacio_mv_alto)

                diferencia_escala_espacio_mv = [espacio_mv_ancho/escala_ancho,espacio_mv_alto/escala_alto]
                
                for objeto in self.objetos_menu:
                    if "video_r" in objeto.keys():
                        cordenadas = [0,0,reproductor_ancho,reproductor_alto]
                        
                        ancho_imagen=int(cordenadas[2]*diferencia_escala_espacio_mv[0])-int(cordenadas[0]*diferencia_escala_espacio_mv[0])
                        alto_imagen=int(cordenadas[3]*diferencia_escala_espacio_mv[1])-int(cordenadas[1]*diferencia_escala_espacio_mv[1])

                        imagen =  ImageTk.PhotoImage(objeto["imagen"].resize((ancho_imagen,alto_imagen), Image.Resampling.LANCZOS))

                        objeto["objeto"].config(image=imagen)
                        objeto["objeto"].image = imagen

                        objeto["objeto"].place(x=int(cordenadas[0]*diferencia_escala_espacio_mv[0]),
                                            y=int(cordenadas[1]*diferencia_escala_espacio_mv[1]),
                                            width=int(cordenadas[2]*diferencia_escala_espacio_mv[0])-int(cordenadas[0]*diferencia_escala_espacio_mv[0]),
                                            height=int(cordenadas[3]*diferencia_escala_espacio_mv[1])-int(cordenadas[1]*diferencia_escala_espacio_mv[1]))
                    elif "imagen" in objeto.keys():
                        cordenadas = objeto["cordenadas"]

                        ancho_imagen=int(cordenadas[2]*diferencia_escala_espacio_mv[0])-int(cordenadas[0]*diferencia_escala_espacio_mv[0])
                        alto_imagen=int(cordenadas[3]*diferencia_escala_espacio_mv[1])-int(cordenadas[1]*diferencia_escala_espacio_mv[1])

                        imagen =  ImageTk.PhotoImage(objeto["imagen"].resize((ancho_imagen,alto_imagen), Image.Resampling.LANCZOS))

                        objeto["objeto"].config(image=imagen)
                        objeto["objeto"].image = imagen

                        objeto["objeto"].place(x=int(cordenadas[0]*diferencia_escala_espacio_mv[0]),
                                            y=int(cordenadas[1]*diferencia_escala_espacio_mv[1]),
                                            width=int(cordenadas[2]*diferencia_escala_espacio_mv[0])-int(cordenadas[0]*diferencia_escala_espacio_mv[0]),
                                            height=int(cordenadas[3]*diferencia_escala_espacio_mv[1])-int(cordenadas[1]*diferencia_escala_espacio_mv[1]))
                    else:
                        cordenadas = objeto["cordenadas"]

                        objeto["objeto"].place(x=int(cordenadas[0]*diferencia_escala_espacio_mv[0]),
                                            y=int(cordenadas[1]*diferencia_escala_espacio_mv[1]),
                                            width=int(cordenadas[2]*diferencia_escala_espacio_mv[0])-int(cordenadas[0]*diferencia_escala_espacio_mv[0]),
                                            height=int(cordenadas[3]*diferencia_escala_espacio_mv[1])-int(cordenadas[1]*diferencia_escala_espacio_mv[1]))

            self.reproductor.update_idletasks()
            self.espacio_mv.update_idletasks()
        except:
            pass
        self.ventana_tk.after(10, self.menu_resize)

    def repdorucir(self):
        paths = MaVM.extrac_type_all(file=self.file, output_folder=self.carpeta_temporal, content_type=None)
        #videos = MaVM.extrac_type_all(file=self.file, output_folder=self.carpeta_temporal, content_type="video/x-matroska")

        self.contenido_dat = {}
        for path in paths:
            directorio, archivo = os.path.split(path)
            self.contenido_dat[archivo] = path
            print(archivo)
        self.start()

    def video(self,video_path):
        subprocess.run(['mpv', video_path])

    def _video(self,video_path):
        self.loop_comandos_on = False
        self.objetos_menu = []
        self.used_vid = {}
        for widget in self.reproductor.winfo_children():
            try:
                if widget is self.espacio_mv:
                    y = False
                else: 
                    widget.destroy()  #elimina cada widget
            except:
                widget.destroy()  #elimina cada widget
        
        for widget in self.espacio_mv.winfo_children():
            try:
                if widget is self.espacio_mv:
                    y = False
                else: 
                    widget.destroy()  #elimina cada widget
            except:
                widget.destroy()  #elimina cada widget
        
        archivo = os.path.basename(video_path)

        file_name, extension = os.path.splitext(archivo)
        
        try:
            shutil.rmtree(os.path.join(self.carpeta_temporal_frames,file_name))
            os.makedirs(os.path.join(self.carpeta_temporal_frames,file_name))
        except:
            os.makedirs(os.path.join(self.carpeta_temporal_frames,file_name))
        
        subprocess.run(["ffmpeg","-i",video_path,"frame_%04d.png"], cwd=f"{os.path.join(self.carpeta_temporal_frames,file_name)}")
        subprocess.run(["ffmpeg","-i",video_path,"-vn","-c:a","liboups",f"{file_name}.opus"], cwd=f"{self.carpeta_temporal_frames}")
        
        #subprocess.run(['mpv', video_path])

        fps = self.get_fps(video_path)

        try:
            audio = [True, pygame.mixer.Sound(os.path.join(self.carpeta_temporal_frames,f"{file_name}.opus"))]
        except:
            audio = [False]
        #audi0.set_volume(50/100)

        frames = sorted(os.listdir(f"{self.carpeta_temporal_frames}/{file_name}"))
        
        self.used_vid[file_name] = [False,0]
        try:
            self.used_vid[file_name][2] = pygame.mixer.Sound(f"{self.carpeta_temporal_frames}/{video_path}.opus")
            self.used_vid[file_name][2].play()
        except:
            pass
        print("vp", video_path)
        
        frame_num  = 0
        frames_num = len(frames)-1

        self.objetos_menu.append({"objeto":tk.Label(self.espacio_mv), "video_r":archivo, "video_path":video_path, "imagen": None})
        vid = len(self.objetos_menu)-1

        if audio[0]:
            audio[1].play()
        
        self.video_b(fps=fps,frames=frames,file_name=file_name,vid=vid,frame_num=frame_num,frames_num=frame_num,audio=audio,play=True)

    def video_b(self,fps,frames,file_name,vid,frame_num,frames_num,audio,play):
        #play = True
        #while not(frame_num == frames_num):
            if not(frame_num == frames_num):
                pass
            elif play:
                try:
                    frame = frames[frame_num]

                    #frame_file_path = os.path.join(os.path.join(self.carpeta_temporal_frames,file_name),frame)
                    #imagen_file = Image.open(frame_file_path)
                    #imagen = ImageTk.PhotoImage(imagen_file)
                    #self.objetos_menu[vid]["objeto"].image = imagen
                    #self.objetos_menu[vid]["imagen"] = imagen_file
                    #self.used_vid[file_name][1] += 1
            
                    segundos_por_fotograma = 1/fps
                    print(frame)
                    fotogramas_cambio = int(10*fps)
                    segundos_cambio = fotogramas_cambio/fps

                    self.ventana_tk.after(0, lambda: self.update_frame_vid_b(frame=frame,file_name=file_name,vid=vid))
                    for i in range(1,40):
                            time.sleep(segundos_por_fotograma/40)
                            accion = self.detectar_botones
                    
                    if accion == "stop-play":
                        if audio[0]:
                            audio[1].pause()
                        play = False
                    elif accion == "adelante":
                        if (frame_num+fotogramas_cambio)>frames_num or (frame_num+fotogramas_cambio)==frames_num:
                            frame_num = frames_num
                            if audio[0]:
                                audio[1].play(start=frame_num/fps)
                        else:
                            if audio[0]:
                                pos_actual = pygame.mixer.music.get_pos() / 1000
                                audio[1].play(start=pos_actual+segundos_cambio)
                            frame_num += fotogramas_cambio
                    elif accion == "atras":
                        if (frame_num-fotogramas_cambio)<0 or (frame_num<fotogramas_cambio)==0:
                            frame_num = frames_num
                            if audio[0]:
                                audio[1].play(start=frame_num/fps)
                        else:
                            if audio[0]:
                                pos_actual = pygame.mixer.music.get_pos() / 1000
                                audio[1].play(start=pos_actual-segundos_cambio)
                            frame_num -= fotogramas_cambio
                    else:
                        frame_num +=1

                    self.ventana_tk.after(int(segundos_por_fotograma*1000), lambda: self.video_b(self,fps,frames,file_name,vid,frame_num,frames_num,audio,play))
                except Exception as e:
                    print(e)
            else:
                accion = self.detectar_botones
                if frame[0] == "stop-play":
                    play = True
                    if audio[0]:
                        audio[1].unpause()
    
    def update_frame_vid_b(self, frame, file_name, vid):
                print("video-r2")
            #if self.used_vid[file_name][0] and self.get_frames_num(video_path) > self.used_vid[file_name][1]:
                try:
                    frame_file = os.path.join(os.path.join(self.carpeta_temporal_frames,file_name),frame)
                    imagen_file = Image.open(frame_file)
                    imagen = ImageTk.PhotoImage(imagen_file)
                    self.objetos_menu[vid]["objeto"].image = imagen
                    self.objetos_menu[vid]["imagen"] = imagen_file
                    self.used_vid[file_name][1] += 1
                    print(frame)
                except Exception as e:
                    print(e)
            #else:
             #   try:
              #      self.used_vid[file_name][2].stop()
               # except:
                #    pass
                #self.used_vid[file_name][0] = False

def args():
    parser = argparse.ArgumentParser(description="reproductor MaVM")
    parser.add_argument("file", nargs='?', help="ruta del video .mavm")
    
    args_var = parser.parse_args()
    
    if args_var.file:
        if not('.mavm' in args_var.file.lower()):
            print("el archivo debe ser .mavm")
            exit()
        elif not(os.path.exists(args_var.file)):
            print("el archivo no existe")
            exit()
        else:
            file = os.path.abspath(args_var.file)
            ventana_tk = tk.Tk()
            ventana(ventana_tk=ventana_tk, file=file)
            ventana_tk.mainloop()
    else:
        ventana_tk = tk.Tk()
        ventana(ventana_tk, None)
        ventana_tk.mainloop()

args()
