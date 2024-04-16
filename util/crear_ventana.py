import tkinter as tk
from tkinter import font
from threading import Thread
from matplotlib.figure import Figure
from config import color_cuerpo_principal, color_menu_lateral, color_barra_superior, color_menu_cursor_encima
import util.centrar_ventana as centrar_ventana
import util.until_imagenes as util_img
from serial import Serial
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from time import sleep

class CrearVentana(tk.Tk):

    def __init__(self):
        #Inicializamos los atributos y las funciones
        super().__init__()
        self.perfil = util_img.leer_imagen("./imagenes/monitoreo_ambiental.png", (100,100))
        self.logo = util_img.leer_imagen("./imagenes/logo.jpg", (800, 555))
        self.serial = Serial('/COM4',9600)
        self.graficando = False
        self.lista_datos = []
        self.lista_temperatura = []
        self.lista_humedad = []
        self.lista_dioxido = []
        self.lista_amoniaco = []
        self.posicion = 0


        self.Configurar_ventana()
        self.paneles()
        self.controles_barra_superior()
        self.controles_menu_lateral()
        self.controles_cuerpo(bandera=False)

    def Configurar_ventana(self):
        self.title('Monitoreo Ambiental')
        self.iconbitmap('./imagenes/monitoreo_ambiental.ico')
        w,h = 1024, 600
        self.geometry(f"{w}x{h}+0+0")
        centrar_ventana.centrar_ventana(self,w,h)

    def paneles(self):

        self.barra_superior = tk.Frame(
            self, bg=color_barra_superior, height=50)
        self.barra_superior.pack(side=tk.TOP, fill='both')

        self.menu_lateral = tk.Frame(self, bg=color_menu_lateral, width=150)
        self.menu_lateral.pack(side=tk.LEFT, fill='both', expand=False)

        self.cuerpo_principal = tk.Frame(self, bg=color_cuerpo_principal)
        self.cuerpo_principal.pack(side=tk.RIGHT, fill='both', expand=True)

    def controles_barra_superior(self):
        self.labelTitulo = tk.Label(self.barra_superior, text="Panel principal")
        self.labelTitulo.config(fg="#fff", font=(
            "Roboto", 15), bg=color_barra_superior, pady=10, width=16)
        self.labelTitulo.pack(side=tk.LEFT)
        

    def controles_menu_lateral(self):

        ancho_menu = 20
        alto_menu = 2
        font_awesome = font.Font(family='FontAwesome', size=15)

        self.labelPefil = tk.Label(self.menu_lateral, image=self.perfil, bg=color_menu_lateral)
        self.labelPefil.pack(side=tk.TOP, pady=10)

        #Creando Botones
        self.buttonDashBoard = tk.Button(self.menu_lateral, command=lambda: self.mostrar_grafico(bandera=False ))
        self.buttonHumedad = tk.Button(self.menu_lateral, command= lambda: self.mostrar_grafico(0, "Humedad", "orange", lista=self.lista_humedad))
        self.buttonTemperatura = tk.Button(self.menu_lateral, command= lambda: self.mostrar_grafico(1, "Temperatura", "blue",lista=self.lista_temperatura))
        self.buttonDioxido = tk.Button(self.menu_lateral, command= lambda: self.mostrar_grafico(2, "Co2", "green", lista=self.lista_dioxido))
        self.buttonAmoniaco = tk.Button(self.menu_lateral, command= lambda: self.mostrar_grafico(3, "Amoniaco", "black", lista=self.lista_amoniaco))

        buttons_info = [
            ("Dashboard", "\uf109", self.buttonDashBoard),
            ("Temperatura", "\uf2c8", self.buttonTemperatura),
            ("Humedad", "\ue4e4", self.buttonHumedad),
            ("Dioxido de carbono", "\uf72e", self.buttonDioxido),
            ("Amoniaco", "\uf0c3", self.buttonAmoniaco)
        ]

        for text, icon, button in buttons_info:
            self.configurar_boton_menu(button, text, icon, font_awesome, ancho_menu, alto_menu)

    def mostrar_grafico(self, parametro=None, nombre=None, color=None,lista=None,bandera=True):
        self.graficando = False

        if bandera:
            for i in range(len(self.lista_datos)):
                if i >= self.posicion and i >= len(self.lista_datos): 
                    self.lista_humedad.append(float(self.lista_datos[i][0])) 
                    self.lista_temperatura.append(float(self.lista_datos[i][1]))
                    self.lista_dioxido.append(float(self.lista_datos[i][2]))
                    self.lista_amoniaco.append(float(self.lista_datos[i][3]))
                    self.posicion +=1
        print(self.lista_humedad)
        sleep(1)

        hilo = Thread(target=self.controles_cuerpo, args=(parametro, nombre, color, lista, bandera))
        hilo.start()

    def controles_cuerpo(self, parametro=None, nombre=None, color=None,lista=None, bandera = False):
        if bandera:
            for widget in self.cuerpo_principal.winfo_children():
                widget.destroy()
            print(lista)
            data_en_tiempo_real = lista
            self.graficando = True
            fig = Figure(figsize=(4, 2), dpi=100)
            ax = fig.add_subplot(111) 
            canvas = FigureCanvasTkAgg(fig, self.cuerpo_principal)
                        
            while self.graficando:               
                line = self.serial.readline().decode('utf-8')
                if "," in line:
                    try:
                        toma_de_datos = list(line.split(","))
                        self.lista_datos.append(toma_de_datos)
                        dato = float(toma_de_datos[int(parametro)])
                        data_en_tiempo_real.append(dato)
                        ax.clear()                     
                        ax.plot(data_en_tiempo_real[-30:], label=nombre, color=color)
                        ax.legend()
                        canvas.draw()
                        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
                    except ValueError:
                        print('No se pudo convertir la cadena a flotante')
                else:
                    print(f'Linea invalida: {line}')
            

        else:
            for widget in self.cuerpo_principal.winfo_children():
                widget.destroy()
            label = tk.Label(self.cuerpo_principal, image=self.logo, bg=color_cuerpo_principal)
            label.place(x=0, y=0, relheight=1, relwidth=1)

    #Logica de los botores
    def configurar_boton_menu(self, button, text, icon, font_awesome, ancho_menu, alto_menu):
        button.config(text=f" {icon}   {text}", anchor="w", font=font_awesome, bd=0, bg = color_menu_lateral, fg="white", width=ancho_menu, height=alto_menu)
        button.pack(side=tk.TOP)
        self.bind_hover_events(button)

    def bind_hover_events(self, button):
        button.bind("<Enter>", lambda event: self.on_enter(event, button))
        button.bind("<Leave>", lambda event: self.on_leave(event, button))

    def on_enter(self, event, button):
        button.config(bg=color_menu_cursor_encima, fg='white')

    def on_leave(self, event, button):
        button.config(bg=color_menu_lateral, fg='white')
