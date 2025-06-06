import streamlit as st
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Page configuration
st.set_page_config(page_title="🧥 Article Allocation Planner", layout="wide")

# API Key input in sidebar
with st.sidebar:
    st.title("API Configuration")
    api_key = st.text_input("Enter OpenAI API/ Anthropic Key", type="password")
    st.markdown("---")
    st.markdown("### About This App")
    st.info(
        "This application helps allocate articles to different stores based on "
        "current godown stock and previous allocation history. It uses LangChain "
        "to provide AI-powered insights about the allocation strategy."
    )

# Main content
st.title("🧥 Article Allocation Planner")

# Store maximum capacities
store_capacities = {
    "BOMBAY": 132,
    "MOGA": 257,
    "DUKE RO": 240,
    "DUKE NIT": 70,
    "MORADABAD": 158
}

# Godown stock data
godown_stock = {
    "Z2393": 27, "Z2263": 12, "Z2250": 12, "Z2327": 9, "Z2312": 7, "Z2329": 7, "Z2265": 7, 
    "Z2289": 7, "Z2308": 7, "Z2253": 7, "Z2303": 6, "Z2394": 6, "Z2333": 6, "Z2323": 6, 
    "Z2288": 5, "Z2321": 5, "Z2356": 5, "Z2272": 4, "Z2402": 4, "Z2328": 4, "Z2326": 4, 
    "Z2342": 4, "Z2377": 4, "Z2386": 4, "Z2258": 4, "Z2281": 4, "Z2294": 4, "Z2350": 4, 
    "Z2276": 4, "Z2282": 4, "Z2292": 4, "Z2330": 4, "Z2331": 3, "Z2266": 3, "Z2318": 3, 
    "Z2344": 3, "Z2254": 3, "Z2298": 3, "Z2271": 3, "Z2293": 3, "Z2279": 2, "Z2374": 2, 
    "Z2392": 2, "Z2305": 2, "Z2324": 2, "Z2362": 2, "Z2259": 2, "Z2291": 2, "Z2306": 2, 
    "Z2315": 2, "Z2341": 2, "Z2351": 2, "Z2280": 2, "Z2290": 2, "Z2297": 2, "Z2300": 2, 
    "Z2256": 2, "Z2285": 2, "Z2302": 2, "Z2268": 1, "Z2283": 1, "Z2304": 1, "Z2345": 1, 
    "Z2287": 1, "Z2301": 1, "Z2338": 1, "Z2379": 1, "Z2387": 1, "SDZ3134": 1, "Z2260": 1, 
    "Z2359": 1, "Z2391": 1, "Z2261": 1, "Z2262": 1, "Z2274": 1, "Z2335": 1, "Z2348": 1, 
    "Z2361": 1, "Z2376": 1, "Z2252": 1, "Z2278": 1, "Z2307": 1, "Z2381": 1, "SDZ2250": 1, 
    "SDZ3084R": 1, "SDZ3102": 1, "SDZ3112": 1, "SDZ3138": 1, "SDZ3170": 1, "SDZ3172": 1, 
    "Z2269": 1, "Z2286": 1, "Z2295": 1, "Z2311": 1, "Z2316": 1, "Z2319": 1, "Z2383": 1
}

# Articles sent to each store in 2024
articles_sent_in_2024 = {
    "BOMBAY": ["Z2250", "Z2252", "Z2253", "Z2256", "Z2259", "Z2260", "Z2261", "Z2262", "Z2263", 
               "Z2265", "Z2266", "Z2268", "Z2271", "Z2272", "Z2276", "Z2277", "Z2278", "Z2282", 
               "Z2283", "Z2285", "Z2286", "Z2288", "Z2289", "Z2291", "Z2293", "Z2294", "Z2295", 
               "Z2297", "Z2300", "Z2301", "Z2302", "Z2304", "Z2306", "Z2307", "Z2308", "Z2311", 
               "Z2312", "Z2316", "Z2318", "Z2321", "Z2323", "Z2327", "Z2330", "Z2333", "Z2338", 
               "Z2342", "Z2344", "Z2345", "Z2348", "Z2356", "Z2361", "Z2362", "Z2374", "Z2377", 
               "Z2379", "Z2381", "Z2386", "Z2391", "Z2393", "Z2394", "Z2402"],
    
    "MOGA": ["Z2250", "Z2252", "Z2253", "Z2254", "Z2256", "Z2258", "Z2259", "Z2260", "Z2261", 
             "Z2262", "Z2263", "Z2265", "Z2266", "Z2268", "Z2269", "Z2271", "Z2272", "Z2274", 
             "Z2276", "Z2277", "Z2279", "Z2281", "Z2282", "Z2283", "Z2285", "Z2286", "Z2287", 
             "Z2288", "Z2289", "Z2290", "Z2292", "Z2293", "Z2294", "Z2295", "Z2297", "Z2298", 
             "Z2300", "Z2301", "Z2302", "Z2303", "Z2304", "Z2305", "Z2306", "Z2307", "Z2308", 
             "Z2311", "Z2312", "Z2315", "Z2316", "Z2318", "Z2319", "Z2321", "Z2323", "Z2324", 
             "Z2326", "Z2327", "Z2328", "Z2329", "Z2330", "Z2331", "Z2333", "Z2335", "Z2338", 
             "Z2341", "Z2342", "Z2344", "Z2345", "Z2348", "Z2350", "Z2351", "Z2356", "Z2359", 
             "Z2361", "Z2374", "Z2377", "Z2381", "Z2383", "Z2386", "Z2387", "Z2391", "Z2392", 
             "Z2393", "Z2394", "Z2402"],
    
    "DUKE RO": ["Z2250", "Z2252", "Z2253", "Z2256", "Z2259", "Z2260", "Z2261", "Z2262", "Z2263", 
                "Z2265", "Z2266", "Z2268", "Z2269", "Z2271", "Z2272", "Z2274", "Z2276", "Z2277", 
                "Z2278", "Z2279", "Z2280", "Z2282", "Z2283", "Z2285", "Z2286", "Z2288", "Z2289", 
                "Z2291", "Z2292", "Z2293", "Z2294", "Z2295", "Z2297", "Z2300", "Z2301", "Z2302", 
                "Z2304", "Z2306", "Z2307", "Z2308", "Z2311", "Z2312", "Z2315", "Z2316", "Z2318", 
                "Z2321", "Z2323", "Z2327", "Z2330", "Z2333", "Z2338", "Z2341", "Z2342", "Z2344", 
                "Z2345", "Z2348", "Z2356", "Z2359", "Z2361", "Z2362", "Z2374", "Z2377", "Z2379", 
                "Z2381", "Z2383", "Z2386", "Z2387", "Z2391", "Z2392", "Z2393", "Z2394", "Z2402", 
                "Z9188CM", "SDZ2250", "SDZ3084R", "SDZ3102", "SDZ3108", "SDZ3112", "SDZ3134", 
                "SDZ3138", "SDZ3161", "SDZ3170", "SDZ3172"],
    
    "DUKE NIT": ["Z2250", "Z2253", "Z2260", "Z2261", "Z2262", "Z2263", "Z2266", "Z2268", "Z2271", 
                 "Z2272", "Z2276", "Z2277", "Z2278", "Z2282", "Z2283", "Z2288", "Z2289", "Z2291", 
                 "Z2293", "Z2295", "Z2297", "Z2301", "Z2302", "Z2304", "Z2306", "Z2307", "Z2308", 
                 "Z2311", "Z2312", "Z2315", "Z2316", "Z2321", "Z2323", "Z2327", "Z2333", "Z2338", 
                 "Z2341", "Z2342", "Z2356", "Z2361", "Z2362", "Z2374", "Z2377", "Z2386", "Z2391", 
                 "Z2392", "Z2393", "Z2394", "Z2402"],
    
    "MORADABAD": ["Z2250", "Z2252", "Z2253", "Z2254", "Z2256", "Z2258", "Z2259", "Z2260", "Z2261", 
                  "Z2262", "Z2263", "Z2265", "Z2266", "Z2268", "Z2271", "Z2272", "Z2276", "Z2277", 
                  "Z2278", "Z2281", "Z2282", "Z2283", "Z2285", "Z2286", "Z2287", "Z2288", "Z2289", 
                  "Z2290", "Z2291", "Z2293", "Z2294", "Z2295", "Z2297", "Z2298", "Z2300", "Z2301", 
                  "Z2302", "Z2303", "Z2304", "Z2305", "Z2306", "Z2307", "Z2308", "Z2311", "Z2312", 
                  "Z2313", "Z2316", "Z2318", "Z2319", "Z2321", "Z2323", "Z2324", "Z2326", "Z2327", 
                  "Z2328", "Z2329", "Z2330", "Z2331", "Z2333", "Z2335", "Z2338", "Z2342", "Z2344", 
                  "Z2345", "Z2348", "Z2350", "Z2356", "Z2361", "Z2362", "Z2374", "Z2376", "Z2377", 
                  "Z2379", "Z2381", "Z2386", "Z2391", "Z2393", "Z2394", "Z2402"]
}

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
    selected_store = st.selectbox("Select Store", options=list(store_capacities.keys()))
    
    # Calculate allocation for selected store
    store_allocation = create_allocation(selected_store)
    
    # Display store information
    st.subheader("Store Information")
    st.metric("Maximum Capacity", f"{store_capacities[selected_store]} pcs")
    st.metric("Allocated", f"{store_allocation['total_allocated']} pcs ({store_allocation['capacity_percentage']}%)")
    st.metric("Available Articles", f"{len(available_articles[selected_store])} (not sent in 2024)")

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
        st.info("Enter your OpenAI API/ Anthropic key in the sidebar to get AI-powered allocation insights.")
    
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
        allocated  = store_allocation["total_allocated"]
        remaining  = store_capacities[selected_store] - allocated
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