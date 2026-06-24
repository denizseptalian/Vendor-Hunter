import streamlit as st
import requests
import json
import re

from datetime import datetime

# ─── Page Config ────────────────────────────────────────────────
st.set_page_config(
    page_title="VendorFinder Indonesia",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Custom CSS ─────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap');

    /* ── Reset & Base ── */
    html, body, .stApp {
        background: #0D1117 !important;
        color: #E6EDF3 !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* ── Hide Streamlit chrome ── */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding: 0 !important; max-width: 100% !important; }

    /* ── Hero Banner ── */
    .hero {
        background: linear-gradient(135deg, #0D1117 0%, #161B22 50%, #0D1117 100%);
        border-bottom: 1px solid #21262D;
        padding: 48px 60px 36px;
        position: relative;
        overflow: hidden;
    }
    .hero::before {
        content: '';
        position: absolute;
        top: -60px; right: -60px;
        width: 350px; height: 350px;
        background: radial-gradient(circle, rgba(88,166,255,0.08) 0%, transparent 70%);
        pointer-events: none;
    }
    .hero-eyebrow {
        font-size: 11px; font-weight: 600; letter-spacing: 2.5px;
        color: #58A6FF; text-transform: uppercase; margin-bottom: 12px;
    }
    .hero-title {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 42px; font-weight: 800; line-height: 1.15;
        color: #E6EDF3; margin: 0 0 12px;
    }
    .hero-title span { color: #58A6FF; }
    .hero-sub {
        font-size: 15px; color: #8B949E; font-weight: 400; max-width: 560px;
    }

    /* ── Search Panel ── */
    .search-panel {
        background: #161B22;
        border: 1px solid #21262D;
        border-radius: 14px;
        padding: 28px 32px;
        margin: 28px 60px;
    }
    .panel-label {
        font-size: 11px; font-weight: 600; letter-spacing: 1.8px;
        color: #58A6FF; text-transform: uppercase; margin-bottom: 18px;
    }

    /* ── Streamlit input overrides ── */
    .stTextInput > div > div > input,
    .stSelectbox > div > div {
        background: #0D1117 !important;
        border: 1px solid #30363D !important;
        border-radius: 8px !important;
        color: #E6EDF3 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 14px !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #58A6FF !important;
        box-shadow: 0 0 0 3px rgba(88,166,255,0.15) !important;
    }
    .stTextInput label, .stSelectbox label {
        color: #8B949E !important;
        font-size: 12px !important;
        font-weight: 500 !important;
        letter-spacing: 0.5px !important;
    }

    /* ── Search Button ── */
    .stButton > button {
        background: linear-gradient(135deg, #1F6FEB 0%, #388BFD 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        padding: 10px 28px !important;
        height: 44px !important;
        width: 100% !important;
        transition: all 0.2s ease !important;
        letter-spacing: 0.3px !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #388BFD 0%, #58A6FF 100%) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 16px rgba(88,166,255,0.35) !important;
    }

    /* ── Status Pills ── */
    .status-bar {
        display: flex; align-items: center; gap: 10px;
        margin: 8px 60px 0; padding-bottom: 4px;
    }
    .pill {
        display: inline-flex; align-items: center; gap: 6px;
        background: #161B22; border: 1px solid #21262D;
        border-radius: 20px; padding: 4px 12px;
        font-size: 11px; color: #8B949E; font-weight: 500;
    }
    .pill-dot { width: 6px; height: 6px; border-radius: 50%; }
    .dot-blue { background: #58A6FF; }
    .dot-green { background: #3FB950; }
    .dot-yellow { background: #D29922; }

    /* ── Results Section ── */
    .results-header {
        margin: 32px 60px 16px;
        display: flex; align-items: center; justify-content: space-between;
    }
    .results-title {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 18px; font-weight: 700; color: #E6EDF3;
    }
    .results-count {
        font-size: 12px; color: #58A6FF; font-weight: 600;
        background: rgba(88,166,255,0.1); border: 1px solid rgba(88,166,255,0.2);
        border-radius: 12px; padding: 3px 10px;
    }

    /* ── Vendor Card ── */
    .vendor-card {
        background: #161B22;
        border: 1px solid #21262D;
        border-radius: 12px;
        padding: 24px 28px;
        margin: 0 60px 16px;
        transition: border-color 0.2s ease;
        position: relative;
    }
    .vendor-card:hover { border-color: #30363D; }
    .vendor-card::before {
        content: ''; position: absolute;
        left: 0; top: 16px; bottom: 16px;
        width: 3px; background: linear-gradient(180deg, #1F6FEB, #388BFD);
        border-radius: 0 2px 2px 0;
    }
    .card-top {
        display: flex; justify-content: space-between;
        align-items: flex-start; margin-bottom: 16px;
    }
    .vendor-name {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 17px; font-weight: 700; color: #E6EDF3; margin-bottom: 4px;
    }
    .vendor-type {
        font-size: 11px; font-weight: 600; letter-spacing: 1.2px;
        color: #58A6FF; text-transform: uppercase;
    }
    .relevance-badge {
        font-size: 11px; font-weight: 700;
        background: rgba(63,185,80,0.12); border: 1px solid rgba(63,185,80,0.25);
        color: #3FB950; border-radius: 6px; padding: 3px 10px;
        white-space: nowrap;
    }
    .card-grid {
        display: grid; grid-template-columns: 1fr 1fr 1fr;
        gap: 14px; margin-bottom: 14px;
    }
    .card-field {
        background: #0D1117;
        border-radius: 8px; padding: 10px 14px;
    }
    .field-label {
        font-size: 10px; font-weight: 600; letter-spacing: 1.5px;
        color: #484F58; text-transform: uppercase; margin-bottom: 5px;
    }
    .field-value {
        font-size: 13px; color: #C9D1D9; line-height: 1.4;
    }
    .field-value a {
        color: #58A6FF; text-decoration: none;
    }
    .field-value a:hover { text-decoration: underline; }
    .card-description {
        font-size: 13px; color: #8B949E; line-height: 1.6;
        background: #0D1117; border-radius: 8px; padding: 12px 14px;
        margin-top: 2px;
    }
    .tag-row {
        display: flex; flex-wrap: wrap; gap: 6px; margin-top: 14px;
    }
    .tag {
        font-size: 11px; font-weight: 500; color: #58A6FF;
        background: rgba(88,166,255,0.08); border: 1px solid rgba(88,166,255,0.15);
        border-radius: 5px; padding: 2px 8px;
    }

    /* ── Empty / Loading States ── */
    .empty-state {
        text-align: center; padding: 80px 40px;
        margin: 0 60px;
    }
    .empty-icon { font-size: 48px; margin-bottom: 16px; }
    .empty-title {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 20px; font-weight: 700; color: #E6EDF3; margin-bottom: 8px;
    }
    .empty-sub { font-size: 14px; color: #484F58; }

    /* ── Divider ── */
    .section-divider {
        border: none; border-top: 1px solid #21262D;
        margin: 0 60px 24px;
    }

    /* ── Spinner override ── */
    .stSpinner > div { border-top-color: #58A6FF !important; }

    /* ── Sidebar ── */
    .css-1d391kg, [data-testid="stSidebar"] {
        background: #161B22 !important;
        border-right: 1px solid #21262D !important;
    }
</style>
""", unsafe_allow_html=True)


# ─── Constants ──────────────────────────────────────────────────
PROVINCES = [
    "Semua Provinsi",
    "DKI Jakarta", "Jawa Barat", "Jawa Tengah", "Jawa Timur", "DI Yogyakarta", "Banten",
    "Sumatera Utara", "Sumatera Barat", "Sumatera Selatan", "Riau", "Kepulauan Riau",
    "Lampung", "Bengkulu", "Jambi", "Aceh", "Kepulauan Bangka Belitung",
    "Kalimantan Barat", "Kalimantan Tengah", "Kalimantan Selatan", "Kalimantan Timur", "Kalimantan Utara",
    "Sulawesi Utara", "Sulawesi Tengah", "Sulawesi Selatan", "Sulawesi Tenggara", "Gorontalo", "Sulawesi Barat",
    "Bali", "Nusa Tenggara Barat", "Nusa Tenggara Timur",
    "Maluku", "Maluku Utara", "Papua", "Papua Barat",
]

CATEGORIES = [
    "Semua Kategori",
    "Pupuk & Agrokimia", "Alat & Mesin Pertanian", "Benih & Bibit",
    "Jasa Konstruksi & Sipil", "Material Bangunan", "Peralatan & Spare Part",
    "Logistik & Transportasi", "IT & Teknologi", "Seragam & APD",
    "Bahan Bakar & Pelumas", "Makanan & Sembako", "Jasa Konsultan",
    "Perlengkapan Kantor", "Peralatan Lab", "Lainnya",
]


# ─── AI Search Function (Gemini) ────────────────────────────────
def search_vendors(keyword: str, location: str, category: str) -> list[dict]:
    """Call Gemini with Google Search grounding to find vendors."""
    api_key = st.secrets.get("GEMINI_API_KEY") or st.secrets.get("gemini_api_key")
    if not api_key:
        st.error("❌ API Key tidak ditemukan! Pastikan Streamlit Secrets sudah diisi dengan GEMINI_API_KEY.")
        return []

    location_ctx = location if location != "Semua Provinsi" else "Indonesia"
    cat_ctx = f" kategori {category}" if category != "Semua Kategori" else ""

    prompt = f"""Cari informasi vendor/supplier yang menjual atau menyediakan "{keyword}"{cat_ctx} di wilayah {location_ctx}, Indonesia.

Gunakan Google Search untuk menemukan vendor nyata. Prioritaskan:
1. Perusahaan atau toko yang beroperasi di {location_ctx}
2. Vendor yang relevan dengan kata kunci: {keyword}
3. Informasi kontak yang dapat diverifikasi

Cari minimal 5 vendor berbeda. Kembalikan hasil HANYA dalam format JSON array berikut (tanpa markdown, tanpa penjelasan tambahan):

[
  {{
    "nama": "Nama Perusahaan/Toko",
    "tipe": "Distributor / Supplier / Toko / Produsen / Importir",
    "alamat": "Alamat lengkap termasuk kota dan provinsi",
    "kota": "Nama kota",
    "provinsi": "Nama provinsi",
    "telepon": "Nomor telepon (jika ada, tulis '-' jika tidak ada)",
    "email": "Email (jika ada, tulis '-' jika tidak ada)",
    "website": "URL website (jika ada, tulis '-' jika tidak ada)",
    "whatsapp": "Nomor WhatsApp (jika ada, tulis '-' jika tidak ada)",
    "produk_utama": "Daftar produk utama yang dijual",
    "deskripsi": "Deskripsi singkat tentang vendor ini dan produknya",
    "tags": ["tag1", "tag2", "tag3"],
    "relevansi": "Tinggi / Sedang"
  }}
]

Kembalikan HANYA JSON array, tidak ada teks lain."""

    import time

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "tools": [{"google_search": {}}],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 4000}
    }

    # Retry dengan exponential backoff untuk handle 429
    max_retries = 4
    wait_seconds = [5, 15, 30, 60]

    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=payload, timeout=60)

            if response.status_code == 429:
                wait = wait_seconds[min(attempt, len(wait_seconds)-1)]
                st.warning(f"⏳ Rate limit tercapai. Mencoba lagi dalam {wait} detik... (percobaan {attempt+1}/{max_retries})")
                import time as _t; _t.sleep(wait)
                continue

            response.raise_for_status()
            data = response.json()

            full_text = ""
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                for part in parts:
                    if "text" in part:
                        full_text += part["text"]

            full_text = re.sub(r"```json|```", "", full_text).strip()

            json_match = re.search(r'\[[\s\S]*\]', full_text)
            if json_match:
                vendors = json.loads(json_match.group())
                return vendors
            return []

        except requests.exceptions.HTTPError as e:
            err_body = e.response.json() if e.response else {}
            msg = err_body.get("error", {}).get("message", str(e))
            st.error(f"❌ Gemini API Error: {msg}")
            return []
        except Exception as e:
            if attempt < max_retries - 1:
                wait = wait_seconds[min(attempt, len(wait_seconds)-1)]
                st.warning(f"⏳ Error sementara, mencoba lagi dalam {wait} detik...")
                import time as _t; _t.sleep(wait)
                continue
            st.error(f"❌ Error saat mencari vendor: {str(e)}")
            return []

    st.error("❌ Gagal setelah beberapa percobaan. Tunggu 1 menit lalu coba lagi.")
    return []


# ─── Render Vendor Card ─────────────────────────────────────────
def render_vendor_card(vendor: dict, idx: int):
    relevansi_color = "#3FB950" if vendor.get("relevansi") == "Tinggi" else "#D29922"
    relevansi_text = vendor.get("relevansi", "Sedang")

    phone = vendor.get("telepon", "-")
    email = vendor.get("email", "-")
    website = vendor.get("website", "-")
    wa = vendor.get("whatsapp", "-")
    
    website_html = f'<a href="{website}" target="_blank">{website}</a>' if website != "-" else "-"
    wa_html = f'<a href="https://wa.me/{wa.replace("+","").replace("-","").replace(" ","")}" target="_blank">{wa}</a>' if wa != "-" else "-"

    tags = vendor.get("tags", [])
    tags_html = "".join([f'<span class="tag">{t}</span>' for t in tags[:6]])

    html = f"""
    <div class="vendor-card">
        <div class="card-top">
            <div>
                <div class="vendor-name">🏢 {vendor.get("nama", "—")}</div>
                <div class="vendor-type">{vendor.get("tipe", "Vendor")}</div>
            </div>
            <div class="relevance-badge" style="color:{relevansi_color};border-color:rgba(63,185,80,0.25);">
                ● Relevansi {relevansi_text}
            </div>
        </div>

        <div class="card-grid">
            <div class="card-field">
                <div class="field-label">📍 Alamat</div>
                <div class="field-value">{vendor.get("alamat", "-")}</div>
            </div>
            <div class="card-field">
                <div class="field-label">📞 Telepon</div>
                <div class="field-value">{phone}</div>
            </div>
            <div class="card-field">
                <div class="field-label">✉️ Email</div>
                <div class="field-value">{email}</div>
            </div>
            <div class="card-field">
                <div class="field-label">💬 WhatsApp</div>
                <div class="field-value">{wa_html}</div>
            </div>
            <div class="card-field">
                <div class="field-label">🌐 Website</div>
                <div class="field-value">{website_html}</div>
            </div>
            <div class="card-field">
                <div class="field-label">📦 Produk Utama</div>
                <div class="field-value">{vendor.get("produk_utama", "-")}</div>
            </div>
        </div>

        <div class="card-description">
            {vendor.get("deskripsi", "-")}
        </div>

        <div class="tag-row">{tags_html}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


# ─── Session State ───────────────────────────────────────────────
if "results" not in st.session_state:
    st.session_state.results = []
if "last_search" not in st.session_state:
    st.session_state.last_search = {}
if "search_done" not in st.session_state:
    st.session_state.search_done = False


# ─── Hero ────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">🔍 Vendor Intelligence Platform</div>
    <div class="hero-title">Temukan <span>Vendor Terbaik</span><br>di Seluruh Indonesia</div>
    <div class="hero-sub">Cari supplier dan vendor berdasarkan produk & lokasi. Data real-time dari seluruh penjuru Indonesia.</div>
</div>
""", unsafe_allow_html=True)

# Status pills
st.markdown("""
<div class="status-bar">
    <span class="pill"><span class="pill-dot dot-green"></span>AI Powered</span>
    <span class="pill"><span class="pill-dot dot-blue"></span>Web Search Aktif</span>
    <span class="pill"><span class="pill-dot dot-yellow"></span>Data Real-time</span>
</div>
""", unsafe_allow_html=True)


# ─── Search Panel ────────────────────────────────────────────────
st.markdown('<div class="search-panel"><div class="panel-label">🔎 Parameter Pencarian</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns([3, 2, 2, 1.2])

with col1:
    keyword = st.text_input(
        "Kata Kunci Barang / Produk",
        placeholder="contoh: pupuk urea, solar panel, genset, besi beton…",
        key="keyword_input",
    )

with col2:
    location = st.selectbox("Provinsi / Wilayah", PROVINCES, key="location_select")

with col3:
    category = st.selectbox("Kategori Vendor", CATEGORIES, key="category_select")

with col4:
    st.markdown("<br>", unsafe_allow_html=True)
    search_clicked = st.button("🔍 Cari Vendor", key="search_btn")

st.markdown('</div>', unsafe_allow_html=True)


# ─── Search Logic ───────────────────────────────────────────────
if search_clicked:
    if not keyword.strip():
        st.warning("⚠️ Masukkan kata kunci produk/barang terlebih dahulu.")
    else:
        with st.spinner("🤖 AI sedang mencari vendor... harap tunggu sebentar"):
            results = search_vendors(keyword.strip(), location, category)
            st.session_state.results = results
            st.session_state.search_done = True
            st.session_state.last_search = {
                "keyword": keyword.strip(),
                "location": location,
                "category": category,
                "timestamp": datetime.now().strftime("%H:%M:%S — %d %B %Y"),
            }


# ─── Results ────────────────────────────────────────────────────
if st.session_state.search_done:
    results = st.session_state.results
    meta = st.session_state.last_search

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # Results header
    count_html = f'<span class="results-count">{len(results)} vendor ditemukan</span>' if results else ""
    st.markdown(f"""
    <div class="results-header">
        <div class="results-title">
            Hasil untuk "<b>{meta.get("keyword","")}</b>" · {meta.get("location","")}
        </div>
        {count_html}
    </div>
    <p style="margin:-4px 60px 20px;font-size:12px;color:#484F58;">
        Dicari pada {meta.get("timestamp","")}
    </p>
    """, unsafe_allow_html=True)

    if results:
        # Sort: Tinggi first
        sorted_results = sorted(results, key=lambda x: 0 if x.get("relevansi") == "Tinggi" else 1)
        for i, vendor in enumerate(sorted_results):
            render_vendor_card(vendor, i)

        # Footer note
        st.markdown(f"""
        <div style="margin:24px 60px 48px;padding:14px 20px;
             background:#161B22;border:1px solid #21262D;border-radius:8px;
             font-size:12px;color:#484F58;line-height:1.6;">
            ⚠️ <b style="color:#8B949E;">Disclaimer:</b>
            Data vendor diperoleh dari web search secara real-time. Selalu verifikasi informasi kontak
            dan reputasi vendor sebelum melakukan transaksi. Jumlah hasil: <b style="color:#58A6FF;">{len(results)} vendor</b>.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">🔎</div>
            <div class="empty-title">Tidak ada vendor ditemukan</div>
            <div class="empty-sub">Coba ubah kata kunci, lokasi, atau kategori pencarian Anda.</div>
        </div>
        """, unsafe_allow_html=True)

elif not st.session_state.search_done:
    # Default empty state
    st.markdown("""
    <div class="empty-state">
        <div class="empty-icon">🏭</div>
        <div class="empty-title">Siap Mencari Vendor</div>
        <div class="empty-sub">Masukkan kata kunci produk dan pilih lokasi,<br>AI akan menemukan vendor terbaik untuk Anda.</div>
    </div>
    """, unsafe_allow_html=True)
