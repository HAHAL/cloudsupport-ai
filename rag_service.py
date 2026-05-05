import hashlib
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from classifier import QuestionCategory, QuestionClassifier
from prompt_manager import PromptManager


load_dotenv()

SUPPORTED_FILE_TYPES = [".md", ".txt", ".pdf"]
VERSION_OVERRIDE_FILE = Path(os.getenv("KNOWLEDGE_VERSION_FILE", "data/knowledge_versions.json"))


@dataclass(frozen=True)
class RetrievedChunk:
    content: str
    source: str
    category: str
    score: float | None = None
    page: int | None = None
    doc_id: str = ""
    title: str = ""
    version: str = "v1.0.0"
    status: str = "active"
    chunk_index: int | None = None
    chunk_id: str = ""
    content_hash: str = ""
    document_hash: str = ""
    effective_from: str = ""
    deprecated_at: str = ""
    tags: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "content": self.content,
            "source": self.source,
            "category": self.category,
            "score": self.score,
            "page": self.page,
            "doc_id": self.doc_id,
            "title": self.title,
            "version": self.version,
            "status": self.status,
            "chunk_index": self.chunk_index,
            "chunk_id": self.chunk_id,
            "content_hash": self.content_hash,
            "document_hash": self.document_hash,
            "effective_from": self.effective_from,
            "deprecated_at": self.deprecated_at,
            "tags": self.tags,
        }


class RAGService:
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
        self.collection_name = collection_name or os.getenv("CHROMA_COLLECTION", "cloudsupport_kb")
        self.chunk_size = chunk_size or int(os.getenv("CHUNK_SIZE", "800"))
        self.chunk_overlap = chunk_overlap or int(os.getenv("CHUNK_OVERLAP", "120"))
        self.top_k = top_k or int(os.getenv("RAG_TOP_K", "4"))

        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")

        self.classifier = QuestionClassifier()
        self.prompt_manager = PromptManager()
        self.provider_ready = self._provider_is_ready()
        self.embeddings = self._build_embeddings() if self.provider_ready else None
        self.llm = self._build_llm() if self.provider_ready else None
        self.vector_store = self._build_vector_store() if self.provider_ready else None

        if self.vector_store is not None:
            self.ensure_index()

    def answer(self, question: str, top_k: int | None = None) -> dict[str, Any]:
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
                    "mode": self.search_mode(),
                },
            }

        if self.llm is None:
            return self._fallback_answer(question, category, retrieved_chunks, top_k=top_k)

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
                "mode": self.search_mode(),
            },
        }

    def knowledge_status(self) -> dict[str, Any]:
        versions = self.list_versions()
        return {
            "knowledge_dir": str(self.knowledge_dir),
            "vector_store": "chroma",
            "chroma_dir": self.chroma_dir,
            "collection": self.collection_name,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "top_k": self.top_k,
            "provider_ready": self.provider_ready,
            "mode": self.search_mode(),
            "document_count": versions["document_count"],
            "active_count": versions["active_count"],
            "deprecated_count": versions["deprecated_count"],
            "draft_count": versions["draft_count"],
            "supported_file_types": SUPPORTED_FILE_TYPES,
            "indexed_status": ["active"],
            "message": (
                "External embedding provider is configured. Chroma vector search is available."
                if self.provider_ready
                else "External embedding provider is not configured. Keyword fallback search is available."
            ),
        }

    def list_versions(self) -> dict[str, Any]:
        documents = self.load_documents(include_draft=True, include_deprecated=True)
        items = []
        counts = {"active": 0, "deprecated": 0, "draft": 0}
        for doc in documents:
            metadata = doc.metadata
            status = str(metadata.get("status", "active"))
            if status in counts:
                counts[status] += 1
            items.append(
                {
                    "doc_id": metadata.get("doc_id", ""),
                    "title": metadata.get("title", ""),
                    "version": metadata.get("version", "v1.0.0"),
                    "status": status,
                    "source": metadata.get("source", ""),
                    "owner": metadata.get("owner", "unknown"),
                    "effective_from": metadata.get("effective_from", ""),
                    "deprecated_at": metadata.get("deprecated_at", ""),
                    "tags": self._tags_to_list(metadata.get("tags", "")),
                    "document_hash": metadata.get("document_hash", ""),
                }
            )
        items.sort(key=lambda item: (item["doc_id"], item["version"], item["source"]))
        return {
            "document_count": len(items),
            "active_count": counts["active"],
            "deprecated_count": counts["deprecated"],
            "draft_count": counts["draft"],
            "documents": items,
        }

    def reindex(self, force: bool = False) -> dict[str, Any]:
        documents_all = self.load_documents(include_draft=True, include_deprecated=True)
        active_documents = [doc for doc in documents_all if doc.metadata.get("status") == "active"]
        chunks = self.split_documents(active_documents)

        if self.vector_store is not None and self.provider_ready:
            if force:
                try:
                    self.vector_store.delete_collection()
                except Exception:
                    pass
                self.vector_store = self._build_vector_store()
            if chunks:
                self.vector_store.add_documents(chunks)

        counts = self._count_statuses(documents_all)
        return {
            "status": "ok",
            "provider_ready": self.provider_ready,
            "mode": self.search_mode(),
            "document_count": len(documents_all),
            "active_count": counts["active"],
            "deprecated_count": counts["deprecated"],
            "draft_count": counts["draft"],
            "chunk_count": len(chunks),
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "indexed_status": ["active"],
            "message": (
                "Knowledge documents loaded and active chunks indexed into Chroma successfully."
                if self.provider_ready
                else "Knowledge documents loaded and active chunks prepared successfully. Keyword fallback search is available."
            ),
        }

    def preview_chunks(
        self,
        *,
        text: str | None = None,
        file_path: str | None = None,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ) -> dict[str, Any]:
        size = chunk_size or self.chunk_size
        overlap = chunk_overlap if chunk_overlap is not None else self.chunk_overlap
        if overlap >= size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")

        if file_path:
            path = self._safe_knowledge_path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"Knowledge file not found: {file_path}")
            documents = self._load_single_file(path, include_draft=True, include_deprecated=True)
        elif text:
            metadata = self._default_metadata("manual-input", text)
            documents = [Document(page_content=text, metadata=metadata)]
        else:
            raise ValueError("Either text or file_path is required")

        chunks = self.split_documents(documents, chunk_size=size, chunk_overlap=overlap)
        return {
            "chunk_size": size,
            "chunk_overlap": overlap,
            "chunk_count": len(chunks),
            "chunks": [self._chunk_preview(chunk) for chunk in chunks],
        }

    def search(self, query: str, top_k: int | None = None, include_deprecated: bool = False) -> dict[str, Any]:
        k = top_k or self.top_k
        chunks = self.retrieve(query, top_k=k, include_deprecated=include_deprecated)
        return {
            "query": query,
            "mode": self.search_mode(),
            "include_deprecated": include_deprecated,
            "top_k": k,
            "results": [self._search_result(chunk) for chunk in chunks],
        }

    def deprecate_document(
        self,
        doc_id: str,
        version: str,
        deprecated_at: str | None = None,
        reason: str | None = None,
    ) -> dict[str, Any]:
        versions = self.list_versions()["documents"]
        match = next(
            (item for item in versions if item["doc_id"] == doc_id and item["version"] == version),
            None,
        )
        if not match:
            raise ValueError(f"Document version not found: {doc_id} {version}")

        overrides = self._load_version_overrides()
        key = self._override_key(doc_id, version)
        overrides[key] = {
            "doc_id": doc_id,
            "version": version,
            "status": "deprecated",
            "deprecated_at": deprecated_at or datetime.now(timezone.utc).date().isoformat(),
            "reason": reason or "",
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        VERSION_OVERRIDE_FILE.parent.mkdir(parents=True, exist_ok=True)
        VERSION_OVERRIDE_FILE.write_text(json.dumps(overrides, ensure_ascii=False, indent=2), encoding="utf-8")
        return {
            "status": "ok",
            "doc_id": doc_id,
            "version": version,
            "new_status": "deprecated",
            "deprecated_at": overrides[key]["deprecated_at"],
            "message": "Document version marked as deprecated.",
        }

    def ensure_index(self) -> None:
        if self.vector_store is None:
            return
        existing = self.vector_store.get(limit=1)
        if existing.get("ids"):
            return
        self.ingest_documents()

    def ingest_documents(self) -> int:
        documents = self.load_documents(include_draft=False, include_deprecated=False)
        chunks = self.split_documents(documents)
        if chunks and self.vector_store is not None:
            self.vector_store.add_documents(chunks)
        return len(chunks)

    def load_documents(
        self,
        *,
        include_draft: bool = False,
        include_deprecated: bool = False,
    ) -> list[Document]:
        if not self.knowledge_dir.exists():
            return []

        documents: list[Document] = []
        supported_files = []
        for suffix in SUPPORTED_FILE_TYPES:
            supported_files.extend(self.knowledge_dir.rglob(f"*{suffix}"))

        for file_path in sorted(supported_files):
            documents.extend(
                self._load_single_file(
                    file_path,
                    include_draft=include_draft,
                    include_deprecated=include_deprecated,
                )
            )
        return documents

    def split_documents(
        self,
        documents: list[Document],
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ) -> list[Document]:
        size = chunk_size or self.chunk_size
        overlap = chunk_overlap if chunk_overlap is not None else self.chunk_overlap
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=size,
            chunk_overlap=overlap,
            separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""],
        )
        chunks = splitter.split_documents(documents)

        counters: dict[str, int] = {}
        indexed_at = datetime.now(timezone.utc).isoformat()
        for chunk in chunks:
            source = str(chunk.metadata.get("source", "unknown"))
            counters[source] = counters.get(source, 0)
            chunk_index = counters[source]
            counters[source] += 1

            doc_id = str(chunk.metadata.get("doc_id", self._slug_from_path(source)))
            version = str(chunk.metadata.get("version", "v1.0.0"))
            content_hash = self._sha256(chunk.page_content)
            chunk.metadata["chunk_index"] = chunk_index
            chunk.metadata["chunk_id"] = f"{doc_id}:{version}:{chunk_index}"
            chunk.metadata["content_hash"] = content_hash
            chunk.metadata["indexed_at"] = indexed_at
            chunk.metadata.setdefault("category", self._category_from_path(source))
            chunk.metadata["tags"] = self._normalize_tags(chunk.metadata.get("tags", ""))
        return chunks

    def retrieve(
        self,
        query: str,
        top_k: int | None = None,
        category: QuestionCategory | None = None,
        include_deprecated: bool = False,
    ) -> list[RetrievedChunk]:
        k = top_k or self.top_k
        category = category or self.classifier.classify(query)

        if self.vector_store is None:
            return self._keyword_retrieve(
                query,
                top_k=k,
                category=category,
                include_deprecated=include_deprecated,
            )

        status_filter = {"status": {"$in": ["active", "deprecated"]}} if include_deprecated else {"status": "active"}
        docs_with_scores = self.vector_store.similarity_search_with_score(query, k=k, filter=status_filter)
        chunks = self._to_retrieved_chunks(docs_with_scores)
        if chunks:
            return chunks

        return self._keyword_retrieve(
            query,
            top_k=k,
            category=category,
            include_deprecated=include_deprecated,
        )

    def parse_front_matter(self, content: str, source: str = "") -> tuple[dict[str, Any], str]:
        if not content.startswith("---\n"):
            return self._default_metadata(source, content), content

        end = content.find("\n---", 4)
        if end == -1:
            return self._default_metadata(source, content), content

        raw_meta = content[4:end].strip()
        body = content[content.find("\n", end + 1) + 1 :]
        try:
            metadata = self._parse_simple_yaml(raw_meta)
        except Exception:
            metadata = self._default_metadata(source, body)
        defaults = self._default_metadata(source, body)
        defaults.update({key: value for key, value in metadata.items() if value is not None})
        defaults["tags"] = self._normalize_tags(defaults.get("tags", ""))
        return defaults, body

    def search_mode(self) -> str:
        return "chroma" if self.provider_ready and self.vector_store is not None else "keyword_fallback"

    def _load_single_file(
        self,
        file_path: Path,
        *,
        include_draft: bool = False,
        include_deprecated: bool = False,
    ) -> list[Document]:
        suffix = file_path.suffix.lower()
        source = self._relative_source(file_path)

        if suffix in {".md", ".txt"}:
            raw = file_path.read_text(encoding="utf-8")
            metadata, body = self.parse_front_matter(raw, source=source)
            metadata.update(self._document_runtime_metadata(source, body, metadata))
            metadata["status"] = self.get_effective_status(metadata)
            if not self._status_allowed(metadata["status"], include_draft, include_deprecated):
                return []
            return [Document(page_content=body, metadata=metadata)]

        if suffix == ".pdf":
            docs = PyPDFLoader(str(file_path)).load()
            for doc in docs:
                metadata = self._default_metadata(source, doc.page_content)
                metadata.update(self._document_runtime_metadata(source, doc.page_content, metadata))
                metadata["status"] = self.get_effective_status(metadata)
                doc.metadata.update(metadata)
            return [
                doc
                for doc in docs
                if self._status_allowed(str(doc.metadata.get("status", "active")), include_draft, include_deprecated)
            ]

        return []

    def get_effective_status(self, doc_metadata: dict[str, Any]) -> str:
        status = str(doc_metadata.get("status", "active") or "active")
        key = self._override_key(str(doc_metadata.get("doc_id", "")), str(doc_metadata.get("version", "")))
        override = self._load_version_overrides().get(key)
        if override:
            doc_metadata["deprecated_at"] = override.get("deprecated_at", doc_metadata.get("deprecated_at", ""))
            return str(override.get("status", status))
        return status

    def _document_runtime_metadata(self, source: str, body: str, metadata: dict[str, Any]) -> dict[str, Any]:
        return {
            "source": source,
            "category": self._category_from_path(source),
            "document_hash": self._sha256(body),
            "doc_id": metadata.get("doc_id") or self._slug_from_path(source),
            "title": metadata.get("title") or self._title_from_source(source),
            "version": metadata.get("version") or "v1.0.0",
            "owner": metadata.get("owner") or "unknown",
            "effective_from": metadata.get("effective_from") or "",
            "deprecated_at": metadata.get("deprecated_at") or "",
            "tags": self._normalize_tags(metadata.get("tags") or self._tags_from_path(source)),
        }

    def _default_metadata(self, source: str, content: str) -> dict[str, Any]:
        return {
            "doc_id": self._slug_from_path(source),
            "title": self._title_from_source(source),
            "version": "v1.0.0",
            "status": "active",
            "owner": "unknown",
            "effective_from": "",
            "deprecated_at": "",
            "tags": self._normalize_tags(self._tags_from_path(source)),
            "source": source,
            "document_hash": self._sha256(content),
            "category": self._category_from_path(source),
        }

    @staticmethod
    def _parse_simple_yaml(raw: str) -> dict[str, Any]:
        result: dict[str, Any] = {}
        lines = raw.splitlines()
        index = 0
        while index < len(lines):
            line = lines[index].rstrip()
            if not line.strip() or line.lstrip().startswith("#"):
                index += 1
                continue
            if ":" not in line:
                index += 1
                continue
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            if value == "":
                values = []
                cursor = index + 1
                while cursor < len(lines) and lines[cursor].strip().startswith("- "):
                    values.append(lines[cursor].strip()[2:].strip().strip('"').strip("'"))
                    cursor += 1
                result[key] = values if values else ""
                index = cursor
                continue
            result[key] = value.strip('"').strip("'")
            index += 1
        return result

    def _keyword_retrieve(
        self,
        query: str,
        top_k: int | None = None,
        category: QuestionCategory | None = None,
        include_deprecated: bool = False,
    ) -> list[RetrievedChunk]:
        documents = self.load_documents(include_draft=False, include_deprecated=include_deprecated)
        documents = self.split_documents(documents)
        query_terms = self._query_terms(query)
        if not query_terms:
            return []

        scored: list[tuple[Document, float]] = []
        for doc in documents:
            status = str(doc.metadata.get("status", "active"))
            if status == "draft":
                continue
            if status == "deprecated" and not include_deprecated:
                continue
            haystack = " ".join(
                [
                    doc.page_content,
                    str(doc.metadata.get("title", "")),
                    str(doc.metadata.get("tags", "")),
                    str(doc.metadata.get("doc_id", "")),
                ]
            ).lower()
            score = sum(1.0 for term in query_terms if term in haystack)
            if score > 0:
                scored.append((doc, score))

        scored.sort(key=lambda item: item[1], reverse=True)
        return self._to_retrieved_chunks(scored[: top_k or self.top_k])

    @staticmethod
    def _query_terms(query: str) -> list[str]:
        terms = [term.lower() for term in re.split(r"[\s,，。；;:/?&=_\-]+", query) if len(term.strip()) >= 2]
        compact = re.sub(r"\s+", "", query.lower())
        for token in ["知识库", "问答", "检索", "不准确", "429", "403", "504", "timeout", "rate", "limit", "rag"]:
            if token in compact or token in query.lower():
                terms.append(token)
        return list(dict.fromkeys(terms))

    @staticmethod
    def _to_retrieved_chunks(docs_with_scores: list[tuple[Document, float]]) -> list[RetrievedChunk]:
        chunks: list[RetrievedChunk] = []
        for doc, score in docs_with_scores:
            metadata = doc.metadata
            page = metadata.get("page")
            chunks.append(
                RetrievedChunk(
                    content=doc.page_content,
                    source=str(metadata.get("source", "unknown")),
                    category=str(metadata.get("category", "general")),
                    score=float(score) if score is not None else None,
                    page=page if isinstance(page, int) else None,
                    doc_id=str(metadata.get("doc_id", "")),
                    title=str(metadata.get("title", "")),
                    version=str(metadata.get("version", "v1.0.0")),
                    status=str(metadata.get("status", "active")),
                    chunk_index=metadata.get("chunk_index") if isinstance(metadata.get("chunk_index"), int) else None,
                    chunk_id=str(metadata.get("chunk_id", "")),
                    content_hash=str(metadata.get("content_hash", "")),
                    document_hash=str(metadata.get("document_hash", "")),
                    effective_from=str(metadata.get("effective_from", "")),
                    deprecated_at=str(metadata.get("deprecated_at", "")),
                    tags=str(metadata.get("tags", "")),
                )
            )
        return chunks

    @staticmethod
    def _format_context(chunks: list[RetrievedChunk]) -> str:
        return "\n\n".join(
            f"[{index}] source={chunk.source}, doc_id={chunk.doc_id}, version={chunk.version}, "
            f"status={chunk.status}, score={chunk.score}\n{chunk.content}"
            for index, chunk in enumerate(chunks, start=1)
        )

    @staticmethod
    def _format_references(chunks: list[RetrievedChunk]) -> list[dict[str, Any]]:
        return [RAGService._search_result(chunk) for chunk in chunks]

    @staticmethod
    def _search_result(chunk: RetrievedChunk) -> dict[str, Any]:
        return {
            "doc_id": chunk.doc_id,
            "title": chunk.title,
            "version": chunk.version,
            "status": chunk.status,
            "source": chunk.source,
            "category": chunk.category,
            "chunk_index": chunk.chunk_index,
            "chunk_id": chunk.chunk_id,
            "score": chunk.score,
            "content_preview": chunk.content[:500],
            "content_hash": chunk.content_hash,
            "document_hash": chunk.document_hash,
            "effective_from": chunk.effective_from,
            "deprecated_at": chunk.deprecated_at,
            "tags": chunk.tags,
        }

    @staticmethod
    def _chunk_preview(chunk: Document) -> dict[str, Any]:
        metadata = chunk.metadata
        return {
            "chunk_index": metadata.get("chunk_index", 0),
            "length": len(chunk.page_content),
            "source": metadata.get("source", ""),
            "title": metadata.get("title", ""),
            "version": metadata.get("version", "v1.0.0"),
            "status": metadata.get("status", "active"),
            "content_preview": chunk.page_content[:500],
            "content_hash": metadata.get("content_hash", ""),
            "chunk_id": metadata.get("chunk_id", ""),
            "doc_id": metadata.get("doc_id", ""),
        }

    def _fallback_answer(
        self,
        question: str,
        category: QuestionCategory,
        retrieved_chunks: list[RetrievedChunk],
        top_k: int | None = None,
    ) -> dict[str, Any]:
        context_preview = "\n\n".join(
            f"- {chunk.title or chunk.source} ({chunk.version}, {chunk.status})\n  摘要：{chunk.content[:260]}"
            for chunk in retrieved_chunks[:3]
        )
        answer = (
            f"当前问题已识别为 {category.value} 类支持问题。系统已从 active 知识库中检索到相关内容，"
            "当前未配置外部 LLM 或 Embedding API Key，因此返回规则兜底分析。\n\n"
            "建议处理方式：\n"
            "1. 先确认问题影响范围、发生时间、客户环境和复现步骤。\n"
            "2. 根据参考来源中的排障步骤收集 request ID、日志、状态码、请求参数和响应头。\n"
            "3. 如涉及持续超时、权限异常或业务中断，整理升级摘要后提交给对应支持团队。\n\n"
            f"参考知识库片段：\n{context_preview}"
        )
        return {
            "question": question,
            "category": category.value,
            "answer": answer,
            "retrieved_contents": [chunk.to_dict() for chunk in retrieved_chunks],
            "references": self._format_references(retrieved_chunks),
            "metadata": {
                "chunk_size": self.chunk_size,
                "chunk_overlap": self.chunk_overlap,
                "retrieval_top_k": top_k or self.top_k,
                "has_context": True,
                "mode": self.search_mode(),
                "include_deprecated": False,
            },
        }

    def _safe_knowledge_path(self, file_path: str) -> Path:
        base = self.knowledge_dir.resolve()
        target = Path(file_path)
        if not target.is_absolute():
            target = Path.cwd() / target
        resolved = target.resolve()
        if base != resolved and base not in resolved.parents:
            raise ValueError("file_path must be inside the knowledge directory")
        return resolved

    def _relative_source(self, file_path: Path) -> str:
        try:
            return str(file_path.relative_to(Path.cwd())).replace("\\", "/")
        except ValueError:
            return str(file_path).replace("\\", "/")

    @staticmethod
    def _status_allowed(status: str, include_draft: bool, include_deprecated: bool) -> bool:
        if status == "active":
            return True
        if status == "deprecated":
            return include_deprecated
        if status == "draft":
            return include_draft
        return False

    @staticmethod
    def _sha256(content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    @staticmethod
    def _slug_from_path(source: str) -> str:
        stem = Path(source).stem or "manual-input"
        return re.sub(r"[^a-zA-Z0-9]+", "-", stem.lower()).strip("-") or "document"

    @staticmethod
    def _title_from_source(source: str) -> str:
        stem = Path(source).stem or "Manual Input"
        return stem.replace("-", " ").replace("_", " ").title()

    @staticmethod
    def _tags_from_path(source: str) -> list[str]:
        parts = Path(source).parts
        if "knowledge" in parts:
            index = parts.index("knowledge")
            return [part for part in parts[index + 1 : -1] if part]
        return []

    @staticmethod
    def _normalize_tags(tags: Any) -> str:
        if isinstance(tags, list):
            return ",".join(str(tag).strip() for tag in tags if str(tag).strip())
        if isinstance(tags, str):
            return ",".join(part.strip() for part in tags.split(",") if part.strip())
        return ""

    @staticmethod
    def _tags_to_list(tags: Any) -> list[str]:
        if isinstance(tags, list):
            return [str(tag) for tag in tags]
        return [part.strip() for part in str(tags or "").split(",") if part.strip()]

    @staticmethod
    def _override_key(doc_id: str, version: str) -> str:
        return f"{doc_id}::{version}"

    @staticmethod
    def _load_version_overrides() -> dict[str, Any]:
        if not VERSION_OVERRIDE_FILE.exists():
            return {}
        try:
            return json.loads(VERSION_OVERRIDE_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}

    @staticmethod
    def _count_statuses(documents: list[Document]) -> dict[str, int]:
        counts = {"active": 0, "deprecated": 0, "draft": 0}
        for doc in documents:
            status = str(doc.metadata.get("status", "active"))
            if status in counts:
                counts[status] += 1
        return counts

    @staticmethod
    def _category_from_path(source: str) -> str:
        normalized = source.lower().replace("\\", "/")
        path_parts = set(normalized.split("/"))
        if {"api", "ai-support", "support-process", "web-app", "deployment"} & path_parts:
            return QuestionCategory.OTHER.value
        path_aliases = {
            QuestionCategory.CDN: {"cdn"},
            QuestionCategory.DNS: {"dns"},
            QuestionCategory.HTTPS: {"https", "ssl", "tls"},
            QuestionCategory.VIDEO_PLAYBACK: {"video", "视频播放", "playback"},
            QuestionCategory.KUBERNETES: {"kubernetes", "k8s"},
            QuestionCategory.OTHER: {"llm", "general", "other", "其他"},
        }
        for category, aliases in path_aliases.items():
            if aliases & path_parts:
                return category.value
        return QuestionCategory.OTHER.value

    def _build_vector_store(self) -> Chroma:
        if self.embeddings is None:
            raise RuntimeError("Embedding provider is not configured")
        return Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.chroma_dir,
        )

    @staticmethod
    def _provider_is_ready() -> bool:
        provider = os.getenv("LLM_PROVIDER", "rule").lower()
        embedding_provider = os.getenv("EMBEDDING_PROVIDER", "local").lower()
        if provider in {"rule", "local", "none"} or embedding_provider in {"rule", "local", "none"}:
            return False
        llm_key = bool(os.getenv("DASHSCOPE_API_KEY")) if provider == "qwen" else bool(os.getenv("OPENAI_API_KEY"))
        embedding_key = (
            bool(os.getenv("DASHSCOPE_API_KEY"))
            if embedding_provider == "qwen"
            else bool(os.getenv("OPENAI_API_KEY"))
        )
        return llm_key and embedding_key

    @staticmethod
    def _build_embeddings():  # type: ignore[no-untyped-def]
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
        provider = os.getenv("LLM_PROVIDER", "openai").lower()
        if provider == "qwen":
            return ChatOpenAI(
                model=os.getenv("QWEN_CHAT_MODEL", "qwen-plus"),
                api_key=os.getenv("DASHSCOPE_API_KEY"),
                base_url=os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
                temperature=float(os.getenv("LLM_TEMPERATURE", "0.2")),
            )
        return ChatOpenAI(
            model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.2")),
        )
