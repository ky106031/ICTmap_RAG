from typing import Any

import streamlit as st

from document_pipeline import run_document_rag
from rag_pipeline import run_pipeline


# ============================================================
# ページ設定
# ============================================================

st.set_page_config(
    page_title="理科ICT授業支援システム",
    page_icon="🔬",
    layout="centered",
)


# ============================================================
# CSS
# ============================================================

def apply_custom_css() -> None:

    st.markdown(
        """
<style>

:root {
    --primary: #176579;
    --primary-dark: #124b5a;
    --text-main: #192b35;
    --text-sub: #6f7e87;
    --border: #dce5e8;
}

.stApp {
    background:
        linear-gradient(
            180deg,
            #f3f7f8 0px,
            #f8fafb 310px,
            #f8fafb 100%
        );
}

.block-container {
    max-width: 980px;
    padding-top: 1.6rem;
    padding-bottom: 8rem;
}

p {
    line-height: 1.7;
}

/* Header */

.st-key-app_header {
    margin-bottom: 2.5rem;
    padding: 1.7rem 2rem;
    border-radius: 22px;

    background:
        linear-gradient(
            135deg,
            #164553,
            #176579 58%,
            #268799
        );

    box-shadow:
        0 16px 44px
        rgba(22,74,88,.14);
}

.st-key-app_header h1 {
    color: white !important;
    font-size: 2.5rem !important;
    margin-bottom: .4rem !important;
}

.st-key-app_header p {
    color:
        rgba(255,255,255,.82)
        !important;
}

/* Cards */

div[class*="st-key-practice_card_"] {
    margin-bottom: .7rem;
}

div[class*="st-key-practice_card_"]
div[data-testid="stVerticalBlock"] {
    gap: .55rem !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    border:
        1px solid #dce5e8 !important;

    border-radius:
        16px !important;

    background:
        white !important;

    box-shadow:
        0 5px 18px
        rgba(30,60,72,.04);
}

div[class*="st-key-practice_card_"] h3 {
    color:
        #176579 !important;

    font-size:
        1.15rem !important;
}

/* checkbox */

div[class*="st-key-practice_card_"]
div[data-testid="stCheckbox"] {
    padding:
        .55rem .75rem;

    border-radius:
        9px;

    background:
        #eef7f8;
}

/* Selected area */

.st-key-selected_practices {
    margin:
        1rem 0 1.5rem;

    padding:
        1rem 1.1rem;

    border:
        1px solid #d6e5e8;

    border-radius:
        13px;

    background:
        #f0f8f9;
}

.st-key-selected_practices h4 {
    margin-bottom:
        .4rem !important;

    color:
        #176579 !important;
}

/* Chat */

div[data-testid="stChatMessage"] {
    margin-bottom:
        .7rem;

    border:
        1px solid #e1e8ea;

    border-radius:
        14px;

    background:
        white;
}

/* Chat input */

div[data-testid="stChatInput"] {
    border-radius:
        14px !important;
}

/* Sticky chat area background */

[data-testid="stBottom"] {
    background:
        linear-gradient(
            to top,
            #f8fafb 75%,
            rgba(248,250,251,0)
        );
}

/* Answer headings */

div[data-testid="stChatMessage"] h2 {
    font-size:
        1.45rem !important;

    color:
        #173b47 !important;
}

div[data-testid="stChatMessage"] h3 {
    font-size:
        1.25rem !important;

    color:
        #173b47 !important;
}

hr {
    margin:
        1.7rem 0 !important;
}

</style>
        """,
        unsafe_allow_html=True,
    )


apply_custom_css()


# ============================================================
# Session State
# ============================================================

DEFAULT_STATE = {
    "initial_query": "",
    "practice_candidates": [],
    "selected_practice_ids": [],
    "research_messages": [],
    "has_generated_candidates": False,
    "pending_graph_query": None,
    "pending_document_query": None,
    "selection_error": None,
}


for key, value in DEFAULT_STATE.items():

    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# State
# ============================================================

def reset_all() -> None:

    # checkboxのwidget stateも削除
    for key in list(
        st.session_state.keys()
    ):

        if key.startswith(
            "select_practice_"
        ):
            del st.session_state[key]

    for key, value in (
        DEFAULT_STATE.items()
    ):

        st.session_state[key] = (
            value.copy()
            if isinstance(
                value,
                list,
            )
            else value
        )


def update_selection(
    practice_id: str,
) -> None:

    widget_key = (
        f"select_practice_{practice_id}"
    )

    selected = set(
        st.session_state.selected_practice_ids
    )

    if st.session_state.get(
        widget_key,
        False,
    ):

        selected.add(
            practice_id
        )

    else:

        selected.discard(
            practice_id
        )

    st.session_state.selected_practice_ids = list(
        selected
    )


# ============================================================
# Helpers
# ============================================================

def join_values(
    values: list[Any],
) -> str:

    return "、".join(
        str(value).strip()
        for value in values
        if str(value).strip()
    )


def get_selected_candidates() -> list[
    dict[str, Any]
]:

    selected_ids = set(
        st.session_state.selected_practice_ids
    )

    return [
        candidate
        for candidate
        in st.session_state.practice_candidates
        if candidate.get(
            "practice_id"
        )
        in selected_ids
    ]


# ============================================================
# Error
# ============================================================

def display_processing_error(
    error: Exception,
    process_name: str,
) -> None:

    text = str(
        error
    )

    if (
        "429" in text
        or "RESOURCE_EXHAUSTED" in text
    ):

        st.warning(
            "現在AIの利用が混み合っています。"
            "少し時間を空けてから再度お試しください。"
        )

    elif (
        "503" in text
        or "UNAVAILABLE" in text
    ):

        st.warning(
            "現在AIへのアクセスが混み合っています。"
            "しばらくしてから再度お試しください。"
        )

    else:

        st.error(
            f"{process_name}中に"
            "エラーが発生しました。"
        )

    with st.expander(
        "エラーの詳細"
    ):

        st.code(
            text
        )


# ============================================================
# Header
# ============================================================

def display_header() -> None:

    with st.container(
        key="app_header"
    ):

        st.caption(
            "研究知見 × 授業づくり"
        )

        st.title(
            "理科ICT授業支援システム"
        )

        st.write(
            "ICTを活用した理科教育研究を検索し、"
            "複数の実践を横断しながら"
            "授業づくりについて相談できます。"
        )


# ============================================================
# GraphRAG処理
# ============================================================

def process_pending_graph_query() -> None:

    query = (
        st.session_state.pending_graph_query
    )

    if not query:
        return

    try:

        with st.spinner(
            "ICT活用実践を探索しています..."
        ):

            result = run_pipeline(
                user_query=query
            )

        candidates = result.get(
            "practice_candidates",
            [],
        )

        st.session_state.practice_candidates = (
            candidates
        )

        st.session_state.has_generated_candidates = True

        st.session_state.pending_graph_query = None

    except Exception as error:

        st.session_state.pending_graph_query = None

        display_processing_error(
            error,
            "実践の検索",
        )


# ============================================================
# Document RAG処理
# ============================================================

def process_pending_document_query() -> None:

    pending = (
        st.session_state.pending_document_query
    )

    if not pending:
        return

    try:

        with st.spinner(
            "選択した論文を横断して確認しています..."
        ):

            result = run_document_rag(
                query=pending[
                    "query"
                ],
                paper_ids=pending[
                    "paper_ids"
                ],
                paper_labels=pending[
                    "paper_labels"
                ],
                top_k=3,
            )

        st.session_state.research_messages.append(
            {
                "role": "assistant",
                "content": result[
                    "answer"
                ],
                "sources": result.get(
                    "sources",
                    [],
                ),
            }
        )

        st.session_state.pending_document_query = None

    except Exception as error:

        st.session_state.pending_document_query = None

        display_processing_error(
            error,
            "回答の作成",
        )


# ============================================================
# Practice Card
# ============================================================

def display_practice_card(
    candidate: dict[str, Any],
) -> None:

    index = candidate.get(
        "index",
        "",
    )

    practice_id = str(
        candidate.get(
            "practice_id",
            "",
        )
    )

    title = candidate.get(
        "title",
        "タイトル不明",
    )

    author = str(
        candidate.get(
            "author",
            "",
        )
    )

    year = str(
        candidate.get(
            "year",
            "",
        )
    )

    with st.container(
        border=True,
        key=(
            f"practice_card_"
            f"{index}_"
            f"{practice_id}"
        ),
    ):

        st.markdown(
            f"### 実践 {index}"
        )

        st.markdown(
            f"#### {title}"
        )

        bibliography = join_values(
            [
                author,
                f"{year}年"
                if year
                else "",
            ]
        )

        if bibliography:
            st.write(
                bibliography
            )

        cols = st.columns(
            3
        )

        with cols[0]:
            st.markdown(
                "**学年**"
            )
            st.write(
                candidate.get(
                    "grade"
                )
                or "記載なし"
            )

        with cols[1]:
            st.markdown(
                "**領域**"
            )
            st.write(
                candidate.get(
                    "field"
                )
                or "記載なし"
            )

        with cols[2]:
            st.markdown(
                "**単元**"
            )
            st.write(
                candidate.get(
                    "unit"
                )
                or "記載なし"
            )

        ict = join_values(
            [
                *candidate.get(
                    "hardware",
                    [],
                ),
                *candidate.get(
                    "software",
                    [],
                ),
            ]
        )

        if ict:

            st.markdown(
                "**ICT**"
            )

            st.write(
                ict
            )

        effects = candidate.get(
            "effects",
            [],
        )

        if effects:

            st.markdown(
                "**この実践で確認されたこと**"
            )

            for effect in effects:

                st.markdown(
                    f"✓ {effect}"
                )

        widget_key = (
            f"select_practice_"
            f"{practice_id}"
        )

        if widget_key not in st.session_state:

            st.session_state[
                widget_key
            ] = (
                practice_id
                in st.session_state.selected_practice_ids
            )

        st.checkbox(
            "この実践を参考にする",
            key=widget_key,
            on_change=update_selection,
            args=(
                practice_id,
            ),
        )


# ============================================================
# Selected
# ============================================================

def display_selected_practices() -> None:

    selected = get_selected_candidates()

    with st.container(
        key="selected_practices"
    ):

        st.markdown(
            "#### 選択中の実践"
        )

        if not selected:

            st.write(
                "深掘りしたい実践を"
                "1件以上選択してください。"
            )

            return

        labels = [
            f"実践{candidate['index']}"
            for candidate
            in selected
        ]

        st.write(
            "・".join(
                labels
            )
        )

        st.caption(
            f"{len(selected)}件の実践を横断して"
            "質問できます。"
        )


# ============================================================
# Chat Message
# ============================================================

def display_research_messages() -> None:

    for message in (
        st.session_state.research_messages
    ):

        with st.chat_message(
            message["role"]
        ):

            st.markdown(
                message["content"]
            )

            sources = message.get(
                "sources",
                [],
            )

            if (
                message["role"]
                == "assistant"
                and sources
            ):

                with st.expander(
                    "回答の根拠を確認する"
                ):

                    for source in sources:

                        label = source.get(
                            "practice_label",
                            "論文",
                        )

                        chunk_index = (
                            source.get(
                                "chunk_index",
                                "",
                            )
                        )

                        st.markdown(
                            f"- **{label}** "
                            f"（本文部分 {chunk_index}）"
                        )


# ============================================================
# 描画前のPending処理
# ============================================================

process_pending_graph_query()
process_pending_document_query()


# ============================================================
# UI
# ============================================================

display_header()


# 初回説明
if not (
    st.session_state.has_generated_candidates
):

    st.markdown(
        "## 授業づくりについて相談する"
    )

    st.write(
        "学年、単元、使いたいICT、"
        "期待する学習効果などを"
        "自由な文章で入力してください。"
    )

    if (
        st.session_state.initial_query
    ):

        with st.chat_message(
            "user"
        ):

            st.markdown(
                st.session_state.initial_query
            )


# GraphRAG結果表示
else:

    if (
        st.session_state.initial_query
    ):

        with st.chat_message(
            "user"
        ):

            st.markdown(
                st.session_state.initial_query
            )

    st.divider()

    st.markdown(
        "## おすすめの授業実践"
    )

    st.write(
        f"{len(st.session_state.practice_candidates)}件の"
        "実践が見つかりました。"
        "参考にしたい実践を選択してください。"
    )

    for candidate in (
        st.session_state.practice_candidates
    ):

        display_practice_card(
            candidate
        )

    display_selected_practices()

    st.divider()

    st.markdown(
        "## 選択した実践について相談する"
    )

    st.caption(
        "1件の実践の深掘りだけでなく、"
        "複数実践の比較や、研究知見を組み合わせた"
        "新しい授業案についても質問できます。"
    )

    if (
        st.session_state.selection_error
    ):

        st.warning(
            st.session_state.selection_error
        )

        st.session_state.selection_error = None

    display_research_messages()

    st.divider()

    if st.button(
        "最初からやり直す",
        use_container_width=False,
    ):

        reset_all()

        st.rerun()


# ============================================================
# 固定チャット入力
# ============================================================

if (
    st.session_state.has_generated_candidates
):

    placeholder = (
        "選択した実践について質問してください"
    )

else:

    placeholder = (
        "授業づくりについて相談してください"
    )


user_input = st.chat_input(
    placeholder
)


# ============================================================
# Chat Input処理
# ============================================================

if user_input:

    normalized_input = (
        user_input.strip()
    )

    if normalized_input:

        # 初回 → GraphRAG
        if not (
            st.session_state.has_generated_candidates
        ):

            st.session_state.initial_query = (
                normalized_input
            )

            st.session_state.pending_graph_query = (
                normalized_input
            )

            st.rerun()

        # 2回目以降 → Document RAG
        else:

            selected_candidates = (
                get_selected_candidates()
            )

            if not selected_candidates:

                st.session_state.selection_error = (
                    "質問する前に、参考にしたい実践を"
                    "1件以上選択してください。"
                )

                st.rerun()

            paper_ids = [
                str(
                    candidate.get(
                        "paper_id",
                        "",
                    )
                )
                for candidate
                in selected_candidates
                if candidate.get(
                    "paper_id"
                )
            ]

            paper_labels = {
                str(
                    candidate[
                        "paper_id"
                    ]
                ):
                (
                    f"実践{candidate['index']}："
                    f"{candidate['title']}"
                )
                for candidate
                in selected_candidates
                if candidate.get(
                    "paper_id"
                )
            }

            st.session_state.research_messages.append(
                {
                    "role": "user",
                    "content": normalized_input,
                }
            )

            st.session_state.pending_document_query = {
                "query": normalized_input,
                "paper_ids": paper_ids,
                "paper_labels": paper_labels,
            }

            st.rerun()