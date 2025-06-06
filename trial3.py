import streamlit as st
import pandas as pd
import io
import PyPDF2
import re
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Page configuration
st.set_page_config(page_title="Jacket Allocation Planner", layout="wide")

# API Key input in sidebar
with st.sidebar:
    st.title("API Configuration")
    api_key = st.text_input("Enter OpenAI API Key", type="password")
    st.markdown("---")
    st.markdown("### About This App")
    st.info(
        "This application helps allocate jackets to different stores based on "
        "current godown stock and previous allocation history. Upload your data files "
        "to get started, and the app will use LangChain to provide AI-powered insights "
        "about the allocation strategy."
    )

# Main content
st.title("Jacket Allocation Planner")

# Functions to extract data from files
def extract_data_from_pdf(pdf_file):
    """Extract text data from PDF files"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
        return ""

def parse_godown_stock(file):
    """Parse godown stock data from uploaded file"""
    try:
        if file.name.endswith('.pdf'):
            text = extract_data_from_pdf(file)
            # Example pattern: This is a simplified pattern and may need to be adjusted
            # based on your actual PDF format
            pattern = r'([Z0-9]+)\s+(\d+)'
            matches = re.findall(pattern, text)
            if matches:
                return {article: int(quantity) for article, quantity in matches}
            else:
                st.error("Could not extract godown stock data from the PDF. Please check the format.")
                return {}
        elif file.name.endswith('.csv'):
            df = pd.read_csv(file)
            # Assuming the CSV has columns 'article' and 'quantity'
            if 'article' in df.columns and 'quantity' in df.columns:
                return dict(zip(df['article'], df['quantity']))
            else:
                # Try to be flexible with column names
                if len(df.columns) >= 2:
                    # Assume first column is article, second is quantity
                    df.columns = ['article', 'quantity'] + list(df.columns[2:])
                    return dict(zip(df['article'], df['quantity']))
                else:
                    st.error("CSV should have at least 2 columns: 'article' and 'quantity' for godown stock data.")
                    return {}
        else:
            st.error("Unsupported file format. Please upload a PDF or CSV file.")
            return {}
    except Exception as e:
        st.error(f"Error parsing godown stock data: {str(e)}")
        return {}

def parse_articles_sent(file):
    """Parse articles sent to each store in 2024 from uploaded file"""
    articles_data = {}
    try:
        if file.name.endswith('.pdf'):
            text = extract_data_from_pdf(file)
            # This is a simplified pattern and needs to be customized based on your PDF structure
            stores = ["BOMBAY", "MOGA", "DUKE RO", "DUKE NIT", "MORADABAD"]
            for store in stores:
                pattern = rf'{store}\s*:(.*?)(?=(?:{"|".join(stores)})|$)'
                match = re.search(pattern, text, re.DOTALL)
                if match:
                    store_data = match.group(1).strip()
                    articles = re.findall(r'([Z0-9]+)', store_data)
                    articles_data[store] = articles
        
        elif file.name.endswith('.csv'):
            df = pd.read_csv(file)
            # Assuming the CSV has 'store' and 'article' columns
            if 'store' in df.columns and 'article' in df.columns:
                for store, group in df.groupby('store'):
                    articles_data[store] = group['article'].tolist()
            else:
                # Try to be flexible with column names
                if len(df.columns) >= 2:
                    # Assume first column is store, second is article
                    df.columns = ['store', 'article'] + list(df.columns[2:])
                    for store, group in df.groupby('store'):
                        articles_data[store] = group['article'].tolist()
                else:
                    st.error("CSV should have at least 2 columns: 'store' and 'article' for articles sent data.")
        
        else:
            st.error("Unsupported file format. Please upload a PDF or CSV file.")
        
        return articles_data
    except Exception as e:
        st.error(f"Error parsing articles sent data: {str(e)}")
        return {}

def parse_store_capacities(file):
    """Parse store capacities from uploaded file"""
    try:
        if file.name.endswith('.pdf'):
            text = extract_data_from_pdf(file)
            # Example pattern: "STORE NAME: XXX"
            stores = ["BOMBAY", "MOGA", "DUKE RO", "DUKE NIT", "MORADABAD"]
            capacities = {}
            for store in stores:
                pattern = rf'{store}\s*:\s*(\d+)'
                match = re.search(pattern, text)
                if match:
                    capacities[store] = int(match.group(1))
        
        elif file.name.endswith('.csv'):
            df = pd.read_csv(file)
            # Assuming the CSV has 'store' and 'capacity' columns
            if 'store' in df.columns and 'capacity' in df.columns:
                capacities = dict(zip(df['store'], df['capacity']))
            else:
                # Try to be flexible with column names
                if len(df.columns) >= 2:
                    # Assume first column is store, second is capacity
                    df.columns = ['store', 'capacity'] + list(df.columns[2:])
                    capacities = dict(zip(df['store'], df['capacity']))
                else:
                    st.error("CSV should have at least 2 columns: 'store' and 'capacity' for store capacities.")
                    capacities = {}
        
        else:
            st.error("Unsupported file format. Please upload a PDF or CSV file.")
            capacities = {}
        
        return capacities
    except Exception as e:
        st.error(f"Error parsing store capacities data: {str(e)}")
        return {}

# Function to create optimal allocation based on stock availability
def create_allocation(store, store_capacities, godown_stock, available_articles):
    # Check if store exists in dictionaries and provide default values if not
    if store not in available_articles:
        st.error(f"Store '{store}' not found in available articles data. Check your input files.")
        available = []
    else:
        available = available_articles[store]
    
    if store not in store_capacities:
        st.error(f"Store '{store}' not found in store capacities data. Check your input files.")
        max_capacity = 0
    else:
        max_capacity = store_capacities[store]
    
    # Make sure we only process articles that exist in godown_stock
    available = [article for article in available if article in godown_stock]
    
    # Sort by quantity available (highest first)
    sorted_articles = sorted(available, key=lambda x: godown_stock[x], reverse=True)
    
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
    
    capacity_percentage = (total_allocated / max_capacity * 100) if max_capacity > 0 else 0
    
    return {
        "allocation": allocation,
        "total_allocated": total_allocated,
        "capacity_percentage": round(capacity_percentage, 1)
    }

# Create tabs for uploading files and viewing results
tab1, tab2 = st.tabs(["Upload Data", "View Allocation"])

# File uploads in the first tab
with tab1:
    st.header("Upload Your Data Files")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Godown Stock")
        godown_file = st.file_uploader("Upload godown stock data (PDF or CSV)", type=["pdf", "csv"], key="godown")
        st.info("File should contain article numbers and their quantities in stock")
        if godown_file:
            with st.expander("Sample Format"):
                st.code("""
                article,quantity
                Z2393,27
                Z2263,12
                Z2250,12
                ...
                """)
    
    with col2:
        st.subheader("Articles Sent in 2024")
        articles_file = st.file_uploader("Upload articles sent data (PDF or CSV)", type=["pdf", "csv"], key="articles")
        st.info("File should list articles sent to each store in 2024")
        if articles_file:
            with st.expander("Sample Format"):
                st.code("""
                store,article
                BOMBAY,Z2250
                BOMBAY,Z2252
                ...
                MOGA,Z2250
                ...
                """)
    
    with col3:
        st.subheader("Store Capacities")
        capacities_file = st.file_uploader("Upload store capacities (PDF or CSV)", type=["pdf", "csv"], key="capacities")
        st.info("File should contain each store name and its maximum capacity")
        if capacities_file:
            with st.expander("Sample Format"):
                st.code("""
                store,capacity
                BOMBAY,132
                MOGA,257
                DUKE RO,240
                DUKE NIT,70
                MORADABAD,158
                """)
    
    # Process button
    if st.button("Process Data"):
        if not godown_file or not articles_file or not capacities_file:
            st.error("Please upload all three required files")
        else:
            # Process the uploaded files
            with st.spinner("Processing files..."):
                # Extract data from uploaded files
                godown_stock = parse_godown_stock(godown_file)
                articles_sent_in_2024 = parse_articles_sent(articles_file)
                store_capacities = parse_store_capacities(capacities_file)
                
                # Store the extracted data in session state for later use
                st.session_state.godown_stock = godown_stock
                st.session_state.articles_sent_in_2024 = articles_sent_in_2024
                st.session_state.store_capacities = store_capacities
                
                # Calculate available articles for each store
                available_articles = {}
                for store in store_capacities:
                    if store in articles_sent_in_2024:
                        available_articles[store] = [article for article in godown_stock 
                                                    if article not in articles_sent_in_2024[store] and godown_stock[article] > 0]
                    else:
                        st.warning(f"No 2024 sending history found for store '{store}'. Using all available articles.")
                        available_articles[store] = [article for article in godown_stock if godown_stock[article] > 0]
                
                st.session_state.available_articles = available_articles
                
                st.success("Data processed successfully! Go to the 'View Allocation' tab to see results.")
                
                # Show summary of loaded data
                st.subheader("Data Summary")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Godown Articles", len(godown_stock))
                    st.write("Top 5 articles by stock:")
                    top_stock = sorted(godown_stock.items(), key=lambda x: x[1], reverse=True)[:5]
                    for article, qty in top_stock:
                        st.write(f"- {article}: {qty} pcs")
                
                with col2:
                    st.metric("Stores", len(store_capacities))
                    for store, capacity in store_capacities.items():
                        st.write(f"- {store}: {capacity} pcs")
                
                with col3:
                    sent_articles_count = {store: len(articles) for store, articles in articles_sent_in_2024.items()}
                    st.metric("Total Sent Articles", sum(sent_articles_count.values()))
                    for store, count in sent_articles_count.items():
                        st.write(f"- {store}: {count} articles")

# Results in the second tab
with tab2:
    if not hasattr(st.session_state, 'godown_stock') or not st.session_state.godown_stock:
        st.info("Please upload and process your data files in the 'Upload Data' tab first.")
    else:
        # Get data from session state
        godown_stock = st.session_state.godown_stock
        articles_sent_in_2024 = st.session_state.articles_sent_in_2024
        store_capacities = st.session_state.store_capacities
        available_articles = st.session_state.available_articles
        
        # Create columns for store selection and info
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Store selection
            if not store_capacities:
                st.error("No store capacity data found. Please check your uploaded files.")
                selected_store = "No stores available"
            else:
                selected_store = st.selectbox("Select Store", options=list(store_capacities.keys()))
            
            # Calculate allocation for selected store
            store_allocation = create_allocation(
                selected_store, 
                store_capacities, 
                godown_stock, 
                available_articles
            )
            
            # Display store information
            st.subheader("Store Information")
            if selected_store in store_capacities:
                st.metric("Maximum Capacity", f"{store_capacities[selected_store]} pcs")
                st.metric("Allocated", f"{store_allocation['total_allocated']} pcs ({store_allocation['capacity_percentage']}%)")
                if selected_store in available_articles:
                    st.metric("Available Articles", f"{len(available_articles[selected_store])} (not sent in 2024)")
                else:
                    st.metric("Available Articles", "0")
            else:
                st.error("Selected store not found in data.")
        
        with col2:
            # LangChain integration for AI insights (if API key is provided)
            if api_key:
                try:
                    st.subheader("AI-Powered Allocation Insights")
                    with st.spinner("Generating insights..."):
                        # Initialize LangChain with the OpenAI API
                        llm = ChatOpenAI(
                            model="gpt-3.5-turbo",
                            temperature=0,
                            openai_api_key=api_key
                        )
                        
                        # Create prompt template
                        prompt_template = PromptTemplate(
                            input_variables=["store", "capacity", "allocated", "percentage"],
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
                st.info("Enter your OpenAI API key in the sidebar to get AI-powered allocation insights.")
            
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
                labels = ["Allocated", "Remaining"]
                values = [
                    store_allocation["total_allocated"], 
                    store_capacities[selected_store] - store_allocation["total_allocated"]
                ]
                
                st.subheader("Capacity Utilization")
                st.bar_chart(
                    {"Pieces": values}, 
                    y="Pieces"
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