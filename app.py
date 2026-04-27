import streamlit as st
import requests
import pandas as pd
import io

# Sayfa Başlığı
st.set_page_config(page_title="BIST Piyasa Değeri", page_icon="📊")

@st.cache_data(ttl=3600)
def veri_cek():
    url = "https://scanner.tradingview.com/turkey/scan"
    headers = {"User-Agent": "Mozilla/5.0"}
    all_data = []
    
    # 600 hisse için döngü (150'şerli paketler)
    for start in range(0, 750, 150):
        payload = {
            "columns": ["name", "description", "market_cap_basic"],
            "markets": ["turkey"],
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

st.title("🇹🇷 BIST Piyasa Değeri Tarayıcı")

if st.button("Piyasayı Tara ve Verileri Getir"):
    df = veri_cek()
    
    if not df.empty:
        st.success(f"{len(df)} şirket verisi başarıyla çekildi.")
        st.dataframe(df, use_container_width=True)

        # Excel Dosyası Hazırlama
        buffer = io.BytesIO()
        # Engine olarak openpyxl kullanıyoruz
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='BIST_Veri')
        
        # İndirme Butonu
        st.download_button(
            label="📥 Excel Dosyasını İndir",
            data=buffer.getvalue(),
            file_name="BIST_Piyasa_Degerleri.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.error("Veri çekilemedi. Lütfen internet bağlantınızı veya API durumunu kontrol edin.")
