import streamlit as st
import json, re
from datetime import datetime
from groq import Groq
import folium
from streamlit_folium import st_folium

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
.map-section{margin:0 60px 8px;background:#161B22;border:1px solid #21262D;border-radius:14px;overflow:hidden}
.map-header{padding:16px 24px 12px;border-bottom:1px solid #21262D;display:flex;align-items:center;justify-content:space-between}
.map-title{font-family:'Plus Jakarta Sans',sans-serif;font-size:15px;font-weight:700;color:#E6EDF3}
.map-sub{font-size:12px;color:#8B949E}
.map-body{padding:0}
.results-header{margin:24px 60px 14px;display:flex;align-items:center;justify-content:space-between}
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

# ─── Koordinat Kota Indonesia ─────────────────────────────────────
CITY_COORDS = {
    # Jawa
    "jakarta": (-6.2088, 106.8456), "jakarta pusat": (-6.1862, 106.8342),
    "jakarta selatan": (-6.2615, 106.8106), "jakarta utara": (-6.1214, 106.9014),
    "jakarta timur": (-6.2250, 106.9004), "jakarta barat": (-6.1683, 106.7639),
    "surabaya": (-7.2575, 112.7521), "bandung": (-6.9175, 107.6191),
    "yogyakarta": (-7.7956, 110.3695), "semarang": (-6.9932, 110.4203),
    "solo": (-7.5755, 110.8243), "malang": (-7.9666, 112.6326),
    "bekasi": (-6.2383, 106.9756), "tangerang": (-6.1702, 106.6402),
    "depok": (-6.4025, 106.7942), "bogor": (-6.5971, 106.8060),
    "cirebon": (-6.7063, 108.5570), "tasikmalaya": (-7.3274, 108.2207),
    "kediri": (-7.8480, 112.0172), "madiun": (-7.6298, 111.5239),
    "mojokerto": (-7.4722, 111.4380), "jember": (-8.1845, 113.6679),
    "banyuwangi": (-8.2192, 114.3691), "sidoarjo": (-7.4478, 112.7181),
    "gresik": (-7.1560, 112.6524), "pasuruan": (-7.6456, 112.9075),
    "probolinggo": (-7.7543, 113.2159), "blitar": (-8.0958, 112.1689),
    "serang": (-6.1201, 106.1503), "cilegon": (-6.0031, 106.0003),
    # Sumatera
    "medan": (3.5952, 98.6722), "palembang": (-2.9761, 104.7754),
    "pekanbaru": (0.5071, 101.4478), "batam": (1.0456, 104.0305),
    "padang": (-0.9471, 100.4172), "jambi": (-1.6101, 103.6131),
    "bandar lampung": (-5.4292, 105.2618), "bengkulu": (-3.7928, 102.2608),
    "banda aceh": (5.5483, 95.3238), "lhokseumawe": (5.1801, 97.1522),
    "pangkal pinang": (-2.1316, 106.1169), "tanjung pinang": (0.9170, 104.4386),
    # Kalimantan
    "balikpapan": (-1.2654, 116.8312), "samarinda": (-0.5022, 117.1536),
    "banjarmasin": (-3.3194, 114.5908), "pontianak": (-0.0263, 109.3425),
    "palangka raya": (-2.2089, 113.9213), "tarakan": (3.2986, 117.6386),
    "bontang": (0.1331, 117.4993), "singkawang": (0.9026, 108.9876),
    # Sulawesi
    "makassar": (-5.1477, 119.4327), "manado": (1.4748, 124.8420),
    "palu": (-0.8978, 119.8701), "kendari": (-3.9985, 122.5129),
    "gorontalo": (0.5435, 123.0595), "mamuju": (-2.6762, 118.8886),
    # Bali & NTT/NTB
    "denpasar": (-8.6705, 115.2126), "singaraja": (-8.1120, 115.0882),
    "mataram": (-8.5833, 116.1167), "kupang": (-10.1772, 123.6070),
    # Maluku & Papua
    "ambon": (-3.6954, 128.1814), "ternate": (0.7903, 127.3804),
    "jayapura": (-2.5916, 140.6690), "sorong": (-0.8620, 131.2506),
    "manokwari": (-0.8610, 134.0622),
    # Provinsi fallback
    "aceh": (4.6951, 96.7494), "sumatera utara": (2.1154, 99.5451),
    "sumatera barat": (-0.7399, 100.8000), "riau": (0.2933, 101.7068),
    "kepulauan riau": (3.9457, 108.1429), "jambi": (-1.6101, 103.6131),
    "sumatera selatan": (-3.3194, 103.9144), "bengkulu": (-3.7928, 102.2608),
    "lampung": (-4.5586, 105.4068), "kepulauan bangka belitung": (-2.7411, 106.4406),
    "dki jakarta": (-6.2088, 106.8456), "jawa barat": (-6.8892, 107.6408),
    "jawa tengah": (-7.1500, 110.1403), "di yogyakarta": (-7.7956, 110.3695),
    "jawa timur": (-7.5360, 112.2384), "banten": (-6.4058, 106.0640),
    "bali": (-8.3405, 115.0920), "nusa tenggara barat": (-8.6529, 117.3616),
    "nusa tenggara timur": (-8.6574, 121.0794), "kalimantan barat": (-0.2787, 111.4752),
    "kalimantan tengah": (-1.6814, 113.3824), "kalimantan selatan": (-3.0926, 115.2838),
    "kalimantan timur": (0.5387, 116.4194), "kalimantan utara": (3.0731, 116.0413),
    "sulawesi utara": (0.6246, 123.9750), "sulawesi tengah": (-1.4300, 121.4456),
    "sulawesi selatan": (-3.6687, 119.9740), "sulawesi tenggara": (-4.1449, 122.1746),
    "gorontalo": (0.6999, 122.4467), "sulawesi barat": (-2.8441, 119.2321),
    "maluku": (-3.2385, 130.1453), "maluku utara": (1.5709, 127.8088),
    "papua barat": (-1.3361, 133.1747), "papua": (-4.2699, 138.0804),
    "indonesia": (-2.5489, 118.0149),
}

def get_coords(vendor: dict) -> tuple:
    """Cari koordinat dari kota/provinsi vendor."""
    for field in ["kota", "provinsi", "alamat"]:
        val = vendor.get(field, "").lower().strip()
        if val in CITY_COORDS:
            return CITY_COORDS[val]
        # Partial match
        for key, coords in CITY_COORDS.items():
            if key in val or val in key:
                return coords
    # Fallback: tengah Indonesia
    return (-2.5489, 118.0149)

# ─── Constants ───────────────────────────────────────────────────
PROVINCES = ["Semua Provinsi","DKI Jakarta","Jawa Barat","Jawa Tengah","Jawa Timur","DI Yogyakarta","Banten","Sumatera Utara","Sumatera Barat","Sumatera Selatan","Riau","Kepulauan Riau","Lampung","Bengkulu","Jambi","Aceh","Kepulauan Bangka Belitung","Kalimantan Barat","Kalimantan Tengah","Kalimantan Selatan","Kalimantan Timur","Kalimantan Utara","Sulawesi Utara","Sulawesi Tengah","Sulawesi Selatan","Sulawesi Tenggara","Gorontalo","Sulawesi Barat","Bali","Nusa Tenggara Barat","Nusa Tenggara Timur","Maluku","Maluku Utara","Papua","Papua Barat"]
CATEGORIES = ["Semua Kategori","Pupuk & Agrokimia","Alat & Mesin Pertanian","Benih & Bibit","Jasa Konstruksi & Sipil","Material Bangunan","Peralatan & Spare Part","Logistik & Transportasi","IT & Teknologi","Seragam & APD","Bahan Bakar & Pelumas","Makanan & Sembako","Jasa Konsultan","Perlengkapan Kantor","Peralatan Lab","Lainnya"]

# ─── AI Search (cached) ──────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def search_vendors(keyword: str, location: str, category: str) -> list:
    api_key = st.secrets.get("GROQ_API_KEY", "")
    if not api_key:
        st.error("❌ GROQ_API_KEY tidak ditemukan di Streamlit Secrets.")
        return []

    location_ctx = location if location != "Semua Provinsi" else "seluruh Indonesia"
    cat_ctx = f" kategori {category}" if category != "Semua Kategori" else ""

    prompt = f"""Kamu adalah database vendor Indonesia. Berikan daftar 6 vendor/supplier nyata yang menjual "{keyword}"{cat_ctx} di {location_ctx}.

Kembalikan HANYA JSON array ini (tanpa markdown, tanpa teks lain):
[
  {{
    "nama": "Nama perusahaan lengkap",
    "tipe": "Distributor/Supplier/Produsen/Toko/Importir",
    "alamat": "Alamat lengkap dengan kota dan provinsi",
    "kota": "Nama kota saja (contoh: Surabaya)",
    "provinsi": "Nama provinsi saja (contoh: Jawa Timur)",
    "telepon": "Nomor telepon format Indonesia, atau '-'",
    "email": "Email atau '-'",
    "website": "URL website atau '-'",
    "whatsapp": "Nomor WA bisnis atau '-'",
    "produk_utama": "Produk-produk utama",
    "deskripsi": "Deskripsi 2-3 kalimat singkat",
    "tags": ["tag1","tag2","tag3"],
    "min_order": "Minimum order atau '-'",
    "area_kirim": "Area pengiriman"
  }}
]
Hanya JSON array, tidak ada teks lain."""

    try:
        client = Groq(api_key=api_key)
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=3000,
        )
        text = resp.choices[0].message.content.strip()
        text = re.sub(r"```json|```", "", text).strip()
        m = re.search(r'\[[\s\S]*\]', text)
        return json.loads(m.group()) if m else []
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return []

# ─── Build Folium Map ────────────────────────────────────────────
def build_map(vendors: list, location: str) -> folium.Map:
    # Tentukan center map
    loc_lower = location.lower()
    center = CITY_COORDS.get(loc_lower, (-2.5489, 118.0149))
    zoom   = 10 if location != "Semua Provinsi" else 5

    m = folium.Map(
        location=center,
        zoom_start=zoom,
        tiles=None,
    )

    # Dark tile layer
    folium.TileLayer(
        tiles="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
        name="Dark Map",
        subdomains="abcd",
        max_zoom=19,
    ).add_to(m)

    colors = ["#58A6FF","#3FB950","#F78166","#D29922","#BC8CFF","#FF7B72"]

    for i, v in enumerate(vendors):
        lat, lng = get_coords(v)
        # Tambah sedikit offset agar pin tidak tumpuk
        lat += (i % 3 - 1) * 0.008
        lng += (i // 3 - 0.5) * 0.008

        color  = colors[i % len(colors)]
        phone  = v.get("telepon", "-")
        email  = v.get("email", "-")
        web    = v.get("website", "-")
        web_lnk= f'<a href="{web}" target="_blank" style="color:#58A6FF">{web[:30]}...</a>' if web != "-" and len(web) > 30 else (f'<a href="{web}" target="_blank" style="color:#58A6FF">{web}</a>' if web != "-" else "-")

        popup_html = f"""
        <div style="font-family:Inter,sans-serif;min-width:220px;max-width:280px">
          <div style="background:#1F6FEB;color:white;padding:8px 12px;border-radius:6px 6px 0 0;font-weight:700;font-size:13px">
            🏢 {v.get("nama","Vendor")}
          </div>
          <div style="background:#1c1c1e;color:#e0e0e0;padding:10px 12px;border-radius:0 0 6px 6px;font-size:12px;line-height:1.7">
            <b style="color:#aaa">Tipe:</b> {v.get("tipe","-")}<br>
            <b style="color:#aaa">Kota:</b> {v.get("kota","-")}, {v.get("provinsi","-")}<br>
            <b style="color:#aaa">Tel:</b> {phone}<br>
            <b style="color:#aaa">Email:</b> {email}<br>
            <b style="color:#aaa">Web:</b> {web_lnk}<br>
            <b style="color:#aaa">Produk:</b> {v.get("produk_utama","-")[:60]}
          </div>
        </div>"""

        folium.Marker(
            location=[lat, lng],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"📍 {v.get('nama','Vendor')} — {v.get('kota','')}",
            icon=folium.DivIcon(
                html=f"""
                <div style="
                  background:{color};
                  color:white;
                  border-radius:50%;
                  width:32px;height:32px;
                  display:flex;align-items:center;justify-content:center;
                  font-weight:800;font-size:13px;
                  border:3px solid white;
                  box-shadow:0 2px 8px rgba(0,0,0,0.5);
                  font-family:Inter,sans-serif;
                ">{i+1}</div>""",
                icon_size=(32, 32),
                icon_anchor=(16, 16),
            ),
        ).add_to(m)

    return m

# ─── Render Vendor Card ──────────────────────────────────────────
def render_card(v: dict, idx: int):
    colors = ["#58A6FF","#3FB950","#F78166","#D29922","#BC8CFF","#FF7B72"]
    c = colors[idx % len(colors)]

    phone  = v.get("telepon", "-")
    email  = v.get("email", "-")
    web    = v.get("website", "-")
    wa     = v.get("whatsapp", "-")

    wa_num  = re.sub(r'\D', '', wa if wa != '-' else phone).lstrip('0')
    wa_url  = f"https://wa.me/62{wa_num}" if wa_num else None
    ph_html = f'<a href="tel:{phone}">{phone}</a>'           if phone != '-' else '-'
    em_html = f'<a href="mailto:{email}">{email}</a>'        if email != '-' else '-'
    wb_html = f'<a href="{web}" target="_blank">{web[:35]}{"..." if len(web)>35 else ""}</a>' if web != '-' else '-'
    wa_html = f'<a href="{wa_url}" target="_blank">💬 Chat WhatsApp</a>' if wa_url else '-'
    tags_h  = "".join(f'<span class="tag">{t}</span>' for t in v.get("tags",[])[:5])

    st.markdown(f"""
    <div class="vendor-card">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:14px">
        <div style="display:flex;align-items:center;gap:12px">
          <div style="background:{c};color:white;border-radius:50%;width:34px;height:34px;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:14px;flex-shrink:0">{idx+1}</div>
          <div>
            <div class="vendor-name">{v.get("nama","—")}</div>
            <div class="vendor-type">{v.get("tipe","Vendor")} · {v.get("kota","")} · {v.get("provinsi","")}</div>
          </div>
        </div>
        <div style="font-size:11px;color:#3FB950;background:rgba(63,185,80,0.1);border:1px solid rgba(63,185,80,0.2);border-radius:6px;padding:3px 10px;white-space:nowrap">
          🚚 {v.get("area_kirim","-")}
        </div>
      </div>
      <div class="card-grid">
        <div class="card-field"><div class="field-label">📍 Alamat</div><div class="field-value">{v.get("alamat","-")}</div></div>
        <div class="card-field"><div class="field-label">📞 Telepon</div><div class="field-value">{ph_html}</div></div>
        <div class="card-field"><div class="field-label">✉️ Email</div><div class="field-value">{em_html}</div></div>
        <div class="card-field"><div class="field-label">💬 WhatsApp</div><div class="field-value">{wa_html}</div></div>
        <div class="card-field"><div class="field-label">🌐 Website</div><div class="field-value">{wb_html}</div></div>
        <div class="card-field"><div class="field-label">📦 Min. Order</div><div class="field-value">{v.get("min_order","-")}</div></div>
      </div>
      <div class="card-desc"><b style="color:#C9D1D9">Produk:</b> {v.get("produk_utama","-")}<br><br>{v.get("deskripsi","-")}</div>
      <div class="tag-row">{tags_h}</div>
    </div>
    """, unsafe_allow_html=True)


# ─── Session State ───────────────────────────────────────────────
for k, d in [("results",[]),("done",False),("meta",{})]:
    if k not in st.session_state: st.session_state[k] = d

# ─── Hero ────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-eyebrow">🔍 Vendor Intelligence Platform</div>
  <div class="hero-title">Temukan <span>Vendor Terbaik</span><br>di Seluruh Indonesia</div>
  <div class="hero-sub">Cari supplier & vendor berdasarkan produk dan lokasi. Peta interaktif dengan pin lokasi vendor.</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="status-bar">
  <span class="pill"><span class="pill-dot dot-green"></span>100% Gratis</span>
  <span class="pill"><span class="pill-dot dot-blue"></span>Groq AI · Llama 3.1</span>
  <span class="pill"><span class="pill-dot dot-yellow"></span>Peta Interaktif</span>
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
        with st.spinner("🤖 AI sedang mencari vendor…"):
            results = search_vendors(keyword.strip(), location, category)
            st.session_state.results = results
            st.session_state.done    = True
            st.session_state.meta    = {
                "keyword": keyword.strip(), "location": location,
                "time": datetime.now().strftime("%H:%M:%S — %d %B %Y")
            }

# ─── Results ─────────────────────────────────────────────────────
if st.session_state.done:
    results = st.session_state.results
    meta    = st.session_state.meta
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    if results:
        # ── 1. PETA INTERAKTIF ──────────────────────────────────
        st.markdown(f"""
        <div class="map-section">
          <div class="map-header">
            <div>
              <div class="map-title">🗺️ Peta Lokasi Vendor</div>
              <div class="map-sub">Klik pin untuk detail vendor · Scroll untuk zoom</div>
            </div>
            <div style="font-size:12px;color:#58A6FF;font-weight:600;background:rgba(88,166,255,0.1);border:1px solid rgba(88,166,255,0.2);border-radius:10px;padding:3px 10px">
              {len(results)} pin vendor
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        with st.container():
            map_col = st.columns([1])[0]
            with map_col:
                vendor_map = build_map(results, meta.get("location","Indonesia"))
                st_folium(vendor_map, width="100%", height=420, returned_objects=[])

        # ── 2. DAFTAR VENDOR ────────────────────────────────────
        st.markdown(f"""
        <div class="results-header">
          <div class="results-title">📋 Daftar Vendor: "<b>{meta.get("keyword","")}</b>" · {meta.get("location","")}</div>
          <span class="results-count">{len(results)} vendor</span>
        </div>
        <p style="margin:-4px 60px 18px;font-size:12px;color:#484F58">🕒 {meta.get("time","")}</p>
        """, unsafe_allow_html=True)

        for i, v in enumerate(results):
            render_card(v, i)

        st.markdown("""
        <div style="margin:20px 60px 48px;padding:12px 18px;background:#161B22;border:1px solid #21262D;border-radius:8px;font-size:12px;color:#484F58">
          ⚠️ <b style="color:#8B949E">Disclaimer:</b> Data dihasilkan oleh AI. Nomor pin di peta sesuai urutan di daftar vendor.
          Selalu verifikasi kontak dan informasi vendor sebelum bertransaksi.
        </div>""", unsafe_allow_html=True)

    else:
        st.markdown('<div class="empty-state"><div class="empty-icon">🔎</div><div class="empty-title">Tidak ada hasil</div><div class="empty-sub">Coba ubah kata kunci atau lokasi.</div></div>', unsafe_allow_html=True)

else:
    st.markdown('<div class="empty-state"><div class="empty-icon">🏭</div><div class="empty-title">Siap Mencari Vendor</div><div class="empty-sub">Masukkan kata kunci dan pilih lokasi untuk mulai.<br>Vendor akan ditampilkan di peta interaktif dan daftar.</div></div>', unsafe_allow_html=True)
