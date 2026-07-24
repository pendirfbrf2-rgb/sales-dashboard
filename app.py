import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Sales Command Center", page_icon="🚀", layout="wide"
)

st.markdown(
    """
    <style>
    .stApp { background-color: #07090e; color: #c9d1d9; }
    h1, h2, h3 { color: #f0f6fc !important; }
    </style>
    """,
    unsafe_allow_html=True,
)


def load_data():
  try:
    df = pd.read_csv("data_sales.csv", header=0, on_bad_lines="skip")
    # Bersihkan seluruh nama kolom dari spasi berlebih
    df.columns = [str(c).strip() for c in df.columns]

    rename_map = {}
    for col in df.columns:
      c_low = col.lower().replace(" ", "_")
      # Deteksi target sales secara fleksibel
      if "target" in c_low and ("sales" in c_low or "val" in c_low):
        rename_map[col] = "Target_Sales"
      elif "target" in c_low and ("qty" in c_low or "vol" in c_low):
        rename_map[col] = "Target_Qty"
      elif "sales" in c_low or c_low == "sales_value":
        rename_map[col] = "Sales_Value"
      elif "qty" in c_low or "volume" in c_low:
        rename_map[col] = "Qty"
      elif "nama_toko" in c_low or c_low == "toko":
        rename_map[col] = "Nama_Toko"
      elif "nama_ac" in c_low or c_low == "ac":
        rename_map[col] = "Nama_AC"
      elif "regional_head" in c_low or c_low == "rh":
        rename_map[col] = "Regional_Head"

    df = df.rename(columns=rename_map)

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
  st.title("🚀 Sales Command Center")
  st.divider()

  # Sidebar Filter
  st.sidebar.header("Filter Wilayah")
  rh_list = ["Semua RH"] + sorted(
      df_transaksi["Regional_Head"].dropna().unique().tolist()
  )
  sel_rh = st.sidebar.selectbox("Regional Head", rh_list)

  df_f = (
      df_transaksi
      if sel_rh == "Semua RH"
      else df_transaksi[df_transaksi["Regional_Head"] == sel_rh]
  )

  ac_list = ["Semua AC"] + sorted(df_f["Nama_AC"].dropna().unique().tolist())
  sel_ac = st.sidebar.selectbox("Area Coordinator", ac_list)

  if sel_ac != "Semua AC":
    df_f = df_f[df_f["Nama_AC"] == sel_ac]

  # Metrik Angka
  tot_sales = df_f["Sales_Value"].sum()
  tot_tgt_sales = (
      df_f["Target_Sales"].sum() if "Target_Sales" in df_f.columns else 0
  )
  tot_qty = df_f["Qty"].sum()
  tot_tgt_qty = (
      df_f["Target_Qty"].sum() if "Target_Qty" in df_f.columns else 0
  )

  ach_sales = (tot_sales / tot_tgt_sales * 100) if tot_tgt_sales > 0 else 0
  ach_qty = (tot_qty / tot_tgt_qty * 100) if tot_tgt_qty > 0 else 0

  c1, c2 = st.columns(2)
  c1.metric(
      "Total Sales (Actual vs Target)",
      f"Rp {tot_sales:,.0f}".replace(",", "."),
      f"Target: Rp {tot_tgt_sales:,.0f} ({ach_sales:.1f}%)".replace(",", "."),
  )
  c2.metric(
      "Total Volume (Actual vs Target)",
      f"{tot_qty:,.0f}".replace(",", "."),
      f"Target: {tot_tgt_qty:,.0f} ({ach_qty:.1f}%)".replace(",", "."),
  )

  st.subheader("📋 Papan Peringkat Toko")
  st.dataframe(df_f, use_container_width=True)
else:
  st.warning(
      "File data_sales.csv belum terbaca dengan benar atau format kolomnya"
      " kosong."
  )
