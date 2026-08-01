# 理科ICT授業実践アシスタント

理科におけるICT活用授業実践を提案し、選択した実践について論文本文をもとに詳しく質問できるWebアプリケーションです。

本システムでは、授業実践の候補提示にGraphRAG、選択した論文の詳細確認にDocument RAGを利用しています。

## 主な機能

- 学年、領域、単元、ICT機器、ICTソフトウェア、期待する教育効果などをもとに授業実践を提案
- 提案された実践をカード形式で表示
- 気になる実践を展開し、その場で詳しく質問
- 論文本文を根拠とした回答生成
- 実践ごとの対話履歴の保持

## システム構成

- フロントエンド: Streamlit
- 生成AI: Gemini API
- Knowledge Graph: Neo4j
- ベクトルデータベース: ChromaDB
- 授業実践の候補提示: GraphRAG
- 論文本文の深掘り: Document RAG

## ディレクトリ構成

```text
ICTmap_RAG/
├── src/
│   ├── app.py
│   ├── rag_pipeline.py
│   ├── graph_retriever.py
│   ├── graph_context_builder.py
│   ├── document_pipeline.py
│   ├── document_retriever.py
│   ├── document_context_builder.py
│   └── document_answer.py
├── data/
│   ├── chroma_db/
│   ├── cleaned_text/
│   └── knowledge_graph.xlsx
├── requirements.txt
├── runtime.txt
├── .gitignore
└── README.md