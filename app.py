import os
import subprocess
import uuid
import streamlit as st

st.set_page_config(page_title="HOUSE 72 — PIXO LAB", page_icon="🏴", layout="centered")

# Estética Pixo SP (Tag Reto / Concreto / Tinta Preta & Branca)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=New+Rocker&family=Rubik+Wet+Paint&family=Teko:wght@500;700&display=swap');

    .stApp {
        background-color: #070708;
        background-image: 
            radial-gradient(circle at 50% 10%, #18181b 0%, #070708 80%);
        color: #f4f4f5;
    }

    /* Título estilo Tag Reto / Pixo SP (Esticado na vertical, pontiagudo e agressivo) */
    .pixo-title {
        font-family: 'New Rocker', cursive;
        font-size: 4.2rem;
        text-align: center;
        color: #ffffff;
        text-transform: uppercase;
        letter-spacing: 8px;
        transform: scaleY(1.55) skewX(-5deg);
        margin-top: 15px;
        margin-bottom: 20px;
        text-shadow: 
            3px 4px 0px #000000,
            0px 0px 15px rgba(255, 255, 255, 0.25);
        line-height: 1.0;
    }

    /* Subtítulo estilo Spray / Stencil Urbano */
    .pixo-sub {
        font-family: 'Teko', sans-serif;
        text-align: center;
        color: #a1a1aa;
        font-size: 1.35rem;
        letter-spacing: 9px;
        text-transform: uppercase;
        margin-top: 10px;
        margin-bottom: 12px;
    }

    /* Linha riscada estilo traço de spray */
    .spray-line {
        height: 2px;
        background: linear-gradient(90deg, transparent, #52525b, #ffffff, #52525b, transparent);
        margin: 8px 0 30px 0;
        opacity: 0.75;
    }

    /* Textos e Labels da interface mais altos e retos */
    label, .stMarkdown p {
        font-family: 'Teko', sans-serif !important;
        font-size: 1.25rem !important;
        letter-spacing: 2px !important;
        text-transform: uppercase;
        color: #e4e4e7 !important;
    }

    /* Caixa de Upload estilo Muro / Concreto Escuro */
    div[data-testid="stFileUploader"] {
        background-color: #0e0e11;
        border: 2px dashed #52525b;
        border-radius: 2px;
        padding: 14px;
    }

    /* Botão Principal estilo Tarja Preta & Branca de Rua */
    .stButton>button {
        font-family: 'New Rocker', cursive;
        background-color: #09090b;
        color: #ffffff;
        border: 2px solid #ffffff;
        border-radius: 0px;
        font-size: 1.3rem;
        letter-spacing: 5px;
        text-transform: uppercase;
        height: 3.4em;
        box-shadow: 4px 4px 0px #3f3f46;
        transition: all 0.15s ease-in-out;
    }

    .stButton>button:hover {
        background-color: #ffffff;
        color: #000000;
        border: 2px solid #ffffff;
        box-shadow: 6px 6px 0px #71717a;
        transform: translate(-1px, -1px);
    }
    </style>

    <div class="pixo-title">HOUSE 72</div>
    <div class="pixo-sub">ESTABILIZADOR DE VÍDEO</div>
    <div class="spray-line"></div>
""", unsafe_allow_html=True)

video_up = st.file_uploader("1. SELECIONAR VÍDEO (.MOV OU .MP4)", type=["mov", "mp4", "m4v"])

suavizacao = st.slider(
    "2. NÍVEL DE SUAVIZAÇÃO (TREMEDEIRA)",
    min_value=5, max_value=60, value=35
)

st.write("")
if st.button("ESTABILIZAR VÍDEO", use_container_width=True):
    if not video_up:
        st.error("SELECIONE UM VÍDEO DA GALERIA PRIMEIRO!")
    else:
        uid = uuid.uuid4().hex[:8]
        input_path = f"raw_{uid}.mov"
        trf_file = f"transforms_{uid}.trf"
        output_file = f"House72_Estabilizado_{uid}.mp4"

        with open(input_path, "wb") as f:
            f.write(video_up.read())

        barra = st.progress(0, text="1/2: ANALISANDO TREMEDEIRA...")

        try:
            # Passo 1: Analisar movimento
            cmd_passo1 = [
                "ffmpeg", "-y", "-i", input_path,
                "-vf", f"vidstabdetect=shakiness=8:accuracy=15:result={trf_file}",
                "-f", "null", "-"
            ]
            subprocess.run(cmd_passo1, check=True)

            # Passo 2: Estabilizar mantendo cores e áudio originais
            barra.progress(50, text="2/2: ESTABILIZANDO VÍDEO...")
            vf_transform = (
                f"vidstabtransform=smoothing={suavizacao}:input={trf_file}:crop=black:zoom=3,"
                f"unsharp=5:5:0.8:3:3:0.4"
            )

            cmd_passo2 = [
                "ffmpeg", "-y", "-i", input_path,
                "-vf", vf_transform,
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                "-pix_fmt", "yuv420p",
                "-c:a", "aac",
                "-movflags", "+faststart",
                output_file
            ]
            subprocess.run(cmd_passo2, check=True)

            barra.progress(100, text="CONCLUÍDO!")
            st.success("VÍDEO ESTABILIZADO COM SUCESSO!")
            st.video(output_file)

            with open(output_file, "rb") as f_out:
                st.download_button(
                    label="⬇️ BAIXAR VÍDEO ESTABILIZADO",
                    data=f_out,
                    file_name=f"House72_Estabilizado_{uid[:4]}.mp4",
                    mime="video/mp4",
                    use_container_width=True
                )

        finally:
            for arq in [input_path, trf_file, output_file]:
                if os.path.exists(arq):
                    os.remove(arq)
