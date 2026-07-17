import streamlit as st
import requests
import pandas as pd
import io

st.set_page_config(page_title="TradingView Screener", page_icon="📊")

# Sekme yazı stili
st.markdown("""
<style>
.stTabs button[data-baseweb="tab"] p {
    font-weight: 700 !important;
}
</style>
""", unsafe_allow_html=True)

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
    ("oper_income_ttm", "Faaliyet Geliri (TTM)"),
    ("ebitda_ttm", "FAVÖK (TTM)"),
    ("net_income_ttm", "Net Kar (TTM)"),
    ("earnings_per_share_basic_ttm", "EPS Temel (TTM)"),
    ("earnings_per_share_diluted_ttm", "EPS Seyreltilmiş (TTM)"),
    ("earnings_per_share_diluted_yoy_growth_ttm", "EPS Büyüme YY % (TTM)"),
    ("gross_margin_ttm", "Brüt Marj % (TTM)"),
    ("operating_margin_ttm", "Faaliyet Marjı % (TTM)"),
    ("net_margin_ttm", "Net Marj % (TTM)"),
    ("price_earnings_ttm", "F/K (FKO)"),
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
]

PERF_KOLONLARI = [
    ("Perf.W", "1 Hafta %"),
    ("Perf.1M", "1 Ay %"),
    ("Perf.3M", "3 Ay %"),
    ("Perf.6M", "6 Ay %"),
    ("Perf.Y", "1 Yıl %"),
]

TEKNIK_KOLONLARI = [
    ("close", "Kapanış"),
    ("SMA50", "SMA50"),
    ("SMA200", "SMA200"),
]

# Özet sekmesinde gösterilecek kolonlar
OZET_ADLARI = [
    "Hisse", "Şirket", "Sektör", "Piyasa Değeri",
    "F/K (FKO)", "FAVÖK (TTM)", "Cari Oran", "Asit-Test Oranı",
]

TUM_KOLONLAR = (
    ORTAK_KOLONLAR + GELIR_KOLONLARI + BILANCO_KOLONLARI
    + NAKIT_KOLONLARI + PERF_KOLONLARI + TEKNIK_KOLONLARI
)


@st.cache_data(ttl=3600)
def veri_cek_v5(market: str, country: str, sadece_yerli: bool, kolonlar: tuple):
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
    api_alanlari = [k[0] for k in kolonlar]
    gosterim_adlari = [k[1] for k in kolonlar]

    filtreler = [{"left": "type", "operation": "equal", "right": "stock"}]
    if sadece_yerli:
        filtreler.append(
            {"left": "country", "operation": "equal", "right": country}
        )

    all_rows = []
    son_hata = None
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
            son_hata = f"HTTP {res.status_code}: {res.text[:500]}"
            break
        data = res.json().get("data", [])
        if not data:
            break
        for item in data:
            d = item["d"]
            row = dict(zip(gosterim_adlari, d))
            row["Sektör"] = SEKTOR_TR.get(row.get("Sektör"), row.get("Sektör") or "")
            # CapEx muhasebede negatif gelir (nakit çıkışı) -> mutlak değere çevir
            capex = row.get("Yatırım Harcamaları / CapEx (TTM)")
            if isinstance(capex, (int, float)):
                row["Yatırım Harcamaları / CapEx (TTM)"] = abs(capex)
            all_rows.append(row)
        if len(data) < 150:
            break
    df_son = pd.DataFrame(all_rows, columns=gosterim_adlari)
    # Olası çift kolon adlarını temizle
    df_son = df_son.loc[:, ~df_son.columns.duplicated()]
    return df_son, son_hata


st.title("📊 TradingView Screener")


@st.cache_data(ttl=86400)
def regresyon_hesapla(semboller: tuple):
    """Her hisse için log-fiyat ~ zaman regresyonu: eğim (yıllık %) ve R²."""
    import numpy as np
    import yfinance as yf

    data = yf.download(
        list(semboller), period="1y", interval="1d",
        auto_adjust=True, progress=False,
    )["Close"]
    if isinstance(data, pd.Series):
        data = data.to_frame()

    sonuclar = []
    for s in data.columns:
        fiyat = data[s].dropna()
        fiyat = fiyat[fiyat > 0]
        if len(fiyat) < 120:  # en az ~6 ay işlem günü
            continue
        y = np.log(fiyat.values)
        x = np.arange(len(y))
        egim, sabit = np.polyfit(x, y, 1)
        y_tahmin = sabit + egim * x
        ss_res = ((y - y_tahmin) ** 2).sum()
        ss_top = ((y - y.mean()) ** 2).sum()
        r2 = 1 - ss_res / ss_top if ss_top > 0 else 0.0
        yillik = (np.exp(egim * 252) - 1) * 100  # yıllıklandırılmış eğim %
        sonuclar.append({
            "Hisse": s.split(".")[0],
            "Yıllık Eğim %": round(yillik, 1),
            "R²": round(r2, 3),
            "Regresyon Skoru": round(yillik * r2, 1),
            "Gün Sayısı": len(fiyat),
        })
    return pd.DataFrame(sonuclar)


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
    st.session_state["tarama"] = veri_cek_v5(
        market, country, sadece_yerli, tuple(TUM_KOLONLAR)
    )

if "tarama" in st.session_state:
    df, hata = st.session_state["tarama"]
    if df.empty:
        st.error("Veri çekilemedi.")
        if hata:
            st.code(hata)
    else:
        st.success(f"{secim}: {len(df)} şirket çekildi.")

        ortak_adlar = [k[1] for k in ORTAK_KOLONLAR]
        perf_adlar = [k[1] for k in PERF_KOLONLARI]
        df_ozet = df[OZET_ADLARI]
        df_genel = df[ortak_adlar]
        df_gelir = df[ortak_adlar + [k[1] for k in GELIR_KOLONLARI]]
        df_bilanco = df[ortak_adlar + [k[1] for k in BILANCO_KOLONLARI]]
        df_nakit = df[ortak_adlar + [k[1] for k in NAKIT_KOLONLARI]]
        df_perf = df[["Hisse", "Şirket", "Sektör"] + perf_adlar]

        sek_ozet, sek_perf, sek_ist, sek_reg, sek1, sek2, sek3, sek4 = st.tabs(
            ["Özet", "Yükselen / Düşen", "İstikrarlı Yükselenler",
             "Regresyon", "Genel", "Gelir Tablosu", "Bilanço", "Nakit Akışı"]
        )
        with sek_ozet:
            st.dataframe(df_ozet, use_container_width=True)
        with sek_perf:
            periyot = st.selectbox("Periyot seç:", perf_adlar)
            adet = st.slider("Kaç hisse listelensin?", 5, 50, 20)
            df_p = df_perf.dropna(subset=[periyot]).sort_values(
                periyot, ascending=False
            )
            df_p[periyot] = df_p[periyot].round(2)
            kol1, kol2 = st.columns(2)
            with kol1:
                st.subheader(f"📈 En Çok Yükselen {adet}")
                st.dataframe(
                    df_p.head(adet).reset_index(drop=True),
                    use_container_width=True,
                )
            with kol2:
                st.subheader(f"📉 En Çok Düşen {adet}")
                st.dataframe(
                    df_p.tail(adet).iloc[::-1].reset_index(drop=True),
                    use_container_width=True,
                )
        with sek_ist:
            st.caption(
                "Skor: her periyottaki yüzdelik sıranın ortalaması (0-100). "
                "Sapma: 1Y ≥ 6A ≥ 3A ≥ 1A ≥ 1H ≥ 0 dizilimine aykırılık sayısı "
                "(0 = kazanç zamana düzgün yayılmış). "
                "Trend: Kapanış > SMA50 > SMA200."
            )
            df_i = df[
                ["Hisse", "Şirket", "Sektör"] + perf_adlar
                + ["Kapanış", "SMA50", "SMA200"]
            ].dropna(subset=perf_adlar).copy()

            # Skor: periyot bazlı yüzdelik sıraların ortalaması
            df_i["Skor"] = (
                df_i[perf_adlar].rank(pct=True).mean(axis=1).mul(100).round(1)
            )

            # Monotonluk sapması: uzun vadeden kısaya kümülatif getiri azalmalı
            sirali = ["1 Yıl %", "6 Ay %", "3 Ay %", "1 Ay %", "1 Hafta %"]
            sapma = (df_i["1 Hafta %"] < 0).astype(int)
            for a, b in zip(sirali[:-1], sirali[1:]):
                sapma += (df_i[a] < df_i[b]).astype(int)
            df_i["Sapma"] = sapma

            df_i["Trend"] = (
                (df_i["Kapanış"] > df_i["SMA50"])
                & (df_i["SMA50"] > df_i["SMA200"])
            )

            f1 = st.checkbox("Tüm periyotlar pozitif olsun", value=True)
            f2 = st.checkbox("Trend yapısı sağlansın (Fiyat > SMA50 > SMA200)",
                             value=True)
            max_sapma = st.slider("İzin verilen maksimum sapma", 0, 5, 1)

            df_f = df_i.copy()
            if f1:
                df_f = df_f[(df_f[perf_adlar] > 0).all(axis=1)]
            if f2:
                df_f = df_f[df_f["Trend"]]
            df_f = df_f[df_f["Sapma"] <= max_sapma]
            df_f = df_f.sort_values("Skor", ascending=False)

            st.write(f"**{len(df_f)} hisse** kriterleri sağlıyor.")
            gosterim = (
                ["Hisse", "Şirket", "Sektör", "Skor", "Sapma", "Trend"]
                + perf_adlar
            )
            df_ist_son = df_f[gosterim].reset_index(drop=True)
            st.dataframe(df_ist_son, use_container_width=True)

        with sek_reg:
            st.caption(
                "Her hissenin 1 yıllık günlük log fiyatı zamana karşı regres "
                "edilir. Yıllık Eğim %: yükseliş hızı. R²: düzenlilik "
                "(1'e yakın = çizgi gibi). Skor = Eğim × R² — hem hızlı hem "
                "düzenli yükselenler üstte."
            )
            if market != "turkey":
                st.info("Regresyon analizi şimdilik sadece Türkiye "
                        "piyasası için destekleniyor.")
            else:
                if st.button("Regresyonu Hesapla (tüm hisseler, ~1-2 dk)"):
                    semboller = tuple(
                        df["Hisse"].astype(str).str.strip() + ".IS"
                    )
                    with st.spinner("Fiyat geçmişi indiriliyor ve "
                                    "regresyon hesaplanıyor..."):
                        st.session_state["regresyon"] = (
                            regresyon_hesapla(semboller)
                        )
                if "regresyon" in st.session_state:
                    df_reg = st.session_state["regresyon"]
                    if df_reg.empty:
                        st.error("Fiyat geçmişi indirilemedi.")
                    else:
                        df_reg = df_reg.merge(
                            df[["Hisse", "Şirket", "Sektör"]],
                            on="Hisse", how="left",
                        )
                        df_reg = df_reg[
                            ["Hisse", "Şirket", "Sektör", "Yıllık Eğim %",
                             "R²", "Regresyon Skoru", "Gün Sayısı"]
                        ].sort_values(
                            "R²", ascending=False
                        ).reset_index(drop=True)
                        st.write(f"**{len(df_reg)} hisse** analiz edildi.")
                        st.dataframe(df_reg, use_container_width=True)

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
            df_ozet.to_excel(writer, index=False, sheet_name="Özet")
            df_p.head(adet).to_excel(
                writer, index=False, sheet_name=f"Yükselenler ({periyot})"
            )
            df_p.tail(adet).iloc[::-1].to_excel(
                writer, index=False, sheet_name=f"Düşenler ({periyot})"
            )
            df_perf.to_excel(writer, index=False, sheet_name="Performans")
            df_ist_son.to_excel(
                writer, index=False, sheet_name="İstikrarlı Yükselenler"
            )
            if "regresyon" in st.session_state and market == "turkey":
                r = st.session_state["regresyon"]
                if not r.empty:
                    r.merge(
                        df[["Hisse", "Şirket", "Sektör"]],
                        on="Hisse", how="left",
                    ).sort_values(
                        "R²", ascending=False
                    ).to_excel(writer, index=False, sheet_name="Regresyon")
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
