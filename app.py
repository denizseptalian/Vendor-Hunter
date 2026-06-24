import streamlit as st
import json, re, requests
from datetime import datetime
from groq import Groq

# ─── Page Config ────────────────────────────────────────────────
st.set_page_config(page_title="VendorFinder Indonesia", page_icon="🔍", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap');
html,body,.stApp{background:#0D1117!important;color:#E6EDF3!important;font-family:'Inter',sans-serif!important}
#MainMenu,footer,header{visibility:hidden}
.block-container{padding:0!important;max-width:100%!important}
.hero{background:linear-gradient(135deg,#0D1117 0%,#161B22 50%,#0D1117 100%);border-bottom:1px solid #21262D;padding:40px 60px 32px;position:relative;overflow:hidden}
.hero::before{content:'';position:absolute;top:-60px;right:-60px;width:350px;height:350px;background:radial-gradient(circle,rgba(88,166,255,0.08) 0%,transparent 70%);pointer-events:none}
.hero-eyebrow{font-size:11px;font-weight:600;letter-spacing:2.5px;color:#58A6FF;text-transform:uppercase;margin-bottom:12px}
.hero-title{font-family:'Plus Jakarta Sans',sans-serif;font-size:38px;font-weight:800;line-height:1.15;color:#E6EDF3;margin:0 0 10px}
.hero-title span{color:#58A6FF}
.hero-sub{font-size:14px;color:#8B949E;max-width:520px}
.search-panel{background:#161B22;border:1px solid #21262D;border-radius:14px;padding:24px 28px;margin:24px 60px}
.panel-label{font-size:11px;font-weight:600;letter-spacing:1.8px;color:#58A6FF;text-transform:uppercase;margin-bottom:16px}
.stTextInput>div>div>input,.stSelectbox>div>div{background:#0D1117!important;border:1px solid #30363D!important;border-radius:8px!important;color:#E6EDF3!important;font-family:'Inter',sans-serif!important;font-size:14px!important}
.stTextInput>div>div>input:focus{border-color:#58A6FF!important;box-shadow:0 0 0 3px rgba(88,166,255,0.15)!important}
.stTextInput label,.stSelectbox label{color:#8B949E!important;font-size:12px!important;font-weight:500!important}
.stButton>button{background:linear-gradient(135deg,#1F6FEB 0%,#388BFD 100%)!important;color:white!important;border:none!important;border-radius:8px!important;font-size:14px!important;font-weight:600!important;height:44px!important;width:100%!important}
.stButton>button:hover{background:linear-gradient(135deg,#388BFD 0%,#58A6FF 100%)!important;transform:translateY(-1px)!important;box-shadow:0 4px 16px rgba(88,166,255,0.35)!important}
.status-bar{display:flex;align-items:center;gap:10px;margin:8px 60px 0}
.pill{display:inline-flex;align-items:center;gap:6px;background:#161B22;border:1px solid #21262D;border-radius:20px;padding:4px 12px;font-size:11px;color:#8B949E;font-weight:500}
.pill-dot{width:6px;height:6px;border-radius:50%}
.dot-green{background:#3FB950}.dot-blue{background:#58A6FF}.dot-yellow{background:#D29922}
.results-header{margin:28px 60px 14px;display:flex;align-items:center;justify-content:space-between}
.results-title{font-family:'Plus Jakarta Sans',sans-serif;font-size:17px;font-weight:700;color:#E6EDF3}
.results-count{font-size:12px;color:#58A6FF;font-weight:600;background:rgba(88,166,255,0.1);border:1px solid rgba(88,166,255,0.2);border-radius:12px;padding:3px 10px}
.vendor-card{background:#161B22;border:1px solid #21262D;border-radius:12px;padding:22px 26px;margin:0 60px 14px;position:relative}
.vendor-card:hover{border-color:#30363D}
.vendor-card::before{content:'';position:absolute;left:0;top:16px;bottom:16px;width:3px;background:linear-gradient(180deg,#1F6FEB,#388BFD);border-radius:0 2px 2px 0}
.vendor-name{font-family:'Plus Jakarta Sans',sans-serif;font-size:16px;font-weight:700;color:#E6EDF3;margin-bottom:4px}
.vendor-type{font-size:11px;color:#58A6FF;font-weight:600;letter-spacing:1px;text-transform:uppercase}
.card-grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin:14px 0}
.card-field{background:#0D1117;border-radius:8px;padding:10px 13px}
.field-label{font-size:10px;font-weight:600;letter-spacing:1.5px;color:#484F58;text-transform:uppercase;margin-bottom:4px}
.field-value{font-size:13px;color:#C9D1D9;line-height:1.4;word-break:break-word}
.field-value a{color:#58A6FF;text-decoration:none}
.card-desc{font-size:13px;color:#8B949E;line-height:1.6;background:#0D1117;border-radius:8px;padding:11px 13px}
.tag-row{display:flex;flex-wrap:wrap;gap:6px;margin-top:12px}
.tag{font-size:11px;color:#58A6FF;background:rgba(88,166,255,0.08);border:1px solid rgba(88,166,255,0.15);border-radius:5px;padding:2px 8px}
.empty-state{text-align:center;padding:70px 40px;margin:0 60px}
.empty-icon{font-size:44px;margin-bottom:14px}
.empty-title{font-family:'Plus Jakarta Sans',sans-serif;font-size:18px;font-weight:700;color:#E6EDF3;margin-bottom:8px}
.empty-sub{font-size:14px;color:#484F58}
hr.divider{border:none;border-top:1px solid #21262D;margin:0 60px 20px}
</style>
""", unsafe_allow_html=True)

# ─── Constants ───────────────────────────────────────────────────
PROVINCES = ["Semua Provinsi","DKI Jakarta","Jawa Barat","Jawa Tengah","Jawa Timur","DI Yogyakarta","Banten","Sumatera Utara","Sumatera Barat","Sumatera Selatan","Riau","Kepulauan Riau","Lampung","Bengkulu","Jambi","Aceh","Kepulauan Bangka Belitung","Kalimantan Barat","Kalimantan Tengah","Kalimantan Selatan","Kalimantan Timur","Kalimantan Utara","Sulawesi Utara","Sulawesi Tengah","Sulawesi Selatan","Sulawesi Tenggara","Gorontalo","Sulawesi Barat","Bali","Nusa Tenggara Barat","Nusa Tenggara Timur","Maluku","Maluku Utara","Papua","Papua Barat"]
CATEGORIES = ["Semua Kategori","Pupuk & Agrokimia","Alat & Mesin Pertanian","Benih & Bibit","Jasa Konstruksi & Sipil","Material Bangunan","Peralatan & Spare Part","Logistik & Transportasi","IT & Teknologi","Seragam & APD","Bahan Bakar & Pelumas","Makanan & Sembako","Jasa Konsultan","Perlengkapan Kantor","Peralatan Lab","Lainnya"]

# ─── Search (cached agar tidak double-request) ──────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def search_vendors(keyword: str, location: str, category: str) -> list:
    api_key = st.secrets.get("GROQ_API_KEY", "")
    if not api_key:
        st.error("❌ GROQ_API_KEY tidak ditemukan di Streamlit Secrets.")
        return []

    location_ctx = location if location != "Semua Provinsi" else "seluruh Indonesia"
    cat_ctx = f" dalam kategori {category}" if category != "Semua Kategori" else ""

    prompt = f"""Kamu adalah database vendor Indonesia. Berikan daftar 6 vendor/supplier nyata yang menjual "{keyword}"{cat_ctx} di {location_ctx}.

Untuk setiap vendor, berikan informasi selengkap mungkin. Kembalikan HANYA JSON array ini (tanpa markdown, tanpa teks lain):

[
  {{
    "nama": "Nama perusahaan lengkap",
    "tipe": "Distributor/Supplier/Produsen/Toko/Importir",
    "alamat": "Alamat lengkap dengan kota dan provinsi",
    "kota": "Nama kota",
    "provinsi": "Nama provinsi",
    "telepon": "Nomor telepon (format Indonesia, atau '-')",
    "email": "Email perusahaan (atau '-')",
    "website": "URL website (atau '-')",
    "whatsapp": "Nomor WA bisnis (atau '-')",
    "produk_utama": "Produk-produk utama yang dijual",
    "deskripsi": "Deskripsi 2-3 kalimat tentang vendor dan keunggulannya",
    "tags": ["tag1", "tag2", "tag3"],
    "min_order": "Minimum order (atau '-')",
    "area_kirim": "Area pengiriman"
  }}
]

Fokus pada vendor yang benar-benar beroperasi di {location_ctx} dengan produk {keyword}. Hanya JSON, tidak ada teks lain."""

    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=3000,
        )
        text = response.choices[0].message.content.strip()
        text = re.sub(r"```json|```", "", text).strip()
        match = re.search(r'\[[\s\S]*\]', text)
        if match:
            return json.loads(match.group())
        return []
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return []


# ─── Render Card ─────────────────────────────────────────────────
def render_card(v: dict):
    phone   = v.get("telepon", "-")
    email   = v.get("email", "-")
    website = v.get("website", "-")
    wa      = v.get("whatsapp", "-")

    wa_num  = re.sub(r'\D', '', wa if wa != '-' else phone).lstrip('0')
    wa_url  = f"https://wa.me/62{wa_num}" if wa_num else None

    ph_html  = f'<a href="tel:{phone}">{phone}</a>'     if phone   != '-' else '-'
    em_html  = f'<a href="mailto:{email}">{email}</a>'  if email   != '-' else '-'
    web_html = f'<a href="{website}" target="_blank">{website[:40]}...</a>' if website != '-' and len(website) > 40 else (f'<a href="{website}" target="_blank">{website}</a>' if website != '-' else '-')
    wa_html  = f'<a href="{wa_url}" target="_blank">💬 Chat WhatsApp</a>' if wa_url else '-'

    tags_html = "".join(f'<span class="tag">{t}</span>' for t in v.get("tags", [])[:5])

    st.markdown(f"""
    <div class="vendor-card">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:14px">
        <div>
          <div class="vendor-name">🏢 {v.get("nama","—")}</div>
          <div class="vendor-type">{v.get("tipe","Vendor")} · {v.get("kota","")} {v.get("provinsi","")}</div>
        </div>
        <div style="font-size:11px;color:#3FB950;background:rgba(63,185,80,0.1);border:1px solid rgba(63,185,80,0.2);border-radius:6px;padding:3px 10px;white-space:nowrap">
          ● Area: {v.get("area_kirim","-")}
        </div>
      </div>
      <div class="card-grid">
        <div class="card-field"><div class="field-label">📍 Alamat</div><div class="field-value">{v.get("alamat","-")}</div></div>
        <div class="card-field"><div class="field-label">📞 Telepon</div><div class="field-value">{ph_html}</div></div>
        <div class="card-field"><div class="field-label">✉️ Email</div><div class="field-value">{em_html}</div></div>
        <div class="card-field"><div class="field-label">💬 WhatsApp</div><div class="field-value">{wa_html}</div></div>
        <div class="card-field"><div class="field-label">🌐 Website</div><div class="field-value">{web_html}</div></div>
        <div class="card-field"><div class="field-label">📦 Min. Order</div><div class="field-value">{v.get("min_order","-")}</div></div>
      </div>
      <div class="card-desc"><b style="color:#C9D1D9">Produk:</b> {v.get("produk_utama","-")}<br><br>{v.get("deskripsi","-")}</div>
      <div class="tag-row">{tags_html}</div>
    </div>
    """, unsafe_allow_html=True)


# ─── Session State ───────────────────────────────────────────────
for k, v in [("results",[]),("done",False),("meta",{})]:
    if k not in st.session_state: st.session_state[k] = v

# ─── Hero ────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-eyebrow">🔍 Vendor Intelligence Platform</div>
  <div class="hero-title">Temukan <span>Vendor Terbaik</span><br>di Seluruh Indonesia</div>
  <div class="hero-sub">Cari supplier & vendor berdasarkan produk dan lokasi. Gratis, cepat, tanpa batas.</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="status-bar">
  <span class="pill"><span class="pill-dot dot-green"></span>100% Gratis</span>
  <span class="pill"><span class="pill-dot dot-blue"></span>Groq AI · Llama 3.1</span>
  <span class="pill"><span class="pill-dot dot-yellow"></span>14.400 req/hari</span>
</div>
""", unsafe_allow_html=True)

# ─── Search Panel ────────────────────────────────────────────────
st.markdown('<div class="search-panel"><div class="panel-label">🔎 Parameter Pencarian</div>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns([3, 2, 2, 1.2])
with c1: keyword  = st.text_input("Kata Kunci Barang / Produk", placeholder="contoh: pupuk urea, genset, besi beton…", key="kw")
with c2: location = st.selectbox("Provinsi / Wilayah", PROVINCES, key="loc")
with c3: category = st.selectbox("Kategori Vendor", CATEGORIES, key="cat")
with c4:
    st.markdown("<br>", unsafe_allow_html=True)
    clicked = st.button("🔍 Cari Vendor")
st.markdown('</div>', unsafe_allow_html=True)

# ─── Search Logic ────────────────────────────────────────────────
if clicked:
    if not keyword.strip():
        st.warning("⚠️ Masukkan kata kunci produk terlebih dahulu.")
    else:
        with st.spinner("🤖 AI sedang mencari vendor terbaik…"):
            results = search_vendors(keyword.strip(), location, category)
            st.session_state.results = results
            st.session_state.done    = True
            st.session_state.meta    = {"keyword": keyword.strip(), "location": location, "time": datetime.now().strftime("%H:%M:%S — %d %B %Y")}

# ─── Results ─────────────────────────────────────────────────────
if st.session_state.done:
    results = st.session_state.results
    meta    = st.session_state.meta
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    cnt = f'<span class="results-count">{len(results)} vendor</span>' if results else ""
    st.markdown(f"""
    <div class="results-header">
      <div class="results-title">Hasil: "<b>{meta.get("keyword","")}</b>" · {meta.get("location","")}</div>
      {cnt}
    </div>
    <p style="margin:-4px 60px 18px;font-size:12px;color:#484F58">{meta.get("time","")}</p>
    """, unsafe_allow_html=True)

    if results:
        for v in results: render_card(v)
        st.markdown("""
        <div style="margin:20px 60px 48px;padding:12px 18px;background:#161B22;border:1px solid #21262D;border-radius:8px;font-size:12px;color:#484F58">
          ⚠️ <b style="color:#8B949E">Disclaimer:</b> Data dihasilkan oleh AI berdasarkan pengetahuan model.
          Selalu verifikasi kontak dan informasi vendor sebelum bertransaksi.
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div class="empty-state"><div class="empty-icon">🔎</div><div class="empty-title">Tidak ada hasil</div><div class="empty-sub">Coba ubah kata kunci atau lokasi.</div></div>', unsafe_allow_html=True)

else:
    st.markdown('<div class="empty-state"><div class="empty-icon">🏭</div><div class="empty-title">Siap Mencari Vendor</div><div class="empty-sub">Masukkan kata kunci dan pilih lokasi untuk mulai.</div></div>', unsafe_allow_html=True)
