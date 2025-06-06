import streamlit as st
import pdfplumber
import pandas as pd
import logging

logging.getLogger("pdfminer").setLevel(logging.ERROR)

st.set_page_config(page_title="🧥 Jacket Allocation Data Extractor", layout="wide")

st.title("🧥 Jacket Allocation Data Extractor")

# ----------- 1. Upload PDFs -----------
st.header("📥 Upload Required PDFs")

stock_file = st.file_uploader("Upload '5_Jacket_Stock.pdf'", type=["pdf"])
supply_file = st.file_uploader("Upload '5_Jacket_Supply_24.pdf'", type=["pdf"])
max_file = st.file_uploader("Upload '5_Max_Pcs.pdf'", type=["pdf"])

# ----------- 2. Helper Functions -----------

def extract_stock_data(file):
    stock_entries = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            lines = page.extract_text().split('\n')
            for line in lines:
                parts = line.strip().split()
                if len(parts) == 2 and parts[1].isdigit():
                    stock_entries.append({
                        "article_number": parts[0],
                        "quantity_available": int(parts[1])
                    })
    return pd.DataFrame(stock_entries)

def extract_supply_data(file):
    supply_entries = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            lines = page.extract_text().split('\n')
            for line in lines:
                parts = line.strip().rsplit(" ", 2)
                if len(parts) == 3 and parts[2].isdigit():
                    supply_entries.append({
                        "store_location": parts[0],
                        "article_number": parts[1],
                        "quantity_supplied_2024": int(parts[2])
                    })
    return pd.DataFrame(supply_entries)

def extract_max_data(file):
    max_entries = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            lines = page.extract_text().split('\n')
            for line in lines:
                parts = line.strip().rsplit(" ", 1)
                if len(parts) == 2 and parts[1].isdigit():
                    max_entries.append({
                        "store_location": parts[0],
                        "max_quantity": int(parts[1])
                    })
    return pd.DataFrame(max_entries)

# ----------- 3. Extract & Display Data -----------
if stock_file and supply_file and max_file:
    df_stock = extract_stock_data(stock_file)
    df_supply = extract_supply_data(supply_file)
    df_max = extract_max_data(max_file)

    st.success("✅ PDFs successfully parsed!")

    st.subheader("✅ Jacket Stock Data")
    st.dataframe(df_stock)

    st.subheader("✅ Jacket Supply 2024 Data")
    st.dataframe(df_supply)

    st.subheader("✅ Max Quantity Per Store Data")
    st.dataframe(df_max)

    # Convert for logic
    store_capacities = dict(zip(df_max['store_location'], df_max['max_quantity']))
    godown_stock = dict(zip(df_stock['article_number'], df_stock['quantity_available']))
    articles_sent_in_2024 = (
        df_supply.groupby('store_location')['article_number']
        .apply(lambda x: sorted(list(set(x)))).to_dict()
    )

    # Show logic dictionaries
    st.subheader("📦 Godown Stock")
    st.json(dict(list(godown_stock.items())[:5]))

    st.subheader("📤 Articles Sent in 2024")
    # Show only first 5 stores and limit each store's articles to top 5
    short_articles_sent = {
        store: articles[:5]  # take only first 5 articles
        for store, articles in list(articles_sent_in_2024.items())[:5]  # only first 5 stores
    }
    st.json(short_articles_sent)

    st.subheader("🏬 Store Capacities")
    st.json(dict(list(store_capacities.items())[:5]))
else:
    st.info("👆 Please upload all three PDF files to proceed.")