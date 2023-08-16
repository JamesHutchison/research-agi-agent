import faiss
import streamlit as st
from langchain.agents import Tool
from langchain.chat_models import ChatOpenAI
from langchain.docstore import InMemoryDocstore
from langchain.embeddings import OpenAIEmbeddings
from langchain.tools.file_management.read import ReadFileTool
from langchain.tools.file_management.write import WriteFileTool
from langchain.utilities import GoogleSearchAPIWrapper
from langchain.vectorstores import FAISS
from langchain_experimental.autonomous_agents import AutoGPT

st.sidebar.text_input("OpenAI API Key", key="api_key")

st.title("Researcher Agent")

user_query = st.chat_input(
    "Enter topic or theory to research. Provide any additional information that may assist the process."
)

# Set up the tools
search = GoogleSearchAPIWrapper()
tools = [
    Tool(
        name="search",
        func=search.run,
        description="An internet search tool for researching information and validating facts",
        return_direct=True,
    ),
    # WriteFileTool(),
    # ReadFileTool(),
]


# Set up the memory
@st.cache
def vector_store():
    embeddings_model = OpenAIEmbeddings(model="text-embedding-ada-002")
    embedding_size = 1536

    index = faiss.IndexFlatL2(embedding_size)
    return FAISS(embeddings_model.embed_query, index, InMemoryDocstore({}), {})


# Set up the model and AutoGPT


if user_query:
    vectorstore = vector_store()

    agent = AutoGPT.from_llm_and_tools(
        ai_name="Jimbo",
        ai_role="Critical Topic Expert",
        tools=tools,
        llm=ChatOpenAI(model="gpt-3.5-turbo", temperature=0),
        memory=vectorstore.as_retriever(),
    )
    # Set verbose to be true
    agent.chain.verbose = True

    agent.run([user_query])
