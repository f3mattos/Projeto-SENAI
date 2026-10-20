"""Indexação da base de conhecimento no ChromaDB."""
from pathlib import Path
import shutil

from langchain_chroma import Chroma
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import load_settings

KNOWLEDGE_DIR = Path("knowledge_base")
CHROMA_DIR = Path("data/chroma")
COLLECTION_NAME = "easy_support_docs"


def build_index() -> None:
    settings = load_settings()

    loader = DirectoryLoader(
        str(KNOWLEDGE_DIR),
        glob="**/*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
        show_progress=True,
    )

    documents = loader.load()

    if not documents:
        raise RuntimeError("Nenhum documento markdown encontrado em knowledge_base.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=900,
        chunk_overlap=150,
        separators=["\n## ", "\n### ", "\n\n", "\n", " "],
    )

    chunks = splitter.split_documents(documents)

    for index, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = f"chunk-{index:04d}"
        chunk.metadata["source_name"] = Path(
            chunk.metadata.get("source", "desconhecido")
        ).name

    if CHROMA_DIR.exists():
        shutil.rmtree(CHROMA_DIR)

    embeddings = OpenAIEmbeddings(
        model=settings.embedding_model,
        api_key=settings.openai_api_key,
    )

    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=str(CHROMA_DIR),
    )

    print("==========================================")
    print("ÍNDICE VETORIAL CRIADO COM SUCESSO")
    print("==========================================")
    print(f"Documentos indexados: {len(documents)}")
    print(f"Total de chunks:      {len(chunks)}")
    print(f"Diretório Chroma:     {CHROMA_DIR}")


if __name__ == "__main__":
    build_index()
