import streamlit as st
from converter import Converter
from formats import PNG, JPEG, WEBP, GIF, BMP, TIFF, ICO, PPM, TGA
import tempfile
import os

formatos = {
    "PNG": PNG,
    "JPEG": JPEG,
    "WEBP": WEBP,
    "GIF": GIF,
    "BMP": BMP,
    "TIFF": TIFF,
    "ICO": ICO,
    "PPM": PPM,
    "TGA": TGA,
}

st.title("yetAnotherConverter")

arquivo = st.file_uploader("Escolha uma imagem")

formato = st.selectbox(
    "Converter para",
    formatos.keys()
)
formato = formatos[formato]

if arquivo and st.button("Converter"):
    origem = None
    destino = None
    try:
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            temp.write(arquivo.getvalue())
            origem = temp.name
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=f".{formato.extension}"
        ) as temp:
            destino = temp.name
        Converter(origem, destino).image(formato)
        st.success("Conversão concluída!")
        with open(destino, "rb") as resultado:
            st.download_button(
                "Baixar imagem",
                resultado,
                file_name=f"yetanotherconverted.{formato.extension}",
            )
    except Exception as erro:
        st.error(f"Erro na conversão: {erro}")
    finally:
        if origem and os.path.exists(origem):
            os.remove(origem)