import os
import subprocess
import uuid
import streamlit as st

st.set_page_config(page_title="Dark Stabilizer & Color Lab", page_icon="🎬", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0b0b0e; color: #e4e4e7; }
    </style>
""", unsafe_allow_html=True)

st.title("🎬 Estabilizador & Filtro Dark")
st.caption("FFmpeg Two-Pass VidStab + Preset Temperamento")

PRESETS = {
    "Temperamento (Frio + Sombras Densas + Vinheta)": ",eq=contrast=1.25:brightness=-0.05:saturation=0.70,colorbalance=bs=0.08:bm=0.05,vignette=PI/4",
    "Dark P&B (Alto Contraste / Realismo)": ",hue=s=0,eq=contrast=1.35:brightness=-0.04,vignette=PI/4",
    "Apenas Estabilizar (Sem filtro de cor)": ""
}

video_up = st.file_uploader("1. Selecionar Vídeo Original (.MOV / .MP4)", type=["mov", "mp4", "m4v"])
suavizacao = st.slider("Nível de Suavização (Tremedeira)", min_value=5, max_value=60, value=35)
preset_escolhido = st.selectbox("Preset de Estilo / Cor:", list(PRESETS.keys()))

if st.button("Renderizar Vídeo Estabilizado", type="primary", use_container_width=True):
    if not video_up:
        st.error("Seleciona um vídeo primeiro!")
    else:
        uid = uuid.uuid4().hex[:8]
        input_path = f"input_{uid}.mov"
        trf_file = f"transforms_{uid}.trf"
        output_file = f"video_estabilizado_{uid}.mp4"
        color_filter = PRESETS[preset_escolhido]

        with open(input_path, "wb") as f:
            f.write(video_up.read())

        barra = st.progress(0, text="1/2: Analisando tremedeira...")

        try:
            cmd_passo1 = [
                "ffmpeg", "-y", "-i", input_path,
                "-vf", f"vidstabdetect=shakiness=8:accuracy=15:result={trf_file}",
                "-f", "null", "-"
            ]
            subprocess.run(cmd_passo1, check=True)

            barra.progress(50, text="2/2: Estabilizando e aplicando estética...")
            vf_transform = (
                f"vidstabtransform=smoothing={suavizacao}:input={trf_file},"
                f"unsharp=5:5:0.8:3:3:0.4{color_filter}"
            )

            cmd_passo2 = [
                "ffmpeg", "-y", "-i", input_path,
                "-vf", vf_transform,
                "-c:v", "libx264", "-preset", "fast", "-crf", "18",
                "-pix_fmt", "yuv420p",
                "-c:a", "aac",
                "-movflags", "+faststart",
                output_file
            ]
            subprocess.run(cmd_passo2, check=True)

            barra.progress(100, text="Concluído com sucesso!")
            st.success("Vídeo pronto!")
            st.video(output_file)

            with open(output_file, "rb") as f_out:
                st.download_button(
                    label="⬇️ Guardar Vídeo Estabilizado",
                    data=f_out,
                    file_name="video_estabilizado.mp4",
                    mime="video/mp4",
                    use_container_width=True
                )

        finally:
            for arq in [input_path, trf_file, output_file]:
                if os.path.exists(arq):
                    os.remove(arq)
