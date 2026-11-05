import os
import subprocess
import uuid
import streamlit as st

st.set_page_config(page_title="House 72 — Ink Lab", page_icon="♠️", layout="centered")

# Estética Chicano / Old English / West Coast Hip-Hop
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pirata+One&family=Oswald:wght@400;600;700&display=swap');

    .stApp {
        background-color: #050507;
        background-image: radial-gradient(circle at 50% 0%, #16161d 0%, #050507 75%);
        color: #e4e4e7;
    }

    /* Cabeçalho Chicano Calligraffiti / Old English */
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

    /* Linha estilo Pinstripe Lowrider */
    .pinstripe {
        height: 2px;
        background: linear-gradient(90deg, transparent, #52525b, #d4af37, #52525b, transparent);
        margin: 10px 0 28px 0;
    }

    .section-tag {
        font-family: 'Oswald', sans-serif;
        color: #d4af37;
        letter-spacing: 2px;
        text-transform: uppercase;
        font-size: 1.05rem;
        margin-top: 12px;
        margin-bottom: 8px;
        border-left: 3px solid #d4af37;
        padding-left: 10px;
    }

    /* Caixas e Painéis Cromados/Dark */
    div[data-testid="stFileUploader"] {
        background-color: #0b0b0f;
        border: 1px dashed #3f3f46;
        border-radius: 8px;
        padding: 12px;
    }

    div[data-testid="stExpander"] {
        background-color: #0b0b0f;
        border: 1px solid #27272a;
        border-left: 3px solid #d4af37;
        border-radius: 6px;
    }

    /* Botão Principal Estilo Placa Preta & Ouro */
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
    <div class="chicano-sub">♠ Black & Grey • Fine Line • Lettering • Dark Lab ♠</div>
    <div class="pinstripe"></div>
""", unsafe_allow_html=True)

# Catálogo de Filtros com pegada Street / Chicano / Tattoo
PRESETS = {
    "1. Temperamento 72 (Clássico Dark Frio + Vinheta)": {
        "contrast": 1.25, "brightness": -0.05, "saturation": 0.68,
        "extra_filter": "colorbalance=bs=0.08:bm=0.05:rh=-0.03",
        "vignette": True, "red_reduce": False, "sharp": 0.9
    },
    "2. Chicano Street Noir (P&B Pesado + Grão 90s Hip-Hop)": {
        "contrast": 1.48, "brightness": -0.07, "saturation": 0.0,
        "extra_filter": "curves=m='0/0 0.30/0.15 0.75/0.85 1/0.92'",
        "vignette": True, "red_reduce": False, "sharp": 1.2
    },
    "3. Black & Grey Realism (P&B Sombra Lisa & Preto Puro)": {
        "contrast": 1.38, "brightness": -0.04, "saturation": 0.0,
        "extra_filter": "curves=m='0/0 0.25/0.18 0.75/0.82 1/0.95'",
        "vignette": True, "red_reduce": False, "sharp": 1.1
    },
    "4. West Coast Lowrider (Sombra Densa + Subtom Ouro Velho)": {
        "contrast": 1.32, "brightness": -0.05, "saturation": 0.62,
        "extra_filter": "colorbalance=rs=0.06:gs=0.03:bs=-0.06:rm=0.04",
        "vignette": True, "red_reduce": True, "sharp": 1.0
    },
    "5. Gothic Darkroom (Subtom Gótico Frio & Sombrio)": {
        "contrast": 1.35, "brightness": -0.08, "saturation": 0.45,
        "extra_filter": "colorbalance=bs=0.14:bm=0.07:gs=-0.04:rs=-0.06",
        "vignette": True, "red_reduce": True, "sharp": 0.9
    },
    "6. Fine Line & Lettering (Agulha Nítida + Pele Neutra)": {
        "contrast": 1.22, "brightness": -0.02, "saturation": 0.75,
        "extra_filter": "colorbalance=rs=-0.10:rm=-0.08:bs=0.03",
        "vignette": False, "red_reduce": True, "sharp": 1.5
    },
    "7. Titanium Piercing Drip (Brilho Metálico + Fundo Escuro)": {
        "contrast": 1.30, "brightness": -0.06, "saturation": 0.80,
        "extra_filter": "colorbalance=bs=0.06:bh=0.06:rm=-0.05",
        "vignette": True, "red_reduce": True, "sharp": 1.5
    },
    "8. Boom Bap VHS Tape (Estética Clipe Rap Anos 90)": {
        "contrast": 1.20, "brightness": -0.03, "saturation": 0.55,
        "extra_filter": "curves=m='0/0.07 0.25/0.22 0.75/0.80 1/0.90',colorbalance=rs=0.04:bs=0.05",
        "vignette": True, "red_reduce": False, "sharp": 0.8
    },
    "9. Raw Cam (Apenas Estabilizar • Sem Filtro)": {
        "contrast": 1.0, "brightness": 0.0, "saturation": 1.0,
        "extra_filter": "",
        "vignette": False, "red_reduce": False, "sharp": 0.5
    }
}

st.markdown('<div class="section-tag">I. Carregar Vídeo Bruto</div>', unsafe_allow_html=True)
video_up = st.file_uploader("Solte o arquivo .MOV ou .MP4 da galeria", type=["mov", "mp4", "m4v"])

st.markdown('<div class="section-tag">II. Estética & Estabilização</div>', unsafe_allow_html=True)
preset_nome = st.selectbox("Visual / Color Grading:", list(PRESETS.keys()))
p_base = PRESETS[preset_nome]

suavizacao = st.slider(
    "Estabilização da Mão (Steady Cam)",
    min_value=0, max_value=60, value=35,
    help="Deixe em 0 se gravou no tripé e quiser só jogar o filtro rápido."
)

st.markdown('<div class="section-tag">III. Ajustes de Bancada (Pele & Luz)</div>', unsafe_allow_html=True)
col_t1, col_t2 = st.columns(2)
with col_t1:
    reduzir_vermelho = st.checkbox("Tirar Vermelhidão da Pele", value=p_base["red_reduce"])
    anti_reflexo = st.checkbox("Lente CPL (Cortar Brilho da Luz)", value=True)
with col_t2:
    formato_reels = st.checkbox("Travar em 9:16 (Reels / TikTok)", value=False)
    remover_audio = st.checkbox("Mutar Áudio Original", value=True)

with st.expander("♠️ PAINEL FINO: CORTE DE PONTAS, PRETO PURO & GRÃO DE RUA"):
    c_trim1, c_trim2 = st.columns(2)
    with c_trim1:
        cortar_inicio = st.number_input("Cortar início (segundos):", min_value=0.0, max_value=30.0, value=0.0, step=0.5)
    with c_trim2:
        duracao_max = st.number_input("Tempo máximo (0 = Vídeo todo):", min_value=0.0, max_value=120.0, value=0.0, step=1.0)

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        contraste = st.slider("Peso do Preto (Contraste)", 0.80, 1.80, float(p_base["contrast"]), 0.05)
        brilho = st.slider("Sombra / Exposição", -0.30, 0.20, float(p_base["brightness"]), 0.01)
        saturacao = st.slider("Saturação", 0.0, 1.50, float(p_base["saturation"]), 0.05)
    with c2:
        nitidez = st.slider("Foco na Agulha / Traço", 0.0, 2.5, float(p_base["sharp"]), 0.1)
        granulado = st.slider("Grão 35mm (Street Texture)", 0, 25, 8 if "Chicano" in preset_nome or "VHS" in preset_nome else 0)
        usar_vinheta = st.checkbox("Borda Escura (Vinheta)", value=p_base["vignette"])

st.write("")
if st.button("♠️ RENDERIZAR NA HOUSE 72 ♠️", use_container_width=True):
    if not video_up:
        st.error("Escolhe um vídeo da galeria primeiro, mano!")
    else:
        uid = uuid.uuid4().hex[:8]
        input_path = f"raw_{uid}.mov"
        trimmed_path = f"trim_{uid}.mov"
        trf_file = f"transforms_{uid}.trf"
        output_file = f"House72_{uid}.mp4"

        with open(input_path, "wb") as f:
            f.write(video_up.read())

        barra = st.progress(0, text="Preparando fita no estúdio...")

        try:
            video_fonte = input_path

            if cortar_inicio > 0 or duracao_max > 0:
                barra.progress(10, text="Cortando pontas do vídeo...")
                cmd_trim = ["ffmpeg", "-y"]
                if cortar_inicio > 0:
                    cmd_trim.extend(["-ss", str(cortar_inicio)])
                cmd_trim.extend(["-i", input_path])
                if duracao_max > 0:
                    cmd_trim.extend(["-t", str(duracao_max)])
                cmd_trim.extend(["-c", "copy", trimmed_path])
                subprocess.run(cmd_trim, check=True)
                video_fonte = trimmed_path

            filtros = []

            if suavizacao > 0:
                barra.progress(25, text="1/2: Estabilizando o movimento da mão...")
                cmd_passo1 = [
                    "ffmpeg", "-y", "-i", video_fonte,
                    "-vf", f"vidstabdetect=shakiness=8:accuracy=15:result={trf_file}",
                    "-f", "null", "-"
                ]
                subprocess.run(cmd_passo1, check=True)
                filtros.append(f"vidstabtransform=smoothing={suavizacao}:input={trf_file}:crop=black:zoom=3")

            barra.progress(60, text="2/2: Jogando estética Dark & calibrando o preto...")

            if formato_reels:
                filtros.append("scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920")
            else:
                filtros.append("scale='min(1080,iw)':-2")

            if nitidez > 0:
                filtros.append(f"unsharp=5:5:{nitidez}:3:3:0.4")

            if reduzir_vermelho and saturacao > 0:
                filtros.append("colorbalance=rs=-0.12:rm=-0.08:rh=-0.04:bs=0.04")

            if anti_reflexo:
                filtros.append("curves=m='0/0 0.5/0.5 0.85/0.82 1/0.90'")

            filtros.append(f"eq=contrast={contraste}:brightness={brilho}:saturation={saturacao}")

            if p_base["extra_filter"]:
                filtros.append(p_base["extra_filter"])

            if granulado > 0:
                filtros.append(f"noise=alls={granulado}:allf=t+u")

            if usar_vinheta:
                filtros.append("vignette=PI/4")

            vf_final = ",".join(filtros)

            cmd_passo2 = [
                "ffmpeg", "-y", "-i", video_fonte,
                "-vf", vf_final,
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                "-pix_fmt", "yuv420p",
                "-movflags", "+faststart"
            ]

            if remover_audio:
                cmd_passo2.append("-an")
            else:
                cmd_passo2.extend(["-c:a", "aac"])

            cmd_passo2.append(output_file)
            subprocess.run(cmd_passo2, check=True)

            barra.progress(100, text="100% Concluído!")
            st.success("♠️ Vídeo finalizado no padrão House 72!")

            aba1, aba2 = st.tabs(["🎬 Take Final", "🔍 Lado a Lado (Bruto x Editado)"])
            with aba1:
                st.video(output_file)
            with aba2:
                col_a, col_b = st.columns(2)
                with col_a:
                    st.caption("Bruto")
                    st.video(video_fonte)
                with col_b:
                    st.caption("House 72 Lab")
                    st.video(output_file)

            with open(output_file, "rb") as f_out:
                st.download_button(
                    label="⬇️ SALVAR VÍDEO NO ROLO DA CÂMERA",
                    data=f_out,
                    file_name=f"House72_{uid[:4]}.mp4",
                    mime="video/mp4",
                    use_container_width=True
                )

        finally:
            for arq in [input_path, trimmed_path, trf_file, output_file]:
                if os.path.exists(arq):
                    os.remove(arq)
