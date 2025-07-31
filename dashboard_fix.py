import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter

# Set layout dan tampilan halaman
st.set_page_config(page_title="Sosiola Insight – Ulasan Produk Sosiola", layout="wide")

st.markdown("""
    <style>
    .main {
        background-color: #fff8f9;
    }
    h1, h2, h3 {
        color: #c94f7c;
    }
    .stButton>button {
        background-color: #f3ccd3;
        color: black;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>💋 Sesiola Product Review </h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Membaca emosi pelanggan lewat kata-kata mereka – karena kecantikan juga tentang perasaan.</p>", unsafe_allow_html=True)

@st.cache_data
def load_data(filepath):
    try:
        df = pd.read_csv(filepath)
        df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
        df['loves_count'] = pd.to_numeric(df['loves_count'], errors='coerce')
        return df
    except FileNotFoundError:
        st.error("💔 File data belum ditemukan. Pastikan `dataset_final.csv` sudah ada di folder `data/`.")
        return None

def interpret_sentiment(df_subset):
    positif = df_subset[df_subset['sentimen'] == 'Positif']['comment_clean'].dropna()
    negatif = df_subset[df_subset['sentimen'] == 'Negatif']['comment_clean'].dropna()

    top_pos = Counter(" ".join(positif).split()).most_common(3)
    top_neg = Counter(" ".join(negatif).split()).most_common(3)

    result = {
        "highlight_pos": ", ".join([f"💖 *{w}*" for w, _ in top_pos]) if top_pos else "Tidak ada kata positif menonjol.",
        "highlight_neg": ", ".join([f"💔 *{w}*" for w, _ in top_neg]) if top_neg else "Tidak ada keluhan signifikan.",
        "vibe": ""
    }

    if len(positif) > 2 * len(negatif):
        result['vibe'] = "🌟 Produk ini sangat disukai! Banyak yang merasa cocok dan puas."
    elif len(negatif) > len(positif):
        result['vibe'] = "😕 Produk ini masih perlu diperbaiki. Cukup banyak yang merasa kurang puas."
    else:
        result['vibe'] = "🤔 Campur aduk. Produk ini punya kelebihan, tapi juga kekurangan."

    return result

# Load dataset
df = load_data("data/dataset_final.csv")

if df is not None:
    st.sidebar.title("✨ Filter Review")
    brand = st.sidebar.selectbox("Pilih Brand", sorted(df['brand_name'].unique()))
    df_brand = df[df['brand_name'] == brand]

    produk = st.sidebar.selectbox("Pilih Produk", sorted(df_brand['product_name'].unique()))
    df_produk = df_brand[df_brand['product_name'] == produk]

    st.markdown(f"## 📌 Produk: **{produk}** dari brand *{brand}*")

    if df_produk.empty:
        st.warning("Tidak ada ulasan yang bisa ditampilkan.")
    else:
        sentimen = interpret_sentiment(df_produk)
        st.markdown(f"**Keyword Positif dari Review:** {sentimen['highlight_pos']}")
        st.markdown(f"**Keyword Negatif dari Review:** {sentimen['highlight_neg']}")
        st.info(sentimen['vibe'])

        st.markdown("### 📊 Sentimen Komentar Pengguna")
        st.bar_chart(df_produk['sentimen'].value_counts())

        # Word Cloud Bagian
        st.markdown("### ☁️ Nuansa Kata dari Komentar")
        col1, col2 = st.columns(2)
        with col1:
            pos_text = " ".join(df_produk[df_produk['sentimen'] == 'Positif']['comment_clean'].dropna())
            st.markdown("**💗 Kata yang Sering Muncul di Review Positif**")
            if pos_text:
                wc = WordCloud(width=450, height=300, background_color="white", colormap="pink").generate(pos_text)
                fig, ax = plt.subplots()
                ax.imshow(wc, interpolation='bilinear')
                ax.axis("off")
                st.pyplot(fig)
            else:
                st.write("Tidak ada review positif.")

        with col2:
            neg_text = " ".join(df_produk[df_produk['sentimen'] == 'Negatif']['comment_clean'].dropna())
            st.markdown("**🖤 Kata yang Sering Muncul di Review Negatif**")
            if neg_text:
                wc = WordCloud(width=450, height=300, background_color="white", colormap="gray").generate(neg_text)
                fig, ax = plt.subplots()
                ax.imshow(wc, interpolation='bilinear')
                ax.axis("off")
                st.pyplot(fig)
            else:
                st.write("Tidak ada review negatif.")

        # Komentar asli pengguna
        with st.expander("💬 Lihat Komentar Lengkap"):
            st.dataframe(df_produk[['sentimen', 'text']].rename(columns={'text': 'Komentar'}), height=300)

        st.markdown("---")
        st.markdown("### 💡 Catatan Akhir")
        st.success("Dengan memahami komentar asli konsumen, brand bisa lebih terhubung secara emosional dan strategis dengan penggunanya. Beauty is data too! 💅")
