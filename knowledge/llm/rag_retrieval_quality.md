# RAG Retrieval Quality Troubleshooting

## Scenario

This document applies when a RAG system retrieves irrelevant context, misses expected documents, cites the wrong source, or produces inaccurate answers because of poor retrieval quality.

## Symptoms

- The expected document exists in the knowledge base but is not returned in Top-K results.
- Retrieved chunks are only loosely related to the question.
- The answer cites the wrong document or misses the key troubleshooting step.
- Newly added knowledge base files are not searchable.
- Similar questions return inconsistent retrieval results.
- Cross-language queries perform worse than expected.

## Possible Causes

- Chunk size is too large or too small, causing incomplete semantic units.
- Chunk overlap is insufficient and important context is split across chunks.
- Embedding model is not suitable for the language or technical domain.
- Metadata filters are too strict or use inconsistent category values.
- Chroma collection was not rebuilt after knowledge base updates.
- Top-K is too small or similarity threshold is too high.
- The user query uses informal wording that does not match knowledge base terminology.

## Troubleshooting Steps

1. Log the original question, rewritten query, Top-K chunks, similarity scores, and metadata.
2. Confirm that documents were loaded, split, embedded, and written to the expected Chroma collection.
3. Inspect sample chunks to verify that each chunk contains enough context and source metadata.
4. Tune chunk_size, chunk_overlap, Top-K, and similarity threshold.
5. Check metadata filters such as category, tenant, product, language, or region.
6. Add query rewriting to expand abbreviations, product names, error codes, and synonyms.
7. Consider reranking when Top-K recall is acceptable but ordering is poor.
8. Rebuild the vector index after changing embedding model or chunking strategy.

## Required Information

- User question and expected document.
- Actual Top-K results, scores, and metadata.
- chunk_size, chunk_overlap, Top-K, and similarity threshold.
- Embedding model name and Chroma collection name.
- Knowledge base source file and ingestion logs.
- Metadata filter conditions.

## Escalation Criteria

- The correct chunk exists in Chroma but is consistently ranked very low.
- Retrieval quality drops after changing embedding model, chunking, or index version.
- Metadata filtering may cause cross-tenant leakage or missing authorized content.
- Chroma persistence, collection loading, or vector write behavior appears inconsistent.
