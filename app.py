import streamlit as st
import requests
import pandas as pd

# Sayfa Başlığı
st.set_page_config(page_title="BIST Piyasa Değeri", page_icon="📊")

@st.cache_data(ttl=3600)
def veri_cek(market: str):
    url = f"https://scanner.tradingview.com/{market}/scan"
    headers = {"User-Agent": "Mozilla/5.0"}
    all_data = []
    
    # 750 hisse için döngü (150'şerli paketler)
    for start in range(0, 750, 150):
        payload = {
            "columns": ["name", "description", "market_cap_basic"],
            "markets": [market],
            "range": [start, start + 150],
            "sort": {"sortBy": "market_cap_basic", "sortOrder": "desc"}
        }
        res = requests.post(url, headers=headers, json=payload)
        if res.status_code == 200:
            data = res.json().get("data", [])
            for item in data:
                all_data.append({
                    "Hisse": item["d"][0],
                    "Şirket": item["d"][1],
                    "Piyasa Değeri (TL)": item["d"][2]
                })
    return pd.DataFrame(all_data)

st.title("📊 TradingView Piyasa Değeri Tarayıcı")

market = st.text_input(
    "Piyasa (ülke) adı:",
    value="turkey",
    help="Örnek: turkey, america, germany, uk, japan, india, france, italy, brazil, china, crypto"
).strip().lower()

if st.button("Piyasayı Tara ve Verileri Getir"):
    df = veri_cek(market)
    
    if not df.empty:
        st.success(f"{len(df)} şirket verisi başarıyla çekildi.")
        st.dataframe(df, use_container_width=True)

        # CSV İndirme
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 CSV Dosyasını İndir",
            data=csv,
            file_name=f"{market}_Piyasa_Degerleri.csv",
            mime="text/csv"
        )
    else:
        st.error("Veri çekilemedi. Piyasa adını kontrol et veya bağlantını test et.")
