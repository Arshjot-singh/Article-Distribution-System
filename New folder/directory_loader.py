from langchain_community.document_loaders import DirectoryLoader, PDFPlumberLoader

loader = DirectoryLoader(
    path = 'aiagent',
    glob = '*.pdf',
    loader_cls = PDFPlumberLoader
)

docs = loader.lazy_load()

for document in docs:
    print(document.metadata)