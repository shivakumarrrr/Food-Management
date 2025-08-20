import pandas as pd
import streamlit as st
import altair as alt
from queries import queries, run_query

# ------------------ CUSTOM FONT & CSS ------------------
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap" rel="stylesheet">

    <style>
    /* Force Poppins globally */
    html, body, [class*="css"], .stApp, .stTextInput, .stSelectbox, .stButton, .stDataFrame, .stMarkdown, .stTabs, .stTable {
        font-family: 'Poppins', sans-serif !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] .stSelectbox, 
    [data-testid="stSidebar"] .stTextInput,
    [data-testid="stSidebar"] button {
        color: #000000 !important;
        font-family: 'Poppins', sans-serif !important;
    }

    /* Main body */
    .stApp {
        background-color: #000000 !important;
        color: #FFFFFF !important;
    }

    /* Headings, titles, markdown text */
    .stMarkdown, .stText, .stHeader, .stSubheader, .stTitle {
        color: #FFFFFF !important;
        font-family: 'Poppins', sans-serif !important;
    }

    /* DataFrames / tables */
    .stDataFrame, .stTable {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        font-family: 'Poppins', sans-serif !important;
    }

    /* Altair chart tooltips */
    .vega-tooltip {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        font-family: 'Poppins', sans-serif !important;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------ CONFIG ------------------
st.set_page_config(page_title="Food Connect Portal", layout="wide")

# ------------------ UTILITIES ------------------
def download_link_from_df(df: pd.DataFrame, filename: str):
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", data=csv, file_name=filename, mime="text/csv")

# ------------------ SIDEBAR ------------------
with st.sidebar:
    st.markdown("<h2 style='color:#000000;'>Filters</h2>", unsafe_allow_html=True)
    # Load initial data for filter options
    df_providers = run_query("SELECT * FROM providers;")
    df_food_listings = run_query("SELECT * FROM food_listings;")
    df_claims = run_query("SELECT * FROM claims;")
    city = st.selectbox("City", ["(All)"] + sorted(df_providers["city"].dropna().unique()))
    food_type = st.selectbox("Food Type", ["(All)"] + sorted(df_food_listings["food_type"].dropna().unique()))
    meal_type = st.selectbox("Meal Type", ["(All)"] + sorted(df_food_listings["meal_type"].dropna().unique()))
    claim_status = st.selectbox("Claim Status", ["(All)"] + sorted(df_claims["status"].dropna().unique()))

    # Helper for filter values
    def null_if_all(v):
        return None if v in (None, "", "(All)") else v

    filters = {
        "city": null_if_all(city),
        "food_type": null_if_all(food_type),
        "meal_type": null_if_all(meal_type),
        "claim_status": null_if_all(claim_status),
    }

# ------------------ TABS ------------------
tabs = st.tabs(["Dashboard", "Results & Reports"])

# ================== DASHBOARD ==================
with tabs[0]:
    st.markdown("<h2 style='color:#FFFFFF;'>📊 Dashboard Overview</h2>", unsafe_allow_html=True)

    # Top Cities by Providers
    st.markdown("### Top Cities by Providers")
    df_city = run_query(queries["Top Cities by Providers"])
    if not df_city.empty:
        chart = alt.Chart(df_city).mark_bar().encode(
            x=alt.X("city:N", sort="-y"),
            y="provider_count:Q",
            tooltip=list(df_city.columns)
        ).properties(height=350)
        st.altair_chart(chart, use_container_width=True)
        st.dataframe(df_city)
        download_link_from_df(df_city, "top_cities.csv")

    # Claims by Status
    st.markdown("### Claims by Status")
    df_status = run_query(queries["Claims by Status"])
    if not df_status.empty:
        pie = alt.Chart(df_status).mark_arc(innerRadius=60).encode(
            theta="total:Q",
            color="status:N",
            tooltip=list(df_status.columns)
        )
        st.altair_chart(pie, use_container_width=True)
        st.dataframe(df_status)
        download_link_from_df(df_status, "claims_status.csv")

    # Top 10 Providers by Food Quantity
    st.markdown("### Top 10 Providers by Food Quantity")
    df_top_providers = run_query(queries["Top 10 Providers by Food Quantity"])
    st.dataframe(df_top_providers, use_container_width=True)
    download_link_from_df(df_top_providers, "top_providers_quantity.csv")

    # Total Claims per Provider
    st.markdown("### Total Claims per Provider")
    df_claims_provider = run_query(queries["Total Claims per Provider"])
    st.dataframe(df_claims_provider, use_container_width=True)
    download_link_from_df(df_claims_provider, "claims_per_provider.csv")

# ================== RESULTS & REPORTS ==================
with tabs[1]:
    st.markdown("<h2 style='color:#FFFFFF;'>📄 Results & Reports</h2>", unsafe_allow_html=True)
    query_choice = st.selectbox("Select a Query", list(queries.keys()))
    sql = queries[query_choice]

   

conditions = []

if filters["city"]:
    conditions.append(f"p.city = '{filters['city']}'")
if filters["food_type"]:
    conditions.append(f"f.food_type = '{filters['food_type']}'")
if filters["meal_type"]:
    conditions.append(f"f.meal_type = '{filters['meal_type']}'")
if filters["claim_status"]:
    conditions.append(f"c.status = '{filters['claim_status']}'")

# Insert WHERE before GROUP BY or ORDER BY
if conditions:
    sql_upper = sql.upper()
    if "WHERE" not in sql_upper:
        if "GROUP BY" in sql_upper:
            sql = sql.replace("GROUP BY", f"WHERE {' AND '.join(conditions)} GROUP BY")
        elif "ORDER BY" in sql_upper:
            sql = sql.replace("ORDER BY", f"WHERE {' AND '.join(conditions)} ORDER BY")
        else:
            sql = sql.strip().rstrip(";") + f" WHERE {' AND '.join(conditions)};"
    else:
        sql = sql.replace("WHERE", f"WHERE {' AND '.join(conditions)} AND ")

df_result = run_query(sql)
if not df_result.empty:
    st.dataframe(df_result, use_container_width=True)
    download_link_from_df(df_result, f"{query_choice}.csv")
else:
    st.info("No data found for the selected query.")
