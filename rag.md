# Retrieval-Augmented Generation (RAG) Tutorial

## Part 1: Introduction to RAG and Minimal Implementation

### Objective

Implement a simple Retrieval-Augmented Generation (RAG) pipeline that uses:

- A local document as a knowledge source
- Vector store for retrieval
- Google Gemini LLM for answering questions

### Steps

#### 1. Document Loading and Splitting

```python
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

loader = WebBaseLoader("https://lilianweng.github.io/posts/2023-06-23-agent/")
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(docs)
```

#### 2. Embeddings and Vector Store

```python
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings

embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
vectorstore = FAISS.from_documents(splits, embedding)
retriever = vectorstore.as_retriever()
```

#### 3. Gemini Model Integration

```python
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA

llm = ChatGoogleGenerativeAI(model="gemini-pro")
rqa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
```

#### 4. Querying the Model

```python
query = "What is Task Decomposition?"
result = rqa.invoke({"query": query})
print(result['result'])
```

---

## Part 2: Conversational RAG and Multi-step Retrieval

### Objective

Extend the implementation to support chat history and multi-step reasoning using:

- LangGraph
- LangSmith (optional for tracing)

### Components

- Chat model: Google Gemini
- Embeddings: OpenAI
- Vector store: InMemoryVectorStore

### Setup

```python
from langchain.chat_models import init_chat_model
from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore

llm = init_chat_model("gemini-2.0-flash", model_provider="google_genai")
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
vector_store = InMemoryVectorStore(embeddings)
```

### Load and Index Documents

```python
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import bs4

loader = WebBaseLoader(
    web_paths=["https://lilianweng.github.io/posts/2023-06-23-agent/"],
    bs_kwargs={"parse_only": bs4.SoupStrainer(class_=("post-content", "post-title", "post-header"))}
)
docs = loader.load()
splits = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200).split_documents(docs)
_ = vector_store.add_documents(splits)
```

### Define Retrieval Tool

```python
from langchain_core.tools import tool

@tool(response_format="content_and_artifact")
def retrieve(query: str):
    retrieved_docs = vector_store.similarity_search(query, k=2)
    serialized = "\n\n".join(f"Source: {doc.metadata}\nContent: {doc.page_content}" for doc in retrieved_docs)
    return serialized, retrieved_docs
```

### LangGraph Setup

```python
from langgraph.graph import MessagesState, StateGraph
from langgraph_core.messages import SystemMessage
from langgraph.prebuilt import ToolNode, tools_condition

graph_builder = StateGraph(MessagesState)
```

### Nodes

```python
def query_or_respond(state: MessagesState):
    llm_with_tools = llm.bind_tools([retrieve])
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

tools = ToolNode([retrieve])

def generate(state: MessagesState):
    tool_messages = [m for m in reversed(state["messages"]) if m.type == "tool"]
    docs_content = "\n\n".join(doc.content for doc in tool_messages[::-1])
    system_prompt = SystemMessage("""
        You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question.
        If you don't know the answer, say so. Keep the answer concise.
        \n\n{docs_content}
    """)
    conversation = [m for m in state["messages"] if m.type in ("human", "system") or (m.type == "ai" and not m.tool_calls)]
    prompt = [system_prompt] + conversation
    return {"messages": [llm.invoke(prompt)]}
```

### Compile the Graph

```python
from langgraph.graph import END

graph_builder.add_node("query_or_respond", query_or_respond)
graph_builder.add_node("tools", tools)
graph_builder.add_node("generate", generate)

graph_builder.set_entry_point("query_or_respond")
graph_builder.add_conditional_edges("query_or_respond", tools_condition, {END: END, "tools": "tools"})
graph_builder.add_edge("tools", "generate")
graph_builder.add_edge("generate", END)

graph = graph_builder.compile()
```

### Stateful Memory (Optional)

```python
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)
config = {"configurable": {"thread_id": "abc123"}}
```

### Example Queries

```python
input_message = "What is Task Decomposition?"

for step in graph.stream({"messages": [{"role": "user", "content": input_message}]}, stream_mode="values", config=config):
    step["messages"][-1].pretty_print()
```

### Agentic Extension

```python
from langgraph.prebuilt import create_react_agent

agent_executor = create_react_agent(llm, [retrieve], checkpointer=memory)
config = {"configurable": {"thread_id": "def234"}}

input_message = """
What is the standard method for Task Decomposition?
Once you get the answer, look up common extensions of that method.
"""

for event in agent_executor.stream({"messages": [{"role": "user", "content": input_message}]}, stream_mode="values", config=config):
    event["messages"][-1].pretty_print()
```

---

## Conclusion

- Part 1: Implemented a basic RAG application
- Part 2: Extended to support chat memory and multi-step reasoning using LangGraph

Explore LangGraph's official documentation for more advanced features like parallelism, dynamic tool routing, and database-backed checkpoints.
