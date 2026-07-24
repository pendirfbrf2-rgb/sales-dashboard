import pandas as pd
import plotly.express as px
import streamlit as st

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Sales Command Center",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- 2. CUSTOM CSS (TEMA FUTURISTIK / COMMAND CENTER) ---
st.markdown(
    """
    <style>
    .stApp { background-color: #07090e; color: #c9d1d9; }
    
    .card-green { background: linear-gradient(135deg, #062314 0%, #0d1b12 100%); border: 1px solid #10b981; padding: 14px 6px; border-radius: 12px; text-align: center; height: 110px; display: flex; flex-direction: column; justify-content: center; align-items: center; }
    .card-yellow { background: linear-gradient(135deg, #272106 0%, #1b190d 100%); border: 1px solid #f59e0b; padding: 14px 6px; border-radius: 12px; text-align: center; height: 110px; display: flex; flex-direction: column; justify-content: center; align-items: center; }
    .card-red { background: linear-gradient(135deg, #270606 0%, #1b0d0d 100%); border: 1px solid #ef4444; padding: 14px 6px; border-radius: 12px; text-align: center; height: 110px; display: flex; flex-direction: column; justify-content: center; align-items: center; }
    .card-blue { background: linear-gradient(135deg, #061a27 0%, #0d151b 100%); border: 1px solid #3b82f6; padding: 14px 6px; border-radius: 12px; text-align: center; height: 110px; display: flex; flex-direction: column; justify-content: center; align-items: center; }
    
    .card-title { color: #94a3b8; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }
    .card-value { color: #ffffff; font-size: 14px; font-weight: bold; white-space: nowrap; }
    
    .panel-box { background-color: #0d1117; border: 1px solid #21262d; padding: 20px; border-radius: 12px; margin-bottom: 20px; }
    h1, h2, h3, h4 { color: #f0f6fc !important; }
    [data-testid="stSidebar"] { background-color: #030407; border-right: 1px solid #21262d; }
    </style>
    """,
    unsafe_allow_html=True,
)


# --- 3. AMBIL DATA DARI GOOGLE SHEETS ---
@st.cache_data(ttl=300)
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
  with st.spinner("Memuat data command center..."):
    df_transaksi = load_data()

  if not df_transaksi.empty:
    st.markdown("### 🚀 Salesperson Performance & Regional Command Center")
    st.divider()

    # --- 4. SIDEBAR FILTER WILAYAH ---
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

    total_sales = df_filtered["Sales_Value"].sum()
    total_qty = df_filtered["Qty"].sum()
    rata_rata_sales = (
        df_filtered["Sales_Value"].mean() if not df_filtered.empty else 0
    )

    formatted_sales = f"Rp {total_sales:,.0f}".replace(",", ".")
    formatted_avg = f"Rp {rata_rata_sales:,.0f}".replace(",", ".")
    formatted_qty = f"{total_qty:,.0f}"

    # --- 5. TAMPILAN UTAMA GRID (KARTU KONTROL) ---
    col_main, col_side = st.columns([2.5, 1])

    with col_main:
      k1, k2, k3, k4, k5 = st.columns(5)
      k1.markdown(
          f'<div class="card-green"><div class="card-title">Total'
          f' Sales</div><div class="card-value">{formatted_sales}</div></div>',
          unsafe_allow_html=True,
      )
      k2.markdown(
          f'<div class="card-green"><div class="card-title">Average'
          f' Value</div><div class="card-value">{formatted_avg}</div></div>',
          unsafe_allow_html=True,
      )
      k3.markdown(
          f'<div class="card-yellow"><div class="card-title">Total'
          f' Volume</div><div class="card-value">{formatted_qty}</div></div>',
          unsafe_allow_html=True,
      )
      k4.markdown(
          '<div class="card-red"><div class="card-title">Target'
          ' Vol</div><div class="card-value">125%</div></div>',
          unsafe_allow_html=True,
      )
      k5.markdown(
          '<div class="card-blue"><div class="card-title">SPD'
          ' Index</div><div class="card-value">145%</div></div>',
          unsafe_allow_html=Thread_val := True,
      )

      st.markdown("<br>", unsafe_allow_html=True)

      # --- GRAFIK INTERAKTIF PLOTLY (SEMUA TOKO, GAYA DIGITAL/NEON) ---
      st.markdown(
          "<div class='panel-box'><h4>📊 Analisis Performa Seluruh Toko"
          " (Digital Command View)</h4>",
          unsafe_allow_html=True,
      )
      if not df_filtered.empty:
        df_chart = (
            df_filtered.groupby("Nama_Toko")["Sales_Value"]
            .sum()
            .reset_index()
            .sort_values(by="Sales_Value", ascending=False)
        )

        fig = px.bar(
            df_chart,
            x="Nama_Toko",
            y="Sales_Value",
            text_auto=".2s",
            color="Sales_Value",
            color_continuous_scale=[
                (0, "#065f46"),
                (0.5, "#10b981"),
                (1, "#34d399"),
            ],
        )

        fig.update_layout(
            plot_bgcolor="#0d1117",
            paper_bgcolor="#0d1117",
            font_color="#c9d1d9",
            xaxis=dict(
                title="", tickangle=-45, showgrid=False, color="#8b949e"
            ),
            yaxis=dict(
                title="Sales Value (Rp)", showgrid=True, gridcolor="#21262d"
            ),
            margin=dict(l=10, r=10, t=10, b=80),
            coloraxis_showscale=False,
        )

        st.plotly_chart(fig, use_container_width=True)

      st.markdown("</div>", unsafe_allow_html=True)

    with col_side:
      st.markdown(
          "<div class='panel-box'><h4>🏆 Top 5 Toko</h4>", unsafe_allow_html=True
      )
      df_leaderboard = (
          df_filtered.groupby(["Nama_AC", "Nama_Toko"])["Sales_Value"]
          .sum()
          .reset_index()
      )
      df_leaderboard = df_leaderboard.sort_values(
          by="Sales_Value", ascending=False
      ).head(5)

      for idx, row in df_leaderboard.iterrows():
        val_str = f"Rp {row['Sales_Value']:,.0f}".replace(",", ".")
        st.markdown(
            f"**{row['Nama_Toko']}**<br><span style='color: #8b949e; font-size:"
            f" 11px;'>AC: {row['Nama_AC']}</span><br><span style='color:"
            f" #10b981; font-weight: bold;'>{val_str}</span>",
            unsafe_allow_html=True,
        )
        st.divider()
      st.markdown("</div>", unsafe_allow_html=True)

    # --- 6. TABEL RINCIAN LENGKAP ---
    st.markdown(
        "<div class='panel-box'><h4>📋 Detail Papan Peringkat Toko"
        " (Leaderboard)</h4>",
        unsafe_allow_html=True,
    )
    df_toko = (
        df_filtered.groupby(["ID_Toko", "Nama_Toko", "Nama_AC", "Regional_Head"])
        .agg({"Sales_Value": "sum", "Qty": "sum"})
        .reset_index()
    )
    df_toko = df_toko.sort_values(by="Sales_Value", ascending=False).reset_index(
        drop=True
    )


    def tambah_lencana(row):
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
      df_toko["Peringkat"] = df_toko.apply(tambah_lencana, axis=1)
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
    st.markdown("</div>", unsafe_allow_html=True)
  else:
    st.warning("Google Spreadsheet Anda terdeteksi kosong.")

except Exception as e:
  st.error(f"Gagal memuat data. Error: {e}")
