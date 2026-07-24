import pandas as pd
import streamlit as st

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Sales Command Center",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- 2. CUSTOM CSS (TAMPILAN FUTURISTIK / SCI-FI COMMAND CENTER) ---
st.markdown(
    """
    <style>
    /* Mengubah background utama menjadi gelap ala Command Center */
    .stApp {
        background-color: #0b0f19;
        color: #ffffff;
    }
    
    /* Styling Kartu Metrik / Kotak Informasi */
    .metric-card {
        background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
        border: 1px solid #3b82f6;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(59, 130, 246, 0.2);
        text-align: center;
    }
    
    /* Judul Kartu */
    .metric-title {
        color: #93c5fd;
        font-size: 14px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Nilai Angka di Kartu */
    .metric-value {
        color: #ffffff;
        font-size: 26px;
        font-weight: bold;
        margin-top: 8px;
    }
    
    /* Styling Header */
    h1, h2, h3 {
        color: #f3f4f6 !important;
        font-family: 'Segoe UI', sans-serif;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #030712;
        border-right: 1px solid #1f2937;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Judul Utama Dashboard
st.title("🚀 Real-Time Sales Command Center")
st.markdown(
    "Pantau performa penjualan *Value* dan *Qty* secara *real-time* dari level"
    " Toko, AC, hingga RH."
)
st.divider()


# --- 3. Ambil Data Langsung dari Link CSV Google Sheets ---
@st.cache_data(ttl=60)
def load_data():
  url_csv = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSkCGIjm8H4oXPxsZtVLH-8CK-jpYyzfMXo_JTJVYXPJetjjJqBGFdE5wWzS-12039hC4GTNx1rNS_c/pub?output=csv"
  df = pd.read_csv(url_csv)

  for col in ["Sales_Value", "Qty"]:
    if col in df.columns:
      df[col] = (
          df[col]
          .astype(str)
          .str.replace("Rp", "", regex=False)
          .str.replace("IDR", "", regex=False)
          .str.replace(".", "", regex=False)
          .str.replace(",", ".", regex=False)
          .str.replace(r"[^\d.-]", "", regex=True)
      )
      df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

  return df


try:
  df_transaksi = load_data()

  if not df_transaksi.empty:

    # --- 4. SIDEBAR: FILTER WILAYAH ---
    st.sidebar.header("🔍 Saring Wilayah")

    list_rh = ["Semua RH"] + sorted(
        df_transaksi["Regional_Head"].dropna().unique().tolist()
    )
    selected_rh = st.sidebar.selectbox("Pilih Regional Head (RH)", list_rh)

    if selected_rh != "Semua RH":
      df_filtered = df_transaksi[df_transaksi["Regional_Head"] == selected_rh]
    else:
      df_filtered = df_transaksi.copy()

    list_ac = ["Semua AC"] + sorted(
        df_filtered["Nama_AC"].dropna().unique().tolist()
    )
    selected_ac = st.sidebar.selectbox("Pilih Area Coordinator (AC)", list_ac)

    if selected_ac != "Semua AC":
      df_filtered = df_filtered[df_filtered["Nama_AC"] == selected_ac]

    # --- 5. RINGKASAN METRIK UTAMA (KARTU NEON) ---
    total_value = df_filtered["Sales_Value"].sum()
    total_qty = df_filtered["Qty"].sum()

    col1, col2 = st.columns(2)

    with col1:
      st.markdown(
          f"""
            <div class="metric-card">
                <div class="metric-title">💰 Total Sales Value</div>
                <div class="metric-value">Rp {total_value:,.0f}</div>
            </div>
            """.replace(
              ",", "."
          ),
          unsafe_allow_html=True,
      )

    with col2:
      st.markdown(
          f"""
            <div class="metric-card">
                <div class="metric-title">📦 Total Qty Terjual</div>
                <div class="metric-value">{total_qty:,.0f}</div>
            </div>
            """,
          unsafe_allow_html=True,
      )

    st.markdown("<br>", unsafe_allow_html=True)

    # --- 6. GRAFIK TREN PENJUALAN (LINE CHART) ---
    st.subheader("📈 Tren Performa Penjualan Berdasarkan Toko")
    if not df_filtered.empty:
      chart_data = df_filtered.set_index("Nama_Toko")[["Sales_Value"]]
      st.line_chart(chart_data, color="#3b82f6")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- 7. PAPAN PERINGKAT TOKO (LEADERBOARD) ---
    st.subheader("🏆 Papan Peringkat Toko (Leaderboard)")

    df_toko = (
        df_filtered.groupby(["ID_Toko", "Nama_Toko", "Nama_AC", "Regional_Head"])
        .agg({"Sales_Value": "sum", "Qty": "sum"})
        .reset_index()
    )

    df_toko = df_toko.sort_values(by="Sales_Value", ascending=False).reset_index(
        drop=True
    )


    def tambah_peringkat_dan_lencana(row):
      idx = row.name
      if idx == 0:
        return "🥇 Juara 1"
      elif idx == 1:
        return "🥈 Juara 2"
      elif idx == 2:
        return "🥉 Juara 3"
      else:
        return f"Level {idx + 1}"


    if not df_toko.empty:
      df_toko["Peringkat"] = df_toko.apply(
          tambah_peringkat_dan_lencana, axis=1
      )

      df_toko = df_toko[[
          "Peringkat",
          "ID_Toko",
          "Nama_Toko",
          "Nama_AC",
          "Regional_Head",
          "Sales_Value",
          "Qty",
      ]]

      st.dataframe(df_toko, use_container_width=True, hide_index=True)
    else:
      st.info("Tidak ada data untuk filter yang dipilih.")

  else:
    st.warning("Google Spreadsheet Anda terdeteksi kosong.")

except Exception as e:
  st.error(
      f"Gagal memuat data. Pastikan format tabel di Google Sheets sudah sesuai. Error: {e}"
  )
