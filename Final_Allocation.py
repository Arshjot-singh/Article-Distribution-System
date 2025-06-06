from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
import streamlit as st
import fitz  # PyMuPDF
import pdfplumber
import pandas as pd
import logging
logging.getLogger("pdfminer").setLevel(logging.ERROR)

# Page configuration
st.set_page_config(page_title="🧥 Article Allocation Planner", layout="wide")

# Utility: Extract lines from a PDF


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


# Initialize session state for page navigation
if 'show_allocation' not in st.session_state:
    st.session_state.show_allocation = False

# CODE 1 - Initial Interface
if not st.session_state.show_allocation:
    # Streamlit App UI
    st.title("🧥 Article Allocation Planner")

    jacket_stock_pdf = st.file_uploader(
        "Upload Article Stock (Godown Stock) PDF", type="pdf")
    jacket_supply_2024_pdf = st.file_uploader(
        "Upload Article Supply 2024 PDF", type="pdf")
    max_pcs_pdf = st.file_uploader("Upload Max Pcs PDF", type="pdf")

    if st.button("Extract Data"):
        if jacket_stock_pdf and jacket_supply_2024_pdf and max_pcs_pdf:
            df_stock = extract_stock_data(jacket_stock_pdf)
            df_supply = extract_supply_data(jacket_supply_2024_pdf)
            df_max = extract_max_data(max_pcs_pdf)

            st.success("✅ PDFs successfully parsed!")

            st.subheader("✅ Jacket Stock Data")
            st.dataframe(df_stock)

            st.subheader("✅ Jacket Supply 2024 Data")
            st.dataframe(df_supply)

            st.subheader("✅ Max Quantity Per Store Data")
            st.dataframe(df_max)

            st.success("✅ Data extracted successfully!")

            # Convert for logic
            store_capacities = dict(
                zip(df_max['store_location'], df_max['max_quantity']))
            godown_stock = dict(
                zip(df_stock['article_number'], df_stock['quantity_available']))
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
                # only first 5 stores
                for store, articles in list(articles_sent_in_2024.items())[:5]
            }
            st.json(short_articles_sent)

            st.subheader("🏬 Store Capacities")
            st.json(dict(list(store_capacities.items())[:5]))

            # Save extracted data in session_state for use in Code 2
            st.session_state.df_stock = df_stock
            st.session_state.df_supply = df_supply
            st.session_state.df_max = df_max

            st.session_state.store_capacities = store_capacities
            st.session_state.godown_stock = godown_stock
            st.session_state.articles_sent_in_2024 = articles_sent_in_2024

        else:
            st.warning("⚠️ Please upload all 3 PDFs before extracting.")

    all_pdfs_uploaded = max_pcs_pdf and jacket_stock_pdf and jacket_supply_2024_pdf

    if st.button("Show Allocation Plan", type="primary", disabled=not all_pdfs_uploaded):
        st.session_state.show_allocation = True
        st.rerun()

    # Show helper text when button is disabled
    if not all_pdfs_uploaded:
        st.caption("📋 Upload all 3 PDFs to enable the allocation plan")


# CODE 2 - Allocation Plan Interface
else:
    # API Key input in sidebar
    with st.sidebar:
        st.title("API Configuration")
        api_key = st.text_input(
            "Enter OpenAI API", type="password")
        backup_api_key = st.text_input("Enter Anthropic API Key (Optional)", type="password")
        st.markdown("---")
        st.markdown("### About This App")
        st.info(
            "This application helps allocate articles to different stores based on "
            "current godown stock and previous allocation history. It uses OpenAI API or Anthropic API "
            "to provide AI-powered insights about the allocation strategy."
        )

        # Back button
        if st.button("← Back to Data Upload"):
            st.session_state.show_allocation = False
            st.rerun()

    # Main content
    st.title("🧥 Article Allocation Planner")

    store_capacities = st.session_state.get("store_capacities")
    godown_stock = st.session_state.get("godown_stock")
    articles_sent_in_2024 = st.session_state.get("articles_sent_in_2024")

    # Check for missing values
    if store_capacities is None or godown_stock is None or articles_sent_in_2024 is None:
        st.error(
            "Required data not found. Please upload the PDFs in the first interface before using this allocation page.")
        st.stop()

    # Calculate available articles for each store
    available_articles = {}
    for store in store_capacities:
        available_articles[store] = [article for article in godown_stock
                                     if article not in articles_sent_in_2024[store] and godown_stock[article] > 0]

    # Function to create optimal allocation based on stock availability
    def create_allocation(store):
        available = available_articles[store]
        max_capacity = store_capacities[store]

        # Sort by quantity available (highest first)
        sorted_articles = sorted(
            available, key=lambda x: godown_stock[x], reverse=True)

        allocation = []
        total_allocated = 0

        # Allocate articles respecting capacity constraints
        for article in sorted_articles:
            if total_allocated < max_capacity and godown_stock[article] > 0:
                # Allocate one piece of this article
                allocation.append({
                    "article": article,
                    "quantity": 1,
                    "available_in_godown": godown_stock[article]
                })
                total_allocated += 1

                if total_allocated >= max_capacity:
                    break

        capacity_percentage = (total_allocated / max_capacity * 100)

        return {
            "allocation": allocation,
            "total_allocated": total_allocated,
            "capacity_percentage": round(capacity_percentage, 1)
        }

    # Create columns for store selection and info
    col1, col2 = st.columns([1, 2])

    st.markdown(
        """
        <style>
        /* closed dropdown */
        div[data-baseweb="select"] > div {
            background-color: #102D48;   /* navy  */
            color: #ffffff;              /* white text */
        }
        /* open menu background */
        div[data-baseweb="popover"] ul {
            background-color: #102D48;
        }
        /* option hover colour */
        div[data-baseweb="popover"] li:hover {
            background-color: #0055aa !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    with col1:
        # Store selection
        selected_store = st.selectbox(
            "Select Store", options=list(store_capacities.keys()))

        # Calculate allocation for selected store
        store_allocation = create_allocation(selected_store)

        # Display store information
        st.subheader("Store Information")
        st.metric("Maximum Capacity",
                  f"{store_capacities[selected_store]} pcs")
        st.metric(
            "Allocated", f"{store_allocation['total_allocated']} pcs ({store_allocation['capacity_percentage']}%)")
        st.metric("Available Articles",
                  f"{len(available_articles[selected_store])} (not sent in 2024)")

    with col2:
        # LangChain integration for AI insights (if API key is provided)
        if api_key:
            try:
                st.subheader("AI-Powered Allocation Insights")
                with st.spinner("Generating insights..."):
                    # Initialize LangChain with the OpenAI API
                    llm = ChatOpenAI(
                        model="gpt-4o-mini",
                        temperature=0,
                        openai_api_key=api_key
                    )

                    # Create prompt template
                    prompt_template = PromptTemplate(
                        input_variables=["store", "capacity",
                                         "allocated", "percentage"],
                        template="""
                        You are a retail inventory management expert. Analyze the following allocation data for {store} store:
                        - Maximum capacity: {capacity} pieces
                        - Currently allocated: {allocated} pieces ({percentage}% of capacity)
                        
                        Provide 3 concise bullet points of insights or recommendations to optimize this jacket allocation.
                        Focus on inventory turnover, store-specific strategy, and efficiency.
                        """
                    )

                    # Create chain
                    chain = LLMChain(llm=llm, prompt=prompt_template)

                    # Run chain
                    response = chain.invoke({
                        "store": selected_store,
                        "capacity": store_capacities[selected_store],
                        "allocated": store_allocation["total_allocated"],
                        "percentage": store_allocation["capacity_percentage"]
                    })

                    # Display insights
                    st.write(response["text"])

            except Exception as e:
                st.error(f"Error connecting to OpenAI API: {str(e)}")
        else:
            st.info(
                "Enter your OpenAI API/ Anthropic key in the sidebar to get AI-powered allocation insights.")

        # Allocation summary
        st.subheader("Allocation Summary")
        st.markdown(f"""
        This allocation plan includes articles that:
        - Are currently available in the godown
        - Were NOT sent to **{selected_store}** in 2024
        - Prioritizes articles with highest stock quantities
        """)

    # Display allocation table
    st.subheader(f"Recommended Allocation for {selected_store}")

    if store_allocation["allocation"]:
        # Convert allocation to DataFrame for display
        df = pd.DataFrame(store_allocation["allocation"])
        st.dataframe(
            df,
            column_config={
                "article": "Article No",
                "quantity": "Allocated Quantity",
                "available_in_godown": "Available in Godown"
            },
            use_container_width=True
        )

        # Download button for allocation data
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download Allocation as CSV",
            data=csv,
            file_name=f"{selected_store}_allocation.csv",
            mime="text/csv"
        )
    else:
        st.error("No articles available for allocation that weren't sent in 2024.")

    # Data visualization
    if store_allocation["allocation"]:
        st.subheader("Allocation Visualization")

        # Create columns for charts
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            # Capacity utilization chart
            allocated = store_allocation["total_allocated"]
            remaining = store_capacities[selected_store] - allocated
            st.subheader("Capacity Utilization")
            st.bar_chart(
                {"Pieces": [allocated, remaining]},
                y="Pieces",
            )

        with chart_col2:
            # Top allocated articles
            top_articles = store_allocation["allocation"][:10]
            df_top = pd.DataFrame({
                "Article": [item["article"] for item in top_articles],
                "Available in Godown": [item["available_in_godown"] for item in top_articles]
            })

            st.subheader("Top Allocated Articles (Available Stock)")
            st.bar_chart(
                df_top.set_index("Article")
            )
