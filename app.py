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


# Kolon grupları: (api_alani, gosterim_adi)
ORTAK_KOLONLAR = [
    ("name", "Hisse"),
    ("description", "Şirket"),
    ("country", "Ülke"),
    ("exchange", "Borsa"),
    ("currency", "Para Birimi"),
    ("sector", "Sektör"),
    ("market_cap_basic", "Piyasa Değeri"),
]

GELIR_KOLONLARI = [
    ("total_revenue_ttm", "Gelir (TTM)"),
    ("total_revenue_yoy_growth_ttm", "Gelir Büyüme YY % (TTM)"),
    ("gross_profit_ttm", "Brüt Kar (TTM)"),
    ("operating_income_ttm", "Faaliyet Geliri (TTM)"),
    ("ebitda_ttm", "FAVÖK (TTM)"),
    ("net_income_ttm", "Net Kar (TTM)"),
    ("earnings_per_share_basic_ttm", "EPS Temel (TTM)"),
    ("earnings_per_share_diluted_ttm", "EPS Seyreltilmiş (TTM)"),
    ("earnings_per_share_diluted_yoy_growth_ttm", "EPS Büyüme YY % (TTM)"),
    ("gross_margin_ttm", "Brüt Marj % (TTM)"),
    ("operating_margin_ttm", "Faaliyet Marjı % (TTM)"),
    ("net_margin_ttm", "Net Marj % (TTM)"),
]

BILANCO_KOLONLARI = [
    ("total_assets_fq", "Toplam Varlıklar"),
    ("total_current_assets_fq", "Dönen Varlıklar"),
    ("cash_n_short_term_invest_fq", "Nakit ve Kısa Vad. Yatırımlar"),
    ("total_liabilities_fq", "Toplam Yükümlülükler"),
    ("total_current_liabilities_fq", "Kısa Vad. Yükümlülükler"),
    ("total_debt_fq", "Toplam Borç"),
    ("long_term_debt_fq", "Uzun Vad. Borç"),
    ("total_equity_fq", "Özkaynaklar"),
    ("book_value_per_share_fq", "Defter Değeri / Hisse"),
    ("current_ratio_fq", "Cari Oran"),
    ("quick_ratio_fq", "Asit-Test Oranı"),
    ("debt_to_equity_fq", "Borç / Özkaynak"),
]

NAKIT_KOLONLARI = [
    ("cash_f_operating_activities_ttm", "Faaliyet Nakit Akışı (TTM)"),
    ("cash_f_investing_activities_ttm", "Yatırım Nakit Akışı (TTM)"),
    ("cash_f_financing_activities_ttm", "Finansman Nakit Akışı (TTM)"),
    ("free_cash_flow_ttm", "Serbest Nakit Akışı (TTM)"),
    ("capital_expenditures_ttm", "Yatırım Harcamaları / CapEx (TTM)"),
    ("net_income_ttm", "Net Kar (TTM)"),
]

TUM_KOLONLAR = ORTAK_KOLONLAR + GELIR_KOLONLARI + BILANCO_KOLONLARI + NAKIT_KOLONLARI


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
    api_alanlari = [k[0] for k in TUM_KOLONLAR]
    gosterim_adlari = [k[1] for k in TUM_KOLONLAR]

    filtreler = [{"left": "type", "operation": "equal", "right": "stock"}]
    if sadece_yerli:
        filtreler.append(
            {"left": "country", "operation": "equal", "right": country}
        )

    all_rows = []
    for start in range(0, 1500, 150):
        payload = {
            "columns": api_alanlari,
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
            row = dict(zip(gosterim_adlari, d))
            # Sektörü Türkçeleştir
            row["Sektör"] = SEKTOR_TR.get(row.get("Sektör"), row.get("Sektör") or "")
            all_rows.append(row)
        if len(data) < 150:
            break
    return pd.DataFrame(all_rows, columns=gosterim_adlari)


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
    if df.empty:
        st.error("Veri çekilemedi. Bağlantını veya API durumunu kontrol et.")
    else:
        st.success(f"{secim}: {len(df)} şirket çekildi.")

        ortak_adlar = [k[1] for k in ORTAK_KOLONLAR]
        df_genel = df[ortak_adlar]
        df_gelir = df[ortak_adlar + [k[1] for k in GELIR_KOLONLARI]]
        df_bilanco = df[ortak_adlar + [k[1] for k in BILANCO_KOLONLARI]]
        df_nakit = df[ortak_adlar + [k[1] for k in NAKIT_KOLONLARI]]

        sek1, sek2, sek3, sek4 = st.tabs(
            ["Genel", "Gelir Tablosu", "Bilanço", "Nakit Akışı"]
        )
        with sek1:
            st.dataframe(df_genel, use_container_width=True)
        with sek2:
            st.dataframe(df_gelir, use_container_width=True)
        with sek3:
            st.dataframe(df_bilanco, use_container_width=True)
        with sek4:
            st.dataframe(df_nakit, use_container_width=True)

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df_genel.to_excel(writer, index=False, sheet_name="Genel")
            df_gelir.to_excel(writer, index=False, sheet_name="Gelir Tablosu")
            df_bilanco.to_excel(writer, index=False, sheet_name="Bilanço")
            df_nakit.to_excel(writer, index=False, sheet_name="Nakit Akışı")
        st.download_button(
            label="📥 Excel Dosyasını İndir",
            data=buffer.getvalue(),
            file_name=f"{market}_Finansallar.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
