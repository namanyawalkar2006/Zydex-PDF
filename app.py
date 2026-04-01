import streamlit as st
import fitz
from PIL import Image, ImageOps

st.set_page_config(layout="wide")

# ---------- CUSTOM CSS ----------
st.markdown("""
<style>
body {
    background-color: #0e0e0e;
}

.main {
    background-color: #0e0e0e;
}

.stButton>button {
    background: rgba(255,255,255,0.1);
    border-radius: 12px;
    color: white;
    border: none;
    padding: 8px 16px;
}

.stSlider label, .stCheckbox label {
    color: white;
}

.viewer-container {
    display: flex;
    justify-content: center;
    align-items: center;
}

.toolbar {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(30,30,30,0.6);
    backdrop-filter: blur(10px);
    padding: 10px 20px;
    border-radius: 20px;
    display: flex;
    gap: 10px;
}
</style>
""", unsafe_allow_html=True)

# ---------- STATE ----------
if "doc" not in st.session_state:
    st.session_state.doc = None
if "page" not in st.session_state:
    st.session_state.page = 0

# ---------- HEADER ----------
st.markdown("<h3 style='text-align:center;color:white;'>Ready for PDF...</h3>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("", type=["pdf"])

zoom = st.slider("Zoom", 1.0, 3.0, 1.5)
night_mode = st.checkbox("🌙")
show_text = st.checkbox("📄")

# ---------- LOAD ----------
if uploaded_file:
    st.session_state.doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")

# ---------- VIEW ----------
if st.session_state.doc:
    doc = st.session_state.doc

    page = doc.load_page(st.session_state.page)
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    if night_mode:
        img = ImageOps.invert(img)

    st.markdown("<div class='viewer-container'>", unsafe_allow_html=True)
    st.image(img)
    st.markdown("</div>", unsafe_allow_html=True)

    # Floating toolbar
    st.markdown("<div class='toolbar'>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("⬅️"):
            if st.session_state.page > 0:
                st.session_state.page -= 1

    with col2:
        st.markdown(f"<p style='color:white;'>Page {st.session_state.page+1}/{len(doc)}</p>", unsafe_allow_html=True)

    with col3:
        if st.button("➡️"):
            if st.session_state.page < len(doc)-1:
                st.session_state.page += 1

    st.markdown("</div>", unsafe_allow_html=True)

    if show_text:
        st.text_area("Text", page.get_text(), height=200)

else:
    st.markdown("<p style='text-align:center;color:gray;'>Upload a PDF</p>", unsafe_allow_html=True)
