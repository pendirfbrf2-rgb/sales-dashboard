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

# --- 2. CUSTOM CSS ---
st.markdown(
    """
    <style>
    .stApp { background-color: #07090e; color: #c9d1d9; }
    .card-green { background: linear-gradient(135deg, #062314 0%, #0d1b12 100%); border: 1px solid #10b981; padding: 10px 4px; border-radius: 12px; height: 135px; display: flex; flex-direction: column; justify-content: space-between; text-align: center; }
    .card-yellow { background: linear-gradient(135deg, #272106 0%, #1b190d 100%); border: 1px solid #f59e0b; padding: 10px 4px; border-radius: 12px; height: 135px; display: flex; flex-direction: column; justify-content: space-between; text-align: center; }
    .card-red { background: linear-gradient(135deg, #270606 0%, #1b0d0d 100%); border: 1px solid #ef4444; padding: 10px 4px; border-radius: 12px; height: 135px; display: flex; flex-direction: column; justify-content: space-between; text-align: center; }
    .card-blue { background: linear-gradient(135deg, #061a27 0%, #0d151b 100%); border: 1px solid #3b82f6; padding: 10px 4px; border-radius: 12px; height: 135px; display: flex; flex-direction: column; justify-content: space-between; text-align: center; }
    .card-title { color: #94a3b8; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 3px; }
    .card-section { font-size: 10px; color: #94a3b8; margin: 1px 0; }
    .card-val { font-weight: bold; color: #ffffff; font-size: 11px; }
    .card-footer { border-top: 1px solid rgba(255,255,255,0.1); padding-top: 3px; font-size: 10px; color: #94a3b8; display: flex; justify-content: center; gap: 4px; }
    .card-pct { font-weight: bold; color: #10b981; font-size: 11px; }
    .panel-box { background-color: #0d1117; border: 1px solid #21262d; padding: 20px; border-radius: 12px; margin-bottom: 20px; }
    .ac-item { padding: 4px 0px; border-bottom: 1px solid #161b22; }
    h1, h2, h3, h4 { color: #f0f6fc !important; }
    [data-testid="stSidebar"] { background-color: #030407; border-right: 1px solid #21262d; }
    </style>
    """,
    unsafe_allow_html=True,
)


# --- 3. AMBIL DATA LOKAL ---
@st.cache_data
def load_data():
  df = pd.read_csv("data_sales.csv", on_bad_lines="skip")
  df.columns = [str(c).strip() for c in df.columns]

  rename_map = {}
  for col in df.columns:
    col_lower = col.lower()
    if "sales_value" in col_lower or col_lower == "sales":
      rename_map[col] = "Sales_Value"
    elif "target_sales" in col_lower:
      rename_map[col] = "Target_Sales"
    elif "qty" in col_lower or col_lower == "volume":
      rename_map[col] = "Qty"
    elif "target_qty" in col_lower or "target_vol" in col_lower:
      rename_map[col] = "Target_Qty"
    elif "nama_toko" in col_lower or col_lower == "toko":
      rename_map[col] = "Nama_Toko"
    elif "nama_ac" in col_lower or col_lower == "ac":
      rename_map[col] = "Nama_AC"
    elif "regional_head" in col_lower or col_lower == "rh":
      rename_map[col] = "Regional_Head"

  df = df.rename(columns=rename_map)

  cols_to_clean = ["Sales_Value", "Qty", "Target_Sales", "Target_Qty"]
  for col in cols_to_clean:
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
    st.markdown("### 🚀 Salesperson Performance & Regional Command Center")
    st.divider()

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
        (total_sales / total_target_sales) * 100
        if total_target_sales > 0
        else 0
    )
    pct_qty = (
        (total_qty / total_target_qty) * 100 if total_target_qty > 0 else 0
    )

    formatted_sales = f"Rp {total_sales:,.0f}".replace(",", ".")
    formatted_target_sales = f"Rp {total_target_sales:,.0f}".replace(",", ".")
    formatted_avg = f"Rp {rata_rata_sales:,.0f}".replace(",", ".")
    formatted_qty = f"{total_qty:,.0f}"
    formatted_target_qty = f"{total_target_qty:,.0f}"

    col_main, col_side = st.columns([2.5, 1])

    with col_main:
      k1, k2, k3, k4, k5 = st.columns(5)

      k1.markdown(
          f"""
            <div class="card-green">
                <div class="card-title">Total Sales</div>
                <div>
                    <div class="card-section">Tgt: <span class="card-val">{formatted_target_sales}</span></div>
                    <div class="card-section">Act: <span class="card-val">{formatted_sales}</span></div>
                </div>
                <div class="card-footer"><span>Ach:</span><span class="card-pct">{pct_sales:.1f}%</span></div>
            </div>
            """,
          unsafe_allow_html=True,
      )

      k2.markdown(
          f"""
            <div class="card-green">
                <div class="card-title">Average Value</div>
                <div>
                    <div class="card-section">Tgt: <span class="card-val">Rp 90.0M</span></div>
                    <div class="card-section">Act: <span class="card-val">{formatted_avg}</span></div>
                </div>
                <div class="card-footer"><span>Ach:</span><span class="card-pct">115.0%</span></div>
            </div>
            """,
          unsafe_allow_html=True,
      )

      k3.markdown(
          f"""
            <div class="card-yellow">
                <div class="card-title">Total Volume</div>
                <div>
                    <div class="card-section">Tgt: <span class="card-val">{formatted_target_qty}</span></div>
                    <div class="card-section">Act: <span class="card-val">{formatted_qty}</span></div>
                </div>
                <div class="card-footer"><span>Ach:</span><span class="card-pct">{pct_qty:.1f}%</span></div>
            </div>
            """,
          unsafe_allow_html=True,
      )

      k4.markdown(
          """
            <div class="card-red">
                <div class="card-title">Target Vol</div>
                <div>
                    <div class="card-section">Tgt: <span class="card-val">100%</span></div>
                    <div class="card-section">Act: <span class="card-val">125%</span></div>
                </div>
                <div class="card-footer"><span>Ach:</span><span class="card-pct">125.0%</span></div>
            </div>
            """,
          unsafe_allow_html=True,
      )

      k5.markdown(
          """
            <div class="card-blue">
                <div class="card-title">SPD Index</div>
                <div>
                    <div class="card-section">Tgt: <span class="card-val">100%</span></div>
                    <div class="card-section">Act: <span class="card-val">145%</span></div>
                </div>
                <div class="card-footer"><span>Ach:</span><span class="card-pct">145.0%</span></div>
            </div>
            """,
          unsafe_allow_html=True,
      )

      st.markdown("<br>", unsafe_allow_html=True)

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
          "<div class='panel-box'><h4>🏆 Ranking Area Coordinator (AC)</h4>",
          unsafe_allow_html=True,
      )
      df_ac_leaderboard = (
          df_filtered.groupby("Nama_AC")["Sales_Value"].sum().reset_index()
      )
      df_ac_leaderboard = df_ac_leaderboard.sort_values(
          by="Sales_Value", ascending=False
      )

      for idx, row in df_ac_leaderboard.iterrows():
        val_str = f"Rp {row['Sales_Value']:,.0f}".replace(",", ".")
        st.markdown(
            f"""
                <div class="ac-item">
                    <div style="font-size: 12px; font-weight: bold; color: #f0f6fc;">{row['Nama_AC']}</div>
                    <div style="font-size: 11px; font-weight: bold; color: #10b981;">{val_str}</div>
                </div>
                """,
            unsafe_allow_html=True,
        )
      st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        "<div class='panel-box'><h4>📋 Detail Papan Peringkat Toko"
        " (Leaderboard)</h4>",
        unsafe_allow_html=True,
    )
    df_toko = (
        df_filtered.groupby(
            [
                col
                for col in [
                    "ID_Toko",
                    "Nama_Toko",
                    "Nama_AC",
                    "Regional_Head",
                    "Target_Sales",
                ]
                if col in df_filtered.columns
            ]
        )
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
      st.dataframe(df_toko, use_container_width=True, hide_index=True)
    else:
      st.info("Data tidak ditemukan.")
    st.markdown("</div>", unsafe_allow_html=True)
  else:
    st.warning("File CSV data terdeteksi kosong.")

except Exception as e:
  st.error(f"Gagal memuat data lokal. Error: {e}")
