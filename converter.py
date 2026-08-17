from PIL import Image
from formats import *

def prepare_image(img, formato):
    if img.mode in formato.modes:
        return img
    if img.mode in ("RGBA", "LA") and "RGB" in formato.modes:
        fundo = Image.new("RGB", img.size, "white")
        fundo.paste(img, mask=img.getchannel("A"))
        return fundo
    if "P" in formato.modes:
        return img.convert("P", palette=Image.Palette.ADAPTIVE)
    return img.convert(formato.modes[0])

def save_animation(destino, img, formato):
    frames = []
    durations = []
    for i in range(img.n_frames):
        img.seek(i)
        frame = img.copy()
        frame = prepare_image(frame, formato)
        frames.append(frame)
        durations.append(img.info.get("duration", 100))
    frames[0].save(destino,format=formato.name,save_all=True,append_images=frames[1:],duration=durations,loop=0)

class Converter:
    def __init__(self, origem, destino):
        self.origem = origem
        self.destino = destino
    
    def image(self, formato):
        img = Image.open(self.origem)
        animated = getattr(img, "n_frames", 1) > 1
        if animated and formato.animated:
            save_animation(self.destino, img, formato)
        else:
            if animated:
                img.seek(0)
                img = img.copy()
            img = prepare_image(img, formato)
            img.save(self.destino, format=formato.name)