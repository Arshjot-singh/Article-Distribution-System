import os
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from dotenv import load_dotenv

load_dotenv()

# hf_token = os.getenv("HUGGINGFACEHUB_ACCESS_TOKEN")

llm = HuggingFaceEndpoint(
    repo_id = "meta-llama/Llama-2-7b-chat-hf",
    task = "text-generation"
    # huggingfacehub_api_token = hf_token
)

# model = ChatHuggingFace(llm = llm)

result = llm.invoke("what is the capital of india")

print(result)