import pandas as pd
import streamlit as st

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Sales Command Center",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- 2. TAMPILAN MODERN COMMAND CENTER ---
st.markdown(
    """
    <style>
    .stApp { background-color: #07090e; color: #c9d1d9; }
    .card-green { background: linear-gradient(135deg, #062314 0%, #0d1b12 100%); border: 1px solid #10b981; padding: 15px; border-radius: 12px; height: 130px; display: flex; flex-direction: column; justify-content: space-between; text-align: center; }
    .card-yellow { background: linear-gradient(135deg, #272106 0%, #1b190d 100%); border: 1px solid #f59e0b; padding: 15px; border-radius: 12px; height: 130px; display: flex; flex-direction: column; justify-content: space-between; text-align: center; }
    .card-title { color: #94a3b8; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 5px; }
    .card-section { font-size: 11px; color: #94a3b8; margin: 2px 0; }
    .card-val { font-weight: bold; color: #ffffff; font-size: 12px; }
    .card-footer { border-top: 1px solid rgba(255,255,255,0.1); padding-top: 5px; font-size: 11px; color: #94a3b8; display: flex; justify-content: center; gap: 6px; }
    .card-pct { font-weight: bold; color: #10b981; font-size: 12px; }
    .panel-box { background-color: #0d1117; border: 1px solid #21262d; padding: 20px; border-radius: 12px; margin-bottom: 20px; }
    h1, h2, h3, h4 { color: #f0f6fc !important; }
    [data-testid="stSidebar"] { background-color: #030407; border-right: 1px solid #21262d; }
    </style>
    """,
    unsafe_allow_html=True,
)


# --- 3. PEMBACAAN DATA PRESISI SESUAI PERMINTAAN ---
def load_data():
  try:
    df = pd.read_csv("data_sales.csv", header=0, on_bad_lines="skip")
    df.columns = [str(c).strip() for c in df.columns]

    # Pemetaan kolom persis sesuai struktur yang Anda tetapkan
    rename_map = {}
    for col in df.columns:
      c_low = col.lower()
      if "target_sales" in c_low or "targetsles" in c_low:
        rename_map[col] = "Target_Sales"
      elif "target_qty" in c_low or "targetqty" in c_low:
        rename_map[col] = "Target_Qty"
      elif "sales_value" in c_low or c_low == "sales":
        rename_map[col] = "Sales_Value"
      elif "qty" in c_low:
        rename_map[col] = "Qty"
      elif "nama_toko" in c_low:
        rename_map[col] = "Nama_Toko"
      elif "nama_ac" in c_low:
        rename_map[col] = "Nama_AC"
      elif "regional_head" in c_low:
        rename_map[col] = "Regional_Head"
      elif "id_toko" in c_low:
        rename_map[col] = "ID_Toko"

    df = df.rename(columns=rename_map)

    # Membersihkan format angka dari simbol mata uang atau pemisah
    for col in ["Sales_Value", "Qty", "Target_Sales", "Target_Qty"]:
      if col in df.columns:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace("Rp", "", regex=False)
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
            .str.replace(r"[^\d.-]", "", regex=True)
        )
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df
  except Exception:
    return pd.DataFrame()


df_transaksi = load_data()

if not df_transaksi.empty:
  st.markdown("### 🚀 Salesperson Performance & Regional Command Center")
  st.divider()

  # --- SIDEBAR FILTER WILAYAH ---
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

  # --- KALKULASI DATA ---
  total_sales = df_filtered["Sales_Value"].sum()
  total_qty = df_filtered["Qty"].sum()
  total_target_sales = (
      df_filtered["Target_Sales"].sum()
      if "Target_Sales" in df_filtered.columns
      else 0
  )
  total_target_qty = (
      df_filtered["Target_Qty"].sum()
      if "Target_Qty" in df_filtered.columns
      else 0
  )

  pct_sales = (
      (total_sales / total_target_sales) * 100 if total_target_sales > 0 else 0
  )
  pct_qty = (total_qty / total_target_qty) * 100 if total_target_qty > 0 else 0

  fmt_sales = f"Rp {total_sales:,.0f}".replace(",", ".")
  fmt_tgt_sales = f"Rp {total_target_sales:,.0f}".replace(",", ".")
  fmt_qty = f"{total_qty:,.0f}"
  fmt_tgt_qty = f"{total_target_qty:,.0f}"

  # --- KARTU METRIK UTAMA ---
  col1, col2 = st.columns(2)

  with col1:
    st.markdown(
        f"""
        <div class="card-green">
            <div class="card-title">Total Sales Performance</div>
            <div>
                <div class="card-section">Target: <span class="card-val">{fmt_tgt_sales}</span></div>
                <div class="card-section">Actual: <span class="card-val">{fmt_sales}</span></div>
            </div>
            <div class="card-footer"><span>Achievement:</span><span class="card-pct">{pct_sales:.1f}%</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

  with col2:
    st.markdown(
        f"""
        <div class="card-yellow">
            <div class="card-title">Total Volume Performance</div>
            <div>
                <div class="card-section">Target: <span class="card-val">{fmt_tgt_qty}</span></div>
                <div class="card-section">Actual: <span class="card-val">{fmt_qty}</span></div>
            </div>
            <div class="card-footer"><span>Achievement:</span><span class="card-pct">{pct_qty:.1f}%</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

  st.markdown("<br>", unsafe_allow_html=True)

  # --- TABEL LEADERBOARD TOKO DENGAN LENCANA ---
  st.markdown(
      "<div class='panel-box'><h4>📋 Detail Papan Peringkat Toko"
      " (Leaderboard)</h4>",
      unsafe_allow_html=True,
  )
  df_toko = df_filtered.sort_values(by="Sales_Value", ascending=False).reset_index(
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
    st.dataframe(df_toko, use_container_width=True, hide_index=True)
  else:
    st.info("Data tidak ditemukan.")
  st.markdown("</div>", unsafe_allow_html=True)
else:
  st.warning("File CSV data terdeteksi kosong.")
