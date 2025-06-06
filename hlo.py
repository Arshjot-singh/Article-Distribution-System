from langchain_community.document_loaders import PDFPlumberLoader
import pandas as pd
import re
from collections import defaultdict

# Load all 3 PDFs with clear variable names
stock_loader = PDFPlumberLoader("5_Jacket_Stock.pdf")
supply_loader = PDFPlumberLoader("5_Jacket_Supply_24.pdf")
max_pcs_loader = PDFPlumberLoader("5_Max_Pcs.pdf")

# Load documents from each PDF
stock_docs = stock_loader.load()
supply_docs = supply_loader.load()
max_pcs_docs = max_pcs_loader.load()

# (Optional) Print first few lines to verify
print("Stock PDF Sample:\n", stock_docs[0].page_content[:200])
print("Supply PDF Sample:\n", supply_docs[0].page_content[:200])
print("Max PCS PDF Sample:\n", max_pcs_docs[0].page_content[:200])


# ----------- 2. Extract Data into DataFrames ----------------- #

# Utility function to extract tabular data from page content
def extract_table_from_text(text, expected_cols):
    rows = []
    for line in text.strip().split('\n'):
        parts = re.split(r'\s{2,}', line.strip())
        if len(parts) == expected_cols:
            rows.append(parts)
    return rows

# Parse stock (Article | Quantity)
stock_rows = extract_table_from_text(stock_docs[0].page_content, 2)
stock_df = pd.DataFrame(stock_rows[1:], columns=['article', 'quantity']).copy()
stock_df['quantity'] = stock_df['quantity'].astype(int)

# Parse supply (Location | Article | Quantity)
supply_rows = extract_table_from_text(supply_docs[0].page_content, 3)
supply_df = pd.DataFrame(supply_rows[1:], columns=['location', 'article', 'quantity']).copy()
supply_df['quantity'] = supply_df['quantity'].astype(int)

# Parse max_pcs (Location | Max Quantity)
max_pcs_rows = extract_table_from_text(max_pcs_docs[0].page_content, 2)
max_pcs_df = pd.DataFrame(max_pcs_rows[1:], columns=['location', 'max_quantity']).copy()
max_pcs_df['max_quantity'] = max_pcs_df['max_quantity'].astype(int)

# ----------- 3. Process Allocation Logic ----------------- #

allocations = []

# Build lookup for already supplied articles per location
supplied_lookup = defaultdict(set)
supplied_qty = defaultdict(int)

for _, row in supply_df.iterrows():
    supplied_lookup[row['location']].add(row['article'])
    supplied_qty[row['location']] += row['quantity']

# Build a dict for stock quantities
stock_lookup = dict(zip(stock_df['article'], stock_df['quantity']))

# Go store by store
for _, row in max_pcs_df.iterrows():
    location = row['location']
    max_allowed = row['max_quantity']
    already_sent_qty = supplied_qty.get(location, 0)
    remaining_capacity = max_allowed - already_sent_qty

    if remaining_capacity <= 0:
        continue

    # Loop through stock articles
    for article, qty_available in stock_lookup.items():
        if qty_available == 0:
            continue
        if article in supplied_lookup[location]:
            continue  # article already sent to this location

        send_qty = min(qty_available, remaining_capacity)
        if send_qty == 0:
            continue

        allocations.append({
            'location': location,
            'article': article,
            'quantity': send_qty
        })

        # Update stock and location capacity
        stock_lookup[article] -= send_qty
        remaining_capacity -= send_qty

        if remaining_capacity == 0:
            break

# ----------- 4. Output Final Allocation ----------------- #

final_df = pd.DataFrame(allocations)
final_df.to_csv("final_allocations_2.csv", index=False)
print("✅ Allocations completed and saved to final_allocations.csv")