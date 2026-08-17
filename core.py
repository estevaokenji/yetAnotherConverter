from PIL import Image as PILImage
from formats import *
import yt_dlp
import subprocess


def prepare_image(img, formato):
    if img.mode in formato.modes:
        return img

    if img.mode in ("RGBA", "LA") and "RGB" in formato.modes:
        fundo = PILImage.new("RGB", img.size, "white")
        fundo.paste(img, mask=img.getchannel("A"))
        return fundo

    if "P" in formato.modes:
        return img.convert("P", palette=PILImage.Palette.ADAPTIVE)

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

    frames[0].save(
        destino,
        format=formato.name,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0
    )


class Image:
    def __init__(self, origem):
        self.origem = origem

    def converter(self, destino, formato):
        img = PILImage.open(self.origem)

        animated = getattr(img, "n_frames", 1) > 1

        if animated and formato.animated:
            save_animation(destino, img, formato)
        else:
            if animated:
                img.seek(0)
                img = img.copy()

            img = prepare_image(img, formato)
            img.save(destino, format=formato.name)


class Audio:
    def __init__(self, origem):
        self.origem = origem

    def converter(self, destino, formato):

        codecs = {
            "MP3": "libmp3lame",
            "M4A": "aac",
            "WAV": "pcm_s16le",
            "OGG": "libvorbis",
            "FLAC": "flac",
        }

        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i", self.origem,
                "-vn",
                "-acodec", codecs[formato],
                destino,
            ],
            check=True,
        )

class Video:
    def __init__(self, origem):
        self.origem = origem

    def converter(self, destino, formato):
        audio_formats = {
            "mp3": "libmp3lame",
            "m4a": "aac",
            "wav": "pcm_s16le",
            "ogg": "libvorbis",
            "flac": "flac",
        }

        if formato in audio_formats:
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-i", self.origem,
                    "-vn",
                    "-acodec", audio_formats[formato],
                    destino,
                ],
                check=True,
            )

        else:
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-i", self.origem,
                    destino,
                ],
                check=True,
            )

    def extract(self, destino):
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i", self.origem,
                "-vn",
                "-acodec", "libmp3lame",
                "-q:a", "2",
                destino,
            ],
            check=True,
        )

class YoutubeVideo:
    def __init__(self, url):
        self.url = url

    def info(self):
        options = {
            "quiet": True,
            "no_warnings": True,
        }

        with yt_dlp.YoutubeDL(options) as ydl:
            return ydl.extract_info(
                self.url,
                download=False
            )

    def download(self, destino, formato):
        if formato == "MP3":

            options = {
                "outtmpl": destino,
                "format": "bestaudio/best",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
            }

            with yt_dlp.YoutubeDL(options) as ydl:
                ydl.download([self.url])

            return
        if formato == "MP4":
            formatos = [
                # 1080p
                "137+251",
                "137+139",
                "137+249",

                "399+251",
                "399+139",
                "399+249",

                # 720p
                "136+251",
                "136+139",
                "136+249",

                "398+251",
                "398+139",
                "398+249",

                # 480p
                "135+251",
                "135+139",
                "135+249",

                "397+251",
                "397+139",
                "397+249",

                # 360p
                "134+251",
                "134+139",
                "134+249",

                "396+251",
                "396+139",
                "396+249",

                # 240p
                "133+251",
                "133+139",
                "133+249",

                "395+251",
                "395+139",
                "395+249",

                # 144p
                "160+251",
                "160+139",
                "160+249",

                "394+251",
                "394+139",
                "394+249",

                # Último recurso: vídeo + áudio juntos
                "18",
            ]
            
            ultimo_erro = None

            for formato_video in formatos:

                try:

                    print(
                        f"Tentando formato: "
                        f"{formato_video}"
                    )

                    options = {
                        "outtmpl": destino,
                        "format": formato_video,
                        "merge_output_format": "mp4",
                    }

                    with yt_dlp.YoutubeDL(options) as ydl:
                        ydl.download([self.url])

                    print(
                        f"Funcionou: "
                        f"{formato_video}"
                    )

                    return

                except Exception as erro:

                    print(
                        f"Falhou: "
                        f"{formato_video}"
                    )

                    ultimo_erro = erro

            raise RuntimeError(
                "Nenhum formato disponível "
                "conseguiu ser baixado."
            ) from ultimo_erro