from typing import Any, Callable

import faiss
import streamlit as st
from langchain.agents import Tool
from langchain.chat_models import ChatOpenAI
from langchain.docstore import InMemoryDocstore
from langchain.embeddings import OpenAIEmbeddings
from langchain.memory import ChatMessageHistory
from langchain.schema.messages import BaseMessage
from langchain.tools.file_management.read import ReadFileTool
from langchain.tools.file_management.write import WriteFileTool
from langchain.utilities import GoogleSearchAPIWrapper
from langchain.vectorstores import FAISS
from langchain_experimental.autonomous_agents import AutoGPT
from pydantic import BaseModel

st.sidebar.text_input("OpenAI API Key (not used yet, use secrets.toml)", key="api_key")

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
@st.cache_resource
def vector_store():
    embeddings_model = OpenAIEmbeddings(model="text-embedding-ada-002")
    embedding_size = 1536

    index = faiss.IndexFlatL2(embedding_size)
    return FAISS(embeddings_model.embed_query, index, InMemoryDocstore({}), {})


class ChatMessageHistoryWithHook(ChatMessageHistory):
    hook: Callable[[str], Any]

    def add_message(self, message: BaseMessage) -> None:
        """Add a self-created message to the store"""
        super().add_message(message)
        self.hook(message.content)


if user_query:
    vectorstore = vector_store()
    history = ChatMessageHistoryWithHook(hook=st.chat_message("AI").write)

    agent = AutoGPT.from_llm_and_tools(
        ai_name="Jimbo",
        ai_role="Critical Topic Expert",
        tools=tools,
        llm=ChatOpenAI(model="gpt-3.5-turbo", temperature=0),
        memory=vectorstore.as_retriever(),
        chat_history_memory=history,
    )
    # Set verbose to be true
    agent.chain.verbose = True

    result = agent.run([user_query])
