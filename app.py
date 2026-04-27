import streamlit as st
import requests
import pandas as pd
import time
import io

# Sayfa Yapılandırması
st.set_page_config(page_title="BIST Piyasa Değeri Tarayıcı", page_icon="📈", layout="centered")

# Veri Çekme Fonksiyonu (Önbelleğe alınmış)
# ttl=3600 -> Çekilen veriyi 1 saat boyunca önbellekte tutar, sunucuyu yormaz.
@st.cache_data(ttl=3600, show_spinner=False)
def get_turkey_market_caps():
    url = "https://scanner.tradingview.com/turkey/scan"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "origin": "https://www.tradingview.com",
        "referer": "https://www.tradingview.com/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    all_data = []
    
    # İlerleme çubuğu (UI için)
    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, start in enumerate(range(0, 1050, 150)):
        status_text.text(f"Veriler çekiliyor... Satır: {start} - {start + 150}")
        
        payload = {
            "columns": ["name", "description", "market_cap_basic"],
            "ignore_unknown_fields": False,
            "markets": ["turkey"],
            "range": [start, start + 150],
            "sort": {"sortBy": "market_cap_basic", "sortOrder": "desc"}
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                rows = response.json().get("data", [])
                if not rows:
                    break 
                    
                for item in rows:
                    all_data.append({
                        "Hisse Kodu": item["d"][0],
                        "Şirket Adı": item["d"][1],
                        "Piyasa Değeri (TL)": item["d"][2]
                    })
                
                # İlerleme çubuğunu güncelle (yaklaşık 7 adım)
                progress = min((i + 1) * 15, 100)
                progress_bar.progress(progress)
                time.sleep(0.5) 
                
            else:
                st.error(f"API Hatası: {response.status_code}. TradingView IP'yi engellemiş olabilir.")
                break
                
        except Exception as e:
            st.error(f"Bağlantı hatası: {e}")
            break

    status_text.empty()
    progress_bar.empty()
    
    df = pd.DataFrame(all_data)
    if not df.empty:
        df = df.dropna(subset=['Piyasa Değeri (TL)'])
    return df

# Arayüz (UI) Tasarımı
st.title("🇹🇷 BIST Piyasa Değeri Tarayıcı")
st.markdown("Bu uygulama TradingView üzerinden Borsa İstanbul'daki şirketlerin anlık piyasa değerlerini çeker.")

if st.button("Verileri Çek / Yenile"):
    # Eğer butona basılırsa önbelleği temizle ve taze veri çek
    st.cache_data.clear()
    
    with st.spinner("TradingView sunucularına bağlanılıyor..."):
        df = get_turkey_market_caps()
    
    if not df.empty:
        st.success(f"Başarılı! Toplam {len(df)} şirket bulundu.")
        
        # Veriyi Ekranda Göster
        st.dataframe(df, use_container_width=True)
        
        # DataFrame'i Excel formatına (Sanal Belleğe) çevirme
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Piyasa Değerleri')
        
        # Excel İndirme Butonu
        st.download_button(
            label="📥 Excel Olarak İndir (.xlsx)",
            data=buffer.getvalue(),
            file_name="BIST_Piyasa_Degerleri.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )
    else:
        st.warning("Veri çekilemedi veya liste boş.")
