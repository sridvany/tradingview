import streamlit as st
import requests
import pandas as pd
import io

st.set_page_config(page_title="TradingView Scanner", page_icon="📊")

# TradingView sektör adları -> Türkçe
SEKTOR_TR = {
    "Commercial Services": "Ticari Hizmetler",
    "Communications": "İletişim",
    "Consumer Durables": "Dayanıklı Tüketim",
    "Consumer Non-Durables": "Tüketim (Dayanıksız)",
    "Consumer Services": "Tüketici Hizmetleri",
    "Distribution Services": "Dağıtım Hizmetleri",
    "Electronic Technology": "Elektronik Teknoloji",
    "Energy Minerals": "Enerji Madenleri",
    "Finance": "Finans",
    "Government": "Devlet",
    "Health Services": "Sağlık Hizmetleri",
    "Health Technology": "Sağlık Teknolojisi",
    "Industrial Services": "Endüstriyel Hizmetler",
    "Miscellaneous": "Çeşitli",
    "Non-Energy Minerals": "Enerji Dışı Madenler",
    "Process Industries": "İşlenebilen Endüstriler",
    "Producer Manufacturing": "Üretici İmalatı",
    "Retail Trade": "Perakende Ticaret",
    "Technology Services": "Teknoloji Hizmetleri",
    "Transportation": "Taşımacılık",
    "Utilities": "Elektrik, Su, Gaz Hizmetleri",
}

# Türkçe isim -> (TradingView market kodu, country alanındaki İngilizce isim)
PIYASALAR = {
    "Türkiye": ("turkey", "Turkey"),
    "ABD": ("america", "United States"),
    "Almanya": ("germany", "Germany"),
    "Arjantin": ("argentina", "Argentina"),
    "Avustralya": ("australia", "Australia"),
    "Avusturya": ("austria", "Austria"),
    "BAE": ("uae", "United Arab Emirates"),
    "Bahreyn": ("bahrain", "Bahrain"),
    "Bangladeş": ("bangladesh", "Bangladesh"),
    "Belçika": ("belgium", "Belgium"),
    "Birleşik Krallık": ("uk", "United Kingdom"),
    "Brezilya": ("brazil", "Brazil"),
    "Çek Cumhuriyeti": ("czech", "Czech Republic"),
    "Çin": ("china", "China"),
    "Danimarka": ("denmark", "Denmark"),
    "Endonezya": ("indonesia", "Indonesia"),
    "Estonya": ("estonia", "Estonia"),
    "Filipinler": ("philippines", "Philippines"),
    "Finlandiya": ("finland", "Finland"),
    "Fransa": ("france", "France"),
    "Güney Afrika": ("rsa", "South Africa"),
    "Güney Kore": ("korea", "South Korea"),
    "Hindistan": ("india", "India"),
    "Hollanda": ("netherlands", "Netherlands"),
    "Hong Kong": ("hongkong", "Hong Kong"),
    "İspanya": ("spain", "Spain"),
    "İsrail": ("israel", "Israel"),
    "İsveç": ("sweden", "Sweden"),
    "İsviçre": ("switzerland", "Switzerland"),
    "İtalya": ("italy", "Italy"),
    "İzlanda": ("iceland", "Iceland"),
    "Japonya": ("japan", "Japan"),
    "Kanada": ("canada", "Canada"),
    "Katar": ("qatar", "Qatar"),
    "Kenya": ("kenya", "Kenya"),
    "Kıbrıs": ("cyprus", "Cyprus"),
    "Kolombiya": ("colombia", "Colombia"),
    "Kuveyt": ("kuwait", "Kuwait"),
    "Letonya": ("latvia", "Latvia"),
    "Litvanya": ("lithuania", "Lithuania"),
    "Lüksemburg": ("luxembourg", "Luxembourg"),
    "Macaristan": ("hungary", "Hungary"),
    "Malezya": ("malaysia", "Malaysia"),
    "Meksika": ("mexico", "Mexico"),
    "Mısır": ("egypt", "Egypt"),
    "Nijerya": ("nigeria", "Nigeria"),
    "Norveç": ("norway", "Norway"),
    "Pakistan": ("pakistan", "Pakistan"),
    "Peru": ("peru", "Peru"),
    "Polonya": ("poland", "Poland"),
    "Portekiz": ("portugal", "Portugal"),
    "Romanya": ("romania", "Romania"),
    "Rusya": ("russia", "Russia"),
    "Singapur": ("singapore", "Singapore"),
    "Sırbistan": ("serbia", "Serbia"),
    "Slovakya": ("slovakia", "Slovakia"),
    "Sri Lanka": ("srilanka", "Sri Lanka"),
    "Suudi Arabistan": ("ksa", "Saudi Arabia"),
    "Şili": ("chile", "Chile"),
    "Tayland": ("thailand", "Thailand"),
    "Tayvan": ("taiwan", "Taiwan"),
    "Tunus": ("tunisia", "Tunisia"),
    "Venezuela": ("venezuela", "Venezuela"),
    "Vietnam": ("vietnam", "Vietnam"),
    "Yeni Zelanda": ("newzealand", "New Zealand"),
    "Yunanistan": ("greece", "Greece"),
}


@st.cache_data(ttl=3600)
def veri_cek(market: str, country: str, sadece_yerli: bool):
    url = f"https://scanner.tradingview.com/{market}/scan"
    headers = {
        "authority": "scanner.tradingview.com",
        "accept": "application/json",
        "content-type": "application/x-www-form-urlencoded;charset=UTF-8",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36",
        "origin": "https://www.tradingview.com",
        "referer": "https://www.tradingview.com/",
    }
    columns = ["name", "description", "country", "exchange",
               "currency", "sector", "market_cap_basic"]
    filtreler = [{"left": "type", "operation": "equal", "right": "stock"}]
    if sadece_yerli:
        filtreler.append(
            {"left": "country", "operation": "equal", "right": country}
        )

    all_data = []
    for start in range(0, 1500, 150):
        payload = {
            "columns": columns,
            "markets": [market],
            "filter": filtreler,
            "range": [start, start + 150],
            "sort": {"sortBy": "market_cap_basic", "sortOrder": "desc"},
        }
        res = requests.post(url, headers=headers, json=payload, timeout=20)
        if res.status_code != 200:
            break
        data = res.json().get("data", [])
        if not data:
            break
        for item in data:
            d = item["d"]
            all_data.append({
                "Hisse": d[0],
                "Şirket": d[1],
                "Ülke": d[2],
                "Borsa": d[3],
                "Para Birimi": d[4],
                "Sektör": SEKTOR_TR.get(d[5], d[5] or ""),
                "Piyasa Değeri": d[6],
            })
        if len(data) < 150:
            break
    return pd.DataFrame(all_data)


st.title("📊 TradingView Scanner")

# Türkçe karakter farkını aşmak için sıralama anahtarı
def tr_key(s: str) -> str:
    return s.translate(str.maketrans("ÇĞİıÖŞÜçğıöşü", "CGIIOSUcgiosu")).lower()

secim = st.selectbox(
    "Piyasa (ülke) seç:",
    options=sorted(PIYASALAR.keys(), key=tr_key),
    index=sorted(PIYASALAR.keys(), key=tr_key).index("Türkiye"),
)
sadece_yerli = st.checkbox(
    "Sadece bu ülkenin şirketleri (yabancı/ETF/çapraz kotluları gizle)",
    value=True,
)

market, country = PIYASALAR[secim]

if st.button("Piyasayı Tara ve Verileri Getir"):
    df = veri_cek(market, country, sadece_yerli)
    if not df.empty:
        st.success(f"{secim}: {len(df)} şirket çekildi.")
        st.dataframe(df, use_container_width=True)

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Veriler")
        st.download_button(
            label="📥 Excel Dosyasını İndir",
            data=buffer.getvalue(),
            file_name=f"{market}_Piyasa_Degerleri.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    else:
        st.error("Veri çekilemedi. Bağlantını veya API durumunu kontrol et.")
