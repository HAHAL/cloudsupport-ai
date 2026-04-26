import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from classifier import QuestionCategory, QuestionClassifier
from prompt_manager import PromptManager


load_dotenv()


@dataclass(frozen=True)
class RetrievedChunk:
    """A document chunk returned by vector search."""

    content: str
    source: str
    category: str
    score: float | None = None
    page: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "content": self.content,
            "source": self.source,
            "category": self.category,
            "score": self.score,
            "page": self.page,
        }


class RAGService:
    """Complete RAG pipeline based on LangChain and Chroma.

    Pipeline:
    1. Load local txt/pdf documents.
    2. Split documents into chunks.
    3. Convert chunks to embeddings.
    4. Store/reuse vectors in Chroma.
    5. Retrieve top-k similar chunks.
    6. Build prompt and call LLM.
    """

    def __init__(
        self,
        knowledge_dir: str | Path | None = None,
        chroma_dir: str | Path | None = None,
        collection_name: str | None = None,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
        top_k: int | None = None,
    ) -> None:
        self.knowledge_dir = Path(knowledge_dir or os.getenv("KNOWLEDGE_DIR", "knowledge"))
        self.chroma_dir = str(chroma_dir or os.getenv("CHROMA_DIR", "chroma_data"))
        self.collection_name = collection_name or os.getenv(
            "CHROMA_COLLECTION",
            "cloudsupport_kb",
        )
        self.chunk_size = chunk_size or int(os.getenv("CHUNK_SIZE", "800"))
        self.chunk_overlap = chunk_overlap or int(os.getenv("CHUNK_OVERLAP", "120"))
        self.top_k = top_k or int(os.getenv("RAG_TOP_K", "4"))

        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")

        self.classifier = QuestionClassifier()
        self.prompt_manager = PromptManager()
        self.embeddings = self._build_embeddings()
        self.llm = self._build_llm()
        self.vector_store = self._build_vector_store()

        # Build the vector index lazily on first startup if Chroma is empty.
        self.ensure_index()

    def answer(self, question: str, top_k: int | None = None) -> dict[str, Any]:
        """Retrieve related chunks and generate an LLM answer."""
        category = self.classifier.classify(question)
        retrieved_chunks = self.retrieve(question, top_k=top_k, category=category)

        if not retrieved_chunks:
            return {
                "question": question,
                "category": category.value,
                "answer": self.prompt_manager.empty_context_answer(category),
                "retrieved_contents": [],
                "references": [],
                "metadata": {
                    "chunk_size": self.chunk_size,
                    "chunk_overlap": self.chunk_overlap,
                    "retrieval_top_k": top_k or self.top_k,
                    "has_context": False,
                },
            }

        context = self._format_context(retrieved_chunks)
        chain = self.prompt_manager.support_qa_prompt() | self.llm
        response = chain.invoke(
            {
                "question": question,
                "category": category.value,
                "context": context,
            }
        )

        return {
            "question": question,
            "category": category.value,
            "answer": response.content,
            "retrieved_contents": [chunk.to_dict() for chunk in retrieved_chunks],
            "references": self._format_references(retrieved_chunks),
            "metadata": {
                "chunk_size": self.chunk_size,
                "chunk_overlap": self.chunk_overlap,
                "retrieval_top_k": top_k or self.top_k,
                "has_context": True,
            },
        }

    def ensure_index(self) -> None:
        """Create Chroma vectors from local files when the collection is empty."""
        existing = self.vector_store.get(limit=1)
        if existing.get("ids"):
            return

        self.ingest_documents()

    def ingest_documents(self) -> int:
        """Load, split, embed, and store local knowledge documents.

        Returns:
            Number of chunks written to Chroma.
        """
        documents = self.load_documents()
        if not documents:
            return 0

        chunks = self.split_documents(documents)
        if not chunks:
            return 0

        self.vector_store.add_documents(chunks)
        return len(chunks)

    def load_documents(self) -> list[Document]:
        """Load local txt and pdf files from the knowledge directory."""
        if not self.knowledge_dir.exists():
            return []

        documents: list[Document] = []
        supported_files = [
            *self.knowledge_dir.rglob("*.txt"),
            *self.knowledge_dir.rglob("*.pdf"),
        ]

        for file_path in supported_files:
            documents.extend(self._load_single_file(file_path))

        for doc in documents:
            source = str(doc.metadata.get("source", ""))
            doc.metadata["category"] = self._category_from_path(source)

        return documents

    def split_documents(self, documents: list[Document]) -> list[Document]:
        """Split documents into chunks for embedding and retrieval."""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""],
        )
        chunks = splitter.split_documents(documents)

        # Add stable chunk metadata for easier debugging and UI display.
        for index, chunk in enumerate(chunks):
            chunk.metadata["chunk_index"] = index
            chunk.metadata.setdefault("category", QuestionCategory.OTHER.value)

        return chunks

    def retrieve(
        self,
        query: str,
        top_k: int | None = None,
        category: QuestionCategory | None = None,
    ) -> list[RetrievedChunk]:
        """Run top-k similarity search in Chroma.

        Category-specific search is attempted first. If nothing is found, the
        method falls back to searching all documents.
        """
        k = top_k or self.top_k
        category = category or self.classifier.classify(query)

        if category != QuestionCategory.OTHER:
            docs_with_scores = self.vector_store.similarity_search_with_score(
                query,
                k=k,
                filter={"category": category.value},
            )
            if docs_with_scores:
                return self._to_retrieved_chunks(docs_with_scores)

        docs_with_scores = self.vector_store.similarity_search_with_score(query, k=k)
        return self._to_retrieved_chunks(docs_with_scores)

    def _load_single_file(self, file_path: Path) -> list[Document]:
        """Load one txt or pdf file using the matching LangChain loader."""
        suffix = file_path.suffix.lower()

        if suffix == ".txt":
            loader = TextLoader(str(file_path), encoding="utf-8")
            return loader.load()

        if suffix == ".pdf":
            loader = PyPDFLoader(str(file_path))
            return loader.load()

        return []

    def _build_vector_store(self) -> Chroma:
        """Create a persistent Chroma vector store."""
        return Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.chroma_dir,
        )

    @staticmethod
    def _category_from_path(source: str) -> str:
        """Infer document category from path segments such as knowledge/cdn/a.txt."""
        normalized = source.lower().replace("\\", "/")
        path_parts = set(normalized.split("/"))

        path_aliases = {
            QuestionCategory.CDN: {"cdn"},
            QuestionCategory.DNS: {"dns"},
            QuestionCategory.HTTPS: {"https", "ssl", "tls"},
            QuestionCategory.VIDEO_PLAYBACK: {"video", "视频播放", "playback"},
            QuestionCategory.KUBERNETES: {"kubernetes", "k8s"},
            QuestionCategory.OTHER: {"general", "other", "其他"},
        }
        for category, aliases in path_aliases.items():
            if aliases & path_parts:
                return category.value

        return QuestionCategory.OTHER.value

    @staticmethod
    def _to_retrieved_chunks(
        docs_with_scores: list[tuple[Document, float]],
    ) -> list[RetrievedChunk]:
        chunks: list[RetrievedChunk] = []
        for doc, score in docs_with_scores:
            page = doc.metadata.get("page")
            chunks.append(
                RetrievedChunk(
                    content=doc.page_content,
                    source=str(doc.metadata.get("source", "unknown")),
                    category=str(doc.metadata.get("category", "general")),
                    score=score,
                    page=page if isinstance(page, int) else None,
                )
            )
        return chunks

    @staticmethod
    def _format_context(chunks: list[RetrievedChunk]) -> str:
        """Format retrieved chunks into a compact prompt context."""
        context_blocks = []
        for index, chunk in enumerate(chunks, start=1):
            page_text = f", page={chunk.page}" if chunk.page is not None else ""
            context_blocks.append(
                f"[{index}] source={chunk.source}{page_text}, score={chunk.score}\n"
                f"{chunk.content}"
            )
        return "\n\n".join(context_blocks)

    @staticmethod
    def _format_references(chunks: list[RetrievedChunk]) -> list[dict[str, Any]]:
        """Return short source references for API clients."""
        return [
            {
                "source": chunk.source,
                "category": chunk.category,
                "score": chunk.score,
                "page": chunk.page,
                "content_preview": chunk.content[:240],
            }
            for chunk in chunks
        ]

    @staticmethod
    def _build_embeddings():  # type: ignore[no-untyped-def]
        """Build embedding model. Supports OpenAI and Qwen/DashScope."""
        provider = os.getenv("EMBEDDING_PROVIDER", "openai").lower()

        if provider == "qwen":
            return DashScopeEmbeddings(
                model=os.getenv("QWEN_EMBEDDING_MODEL", "text-embedding-v2"),
                dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),
            )

        return OpenAIEmbeddings(
            model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
            api_key=os.getenv("OPENAI_API_KEY"),
        )

    @staticmethod
    def _build_llm() -> ChatOpenAI:
        """Build chat model. Qwen uses OpenAI-compatible DashScope endpoint."""
        provider = os.getenv("LLM_PROVIDER", "openai").lower()

        if provider == "qwen":
            return ChatOpenAI(
                model=os.getenv("QWEN_CHAT_MODEL", "qwen-plus"),
                api_key=os.getenv("DASHSCOPE_API_KEY"),
                base_url=os.getenv(
                    "QWEN_BASE_URL",
                    "https://dashscope.aliyuncs.com/compatible-mode/v1",
                ),
                temperature=float(os.getenv("LLM_TEMPERATURE", "0.2")),
            )

        return ChatOpenAI(
            model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.2")),
        )
