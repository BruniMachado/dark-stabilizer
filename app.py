import os
import subprocess
import uuid
import streamlit as st

st.set_page_config(page_title="House 72 — Pro Ink Lab", page_icon="🖤", layout="centered")

# Tema Dark Gótico de Estúdio
st.markdown("""
    <style>
    .stApp { background-color: #08080a; color: #f4f4f5; }
    div[data-testid="stExpander"] { background-color: #111115; border: 1px solid #27272a; border-radius: 10px; }
    .stButton>button { background-color: #dc2626; color: white; border-radius: 8px; font-weight: 700; border: none; height: 3.2em; letter-spacing: 0.5px; }
    .stButton>button:hover { background-color: #991b1b; color: white; }
    </style>
""", unsafe_allow_html=True)

st.title("🖤 House 72 — Pro Tattoo Video Lab")
st.caption("Estabilização VidStab + Correção de Pele & Filtros Dark para Tatuadores")

# Catálogo expandido de filtros para Tattoo & Piercing
PRESETS = {
    "1. Temperamento (Frio + Sombras Densas + Vinheta)": {
        "contrast": 1.25, "brightness": -0.05, "saturation": 0.68,
        "extra_filter": "colorbalance=bs=0.08:bm=0.05:rh=-0.03",
        "vignette": True, "red_reduce": False, " sharp": 0.9
    },
    "2. Black & Grey Master (P&B Realismo Profundo)": {
        "contrast": 1.38, "brightness": -0.04, "saturation": 0.0,
        "extra_filter": "curves=m='0/0 0.25/0.18 0.75/0.82 1/0.95'",
        "vignette": True, "red_reduce": False, "sharp": 1.1
    },
    "3. Chicano Street Noir (P&B Dramático + Textura)": {
        "contrast": 1.48, "brightness": -0.07, "saturation": 0.0,
        "extra_filter": "curves=m='0/0 0.30/0.15 0.75/0.85 1/0.92'",
        "vignette": True, "red_reduce": False, "sharp": 1.2
    },
    "4. Gothic Darkroom (Sombrio + Tons Frios Azuis)": {
        "contrast": 1.35, "brightness": -0.08, "saturation": 0.45,
        "extra_filter": "colorbalance=bs=0.14:bm=0.07:gs=-0.04:rs=-0.06",
        "vignette": True, "red_reduce": True, "sharp": 0.9
    },
    "5. Fine Line & Whip Shading (Nitidez + Pele Sem Vermelhidão)": {
        "contrast": 1.20, "brightness": -0.02, "saturation": 0.75,
        "extra_filter": "colorbalance=rs=-0.10:rm=-0.08:bs=0.03",
        "vignette": False, "red_reduce": True, "sharp": 1.4
    },
    "6. Titanium Piercing Glow (Destaque Metálico + Fundo Dark)": {
        "contrast": 1.30, "brightness": -0.06, "saturation": 0.80,
        "extra_filter": "colorbalance=bs=0.06:bh=0.06:rm=-0.05",
        "vignette": True, "red_reduce": True, "sharp": 1.5
    },
    "7. Matte Cinema Ink (Pretos Acinzentados Estilo Filme)": {
        "contrast": 1.18, "brightness": -0.03, "saturation": 0.55,
        "extra_filter": "curves=m='0/0.06 0.25/0.20 0.75/0.80 1/0.92'",
        "vignette": True, "red_reduce": False, "sharp": 0.8
    },
    "8. Apenas Estabilizar (Cores Originais da Câmera)": {
        "contrast": 1.0, "brightness": 0.0, "saturation": 1.0,
        "extra_filter": "",
        "vignette": False, "red_reduce": False, "sharp": 0.5
    }
}

video_up = st.file_uploader("📱 1. Selecionar Vídeo da Tattoo / Piercing (.MOV ou .MP4)", type=["mov", "mp4", "m4v"])

preset_nome = st.selectbox("🎨 2. Escolher Estética / Filtro Dark:", list(PRESETS.keys()))
p_base = PRESETS[preset_nome]

suavizacao = st.slider(
    "⚖️ 3. Nível de Estabilização (Tremedeira da Mão)",
    min_value=0, max_value=60, value=35,
    help="Coloque em 0 se o vídeo já estiver no tripé e você quiser apenas aplicar o filtro rápido."
)

# Ferramentas Exclusivas para Estúdio de Tattoo
st.markdown("##### 🛠️ Ferramentas de Estúdio (Pele & Iluminação)")
col_t1, col_t2 = st.columns(2)
with col_t1:
    reduzir_vermelho = st.checkbox("🩹 Suavizar Vermelhidão da Pele", value=p_base["red_reduce"], help="Diminui o tom avermelhado da pele recém-tatuada.")
    anti_reflexo = st.checkbox("💡 Filtro Polarizador (Reduzir Reflexo da Luz)", value=True, help="Ameniza o brilho branco estourado da Ring Light / Vaselina.")
with col_t2:
    formato_reels = st.checkbox("📐 Forçar Formato Reels 9:16 (1080x1920)", value=False, help="Corta e centraliza automaticamente no formato vertical do Instagram.")
    remover_audio = st.checkbox("🔇 Silenciar Vídeo (Tirar barulho de fundo)", value=True)

# Corte de início/fim e Ajustes Finos
with st.expander("✂️ Cortar Pontas do Vídeo & Ajustes Finos Manuais"):
    st.caption("Útil para cortar o momento em que você aperta o botão de gravar/parar:")
    c_trim1, c_trim2 = st.columns(2)
    with c_trim1:
        cortar_inicio = st.number_input("Cortar segundos no INÍCIO:", min_value=0.0, max_value=30.0, value=0.0, step=0.5)
    with c_trim2:
        duracao_max = st.number_input("Duração máxima do vídeo (0 = Tudo):", min_value=0.0, max_value=120.0, value=0.0, step=1.0)

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        contraste = st.slider("Contraste (Força do Preto)", 0.80, 1.80, float(p_base["contrast"]), 0.05)
        brilho = st.slider("Exposição / Escurecer Fundo", -0.30, 0.20, float(p_base["brightness"]), 0.01)
        saturacao = st.slider("Saturação Geral", 0.0, 1.50, float(p_base["saturation"]), 0.05)
    with c2:
        nitidez = st.slider("Nitidez do Traço (Fine Line / Sombra)", 0.0, 2.5, float(p_base["sharp"]), 0.1)
        granulado = st.slider("Textura Granulada (Grain Dark)", 0, 25, 6 if "Chicano" in preset_nome or "Gothic" in preset_nome else 0)
        usar_vinheta = st.checkbox("Bordas Escuras (Vinheta)", value=p_base["vignette"])

if st.button("🔥 PROCESSAR VÍDEO NO DARK LAB", use_container_width=True):
    if not video_up:
        st.error("Selecione um vídeo da sua galeria primeiro!")
    else:
        uid = uuid.uuid4().hex[:8]
        input_path = f"raw_{uid}.mov"
        trimmed_path = f"trim_{uid}.mov"
        trf_file = f"transforms_{uid}.trf"
        output_file = f"House72_{uid}.mp4"

        with open(input_path, "wb") as f:
            f.write(video_up.read())

        barra = st.progress(0, text="Preparando arquivo...")

        try:
            video_fonte = input_path

            # Se o usuário pediu para cortar o início ou limitar duração
            if cortar_inicio > 0 or duracao_max > 0:
                barra.progress(10, text="Cortando início/fim do vídeo...")
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

            # Passo 1: Estabilização Two-Pass
            if suavizacao > 0:
                barra.progress(25, text="1/2: Analisando tremedeira da mão...")
                cmd_passo1 = [
                    "ffmpeg", "-y", "-i", video_fonte,
                    "-vf", f"vidstabdetect=shakiness=8:accuracy=15:result={trf_file}",
                    "-f", "null", "-"
                ]
                subprocess.run(cmd_passo1, check=True)
                filtros.append(f"vidstabtransform=smoothing={suavizacao}:input={trf_file}:crop=black:zoom=3")

            barra.progress(60, text="2/2: Aplicando estética Dark, corrigindo pele e renderizando...")

            # Enquadramento 9:16 ou Otimização 1080p
            if formato_reels:
                filtros.append("scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920")
            else:
                filtros.append("scale='min(1080,iw)':-2")

            # Nitidez nos traços da tattoo
            if nitidez > 0:
                filtros.append(f"unsharp=5:5:{nitidez}:3:3:0.4")

            # Redutor de vermelhidão da pele irritada (atua se o vídeo não for P&B)
            if reduzir_vermelho and saturacao > 0:
                filtros.append("colorbalance=rs=-0.12:rm=-0.08:rh=-0.04:bs=0.04")

            # Filtro Polarizador Digital (segura o estouro branco da luz na pele)
            if anti_reflexo:
                filtros.append("curves=m='0/0 0.5/0.5 0.85/0.82 1/0.90'")

            # Ajuste base de Contraste, Brilho e Saturação
            filtros.append(f"eq=contrast={contraste}:brightness={brilho}:saturation={saturacao}")

            # Filtro extra específico do Preset escolhido
            if p_base["extra_filter"]:
                filtros.append(p_base["extra_filter"])

            # Granulado estilo filme
            if granulado > 0:
                filtros.append(f"noise=alls={granulado}:allf=t+u")

            # Vinheta escura
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

            barra.progress(100, text="Vídeo finalizado!")
            st.success("✅ Pronto para postar!")

            aba1, aba2 = st.tabs(["🎬 Resultado Final", "🔍 Antes x Depois"])
            with aba1:
                st.video(output_file)
            with aba2:
                col_a, col_b = st.columns(2)
                with col_a:
                    st.caption("Original")
                    st.video(video_fonte)
                with col_b:
                    st.caption("Dark Lab")
                    st.video(output_file)

            with open(output_file, "rb") as f_out:
                st.download_button(
                    label="⬇️ BAIXAR VÍDEO PRONTO",
                    data=f_out,
                    file_name=f"House72_Ink_{uid[:4]}.mp4",
                    mime="video/mp4",
                    use_container_width=True
                )

        finally:
            for arq in [input_path, trimmed_path, trf_file, output_file]:
                if os.path.exists(arq):
                    os.remove(arq)
