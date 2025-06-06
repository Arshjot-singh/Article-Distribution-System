from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader('about company.pdf')

docs = loader.load()

print(docs[0].page_content)
print(docs[1].metadata)