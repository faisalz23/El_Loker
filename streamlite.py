import streamlit as st
import pandas as pd
from pymongo import MongoClient
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import nltk
import re

# Download stopwords (hanya perlu sekali)
nltk.download('stopwords')
from nltk.corpus import stopwords

# Setup koneksi MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['jobstreet2']
collection = db['job']

# Ambil data dari MongoDB
data = list(collection.find({}, {'_id': 0}))
df = pd.DataFrame(data)

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
st.dataframe(filtered_df[['title', 'company', 'location', 'salary', 'job_type', 'posted_date']])

# Visualisasi: Jumlah lowongan per kategori
st.subheader("📈 Jumlah Lowongan per Kategori")
category_counts = df['category'].value_counts().sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(x=category_counts.index, y=category_counts.values, ax=ax, palette="viridis")
plt.xticks(rotation=45, ha="right")
plt.xlabel("Kategori")
plt.ylabel("Jumlah Lowongan")
plt.title("Distribusi Lowongan Berdasarkan Kategori")
st.pyplot(fig)

# Visualisasi: Jenis pekerjaan dalam kategori terpilih
st.subheader(f"🧪 Distribusi Tipe Pekerjaan di Kategori {selected_category}")
job_type_counts = filtered_df['job_type'].value_counts()

fig2, ax2 = plt.subplots()
job_type_counts.plot(kind='pie', autopct='%1.1f%%', ax=ax2, startangle=90, shadow=True)
ax2.set_ylabel('')
ax2.set_title("Distribusi Tipe Pekerjaan")
st.pyplot(fig2)

# WordCloud: dari Judul Lowongan
st.subheader(f"☁️ WordCloud Judul Lowongan: {selected_category}")
text = ' '.join(filtered_df['title'].dropna().tolist())
text = re.sub(r'[^a-zA-Z\s]', '', text)

# Gabungkan stopwords Indonesia dan Inggris
stop_words = set(stopwords.words('indonesian')) | set(stopwords.words('english'))

wordcloud = WordCloud(width=800, height=400, background_color='white',
                      stopwords=stop_words, colormap='viridis').generate(text)

fig_wc, ax_wc = plt.subplots(figsize=(10, 5))
ax_wc.imshow(wordcloud, interpolation='bilinear')
ax_wc.axis('off')
st.pyplot(fig_wc)
