from PIL import ImageTk, Image

def leer_imagen(path, size):
    #Hace que la imagen sea posible usarla en tkinter
    return ImageTk.PhotoImage(Image.open(path).resize(size, Image.ADAPTIVE))