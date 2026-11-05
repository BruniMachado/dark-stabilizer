import os
import subprocess
import uuid
import streamlit as st

st.set_page_config(page_title="House 72 — Stabilizer", page_icon="♠️", layout="centered")

# Estética Chicano / Old English limpa e direta
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pirata+One&family=Oswald:wght@400;600;700&display=swap');

    .stApp {
        background-color: #050507;
        background-image: radial-gradient(circle at 50% 0%, #16161d 0%, #050507 75%);
        color: #e4e4e7;
    }

    .chicano-title {
        font-family: 'Pirata One', cursive;
        font-size: 3.6rem;
        text-align: center;
        color: #f4f4f5;
        text-shadow: 0px 4px 18px rgba(0, 0, 0, 0.95), 0px 0px 10px rgba(212, 175, 55, 0.25);
        letter-spacing: 3px;
        margin-bottom: -10px;
        line-height: 1.1;
    }

    .chicano-sub {
        font-family: 'Oswald', sans-serif;
        text-align: center;
        color: #d4af37;
        font-size: 0.9rem;
        letter-spacing: 5px;
        text-transform: uppercase;
        margin-bottom: 18px;
    }

    .pinstripe {
        height: 2px;
        background: linear-gradient(90deg, transparent, #52525b, #d4af37, #52525b, transparent);
        margin: 10px 0 28px 0;
    }

    div[data-testid="stFileUploader"] {
        background-color: #0b0b0f;
        border: 1px dashed #3f3f46;
        border-radius: 8px;
        padding: 12px;
    }

    .stButton>button {
        font-family: 'Oswald', sans-serif;
        background: linear-gradient(180deg, #27272a 0%, #09090b 100%);
        color: #d4af37;
        border: 1px solid #d4af37;
        border-radius: 4px;
        font-size: 1.15rem;
        font-weight: 700;
        letter-spacing: 3px;
        text-transform: uppercase;
        height: 3.4em;
        box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.8);
        transition: all 0.25s ease;
    }

    .stButton>button:hover {
        background: linear-gradient(180deg, #d4af37 0%, #9a7b1c 100%);
        color: #050507;
        border: 1px solid #f4f4f5;
        box-shadow: 0px 0px 18px rgba(212, 175, 55, 0.5);
    }
    </style>

    <div class="chicano-title">House 72</div>
    <div class="chicano-sub">♠ Video Stabilizer ♠</div>
    <div class="pinstripe"></div>
""", unsafe_allow_html=True)

video_up = st.file_uploader("1. Selecionar Vídeo (.MOV ou .MP4)", type=["mov", "mp4", "m4v"])

suavizacao = st.slider(
    "2. Nível de Suavização (Tremedeira)",
    min_value=5, max_value=60, value=35
)

st.write("")
if st.button("♠️ ESTABILIZAR VÍDEO ♠️", use_container_width=True):
    if not video_up:
        st.error("Selecione um vídeo da galeria primeiro!")
    else:
        uid = uuid.uuid4().hex[:8]
        input_path = f"raw_{uid}.mov"
        trf_file = f"transforms_{uid}.trf"
        output_file = f"House72_Estabilizado_{uid}.mp4"

        with open(input_path, "wb") as f:
            f.write(video_up.read())

        barra = st.progress(0, text="1/2: Analisando tremedeira...")

        try:
            # Passo 1: Analisar movimento
            cmd_passo1 = [
                "ffmpeg", "-y", "-i", input_path,
                "-vf", f"vidstabdetect=shakiness=8:accuracy=15:result={trf_file}",
                "-f", "null", "-"
            ]
            subprocess.run(cmd_passo1, check=True)

            # Passo 2: Aplicar estabilização mantendo as cores originais
            barra.progress(50, text="2/2: Estabilizando vídeo...")
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

            barra.progress(100, text="Concluído com sucesso!")
            st.success("♠️ Vídeo estabilizado!")
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
