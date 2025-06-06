import os
import pandas as pd
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, Tool
from langchain.agents.agent_types import AgentType
from langchain.tools import tool
from langchain.document_loaders import PDFPlumberLoader
from langchain_core.output_parsers import JsonOutputParser

# Load environment
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# --- 1. Load PDFs ---
stock_loader = PDFPlumberLoader("5_Jacket_Stock.pdf")
supply_loader = PDFPlumberLoader("5_Jacket_Supply_24.pdf")
max_pcs_loader = PDFPlumberLoader("5_Max_Pcs.pdf")

stock_docs = stock_loader.load()
supply_docs = supply_loader.load()
max_pcs_docs = max_pcs_loader.load()

# --- 2. Tools using LangChain @tool decorator ---

# @tool
# def get_stock(_) -> str:
#     """Returns godown stock: article number and quantity available."""
#     return stock_docs[0].page_content

# @tool
# def get_supply(_) -> str:
#     """Returns supply data for 2024: location, article, and quantity sent."""
#     return supply_docs[0].page_content

# @tool
# def get_max_limits(_) -> str:
#     """Returns max quantity allowed for each store/location."""
#     return max_pcs_docs[0].page_content

@tool
def get_stock(input_text: str) -> str:
    """Returns godown stock: article number and quantity available."""
    # Join all pages content into one string
    return "\n".join([doc.page_content for doc in stock_docs])

@tool
def get_supply(input_text: str) -> str:
    """Returns supply data for 2024: location, article, and quantity sent."""
    return "\n".join([doc.page_content for doc in supply_docs])

@tool
def get_max_limits(input_text: str) -> str:
    """Returns max quantity allowed for each store/location."""
    return "\n".join([doc.page_content for doc in max_pcs_docs])

# --- 3. Initialize Agent with Tools ---
tools = [get_stock, get_supply, get_max_limits]
llm = ChatOpenAI(temperature=0)

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# --- 4. Query the Agent ---
query = """
You are a supply chain assistant.

Inputs:
- Godown stock: article number and quantity.
- Supply 2024: store, article, and quantity already sent.
- Max limits: store and max quantity allowed.

Task:
- Allocate articles to stores.
- Do not repeat articles already sent to a store.
- Do not exceed each store's max quantity.
- Use only available stock.

Output:
Give a JSON list like:
[
  {"store": "Delhi", "article": "A101", "quantity": 10},
  {"store": "Mumbai", "article": "A202", "quantity": 5}
]
No explanation. Use only keys: store, article, quantity.
"""



# Run agent
response = agent.run(query)
print("Raw Output from Agent:\n", response)

# Try to parse
try:
    parser = JsonOutputParser()
    allocations = parser.parse(response)
    
    print("\n✅ Final Parsed Allocations:")
    for alloc in allocations:
        print(f"Store: {alloc.get('store')}, Article: {alloc.get('article')}, Quantity: {alloc.get('quantity')}")
    
    # Save to CSV
    df = pd.DataFrame(allocations)
    df.to_csv("final_allocations.csv", index=False)
    print("\n✅ Allocations saved to final_allocations.csv")

except Exception as e:
    print("\n❌ Failed to parse response as JSON. Here's the raw response:")
    print(response)
    print("\nError:", e)