from pathlib import Path
import os
import re

import pandas as pd
from dotenv import load_dotenv
from neo4j import GraphDatabase


load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]
EXCEL_PATH = BASE_DIR / "data" / "knowledge_graph.xlsx"

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "ictmap")


def safe_identifier(value: str) -> str:
    """Neo4jのラベル・リレーション名として安全か確認する"""
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", str(value)):
        raise ValueError(f"Invalid Neo4j identifier: {value}")
    return value


def node_key(label: str) -> str:
    if label == "Paper":
        return "paper_id"
    if label == "Practice":
        return "practice_id"
    return "name"


def clear_database(tx):
    tx.run("MATCH (n) DETACH DELETE n")


def create_node(tx, label: str, key: str, value: str, properties: dict):
    label = safe_identifier(label)

    query = f"""
    MERGE (n:{label} {{{key}: $value}})
    SET n += $properties
    """

    tx.run(query, value=value, properties=properties)


def create_relationship(
    tx,
    source_label: str,
    source_key: str,
    source_value: str,
    target_label: str,
    target_key: str,
    target_value: str,
    rel_type: str,
    properties: dict,
):
    source_label = safe_identifier(source_label)
    target_label = safe_identifier(target_label)
    rel_type = safe_identifier(rel_type)

    query = f"""
    MATCH (s:{source_label} {{{source_key}: $source_value}})
    MATCH (t:{target_label} {{{target_key}: $target_value}})
    MERGE (s)-[r:{rel_type} {{edge_id: $edge_id}}]->(t)
    SET r += $properties
    """

    tx.run(
        query,
        source_value=source_value,
        target_value=target_value,
        edge_id=properties["edge_id"],
        properties=properties,
    )


def main():
    print("Excel読み込み中...")

    papers = pd.read_excel(EXCEL_PATH, sheet_name="Papers").fillna("")
    practices = pd.read_excel(EXCEL_PATH, sheet_name="Practices").fillna("")
    edges = pd.read_excel(EXCEL_PATH, sheet_name="Edges").fillna("")

    print(f"Papers: {len(papers)}")
    print(f"Practices: {len(practices)}")
    print(f"Edges: {len(edges)}")

    driver = GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USER, NEO4J_PASSWORD),
    )

    with driver.session(database=NEO4J_DATABASE) as session:
        print("既存データを削除中...")
        session.execute_write(clear_database)

        print("Paperノード作成中...")
        for _, row in papers.iterrows():
            props = row.to_dict()
            session.execute_write(
                create_node,
                "Paper",
                "paper_id",
                str(row["paper_id"]),
                props,
            )

        print("Practiceノード作成中...")
        for _, row in practices.iterrows():
            props = row.to_dict()
            session.execute_write(
                create_node,
                "Practice",
                "practice_id",
                str(row["practice_id"]),
                props,
            )

        print("Edgesからノード・リレーション作成中...")
        for _, row in edges.iterrows():
            source_label = str(row["source_type"])
            target_label = str(row["target_type"])
            rel_type = str(row["edge_type"])

            source_key = node_key(source_label)
            target_key = node_key(target_label)

            source_value = str(row["source_node"])
            target_value = str(row["target_node"])

            source_props = {
                source_key: source_value,
                "name": source_value,
                "node_type": source_label,
            }

            target_props = {
                target_key: target_value,
                "name": target_value,
                "node_type": target_label,
            }

            session.execute_write(
                create_node,
                source_label,
                source_key,
                source_value,
                source_props,
            )

            session.execute_write(
                create_node,
                target_label,
                target_key,
                target_value,
                target_props,
            )

            rel_props = {
                "edge_id": str(row["edge_id"]),
                "paper_id": str(row["paper_id"]),
                "practice_id": str(row["practice_id"]),
            }

            session.execute_write(
                create_relationship,
                source_label,
                source_key,
                source_value,
                target_label,
                target_key,
                target_value,
                rel_type,
                rel_props,
            )

    driver.close()
    print("Knowledge Graph作成完了！")


if __name__ == "__main__":
    main()