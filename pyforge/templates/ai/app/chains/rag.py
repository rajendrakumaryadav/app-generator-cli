"""
Retrieval-Augmented Generation (RAG) chain.

Usage:
    from app.chains.rag import build_rag_chain
    chain = build_rag_chain(vectorstore)
    answer = await chain.ainvoke({"question": "What is LangGraph?"})
"""
from __future__ import annotations

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.vectorstores import VectorStore
from langchain_openai import ChatOpenAI

from app.config import settings

RAG_PROMPT = ChatPromptTemplate.from_template(
    """You are a helpful assistant. Answer the question using ONLY the provided context.
If the answer is not in the context, say "I don't know".

Context:
{context}

Question: {question}

Answer:"""
)


def build_rag_chain(vectorstore: VectorStore):
    """Build a RAG chain from a pre-loaded vector store."""
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    llm = ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=0,
    )

    def format_docs(docs: list) -> str:
        return "\n\n".join(doc.page_content for doc in docs)

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | RAG_PROMPT
        | llm
        | StrOutputParser()
    )
    return chain
