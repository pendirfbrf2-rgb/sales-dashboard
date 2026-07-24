import pandas as pd
import streamlit as st
import gspread

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Sales Command Center",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Judul Utama Dashboard
st.title("🚀 Real-Time Sales Command Center")
st.markdown(
    "Pantau performa penjualan *Value* dan *Qty* secara *real-time* dari level"
    " Toko, AC, hingga RH."
)
st.divider()


# --- 2. Koneksi & Ambil Data dari Google Sheets (Gspread) ---
@st.cache_data(ttl=60)  # Data otomatis di-refresh setiap 60 detik
def load_data_from_gspread():
  # Mengambil kredensial dari secrets Streamlit Cloud
  creds_dict = dict(st.secrets["gcp_service_account"])
  gc = gspread.service_account_from_dict(creds_dict)

  # Sesuaikan dengan Judul File Google Spreadsheet Anda
  sh = gc.open("Nama_File_Google_Sheets_Anda")
  worksheet = sh.get_worksheet(0)  # Mengambil tab pertama

  data = worksheet.get_all_records()
  df = pd.DataFrame(data)
  return df


try:
  df_transaksi = load_data_from_gspread()

  if not df_transaksi.empty:

    # --- 3. SIDEBAR: FILTER WILAYAH ---
    st.sidebar.header("🔍 Saring Wilayah")

    # Filter Regional Head (RH)
    list_rh = ["Semua RH"] + sorted(
        df_transaksi["Regional_Head"].dropna().unique().tolist()
    )
    selected_rh = st.sidebar.selectbox("Pilih Regional Head (RH)", list_rh)

    if selected_rh != "Semua RH":
      df_filtered = df_transaksi[df_transaksi["Regional_Head"] == selected_rh]
    else:
      df_filtered = df_transaksi.copy()

    # Filter Area Coordinator (AC)
    list_ac = ["Semua AC"] + sorted(
        df_filtered["Nama_AC"].dropna().unique().tolist()
    )
    selected_ac = st.sidebar.selectbox("Pilih Area Coordinator (AC)", list_ac)

    if selected_ac != "Semua AC":
      df_filtered = df_filtered[df_filtered["Nama_AC"] == selected_ac]

    # --- 4. RINGKASAN METRIK UTAMA (TOP LEVEL) ---
    total_value = df_filtered["Sales_Value"].sum()
    total_qty = df_filtered["Qty"].sum()

    col1, col2 = st.columns(2)
    col1.metric(
        label="💰 Total Sales Value",
        value=f"Rp {total_value:,.0f}".replace(",", "."),
    )
    col2.metric(label="📦 Total Qty Terjual", value=f"{total_qty:,.0f}")

    st.markdown("")

    # --- 5. PAPAN PERINGKAT TOKO (LEADERBOARD) ---
    st.subheader("🏆 Papan Peringkat Toko (Leaderboard)")

    # Agregasi data per Toko
    df_toko = (
        df_filtered.groupby(["ID_Toko", "Nama_Toko", "Nama_AC", "Regional_Head"])
        .agg({"Sales_Value": "sum", "Qty": "sum"})
        .reset_index()
    )

    # Urutkan dari sales value terbesar ke terkecil
    df_toko = df_toko.sort_values(by="Sales_Value", ascending=False).reset_index(
        drop=True
    )


    # Fungsi penambah lencana gamifikasi di tabel
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

      # Atur ulang urutan kolom agar Peringkat di depan
      df_toko = df_toko[[
          "Peringkat",
          "ID_Toko",
          "Nama_Toko",
          "Nama_AC",
          "Regional_Head",
          "Sales_Value",
          "Qty",
      ]]

      # Tampilkan tabel interaktif di web
      st.dataframe(df_toko, use_container_width=True, hide_index=True)
    else:
      st.info("Tidak ada data untuk filter yang dipilih.")

  else:
    st.warning("Google Spreadsheet Anda terdeteksi kosong.")

except Exception as e:
    st.error(
        f"Gagal memuat data. Pastikan nama file Google Sheets di kode sudah"
        f" sesuai dan *sharing* email sudah benar. Error: {e}"
    )
