import streamlit as st
import json, re
from datetime import datetime
from urllib.parse import quote_plus
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
/* Hero */
.hero{background:linear-gradient(135deg,#0D1117 0%,#161B22 50%,#0D1117 100%);border-bottom:1px solid #21262D;padding:40px 60px 32px;position:relative;overflow:hidden}
.hero::before{content:'';position:absolute;top:-60px;right:-60px;width:350px;height:350px;background:radial-gradient(circle,rgba(88,166,255,0.08) 0%,transparent 70%);pointer-events:none}
.hero-eyebrow{font-size:11px;font-weight:600;letter-spacing:2.5px;color:#58A6FF;text-transform:uppercase;margin-bottom:12px}
.hero-title{font-family:'Plus Jakarta Sans',sans-serif;font-size:38px;font-weight:800;line-height:1.15;color:#E6EDF3;margin:0 0 10px}
.hero-title span{color:#58A6FF}
.hero-sub{font-size:14px;color:#8B949E;max-width:560px}
/* Inputs */
.stTextInput>div>div>input,.stSelectbox>div>div,.stTextArea>div>div>textarea{background:#0D1117!important;border:1px solid #30363D!important;border-radius:8px!important;color:#E6EDF3!important;font-family:'Inter',sans-serif!important;font-size:14px!important}
.stTextInput>div>div>input:focus,.stTextArea>div>div>textarea:focus{border-color:#58A6FF!important;box-shadow:0 0 0 3px rgba(88,166,255,0.15)!important}
.stTextInput label,.stSelectbox label,.stTextArea label{color:#8B949E!important;font-size:12px!important;font-weight:500!important}
/* Button */
.stButton>button{background:linear-gradient(135deg,#1F6FEB 0%,#388BFD 100%)!important;color:white!important;border:none!important;border-radius:8px!important;font-size:14px!important;font-weight:600!important;height:44px!important;width:100%!important}
.stButton>button:hover{background:linear-gradient(135deg,#388BFD 0%,#58A6FF 100%)!important;transform:translateY(-1px)!important;box-shadow:0 4px 16px rgba(88,166,255,0.35)!important}
/* Pills */
.status-bar{display:flex;align-items:center;gap:10px;margin:8px 60px 0}
.pill{display:inline-flex;align-items:center;gap:6px;background:#161B22;border:1px solid #21262D;border-radius:20px;padding:4px 12px;font-size:11px;color:#8B949E;font-weight:500}
.pill-dot{width:6px;height:6px;border-radius:50%}
.dot-green{background:#3FB950}.dot-blue{background:#58A6FF}.dot-yellow{background:#D29922}.dot-purple{background:#BC8CFF}
/* Panels */
.search-panel{background:#161B22;border:1px solid #21262D;border-radius:14px;padding:24px 28px;margin:24px 60px}
.panel-label{font-size:11px;font-weight:600;letter-spacing:1.8px;color:#58A6FF;text-transform:uppercase;margin-bottom:16px}
/* Section headers */
.section-wrap{margin:28px 60px 0}
.section-hdr{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px}
.section-title{font-family:'Plus Jakarta Sans',sans-serif;font-size:16px;font-weight:700;color:#E6EDF3}
.section-badge{font-size:11px;color:#58A6FF;font-weight:600;background:rgba(88,166,255,0.1);border:1px solid rgba(88,166,255,0.2);border-radius:10px;padding:3px 10px}
/* Price cards */
.price-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:16px}
.price-card{background:#161B22;border:1px solid #21262D;border-radius:10px;padding:16px 18px;text-align:center}
.price-label{font-size:10px;font-weight:600;letter-spacing:1.5px;color:#484F58;text-transform:uppercase;margin-bottom:8px}
.price-value{font-family:'Plus Jakarta Sans',sans-serif;font-size:18px;font-weight:800;color:#3FB950}
.price-note{font-size:11px;color:#8B949E;margin-top:4px}
.price-info-box{background:#161B22;border:1px solid #21262D;border-radius:10px;padding:14px 18px;font-size:13px;color:#8B949E;line-height:1.7}
/* Map */
.map-wrap{margin:24px 60px 0;background:#161B22;border:1px solid #21262D;border-radius:14px;overflow:hidden}
.map-hdr{padding:14px 22px 12px;border-bottom:1px solid #21262D;display:flex;align-items:center;justify-content:space-between}
.map-title{font-family:'Plus Jakarta Sans',sans-serif;font-size:15px;font-weight:700;color:#E6EDF3}
.map-sub{font-size:12px;color:#8B949E}
/* Vendor cards */
.vendor-card{background:#161B22;border:1px solid #21262D;border-radius:12px;padding:22px 26px;margin-bottom:14px;position:relative}
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
.action-row{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px}
.action-btn{display:inline-flex;align-items:center;gap:5px;padding:7px 14px;border-radius:7px;font-size:12px;font-weight:600;text-decoration:none!important;border:1px solid;transition:opacity 0.2s}
.action-btn:hover{opacity:0.8}
.btn-google{background:rgba(66,133,244,0.12);border-color:rgba(66,133,244,0.3);color:#4285F4!important}
.btn-maps{background:rgba(52,168,83,0.12);border-color:rgba(52,168,83,0.3);color:#34A853!important}
.btn-tokped{background:rgba(66,181,73,0.12);border-color:rgba(66,181,73,0.3);color:#42b549!important}
.btn-shopee{background:rgba(238,77,45,0.12);border-color:rgba(238,77,45,0.3);color:#ee4d2d!important}
.btn-wa{background:rgba(37,211,102,0.12);border-color:rgba(37,211,102,0.3);color:#25D366!important}
.unverified-notice{display:flex;align-items:center;gap:8px;background:rgba(210,153,34,0.08);border:1px solid rgba(210,153,34,0.2);border-radius:8px;padding:10px 14px;font-size:12px;color:#D29922;margin-bottom:14px}
/* Online store cards */
.store-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
.store-card{background:#161B22;border:1px solid #21262D;border-radius:12px;padding:18px 20px;text-align:left;transition:border-color 0.2s}
.store-card:hover{border-color:#30363D}
.store-logo{font-size:28px;margin-bottom:10px}
.store-name{font-family:'Plus Jakarta Sans',sans-serif;font-size:14px;font-weight:700;color:#E6EDF3;margin-bottom:4px}
.store-price{font-size:13px;color:#3FB950;font-weight:600;margin-bottom:6px}
.store-note{font-size:12px;color:#8B949E;line-height:1.5;margin-bottom:12px}
.store-btn{display:inline-block;background:linear-gradient(135deg,#1F6FEB,#388BFD);color:white!important;text-decoration:none!important;border-radius:7px;padding:7px 16px;font-size:12px;font-weight:600}
/* Misc */
.empty-state{text-align:center;padding:70px 40px;margin:0 60px}
.empty-icon{font-size:44px;margin-bottom:14px}
.empty-title{font-family:'Plus Jakarta Sans',sans-serif;font-size:18px;font-weight:700;color:#E6EDF3;margin-bottom:8px}
.empty-sub{font-size:14px;color:#484F58}
hr.divider{border:none;border-top:1px solid #21262D;margin:0 60px 20px}
.spec-badge{display:inline-block;background:rgba(188,140,255,0.1);border:1px solid rgba(188,140,255,0.25);color:#BC8CFF;border-radius:6px;padding:2px 10px;font-size:11px;font-weight:600;margin-left:8px}
</style>
""", unsafe_allow_html=True)

# ─── Koordinat Kota Indonesia ────────────────────────────────────
CITY_COORDS = {
    "jakarta":(-6.2088,106.8456),"jakarta pusat":(-6.1862,106.8342),"jakarta selatan":(-6.2615,106.8106),
    "jakarta utara":(-6.1214,106.9014),"jakarta timur":(-6.2250,106.9004),"jakarta barat":(-6.1683,106.7639),
    "surabaya":(-7.2575,112.7521),"bandung":(-6.9175,107.6191),"yogyakarta":(-7.7956,110.3695),
    "semarang":(-6.9932,110.4203),"solo":(-7.5755,110.8243),"malang":(-7.9666,112.6326),
    "bekasi":(-6.2383,106.9756),"tangerang":(-6.1702,106.6402),"depok":(-6.4025,106.7942),
    "bogor":(-6.5971,106.8060),"cirebon":(-6.7063,108.5570),"kediri":(-7.8480,112.0172),
    "madiun":(-7.6298,111.5239),"jember":(-8.1845,113.6679),"banyuwangi":(-8.2192,114.3691),
    "sidoarjo":(-7.4478,112.7181),"gresik":(-7.1560,112.6524),"serang":(-6.1201,106.1503),
    "medan":(3.5952,98.6722),"palembang":(-2.9761,104.7754),"pekanbaru":(0.5071,101.4478),
    "batam":(1.0456,104.0305),"padang":(-0.9471,100.4172),"jambi":(-1.6101,103.6131),
    "bandar lampung":(-5.4292,105.2618),"bengkulu":(-3.7928,102.2608),"banda aceh":(5.5483,95.3238),
    "balikpapan":(-1.2654,116.8312),"samarinda":(-0.5022,117.1536),"banjarmasin":(-3.3194,114.5908),
    "pontianak":(-0.0263,109.3425),"palangka raya":(-2.2089,113.9213),"tarakan":(3.2986,117.6386),
    "makassar":(-5.1477,119.4327),"manado":(1.4748,124.8420),"palu":(-0.8978,119.8701),
    "kendari":(-3.9985,122.5129),"gorontalo":(0.5435,123.0595),
    "denpasar":(-8.6705,115.2126),"mataram":(-8.5833,116.1167),"kupang":(-10.1772,123.6070),
    "ambon":(-3.6954,128.1814),"jayapura":(-2.5916,140.6690),"sorong":(-0.8620,131.2506),
    "aceh":(4.6951,96.7494),"sumatera utara":(2.1154,99.5451),"sumatera barat":(-0.7399,100.8000),
    "riau":(0.2933,101.7068),"kepulauan riau":(3.9457,108.1429),"sumatera selatan":(-3.3194,103.9144),
    "lampung":(-4.5586,105.4068),"kepulauan bangka belitung":(-2.7411,106.4406),
    "dki jakarta":(-6.2088,106.8456),"jawa barat":(-6.8892,107.6408),"jawa tengah":(-7.1500,110.1403),
    "di yogyakarta":(-7.7956,110.3695),"jawa timur":(-7.5360,112.2384),"banten":(-6.4058,106.0640),
    "bali":(-8.3405,115.0920),"nusa tenggara barat":(-8.6529,117.3616),"nusa tenggara timur":(-8.6574,121.0794),
    "kalimantan barat":(-0.2787,111.4752),"kalimantan tengah":(-1.6814,113.3824),
    "kalimantan selatan":(-3.0926,115.2838),"kalimantan timur":(0.5387,116.4194),"kalimantan utara":(3.0731,116.0413),
    "sulawesi utara":(0.6246,123.9750),"sulawesi tengah":(-1.4300,121.4456),"sulawesi selatan":(-3.6687,119.9740),
    "sulawesi tenggara":(-4.1449,122.1746),"sulawesi barat":(-2.8441,119.2321),
    "maluku":(-3.2385,130.1453),"maluku utara":(1.5709,127.8088),
    "papua barat":(-1.3361,133.1747),"papua":(-4.2699,138.0804),"indonesia":(-2.5489,118.0149),
}

def get_coords(vendor: dict):
    for field in ["kota","provinsi","alamat"]:
        val = vendor.get(field,"").lower().strip()
        if val in CITY_COORDS: return CITY_COORDS[val]
        for k,c in CITY_COORDS.items():
            if k in val or val in k: return c
    return (-2.5489,118.0149)

# ─── Online Store Config ─────────────────────────────────────────
def get_store_url(platform: str, keyword: str, location: str) -> str:
    q = quote_plus(f"{keyword} {location}" if location != "Semua Provinsi" else keyword)
    urls = {
        "Tokopedia"  : f"https://www.tokopedia.com/search?st=product&q={q}",
        "Shopee"     : f"https://shopee.co.id/search?keyword={q}",
        "Lazada"     : f"https://www.lazada.co.id/catalog/?q={q}",
        "Bukalapak"  : f"https://www.bukalapak.com/products?search%5Bkeywords%5D={q}",
        "Blibli"     : f"https://www.blibli.com/cari/{q}",
        "Indotrading": f"https://www.indotrading.com/search/?keyword={q}",
    }
    return urls.get(platform, "#")

STORE_META = {
    "Tokopedia"  : {"emoji":"🟢","warna":"#42b549","catatan":"Gratis ongkir, COD tersedia, toko resmi banyak"},
    "Shopee"     : {"emoji":"🟠","warna":"#ee4d2d","catatan":"Flash sale, voucher, ShopeePay cashback"},
    "Lazada"     : {"emoji":"🔵","warna":"#0f146d","catatan":"LazMall, voucher brand, pengiriman cepat"},
    "Bukalapak"  : {"emoji":"🔴","warna":"#e31e25","catatan":"BukaMall, cicilan 0%, poin reward"},
    "Blibli"     : {"emoji":"🔷","warna":"#0095da","catatan":"Produk original, garansi resmi"},
    "Indotrading": {"emoji":"🏭","warna":"#1a73e8","catatan":"Khusus B2B, supplier & grosir"},
}

# ─── Constants ───────────────────────────────────────────────────
PROVINCES = ["Semua Provinsi","DKI Jakarta","Jawa Barat","Jawa Tengah","Jawa Timur","DI Yogyakarta","Banten","Sumatera Utara","Sumatera Barat","Sumatera Selatan","Riau","Kepulauan Riau","Lampung","Bengkulu","Jambi","Aceh","Kepulauan Bangka Belitung","Kalimantan Barat","Kalimantan Tengah","Kalimantan Selatan","Kalimantan Timur","Kalimantan Utara","Sulawesi Utara","Sulawesi Tengah","Sulawesi Selatan","Sulawesi Tenggara","Gorontalo","Sulawesi Barat","Bali","Nusa Tenggara Barat","Nusa Tenggara Timur","Maluku","Maluku Utara","Papua","Papua Barat"]
CATEGORIES = ["Semua Kategori","Pupuk & Agrokimia","Alat & Mesin Pertanian","Benih & Bibit","Jasa Konstruksi & Sipil","Material Bangunan","Peralatan & Spare Part","Logistik & Transportasi","IT & Teknologi","Seragam & APD","Bahan Bakar & Pelumas","Makanan & Sembako","Jasa Konsultan","Perlengkapan Kantor","Peralatan Lab","Lainnya"]

# ─── AI Search (cached) ──────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def search_all(keyword: str, location: str, category: str, spesifikasi: str) -> dict:
    api_key = st.secrets.get("GROQ_API_KEY","")
    if not api_key:
        st.error("❌ GROQ_API_KEY tidak ditemukan di Streamlit Secrets.")
        return {}

    location_ctx = location if location != "Semua Provinsi" else "seluruh Indonesia"
    cat_ctx  = f" kategori {category}" if category != "Semua Kategori" else ""
    spec_ctx = f" dengan spesifikasi: {spesifikasi}" if spesifikasi.strip() else ""

    prompt = f"""Kamu adalah database vendor dan harga pasar Indonesia.
Barang dicari: "{keyword}"{cat_ctx}{spec_ctx}
Wilayah: {location_ctx}

Kembalikan HANYA satu JSON object ini (tanpa markdown, tanpa teks lain):

{{
  "vendors": [
    {{
      "nama": "Nama perusahaan lengkap dan spesifik",
      "tipe": "Distributor/Supplier/Produsen/Toko/Importir",
      "alamat": "Alamat lengkap dengan nama jalan, kelurahan, kecamatan, kota, provinsi",
      "kota": "Nama kota",
      "provinsi": "Nama provinsi",
      "produk_utama": "Produk utama yang dijual",
      "deskripsi": "Deskripsi 2-3 kalimat tentang vendor dan keunggulannya",
      "tags": ["tag1","tag2","tag3"],
      "min_order": "Minimum order atau '-'",
      "area_kirim": "Area pengiriman",
      "tahun_berdiri": "Tahun berdiri atau '-'",
      "skala": "UMKM/Menengah/Besar"
    }}
  ],
  "harga_pasar": {{
    "satuan": "unit satuan (kg/unit/liter/dll)",
    "tipe_harga": [
      {{"label": "Harga Eceran",      "harga": "Rp X.XXX",  "keterangan": "penjelasan singkat"}},
      {{"label": "Harga Grosir",      "harga": "Rp Y.YYY",  "keterangan": "penjelasan singkat"}},
      {{"label": "Harga Distributor", "harga": "Rp Z.ZZZ",  "keterangan": "penjelasan singkat"}},
      {{"label": "Harga Online",      "harga": "Rp W.WWW",  "keterangan": "rata-rata marketplace"}}
    ],
    "faktor_harga": "Penjelasan faktor yang mempengaruhi harga (musim, kualitas, merek, dll)",
    "trend": "naik/turun/stabil",
    "catatan_spesifikasi": "Catatan harga khusus jika ada spesifikasi tertentu, atau kosong"
  }},
  "toko_online": [
    {{
      "platform": "Tokopedia",
      "estimasi_harga": "Rp X.XXX - Rp Y.YYY",
      "produk_populer": "nama produk populer di platform ini",
      "keunggulan": "keunggulan platform untuk produk ini"
    }},
    {{"platform":"Shopee","estimasi_harga":"Rp X - Rp Y","produk_populer":"...","keunggulan":"..."}},
    {{"platform":"Lazada","estimasi_harga":"Rp X - Rp Y","produk_populer":"...","keunggulan":"..."}},
    {{"platform":"Bukalapak","estimasi_harga":"Rp X - Rp Y","produk_populer":"...","keunggulan":"..."}},
    {{"platform":"Blibli","estimasi_harga":"Rp X - Rp Y","produk_populer":"...","keunggulan":"..."}},
    {{"platform":"Indotrading","estimasi_harga":"Rp X - Rp Y","produk_populer":"...","keunggulan":"..."}}
  ]
}}

Berikan 6 vendor. Hanya JSON, tidak ada teks lain."""

    try:
        client = Groq(api_key=api_key)
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role":"user","content":prompt}],
            temperature=0.3,
            max_tokens=4000,
        )
        text = resp.choices[0].message.content.strip()
        text = re.sub(r"```json|```","",text).strip()
        m = re.search(r'\{[\s\S]*\}', text)
        return json.loads(m.group()) if m else {}
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return {}

# ─── Build Map ───────────────────────────────────────────────────
def build_map(vendors: list, location: str) -> folium.Map:
    from urllib.parse import quote_plus
    loc_lower = location.lower()
    center = CITY_COORDS.get(loc_lower, (-2.5489, 118.0149))
    zoom   = 10 if location != "Semua Provinsi" else 5

    m = folium.Map(location=center, zoom_start=zoom, tiles=None)
    folium.TileLayer(
        tiles="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        attr='&copy; OpenStreetMap &copy; CARTO', subdomains="abcd", max_zoom=19
    ).add_to(m)

    colors = ["#58A6FF","#3FB950","#F78166","#D29922","#BC8CFF","#FF7B72"]
    for i, v in enumerate(vendors):
        lat, lng = get_coords(v)
        lat += (i%3-1)*0.008; lng += (i//3-0.5)*0.008
        color = colors[i % len(colors)]
        q_g = quote_plus(f"{v.get('nama','')} {v.get('kota','')}")
        q_m = quote_plus(f"{v.get('nama','')} {v.get('alamat','')}")
        popup = f"""<div style="font-family:Inter,sans-serif;min-width:230px">
          <div style="background:{color};color:white;padding:7px 11px;border-radius:5px 5px 0 0;font-weight:700;font-size:12px">🏢 {v.get("nama","Vendor")}</div>
          <div style="background:#1c1c1e;color:#ddd;padding:9px 11px;border-radius:0 0 5px 5px;font-size:11px;line-height:1.7">
            <b style="color:#aaa">Tipe:</b> {v.get("tipe","-")}<br>
            <b style="color:#aaa">Kota:</b> {v.get("kota","-")}, {v.get("provinsi","-")}<br>
            <b style="color:#aaa">Produk:</b> {v.get("produk_utama","-")[:40]}<br>
            <b style="color:#aaa">Skala:</b> {v.get("skala","-")}<br>
            <div style="margin-top:8px;display:flex;gap:6px;flex-wrap:wrap">
              <a href="https://www.google.com/search?q={q_g}" target="_blank" style="background:#4285F4;color:white;padding:3px 8px;border-radius:4px;text-decoration:none;font-size:10px;font-weight:600">🔍 Google</a>
              <a href="https://www.google.com/maps/search/{q_m}" target="_blank" style="background:#34A853;color:white;padding:3px 8px;border-radius:4px;text-decoration:none;font-size:10px;font-weight:600">📍 Maps</a>
            </div>
          </div></div>"""
        folium.Marker(
            location=[lat,lng],
            popup=folium.Popup(popup, max_width=300),
            tooltip=f"📍 {i+1}. {v.get('nama','')} — {v.get('kota','')}",
            icon=folium.DivIcon(
                html=f'<div style="background:{color};color:white;border-radius:50%;width:30px;height:30px;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:13px;border:3px solid white;box-shadow:0 2px 8px rgba(0,0,0,0.5)">{i+1}</div>',
                icon_size=(30,30), icon_anchor=(15,15)
            )
        ).add_to(m)
    return m

# ─── Render Sections ─────────────────────────────────────────────
def render_harga(harga: dict, keyword: str, spesifikasi: str):
    tipe  = harga.get("tipe_harga", [])
    satuan= harga.get("satuan","unit")
    trend = harga.get("trend","stabil")
    trend_icon = "📈" if trend=="naik" else ("📉" if trend=="turun" else "➡️")
    trend_col  = "#F78166" if trend=="naik" else ("#3FB950" if trend=="turun" else "#D29922")

    spec_note = ""
    if spesifikasi.strip() and harga.get("catatan_spesifikasi","").strip():
        spec_note = f'<div style="background:rgba(188,140,255,0.08);border:1px solid rgba(188,140,255,0.2);border-radius:8px;padding:10px 14px;font-size:13px;color:#BC8CFF;margin-bottom:14px">💜 <b>Catatan untuk spesifikasi "{spesifikasi}":</b> {harga["catatan_spesifikasi"]}</div>'

    price_cards = ""
    for t in tipe:
        price_cards += f"""<div class="price-card">
          <div class="price-label">{t.get("label","")}</div>
          <div class="price-value">{t.get("harga","—")}</div>
          <div class="price-note">per {satuan}</div>
          <div style="font-size:11px;color:#484F58;margin-top:4px">{t.get("keterangan","")}</div>
        </div>"""

    st.markdown(f"""
    <div class="section-wrap">
      <div class="section-hdr">
        <div class="section-title">💰 Harga Pasar — <span style="color:#8B949E;font-weight:400;font-size:14px">{keyword}</span></div>
        <div style="font-size:12px;color:{trend_col};font-weight:600;background:rgba(88,166,255,0.05);border:1px solid #21262D;border-radius:10px;padding:3px 10px">
          {trend_icon} Tren: {trend.capitalize()}
        </div>
      </div>
      {spec_note}
      <div class="price-grid">{price_cards}</div>
      <div class="price-info-box">ℹ️ {harga.get("faktor_harga","")}</div>
    </div>
    """, unsafe_allow_html=True)


def render_vendor_card(v: dict, idx: int):
    from urllib.parse import quote_plus
    colors = ["#58A6FF","#3FB950","#F78166","#D29922","#BC8CFF","#FF7B72"]
    c = colors[idx % len(colors)]
    nama    = v.get("nama","")
    kota    = v.get("kota","")
    provinsi= v.get("provinsi","")
    alamat  = v.get("alamat","-")
    skala   = v.get("skala","-")
    tahun   = v.get("tahun_berdiri","-")

    # Build verified search URLs (real links, bukan data AI)
    q_nama   = quote_plus(f"{nama} {kota} {provinsi}")
    q_maps   = quote_plus(f"{nama} {alamat}")
    q_tokped = quote_plus(f"{v.get('produk_utama','')} {kota}")
    q_shopee = quote_plus(f"{v.get('produk_utama','')} {kota}")
    q_wa     = quote_plus(f"supplier {v.get('produk_utama','')} {kota}")

    url_google = f"https://www.google.com/search?q={q_nama}"
    url_maps   = f"https://www.google.com/maps/search/{q_maps}"
    url_tokped = f"https://www.tokopedia.com/search?st=product&q={q_tokped}"
    url_shopee = f"https://shopee.co.id/search?keyword={q_shopee}"
    url_wa     = f"https://wa.me/?text={q_wa}"

    tags_h = "".join(f'<span class="tag">{t}</span>' for t in v.get("tags",[])[:5])

    st.markdown(f"""
    <div class="vendor-card">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:14px">
        <div style="display:flex;align-items:center;gap:12px">
          <div style="background:{c};color:white;border-radius:50%;width:34px;height:34px;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:14px;flex-shrink:0">{idx+1}</div>
          <div>
            <div class="vendor-name">{nama}</div>
            <div class="vendor-type">{v.get("tipe","Vendor")} · {kota} · {provinsi}</div>
          </div>
        </div>
        <div style="font-size:11px;color:#3FB950;background:rgba(63,185,80,0.1);border:1px solid rgba(63,185,80,0.2);border-radius:6px;padding:3px 10px;white-space:nowrap">🚚 {v.get("area_kirim","-")}</div>
      </div>

      <div class="unverified-notice">
        ⚠️ <span>Kontak tidak ditampilkan karena data AI tidak dapat diverifikasi. Gunakan tombol di bawah untuk mencari kontak asli vendor ini.</span>
      </div>

      <div class="card-grid">
        <div class="card-field"><div class="field-label">📍 Alamat</div><div class="field-value">{alamat}</div></div>
        <div class="card-field"><div class="field-label">📦 Produk Utama</div><div class="field-value">{v.get("produk_utama","-")}</div></div>
        <div class="card-field"><div class="field-label">🏷️ Min. Order</div><div class="field-value">{v.get("min_order","-")}</div></div>
        <div class="card-field"><div class="field-label">🏢 Skala Bisnis</div><div class="field-value">{skala}</div></div>
        <div class="card-field"><div class="field-label">📅 Tahun Berdiri</div><div class="field-value">{tahun}</div></div>
        <div class="card-field"><div class="field-label">🚚 Area Kirim</div><div class="field-value">{v.get("area_kirim","-")}</div></div>
      </div>

      <div class="card-desc">{v.get("deskripsi","-")}</div>

      <div class="action-row">
        <a href="{url_google}" target="_blank" class="action-btn btn-google">🔍 Cari di Google</a>
        <a href="{url_maps}"   target="_blank" class="action-btn btn-maps">📍 Google Maps</a>
        <a href="{url_tokped}" target="_blank" class="action-btn btn-tokped">🟢 Cari di Tokopedia</a>
        <a href="{url_shopee}" target="_blank" class="action-btn btn-shopee">🟠 Cari di Shopee</a>
        <a href="{url_wa}"     target="_blank" class="action-btn btn-wa">💬 Cari via WhatsApp</a>
      </div>
      <div class="tag-row">{tags_h}</div>
    </div>
    """, unsafe_allow_html=True)

def render_toko_online(toko_list: list, keyword: str, location: str):
    store_cards = ""
    for t in toko_list:
        platform = t.get("platform","")
        meta     = STORE_META.get(platform, {"emoji":"🛒","warna":"#58A6FF","catatan":""})
        url      = get_store_url(platform, keyword, location)
        store_cards += f"""
        <div class="store-card">
          <div class="store-logo">{meta["emoji"]}</div>
          <div class="store-name">{platform}</div>
          <div class="store-price">{t.get("estimasi_harga","Cek di platform")}</div>
          <div class="store-note">
            <b style="color:#C9D1D9">Produk populer:</b> {t.get("produk_populer","-")}<br>
            {t.get("keunggulan", meta["catatan"])}
          </div>
          <a href="{url}" target="_blank" class="store-btn" style="background:linear-gradient(135deg,{meta['warna']},{meta['warna']}cc)">
            🔗 Cari di {platform}
          </a>
        </div>"""

    st.markdown(f"""
    <div class="section-wrap" style="margin-bottom:28px">
      <div class="section-hdr">
        <div class="section-title">🛒 Toko Online</div>
        <div class="section-badge">6 platform</div>
      </div>
      <div class="store-grid">{store_cards}</div>
    </div>
    """, unsafe_allow_html=True)


# ─── Session State ───────────────────────────────────────────────
for k,d in [("data",{}),("done",False),("meta",{})]:
    if k not in st.session_state: st.session_state[k] = d

# ─── Hero ────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-eyebrow">🔍 Vendor Intelligence Platform</div>
  <div class="hero-title">Temukan <span>Vendor Terbaik</span><br>di Seluruh Indonesia</div>
  <div class="hero-sub">Cari supplier, harga pasar, & toko online — semuanya dalam satu pencarian.</div>
</div>
""", unsafe_allow_html=True)
st.markdown("""
<div class="status-bar">
  <span class="pill"><span class="pill-dot dot-green"></span>100% Gratis</span>
  <span class="pill"><span class="pill-dot dot-blue"></span>Groq AI · Llama 3.1</span>
  <span class="pill"><span class="pill-dot dot-yellow"></span>Peta Interaktif</span>
  <span class="pill"><span class="pill-dot dot-purple"></span>Harga Pasar</span>
</div>
""", unsafe_allow_html=True)

# ─── Search Panel ────────────────────────────────────────────────
st.markdown('<div class="search-panel"><div class="panel-label">🔎 Parameter Pencarian</div>', unsafe_allow_html=True)

r1c1, r1c2, r1c3 = st.columns([3, 2, 2])
with r1c1: keyword  = st.text_input("Kata Kunci Barang / Produk *", placeholder="contoh: pupuk urea, genset, besi beton, solar panel…", key="kw")
with r1c2: location = st.selectbox("Provinsi / Wilayah *", PROVINCES, key="loc")
with r1c3: category = st.selectbox("Kategori Vendor", CATEGORIES, key="cat")

# Spesifikasi khusus (opsional)
with st.expander("⚙️ Spesifikasi Khusus Barang (opsional)", expanded=False):
    spesifikasi = st.text_area(
        "Masukkan spesifikasi detail jika diperlukan",
        placeholder="Contoh:\n• Pupuk urea: kadar N minimal 46%, kemasan 50kg\n• Genset: daya 10 kVA, bahan bakar solar, silent type\n• Besi beton: diameter 12mm, SNI, panjang 12m",
        height=100, key="spec",
        help="Spesifikasi akan digunakan AI untuk menyesuaikan rekomendasi vendor dan estimasi harga"
    )
    if spesifikasi.strip():
        st.markdown(f'<span class="spec-badge">✔ Spesifikasi aktif: {spesifikasi[:60]}{"..." if len(spesifikasi)>60 else ""}</span>', unsafe_allow_html=True)
# spesifikasi captured from expander above
spesifikasi = st.session_state.get("spec","")

_, btn_col, _ = st.columns([3, 2, 3])
with btn_col:
    clicked = st.button("🔍 Cari Vendor & Harga", key="search_btn")
st.markdown('</div>', unsafe_allow_html=True)

# ─── Search Logic ────────────────────────────────────────────────
if clicked:
    if not keyword.strip():
        st.warning("⚠️ Masukkan kata kunci produk terlebih dahulu.")
    else:
        with st.spinner("🤖 AI mencari vendor, harga pasar, dan toko online…"):
            data = search_all(keyword.strip(), location, category, spesifikasi.strip())
            st.session_state.data = data
            st.session_state.done = True
            st.session_state.meta = {
                "keyword":keyword.strip(), "location":location,
                "spesifikasi":spesifikasi.strip(),
                "time":datetime.now().strftime("%H:%M — %d %B %Y")
            }

# ─── Results ─────────────────────────────────────────────────────
if st.session_state.done:
    data     = st.session_state.data
    meta     = st.session_state.meta
    vendors  = data.get("vendors",[])
    harga    = data.get("harga_pasar",{})
    toko     = data.get("toko_online",[])
    kw       = meta.get("keyword","")
    loc      = meta.get("location","")
    spec     = meta.get("spesifikasi","")

    st.markdown('<hr class="divider" style="margin-top:28px">', unsafe_allow_html=True)
    spec_badge = f'<span class="spec-badge">⚙ {spec[:40]}{"..." if len(spec)>40 else ""}</span>' if spec else ""
    st.markdown(f'<p style="margin:0 60px 4px;font-size:13px;color:#8B949E">Hasil pencarian: <b style="color:#E6EDF3">{kw}</b> · {loc} {spec_badge}</p>', unsafe_allow_html=True)
    st.markdown(f'<p style="margin:0 60px 8px;font-size:11px;color:#484F58">🕒 {meta.get("time","")}</p>', unsafe_allow_html=True)

    # 1. HARGA PASAR
    if harga:
        render_harga(harga, kw, spec)

    # 2. PETA INTERAKTIF
    if vendors:
        st.markdown(f"""
        <div class="map-wrap">
          <div class="map-hdr">
            <div><div class="map-title">🗺️ Peta Lokasi Vendor</div>
            <div class="map-sub">Klik pin untuk detail · Scroll untuk zoom</div></div>
            <div class="section-badge">{len(vendors)} pin vendor</div>
          </div>
        </div>""", unsafe_allow_html=True)
        with st.container():
            vendor_map = build_map(vendors, loc)
            with st.columns([1,30,1])[1]:
                st_folium(vendor_map, width="100%", height=430, returned_objects=[])

    # 3. DAFTAR VENDOR
    if vendors:
        st.markdown(f"""
        <div class="section-wrap">
          <div class="section-hdr">
            <div class="section-title">🏭 Daftar Supplier & Vendor</div>
            <div class="section-badge">{len(vendors)} vendor</div>
          </div>
        </div>""", unsafe_allow_html=True)
        with st.container():
            st.markdown('<div style="margin:0 60px">', unsafe_allow_html=True)
            for i,v in enumerate(vendors): render_vendor_card(v,i)
            st.markdown('</div>', unsafe_allow_html=True)

    # 4. TOKO ONLINE
    if toko:
        render_toko_online(toko, kw, loc)

    # Disclaimer
    st.markdown("""
    <div style="margin:8px 60px 48px;padding:12px 18px;background:#161B22;border:1px solid #21262D;border-radius:8px;font-size:12px;color:#484F58">
      ⚠️ <b style="color:#8B949E">Disclaimer:</b> Data vendor, harga, dan informasi toko dihasilkan oleh AI berdasarkan pengetahuan model — bukan data real-time.
      Selalu verifikasi langsung ke vendor/platform sebelum bertransaksi. Harga aktual dapat berbeda.
    </div>""", unsafe_allow_html=True)

else:
    st.markdown("""
    <div class="empty-state">
      <div class="empty-icon">🏭</div>
      <div class="empty-title">Siap Mencari Vendor</div>
      <div class="empty-sub">Masukkan kata kunci, pilih lokasi, dan optionally tambahkan spesifikasi barang.<br>
      Hasil mencakup: harga pasar · peta vendor · daftar supplier · toko online.</div>
    </div>""", unsafe_allow_html=True)
