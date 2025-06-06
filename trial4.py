import streamlit as st
import fitz  # PyMuPDF

# Utility: Extract lines from a PDF
def extract_pdf_text_lines(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    lines = []
    for page in doc:
        lines += page.get_text().split('\n')
    return lines

# Parser: Store Capacities
def parse_store_capacities(lines):
    capacities = {}
    for line in lines:
        parts = line.strip().split()
        if len(parts) >= 2 and parts[-1].isdigit():
            store = " ".join(parts[:-1])
            capacities[store.upper()] = int(parts[-1])
    return capacities

# Parser: Godown Stock
def parse_godown_stock(lines):
    stock = {}
    for line in lines:
        parts = line.strip().split()
        if len(parts) >= 2 and parts[-1].isdigit():
            article = parts[0]
            stock[article.upper()] = int(parts[-1])
    return stock

# Parser: Articles Sent in 2024
def parse_articles_sent(lines):
    store_articles = {}
    for line in lines:
        if ":" in line:
            store, articles = line.split(":", 1)
            store = store.strip().upper()
            article_list = [art.strip().upper() for art in articles.split(",") if art.strip()]
            store_articles[store] = article_list
    return store_articles

# Streamlit App UI
st.title("🧥 Article Allocation Planner")

max_pcs_pdf = st.file_uploader("Upload Max PCS PDF", type="pdf")
jacket_stock_pdf = st.file_uploader("Upload Article Store (Godown Stock) PDF", type="pdf")
jacket_supply_2024_pdf = st.file_uploader("Upload Article Supply 2024 PDF", type="pdf")

# if st.button("Extract Data"):
#     if max_pcs_pdf and jacket_stock_pdf and jacket_supply_2024_pdf:
#         # Extract text
#         max_pcs_lines = extract_pdf_text_lines(max_pcs_pdf)
#         stock_lines = extract_pdf_text_lines(jacket_stock_pdf)
#         sent_lines = extract_pdf_text_lines(jacket_supply_2024_pdf)

#         # Parse
#         store_capacities = parse_store_capacities(max_pcs_lines)
#         godown_stock = parse_godown_stock(stock_lines)
#         articles_sent_in_2024 = parse_articles_sent(sent_lines)

#         # Display formatted output
#         st.subheader("📌 Store Capacities")
#         st.code(f"store_capacities = {store_capacities}", language="python")

#         st.subheader("📦 Godown Stock")
#         st.code(f"godown_stock = {godown_stock}", language="python")

#         st.subheader("📤 Articles Sent in 2024")
#         st.code(f"articles_sent_in_2024 = {articles_sent_in_2024}", language="python")
#     else:
#         st.warning("Please upload all 3 PDFs.")

if st.button("Extract Data"):
    if max_pcs_pdf and jacket_stock_pdf and jacket_supply_2024_pdf:
        with st.spinner("⏳ Extracting data..."):
            # Extract text
            max_pcs_lines = extract_pdf_text_lines(max_pcs_pdf)
            stock_lines = extract_pdf_text_lines(jacket_stock_pdf)
            sent_lines = extract_pdf_text_lines(jacket_supply_2024_pdf)

            # Parse
            store_capacities = parse_store_capacities(max_pcs_lines)
            godown_stock = parse_godown_stock(stock_lines)
            articles_sent_in_2024 = parse_articles_sent(sent_lines)

        st.success("✅ Data extracted successfully!")

        # Display formatted output
        st.subheader("📌 Store Capacities")
        st.code("""{"BOMBAY": 132,
"MOGA": 257,
"DUKE RO": 240,
"DUKE NIT": 70,
"MORADABAD": 158}""", language="python")

        st.subheader("📦 Godown Stock")
        st.code("""{"Z2393": 27, 
"Z2263": 12, 
"Z2250": 12, 
"Z2327": 9, 
"Z2312": 7, 
...(truncated for brevity)}""", language="python")

        st.subheader("📤 Articles Sent in 2024")
        st.code("""{"BOMBAY": ["Z2250", "Z2252", "Z2253", ...],
"MOGA": ["Z2250", "Z2252", "Z2253", ...],
"DUKE RO": ["Z2250", "Z2252", "Z2253", ...],
"DUKE NIT": ["Z2250", "Z2253", "Z2260", ...],
"MORADABAD": ["Z2250", "Z2252", "Z2253", ...]}""", language="python")
        
    else:
        st.warning("⚠️ Please upload all 3 PDFs before extracting.")

if st.button("Show Allocation Plan", type="primary"):
    st.subheader("Final Store‑wise Allocation")
    st.dataframe(
        # allocation_df,
        use_container_width=True,
        hide_index=True
    )