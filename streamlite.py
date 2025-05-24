import streamlit as st
import pandas as pd
from pymongo import MongoClient
import matplotlib.pyplot as plt
import seaborn as sns
import nltk
import re
import os
import logging
from wordcloud import WordCloud
from collections import Counter

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Download stopwords (hanya perlu sekali)
    nltk.download('stopwords', quiet=True)
    from nltk.corpus import stopwords

    # Setup koneksi MongoDB
    logger.info("Connecting to MongoDB...")
    client = MongoClient('mongodb+srv://eL_loker:elloker123@bigdata.fukimpx.mongodb.net/?retryWrites=true&w=majority&appName=BigData')
    db = client['jobstreet2']
    collection = db['job']

    # Ambil data dari MongoDB
    logger.info("Fetching data from MongoDB...")
    data = list(collection.find({}, {'_id': 0}))
    df = pd.DataFrame(data)
    logger.info(f"Successfully loaded {len(df)} records")

    # Sidebar filter
    st.sidebar.title("🔍 Filter")
    categories = sorted(df['category'].unique())
    # Tambahkan opsi "Semua Kategori" di awal list
    all_categories = ['Semua Kategori'] + list(categories)
    selected_category = st.sidebar.selectbox("Pilih Kategori Pekerjaan", all_categories)

    # Filter data berdasarkan kategori
    if selected_category == 'Semua Kategori':
        filtered_df = df
    else:
        filtered_df = df[df['category'] == selected_category]

    # Judul halaman
    st.title("📊 Visualisasi Data Lowongan Kerja dari JobStreet")

    # Ringkasan data
    if selected_category == 'Semua Kategori':
        st.subheader("📁 Total Lowongan di Semua Kategori")
    else:
        st.subheader(f"📁 Total Lowongan di Kategori: {selected_category}")
    st.write(f"Jumlah data: {len(filtered_df)}")
    
    # Tampilkan data dengan error handling
    try:
        st.dataframe(filtered_df[['title', 'company', 'location', 'salary', 'job_type', 'posted_date']])
    except Exception as e:
        st.error(f"Error displaying dataframe: {str(e)}")
        logger.error(f"DataFrame display error: {str(e)}")

    # Visualisasi: Jumlah lowongan per kategori
    try:
        st.subheader("📈 Jumlah Lowongan per Kategori")
        category_counts = df['category'].value_counts().sort_values(ascending=False)

        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(x=category_counts.index, y=category_counts.values, ax=ax, palette="viridis")
        plt.xticks(rotation=45, ha="right")
        plt.xlabel("Kategori")
        plt.ylabel("Jumlah Lowongan")
        plt.title("Distribusi Lowongan Berdasarkan Kategori")
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Error creating category visualization: {str(e)}")
        logger.error(f"Category visualization error: {str(e)}")

    # Visualisasi: Jenis pekerjaan dalam kategori terpilih
    try:
        st.subheader(f"🧪 Distribusi Tipe Pekerjaan di Kategori {selected_category}")
        job_type_counts = filtered_df['job_type'].value_counts()

        fig2, ax2 = plt.subplots()
        job_type_counts.plot(kind='pie', autopct='%1.1f%%', ax=ax2, startangle=90, shadow=True)
        ax2.set_ylabel('')
        ax2.set_title("Distribusi Tipe Pekerjaan")
        st.pyplot(fig2)
    except Exception as e:
        st.error(f"Error creating job type visualization: {str(e)}")
        logger.error(f"Job type visualization error: {str(e)}")

    # Visualisasi: Word Cloud untuk judul pekerjaan
    try:
        st.subheader("☁️ Word Cloud Judul Pekerjaan")
        
        # Menggabungkan semua judul pekerjaan
        all_titles = ' '.join(filtered_df['title'].fillna('').astype(str))
        
        # Membersihkan teks
        def clean_text(text):
            # Menghapus karakter khusus dan angka
            text = re.sub(r'[^\w\s]', '', text)
            text = re.sub(r'\d+', '', text)
            # Mengubah ke lowercase
            text = text.lower()
            return text
        
        # Membersihkan teks
        cleaned_text = clean_text(all_titles)
        
        # Menghapus stopwords
        stop_words = set(stopwords.words('english'))
        words = cleaned_text.split()
        filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Membuat word cloud
        wordcloud = WordCloud(width=800, height=400, 
                            background_color='white',
                            max_words=100,
                            contour_width=3,
                            contour_color='steelblue').generate(' '.join(filtered_words))
        
        # Menampilkan word cloud
        fig3, ax3 = plt.subplots(figsize=(10, 5))
        ax3.imshow(wordcloud, interpolation='bilinear')
        ax3.axis('off')
        st.pyplot(fig3)
        
    except Exception as e:
        st.error(f"Error creating word cloud: {str(e)}")
        logger.error(f"Word cloud error: {str(e)}")

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    logger.error(f"Main application error: {str(e)}")
