import os
import tempfile

import streamlit as st
import streamlit.components.v1 as components

from core import Image, Audio, Video, YoutubeVideo
from formats import (
    PNG,
    JPEG,
    WEBP,
    GIF,
    BMP,
    TIFF,
    ICO,
    PPM,
    TGA,
)


# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="Yet Another Converter",
    page_icon="🔄",
    layout="centered",
)


# ============================================================
# CONVERTER ARQUIVOS
# ============================================================

def converter_page():

    if st.button("← Voltar"):
        st.session_state.pagina = "home"
        st.rerun()

    st.title("Converter arquivos")

    # ========================================================
    # FORMATOS
    # ========================================================

    formatos = {
        # Imagens
        "png": "PNG",
        "jpg": "JPEG",
        "jpeg": "JPEG",
        "webp": "WEBP",
        "gif": "GIF",
        "bmp": "BMP",
        "tiff": "TIFF",
        "ico": "ICO",
        "ppm": "PPM",
        "tga": "TGA",

        # Áudio
        "mp3": "MP3",
        "m4a": "M4A",
        "wav": "WAV",
        "ogg": "OGG",
        "flac": "FLAC",

        # Vídeo
        "mp4": "MP4",
        "webm": "WEBM",
        "mkv": "MKV",
        "avi": "AVI",
        "mov": "MOV",
        "flv": "FLV",
        "wmv": "WMV",
    }

    extensoes_imagem = {
        "png",
        "jpg",
        "jpeg",
        "webp",
        "gif",
        "bmp",
        "tiff",
        "ico",
        "ppm",
        "tga",
    }

    extensoes_audio = {
        "mp3",
        "m4a",
        "wav",
        "ogg",
        "flac",
    }

    extensoes_video = {
        "mp4",
        "webm",
        "mkv",
        "avi",
        "mov",
        "flv",
        "wmv",
    }

    # ========================================================
    # UPLOAD
    # ========================================================

    arquivo = st.file_uploader(
        "Escolha um arquivo",
        type=list(formatos.keys()),
    )

    if not arquivo:
        return

    # ========================================================
    # DETECTAR EXTENSÃO
    # ========================================================

    extensao = (
        os.path.splitext(arquivo.name)[1]
        .lower()
        .removeprefix(".")
    )

    # ========================================================
    # DETECTAR TIPO
    # ========================================================

    if extensao in extensoes_imagem:

        tipo = "imagem"

    elif extensao in extensoes_audio:

        tipo = "audio"

    elif extensao in extensoes_video:

        tipo = "video"

    else:

        st.error("Formato não suportado.")
        return

    # ========================================================
    # FORMATOS DISPONÍVEIS
    # ========================================================

    if tipo == "imagem":

        formatos_disponiveis = {
            ext: nome
            for ext, nome in formatos.items()
            if ext in extensoes_imagem
        }

    elif tipo == "audio":

        formatos_disponiveis = {
            ext: nome
            for ext, nome in formatos.items()
            if ext in extensoes_audio
        }

    else:
        # Vídeos primeiro, áudios depois
        formatos_disponiveis = {
            **{
                ext: nome
                for ext, nome in formatos.items()
                if ext in extensoes_video
            },
            **{
                ext: nome
                for ext, nome in formatos.items()
                if ext in extensoes_audio
            },
        }

    # ========================================================
    # ÍCONE AUTOMÁTICO
    # ========================================================

    def icone_formato(extensao):

        if extensao in extensoes_imagem:
            return "🖼️"

        if extensao in extensoes_audio:
            return "🎵"

        if extensao in extensoes_video:
            return "🎬"

        return "📄"

    # ========================================================
    # LABEL DO SELECTBOX
    # ========================================================

    opcoes = {
        ext: (
            f"{icone_formato(ext)} "
            f"{nome}"
        )
        for ext, nome in formatos_disponiveis.items()
    }

    # ========================================================
    # INFORMAÇÕES
    # ========================================================

    tamanho = len(arquivo.getvalue())

    if tamanho >= 1024 ** 3:

        tamanho_formatado = (
            f"{tamanho / 1024 ** 3:.2f} GB"
        )

    elif tamanho >= 1024 ** 2:

        tamanho_formatado = (
            f"{tamanho / 1024 ** 2:.2f} MB"
        )

    elif tamanho >= 1024:

        tamanho_formatado = (
            f"{tamanho / 1024:.2f} KB"
        )

    else:

        tamanho_formatado = f"{tamanho} B"

    icone_origem = icone_formato(extensao)

    st.write(
        f"{icone_origem} **{arquivo.name}**"
    )

    st.caption(
        f"Tamanho: {tamanho_formatado}"
    )

    # ========================================================
    # FORMATO DE DESTINO
    # ========================================================

    formato_ext = st.selectbox(
        "Converter para",
        list(opcoes.keys()),
        format_func=lambda ext: opcoes[ext],
    )

    formato_nome = formatos[formato_ext]

    # ========================================================
    # MESMO FORMATO
    # ========================================================

    if formato_ext == extensao:

        st.info(
            "O arquivo já está nesse formato."
        )

    # ========================================================
    # CONVERTER
    # ========================================================

    if st.button(
        "🔄 Converter",
        use_container_width=True,
    ):

        if formato_ext == extensao:

            st.warning(
                "Escolha um formato diferente "
                "do arquivo original."
            )

            return

        with tempfile.TemporaryDirectory() as pasta:

            origem = os.path.join(
                pasta,
                arquivo.name,
            )

            destino = os.path.join(
                pasta,
                f"yetanotherconverted.{formato_ext}",
            )

            try:

                # --------------------------------------------
                # SALVAR ORIGINAL
                # --------------------------------------------

                with open(origem, "wb") as f:

                    f.write(
                        arquivo.getvalue()
                    )

                # --------------------------------------------
                # CONVERTER
                # --------------------------------------------

                with st.spinner(
                    "Convertendo arquivo..."
                ):

                    if tipo == "imagem":

                        Image(origem).converter(
                            destino,
                            formatos[formato_ext],
                        )

                    elif tipo == "audio":

                        Audio(origem).converter(
                            destino,
                            formato_nome,
                        )

                    elif tipo == "video":

                        Video(origem).converter(
                            destino,
                            formato_ext,
                        )

                # --------------------------------------------
                # RESULTADO
                # --------------------------------------------

                with open(
                    destino,
                    "rb",
                ) as f:

                    dados = f.read()

                st.success(
                    "Conversão concluída!"
                )

                st.download_button(
                    "⬇️ Baixar arquivo",
                    data=dados,
                    file_name=(
                        f"yetanotherconverted."
                        f"{formato_ext}"
                    ),
                    mime="application/octet-stream",
                    use_container_width=True,
                )

            except Exception as erro:

                st.error(
                    f"Erro na conversão: {erro}"
                )

# ============================================================
# YOUTUBE
# ============================================================

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


def video_card(info):

    video_id = info.get("id")

    title = info.get(
        "title",
        "Sem título",
    )

    uploader = info.get(
        "uploader",
        "Canal desconhecido",
    )

    duration = info.get(
        "duration_string",
        "N/A",
    )

    views = format_views(
        info.get("view_count")
    )

    components.html(
        f"""
        <style>

            body {{
                margin: 0;
                font-family: sans-serif;
                color: #262730;
            }}

            .video-card {{
                box-sizing: border-box;
                border: 1px solid rgba(128,128,128,.25);
                border-radius: 18px;
                padding: 20px;
                background: rgba(128,128,128,.08);
            }}

            .video-top {{
                display: flex;
                gap: 20px;
            }}

            iframe {{
                width: 50%;
                aspect-ratio: 16 / 9;
                border: none;
                border-radius: 12px;
            }}

            .details {{
                flex: 1;
            }}

            .title {{
                font-size: 23px;
                font-weight: 600;
                line-height: 1.25;
                color: #262730;
            }}

            .channel {{
                margin-top: 8px;
                opacity: .65;
            }}

            .stats {{
                margin-top: 20px;
                display: flex;
                gap: 18px;
                opacity: .7;
            }}

            @media (prefers-color-scheme: dark) {{

                body {{
                    color: #fafafa;
                }}

                .title {{
                    color: #fafafa;
                }}

                .video-card {{
                    background: rgba(255,255,255,.05);
                    border-color: rgba(255,255,255,.15);
                }}
            }}

        </style>

        <div class="video-card">

            <div class="video-top">

                <iframe
                    src="https://www.youtube.com/embed/{video_id}"
                    allow="accelerometer;
                           autoplay;
                           clipboard-write;
                           encrypted-media;
                           gyroscope;
                           picture-in-picture"
                    allowfullscreen>
                </iframe>

                <div class="details">

                    <div class="title">
                        {title}
                    </div>

                    <div class="channel">
                        {uploader}
                    </div>

                    <div class="stats">
                        <span>⏱️ {duration}</span>
                        <span>👁️ {views}</span>
                    </div>

                </div>

            </div>

        </div>
        """,
        height=230,
        scrolling=False,
    )


def buscar_video():

    url = st.session_state.youtube_url

    if not url:
        return

    try:

        with st.spinner(
            "Buscando informações..."
        ):

            info = YoutubeVideo(
                url
            ).info()

        st.session_state.video_info = info
        st.session_state.video_error = None

    except Exception as erro:

        st.session_state.video_info = None
        st.session_state.video_error = str(
            erro
        )


def youtube_page():

    if st.button("← Voltar"):

        st.session_state.pagina = "home"
        st.rerun()

    st.title("YouTube Downloader")

    st.text_input(
        "Link do vídeo",
        placeholder=(
            "https://www.youtube.com/watch?v=..."
        ),
        key="youtube_url",
        on_change=buscar_video,
    )

    if (
        "video_error" in st.session_state
        and st.session_state.video_error
    ):

        st.error(
            st.session_state.video_error
        )

        return

    if "video_info" not in st.session_state:
        return

    info = st.session_state.video_info

    video_card(info)

    formatos = {
        "Vídeo (MP4)": "MP4",
        "Música (MP3)": "MP3",
    }

    formato_nome = st.selectbox(
        "Formato",
        formatos.keys(),
    )

    formato = formatos[formato_nome]

    if st.button(
        "⬇️ Baixar",
        use_container_width=True,
    ):

        with tempfile.TemporaryDirectory() as pasta:

            try:

                destino = os.path.join(
                    pasta,
                    "yetanotherdownload.%(ext)s",
                )

                with st.spinner(
                    "Baixando..."
                ):

                    YoutubeVideo(
                        st.session_state.youtube_url
                    ).download(
                        destino,
                        formato,
                    )

                extensao = formato.lower()

                arquivo_final = next(
                    (
                        os.path.join(
                            pasta,
                            arquivo,
                        )
                        for arquivo in os.listdir(
                            pasta
                        )
                        if arquivo.lower().endswith(
                            f".{extensao}"
                        )
                    ),
                    None,
                )

                if arquivo_final is None:

                    raise FileNotFoundError(
                        f"O arquivo .{extensao} "
                        "não foi encontrado."
                    )

                with open(
                    arquivo_final,
                    "rb",
                ) as arquivo:

                    dados = arquivo.read()

                st.success(
                    "Download concluído!"
                )

                st.download_button(
                    f"Baixar {formato_nome}",
                    data=dados,
                    file_name=(
                        f"yetanotherdownload."
                        f"{extensao}"
                    ),
                    use_container_width=True,
                )

            except Exception as erro:

                st.error(
                    f"Erro no download: {erro}"
                )


# ============================================================
# HOME
# ============================================================

def home_page():

    st.title(
        "Yet Another Converter"
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "📁\nConverter arquivos",
            use_container_width=True,
        ):

            st.session_state.pagina = (
                "converter"
            )

            st.rerun()

    with col2:

        if st.button(
            "▶️\nYouTube Downloader",
            use_container_width=True,
        ):

            st.session_state.pagina = (
                "youtube"
            )

            st.rerun()


# ============================================================
# NAVEGAÇÃO
# ============================================================

if "pagina" not in st.session_state:
    st.session_state.pagina = "home"


if st.session_state.pagina == "home":

    home_page()

elif st.session_state.pagina == "converter":

    converter_page()

elif st.session_state.pagina == "youtube":

    youtube_page()