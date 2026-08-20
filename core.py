from PIL import Image as PILImage
from formats import *
import yt_dlp
import subprocess

AUDIO_FORMATS = {"MP3": "libmp3lame", "M4A": "aac", "WAV": "pcm_s16le", "OGG": "libvorbis", "FLAC": "flac"}

class Image:
    def __init__(self, origem):
        self.origem = origem

    def converter(self, destino, formato):
        img = PILImage.open(self.origem)
        animated = getattr(img, "n_frames", 1) > 1
        if animated and formato.animated:
            frames = []
            durations = []
            for i in range(img.n_frames):
                img.seek(i)
                frame = img.copy()
                frame = self.prepare_image(frame, formato)
                frames.append(frame)
                durations.append(img.info.get("duration", 100))
            frames[0].save(destino, format=formato.name, save_all=True, append_images=frames[1:], duration=durations, loop=0)
        else:
            if animated:
                img.seek(0)
                img = img.copy()
            img = self.prepare_image(img, formato)
            img.save(destino, format=formato.name)
            
    def prepare_image(self, img, formato):
        if img.mode in formato.modes:
            return img
        if img.mode in ("RGBA", "LA") and "RGB" in formato.modes:
            fundo = PILImage.new("RGB", img.size, "white")
            fundo.paste(img, mask=img.getchannel("A"))
            return fundo
        if "P" in formato.modes:
            return img.convert("P", palette=PILImage.Palette.ADAPTIVE)
        return img.convert(formato.modes[0])

class Audio:
    def __init__(self, origem):
        self.origem = origem

    def converter(self, destino, formato):
        subprocess.run(["ffmpeg", "-y", "-i", self.origem, "-vn", "-acodec", AUDIO_FORMATS[formato], destino], check=True)

class Video:
    def __init__(self, origem):
        self.origem = origem

    def converter(self, destino, formato):
        if formato in AUDIO_FORMATS:
            Audio.converter(destino, formato)
        else:
            subprocess.run(["ffmpeg", "-y", "-i", self.origem, destino], check=True)

    def extract(self, destino):
        subprocess.run(["ffmpeg", "-y", "-i", self.origem, "-vn", "-acodec", "libmp3lame", "-q:a", "2", destino], check=True)

class YoutubeVideo:
    def __init__(self, url: str):
        self.url = url

    def info(self):
        options = {"quiet": True, "no_warnings": True}
        with yt_dlp.YoutubeDL(options) as ydl:
            return ydl.extract_info(self.url, download=False)

    def download(self, destino, formato):
        options = {"outtmpl": destino, "remote_components": "ejs:github"}
        
        if formato[0] == "áudio":
            options |= {"format": "bestaudio/best/worst", "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": formato[1], "preferredquality": "192"}]}
    
        if formato[0] == "vídeo":
            options |= {"format": "bestvideo+bestaudio/best/worst", "merge_output_format": formato[1]}
            
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([self.url])
        return