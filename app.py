import os
import tempfile
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from core import *

# ============================================================
# CONFIGURAÇÃO
# ============================================================

PATH = Path(__file__).parent

st.set_page_config(page_title="Yet Another Converter", page_icon="🔄", layout="centered")
st.markdown(f"<style>{(PATH / "style.css").read_text(encoding="utf-8")}</style>", unsafe_allow_html=True)

# ============================================================
# CONSTANTES
# ============================================================

FORMATOS = {
    # Imagens
    "png": "PNG", "jpg": "JPEG", "jpeg": "JPEG", "webp": "WEBP", "gif": "GIF",
    "bmp": "BMP", "tiff": "TIFF", "ico": "ICO", "ppm": "PPM", "tga": "TGA",
    # Áudio
    "mp3": "MP3", "m4a": "M4A", "wav": "WAV", "ogg": "OGG", "flac": "FLAC",
    # Vídeo
    "mp4": "MP4", "webm": "WEBM", "mkv": "MKV", "avi": "AVI", "mov": "MOV",
    "flv": "FLV", "wmv": "WMV",
}

EXT_IMAGEM = {"png", "jpg", "jpeg", "webp", "gif", "bmp", "tiff", "ico", "ppm", "tga"}
EXT_AUDIO = {"mp3", "m4a", "wav", "ogg", "flac"}
EXT_VIDEO = {"mp4", "webm", "mkv", "avi", "mov", "flv", "wmv"}


def icone_formato(extensao, icone = False):
    if extensao in EXT_IMAGEM:
        if icone: return Md.icon("image")
        return "🖼️"
    if extensao in EXT_AUDIO:
        if icone: return Md.icon("music")
        return "🎵"
    if extensao in EXT_VIDEO:
        if icone: return Md.icon("video")
        return "🎬"
    if icone: return Md.icon("file")
    return "📄"


def formatar_tamanho(tamanho):
    if tamanho >= 1024 ** 3:
        return f"{tamanho / 1024 ** 3:.2f} GB"
    if tamanho >= 1024 ** 2:
        return f"{tamanho / 1024 ** 2:.2f} MB"
    if tamanho >= 1024:
        return f"{tamanho / 1024:.2f} KB"
    return f"{tamanho} B"


def format_views(views):
    if views is None:
        return "N/A"
    if views >= 1_000_000_000:
        return f"{views / 1_000_000_000:.1f} bi"
    if views >= 1_000_000:
        return f"{views / 1_000_000:.1f} mi"
    if views >= 1_000:
        return f"{views / 1_000:.1f} mil"
    return str(views)

# ============================================================
# MARKDOWN
# ============================================================

class Md:
    @staticmethod
    def div(class_, value):
        st.markdown(f'<div class="{class_}">{value}</div>', unsafe_allow_html=True)
        
    @staticmethod
    def h1(value):
        st.markdown(f'<h1 style="text-align:center;">{value}</h1', unsafe_allow_html=True)
            
    @staticmethod
    def p(value):
        st.markdown(f'<p style="text-align:center; opacity:.65;">{value}</p>', unsafe_allow_html=True)
    
    @staticmethod
    def logo(value):
        return f'<i class="fa-brands fa-{value}"></i>'
    
    @staticmethod
    def icon(value):
        return f'<i class="fa-solid fa-{value}"></i>'

# ============================================================
# CONVERTER ARQUIVOS
# ============================================================

def converter_page():
    if st.button("← Voltar"):
        st.session_state.pagina = "home"
        st.rerun()

    Md.h1(f"{Md.icon("rotate")} Converter arquivos")

    arquivo = st.file_uploader("Escolha um arquivo", type=list(FORMATOS.keys()))
    if not arquivo:
        return

    extensao = os.path.splitext(arquivo.name)[1].lower().removeprefix(".")

    if extensao in EXT_IMAGEM:
        tipo = "imagem"
        formatos_disponiveis = {e: n for e, n in FORMATOS.items() if e in EXT_IMAGEM}
    elif extensao in EXT_AUDIO:
        tipo = "audio"
        formatos_disponiveis = {e: n for e, n in FORMATOS.items() if e in EXT_AUDIO}
    elif extensao in EXT_VIDEO:
        tipo = "video"
        # Vídeos primeiro, áudios depois
        formatos_disponiveis = {
            **{e: n for e, n in FORMATOS.items() if e in EXT_VIDEO},
            **{e: n for e, n in FORMATOS.items() if e in EXT_AUDIO},
        }
    else:
        st.error("Formato não suportado.")
        return

    opcoes = {e: f"{icone_formato(e)} {n}" for e, n in formatos_disponiveis.items()}

    st.write(f"{icone_formato(extensao)} **{arquivo.name}**")
    st.caption(f"Tamanho: {formatar_tamanho(len(arquivo.getvalue()))}")

    formato_ext = st.selectbox("Converter para", list(opcoes.keys()), format_func=lambda e: opcoes[e])
    formato_nome = FORMATOS[formato_ext]

    if formato_ext == extensao:
        st.info("O arquivo já está nesse formato.")

    if not st.button("🔄 Converter", use_container_width=True):
        return

    if formato_ext == extensao:
        st.warning("Escolha um formato diferente do arquivo original.")
        return

    with tempfile.TemporaryDirectory() as pasta:
        origem = os.path.join(pasta, arquivo.name)
        destino = os.path.join(pasta, f"yetanotherconverted.{formato_ext}")

        try:
            with open(origem, "wb") as f:
                f.write(arquivo.getvalue())

            with st.spinner("Convertendo arquivo..."):
                if tipo == "imagem":
                    Image(origem).converter(destino, FORMATOS[formato_ext])
                elif tipo == "audio":
                    Audio(origem).converter(destino, formato_nome)
                elif tipo == "video":
                    Video(origem).converter(destino, formato_ext)

            with open(destino, "rb") as f:
                dados = f.read()

            st.success("Conversão concluída!")
            st.download_button(
                "⬇️ Baixar arquivo",
                data=dados,
                file_name=f"yetanotherconverted.{formato_ext}",
                mime="application/octet-stream",
                use_container_width=True,
            )

        except Exception as erro:
            st.error(f"Erro na conversão: {erro}")


# ============================================================
# YOUTUBE
# ============================================================

def video_card(info):
    video_id = info.get("id")
    title = info.get("title", "Sem título")
    uploader = info.get("uploader", "Canal desconhecido")
    duration = info.get("duration_string", "N/A")
    views = format_views(info.get("view_count"))

    components.html(
        f"""
        <style>
            body {{ margin: 0; font-family: sans-serif; color: #262730; }}
            .video-card {{
                box-sizing: border-box;
                border: 1px solid rgba(128,128,128,.25);
                border-radius: 18px;
                padding: 20px;
                background: rgba(128,128,128,.08);
            }}
            .video-top {{ display: flex; gap: 20px; }}
            iframe {{ width: 50%; aspect-ratio: 16 / 9; border: none; border-radius: 12px; }}
            .details {{ flex: 1; }}
            .title {{ font-size: 23px; font-weight: 600; line-height: 1.25; color: #262730; }}
            .channel {{ margin-top: 8px; opacity: .65; }}
            .stats {{ margin-top: 20px; display: flex; gap: 18px; opacity: .7; }}

            @media (prefers-color-scheme: dark) {{
                body {{ color: #fafafa; }}
                .title {{ color: #fafafa; }}
                .video-card {{ background: rgba(255,255,255,.05); border-color: rgba(255,255,255,.15); }}
            }}
        </style>

        <div class="video-card">
            <div class="video-top">
                <iframe
                    src="https://www.youtube.com/embed/{video_id}"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowfullscreen>
                </iframe>
                <div class="details">
                    <div class="title">{title}</div>
                    <div class="channel">{uploader}</div>
                    <div class="stats">
                        <span>⏱️ {duration}</span>
                        <span>👁️ {views}</span>
                    </div>
                </div>
            </div>
        </div>
        """,
        height=320,
        scrolling=False,
    )


def buscar_video():
    url = st.session_state.youtube_url
    if not url:
        return

    try:
        with st.spinner("Buscando informações..."):
            info = YoutubeVideo(url).info()
        st.session_state.video_info = info
        st.session_state.video_error = None
    except Exception:
        st.session_state.video_info = None
        st.session_state.video_error = "Erro: Vídeo não foi encontrado"


def youtube_page():
    if st.button("← Voltar"):
        st.session_state.pagina = "home"
        st.rerun()

    Md.h1(f"{Md.logo("youtube")} YouTube Downloader")

    st.text_input(
        "Link do vídeo",
        placeholder="https://www.youtube.com/watch?v=...",
        key="youtube_url",
        on_change=buscar_video,
    )

    if st.session_state.get("video_error"):
        st.error(st.session_state.video_error)
        return

    if "video_info" not in st.session_state:
        return

    video_card(st.session_state.video_info)

    formatos = {
        "🎬 Vídeo — MP4": "vídeo/mp4",
        "🎬 Vídeo — WebM": "vídeo/webm",
        "🎬 Vídeo — MKV": "vídeo/mkv",
        "🎬 Vídeo — AVI": "vídeo/avi",
        "🎬 Vídeo — MOV": "vídeo/mov",
        "🎵 Áudio — MP3": "áudio/mp3",
        "🎵 Áudio — M4A": "áudio/m4a",
        "🎵 Áudio — WAV": "áudio/wav",
        "🎵 Áudio — FLAC": "áudio/flac",
        "🎵 Áudio — OGG": "áudio/ogg",
    }
    formato = formatos[st.selectbox("Formato", formatos.keys())].split("/")
    formato_tipo = formato[0]
    formato_nome = formato[1]

    if not st.button("🔄 Converter", use_container_width=True):
        return

    with tempfile.TemporaryDirectory() as pasta:
        try:
            destino = os.path.join(pasta, "yetanotherdownload.%(ext)s")

            with st.spinner("Convertendo..."):
                YoutubeVideo(st.session_state.youtube_url).download(destino, formato)

            extensao = formato_nome.lower()
            arquivo_final = next(
                (
                    os.path.join(pasta, arquivo)
                    for arquivo in os.listdir(pasta)
                    if arquivo.lower().endswith(f".{extensao}")
                ),
                None,
            )

            if arquivo_final is None:
                raise FileNotFoundError(f"O arquivo .{extensao} não foi encontrado.")

            with open(arquivo_final, "rb") as arquivo:
                dados = arquivo.read()

            st.success("Conversão concluída!")
            st.download_button(
                f"⬇️ Baixar {formato_tipo.capitalize()}",
                data=dados,
                file_name=f"yetanotherdownload.{extensao}",
                use_container_width=True,
            )

        except Exception as e:
            st.error(f"Erro: Conversão não pode ser realizada: {e}")
            print(e)

# ============================================================
# HOME
# ============================================================

def create_columns(paginas: dict):
    cols = st.columns(len(paginas))
    for n, i in enumerate(paginas):
        with cols[n]:
            if st.button(paginas[i], use_container_width=True):
                st.session_state.pagina = i
                st.rerun()

def home_page():
    Md.div("main-title","Yet Another Converter")
    Md.div("subtitle","Converta seus arquivos e baixe vídeos do YouTube.")
    create_columns({"converter":"📁\nConverter Arquivos","youtube":"▶️\nYouTube Downloader"})
    Md.div("footer","Yet Another Converter • Simples, rápido e gratuito")

# ============================================================
# NAVEGAÇÃO
# ============================================================

if "pagina" not in st.session_state:
    st.session_state.pagina = "home"

globals()[st.session_state.pagina + "_page"]()