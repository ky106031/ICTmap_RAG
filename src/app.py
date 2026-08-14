import json
import time
from pathlib import Path
from typing import Any

import streamlit as st


# ============================================================
# 基本設定
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

DEMO_BACKUP_DIR = (
    BASE_DIR
    / "data"
    / "demo_backup"
)

PRACTICE_SEARCH_PATH = (
    DEMO_BACKUP_DIR
    / "practice_search.json"
)

DOCUMENT_ANSWER_01_PATH = (
    DEMO_BACKUP_DIR
    / "document_answer_01.json"
)

DOCUMENT_ANSWER_02_PATH = (
    DEMO_BACKUP_DIR
    / "document_answer_02.json"
)

# 保存済みデータを読み込む際の短い待機時間。
# 外部API処理を模倣する目的ではなく、
# UIの切り替わりを自然にするための待機。
PRACTICE_LOADING_SECONDS = 4.5
DOCUMENT_LOADING_SECONDS = 5.5


# ============================================================
# JSON読み込み
# ============================================================

def load_json(
    path: Path,
) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(
            f"データが見つかりません: {path}"
        )

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as f:
        return json.load(f)


def load_practice_search() -> dict[str, Any]:
    """
    最初のGraphRAG検索結果を読み込む。
    """
    return load_json(
        PRACTICE_SEARCH_PATH
    )


def load_document_answer(
    turn: int,
) -> dict[str, Any]:
    """
    Document RAGの保存済み回答を読み込む。

    Args:
        turn:
            1なら1回目の回答、
            2なら2回目の回答。
    """
    if turn == 1:
        path = DOCUMENT_ANSWER_01_PATH

    elif turn == 2:
        path = DOCUMENT_ANSWER_02_PATH

    else:
        raise ValueError(
            "error"
        )

    return load_json(
        path
    )


# ============================================================
# ページ設定
# ============================================================

st.set_page_config(
    page_title="理科ICT授業実践アシスタント",
    page_icon="🔬",
    layout="centered",
)

st.title(
    "理科ICT授業実践アシスタント"
)

st.caption(
    "授業づくりの条件を入力すると、参考になる実践事例を提案します。"
    "気になる実践については、論文本文をもとに詳しく質問できます。"
)


# ============================================================
# Session State
# ============================================================

if "user_request" not in st.session_state:
    st.session_state.user_request = ""

if "practice_candidates" not in st.session_state:
    st.session_state.practice_candidates = []

if "expanded_practice_id" not in st.session_state:
    st.session_state.expanded_practice_id = None

if "document_messages" not in st.session_state:
    st.session_state.document_messages = {}

if "document_pending_queries" not in st.session_state:
    st.session_state.document_pending_queries = {}

if "has_generated_candidates" not in st.session_state:
    st.session_state.has_generated_candidates = False

if "document_answer_counts" not in st.session_state:
    st.session_state.document_answer_counts = {}


# ============================================================
# 状態操作
# ============================================================

def reset_all() -> None:
    """
    入力内容・実践候補・会話履歴をすべて初期化する。
    """
    st.session_state.user_request = ""

    st.session_state.practice_candidates = []

    st.session_state.expanded_practice_id = None

    st.session_state.document_messages = {}

    st.session_state.document_pending_queries = {}

    st.session_state.document_answer_counts = {}

    st.session_state.has_generated_candidates = False


def initialize_document_state(
    practice_id: str,
) -> None:
    """
    practice_idごとの会話状態を初期化する。
    """
    if (
        practice_id
        not in st.session_state.document_messages
    ):
        st.session_state.document_messages[
            practice_id
        ] = []

    if (
        practice_id
        not in st.session_state.document_pending_queries
    ):
        st.session_state.document_pending_queries[
            practice_id
        ] = None

    if (
        practice_id
        not in st.session_state.document_answer_counts
    ):
        st.session_state.document_answer_counts[
            practice_id
        ] = 0


def toggle_practice(
    practice_id: str,
) -> None:
    """
    実践カードの展開・閉じるを切り替える。
    """
    if (
        st.session_state.expanded_practice_id
        == practice_id
    ):
        st.session_state.expanded_practice_id = None

    else:
        st.session_state.expanded_practice_id = (
            practice_id
        )

    initialize_document_state(
        practice_id=practice_id
    )


# ============================================================
# エラー表示
# ============================================================

def display_demo_error(
    error: Exception,
) -> None:
    st.error(
        "データを読み込めませんでした。"
    )

    with st.expander(
        "エラーの詳細"
    ):
        st.code(
            str(error)
        )


# ============================================================
# 表示用ヘルパー
# ============================================================

def join_values(
    values: list[Any],
) -> str:
    """
    空の値を除外して「、」で連結する。
    """
    normalized_values = [
        str(value).strip()
        for value in values
        if str(value).strip()
    ]

    return "、".join(
        normalized_values
    )


def display_basic_information(
    candidate: dict[str, Any],
) -> None:
    """
    学年・領域・単元を3列で表示する。
    """
    columns = st.columns(
        3
    )

    with columns[0]:
        st.markdown(
            "**学年**"
        )

        st.write(
            candidate.get("grade")
            or "記載なし"
        )

    with columns[1]:
        st.markdown(
            "**領域**"
        )

        st.write(
            candidate.get("field")
            or "記載なし"
        )

    with columns[2]:
        st.markdown(
            "**単元**"
        )

        st.write(
            candidate.get("unit")
            or "記載なし"
        )


def display_document_message(
    message: dict[str, Any],
) -> None:
    role = message.get(
        "role",
        "assistant",
    )

    content = str(
        message.get(
            "content",
            "",
        )
    ).strip()

    if not content:
        return

    with st.chat_message(
        role
    ):
        st.markdown(
            content
        )

        sources = message.get(
            "sources",
            [],
        )

        if (
            role == "assistant"
            and sources
        ):
            with st.expander(
                "回答の根拠を確認する"
            ):
                for source in sources:
                    chunk_index = source.get(
                        "chunk_index",
                        "",
                    )

                    if chunk_index == "":
                        st.markdown(
                            "- 論文本文の該当箇所"
                        )

                    else:
                        st.markdown(
                            "- 論文本文の該当箇所"
                            f"（部分 {chunk_index}）"
                        )


# ============================================================
# Document RAG会話
# ============================================================

def display_document_conversation(
    candidate: dict[str, Any],
) -> None:
    practice_id = str(
        candidate.get(
            "practice_id",
            "",
        )
    ).strip()

    paper_id = str(
        candidate.get(
            "paper_id",
            "",
        )
    ).strip()

    if not practice_id:
        st.warning(
            "この実践を識別する情報を"
            "確認できません。"
        )
        return

    if not paper_id:
        st.warning(
            "この実践に対応する論文本文を"
            "確認できません。"
        )
        return

    initialize_document_state(
        practice_id=practice_id
    )

    messages = (
        st.session_state.document_messages[
            practice_id
        ]
    )

    pending_query = (
        st.session_state.document_pending_queries[
            practice_id
        ]
    )

    answer_count = (
        st.session_state.document_answer_counts[
            practice_id
        ]
    )

    st.divider()

    st.markdown(
        "### この実践について質問する"
    )

    st.caption(
        "選択した実践の論文本文をもとに回答します。"
        "本文を参考にした授業への応用についても"
        "相談できます。"
    )

    if (
        not messages
        and not pending_query
    ):
        st.info(
            "例えば、"
            "「生徒はどのような活動をしましたか？」"
            "「ICTをどのように活用しましたか？」"
            "「別の学年へ応用するとしたら、"
            "どのような授業が考えられますか？」"
            "などと質問できます。"
        )

    # --------------------------------------------------------
    # 過去の会話履歴
    # --------------------------------------------------------

    for message in messages:
        display_document_message(
            message=message
        )

    # --------------------------------------------------------
    # 回答待ちの質問がある場合
    # --------------------------------------------------------

    if pending_query:
        try:
            next_turn = (
                answer_count + 1
            )

            if next_turn > 2:
                st.session_state.document_pending_queries[
                    practice_id
                ] = None

                st.info(
                    "error"
                )

                return

            with st.chat_message(
                "assistant"
            ):
                with st.spinner(
                    "ICTマップを探索しています..."
                ):
                    time.sleep(
                        DOCUMENT_LOADING_SECONDS
                    )

                    demo_data = (
                        load_document_answer(
                            turn=next_turn
                        )
                    )

            answer = str(
                demo_data.get(
                    "answer",
                    "",
                )
            ).strip()

            sources = demo_data.get(
                "sources",
                [],
            )

            if not answer:
                raise RuntimeError(
                    "error"
                )

            assistant_message = {
                "role": "assistant",
                "content": answer,
                "sources": sources,
            }

            messages.append(
                assistant_message
            )

            st.session_state.document_answer_counts[
                practice_id
            ] = next_turn

            st.session_state.document_pending_queries[
                practice_id
            ] = None

            st.rerun()

        except Exception as error:
            st.session_state.document_pending_queries[
                practice_id
            ] = None

            display_demo_error(
                error=error
            )

    # --------------------------------------------------------
    # 質問入力欄
    # --------------------------------------------------------

    user_question = st.chat_input(
        "この実践について質問してください",
        key=(
            f"document_chat_input_{practice_id}"
        ),
    )

    if not user_question:
        return

    normalized_question = (
        user_question.strip()
    )

    if not normalized_question:
        st.warning(
            "質問を入力してください。"
        )
        return

    messages.append(
        {
            "role": "user",
            "content": normalized_question,
        }
    )

    st.session_state.document_pending_queries[
        practice_id
    ] = normalized_question

    st.rerun()


# ============================================================
# 実践カード
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
            f"practice_{index}",
        )
    ).strip()

    paper_id = str(
        candidate.get(
            "paper_id",
            "",
        )
    ).strip()

    title = (
        candidate.get(
            "title"
        )
        or "タイトル不明"
    )

    author = str(
        candidate.get(
            "author",
            "",
        )
    ).strip()

    year = str(
        candidate.get(
            "year",
            "",
        )
    ).strip()

    hardware = candidate.get(
        "hardware",
        [],
    )

    software = candidate.get(
        "software",
        [],
    )

    effects = candidate.get(
        "effects",
        [],
    )

    is_expanded = (
        st.session_state.expanded_practice_id
        == practice_id
    )

    with st.container(
        border=True
    ):
        st.markdown(
            f"### 実践{index}"
        )

        st.markdown(
            f"**{title}**"
        )

        bibliographic_values = [
            author,
            f"{year}年" if year else "",
        ]

        bibliographic_text = join_values(
            bibliographic_values
        )

        if bibliographic_text:
            st.caption(
                bibliographic_text
            )

        display_basic_information(
            candidate
        )

        ict_values = [
            *hardware,
            *software,
        ]

        ict_text = join_values(
            ict_values
        )

        if ict_text:
            st.markdown(
                f"**使用したICT：** {ict_text}"
            )

        if effects:
            st.markdown(
                "**この実践で確認されたこと**"
            )

            for effect in effects:
                st.markdown(
                    f"- {effect}"
                )

        button_text = (
            "閉じる"
            if is_expanded
            else "この実践を詳しく見る"
        )

        if st.button(
            button_text,
            key=(
                f"toggle_{practice_id}"
            ),
            disabled=not bool(
                paper_id
            ),
            use_container_width=True,
        ):
            toggle_practice(
                practice_id=practice_id
            )

            st.rerun()

        if not paper_id:
            st.caption(
                "この実践は、現在詳しい内容を"
                "確認できません。"
            )

        if is_expanded:
            display_document_conversation(
                candidate=candidate
            )


# ============================================================
# 最初の相談内容
# ============================================================

def display_request_form() -> None:

    st.markdown(
        "## 授業づくりについて相談する"
    )

    st.write(
        "学年、単元、使いたいICT、"
        "期待する学習効果などを入力してください。"
    )

    with st.form(
        key="practice_request_form",
        clear_on_submit=False,
    ):
        user_request = st.text_area(
            "相談内容",
            value=(
                st.session_state.user_request
            ),
            placeholder=(
                "例：観察に意欲的に取り組めるような"
                "授業にしたいです。"
            ),
            height=120,
        )

        submitted = st.form_submit_button(
            "参考になる実践を提案してもらう",
            use_container_width=True,
        )

    if not submitted:
        return

    normalized_request = (
        user_request.strip()
    )

    if not normalized_request:
        st.warning(
            "相談内容を入力してください。"
        )
        return

    try:
        with st.spinner(
            "..."
        ):
            time.sleep(
                PRACTICE_LOADING_SECONDS
            )

            demo_data = (
                load_practice_search()
            )

        result = demo_data.get(
            "result",
            {},
        )

        practice_candidates = (
            result.get(
                "practice_candidates",
                [],
            )
        )

        if not practice_candidates:
            raise RuntimeError(
                "error"
            )

        st.session_state.user_request = (
            normalized_request
        )

        st.session_state.practice_candidates = (
            practice_candidates
        )

        st.session_state.expanded_practice_id = None

        st.session_state.document_messages = {}

        st.session_state.document_pending_queries = {}

        st.session_state.document_answer_counts = {}

        st.session_state.has_generated_candidates = True

        st.rerun()

    except Exception as error:
        display_demo_error(
            error=error
        )


# ============================================================
# 提案結果
# ============================================================

def display_practice_candidates() -> None:

    if not (
        st.session_state.has_generated_candidates
    ):
        return

    candidates = (
        st.session_state.practice_candidates
    )

    st.divider()

    st.markdown(
        "## おすすめの授業実践"
    )

    if not candidates:
        st.info(
            "実践候補を表示できませんでした。"
        )

    else:
        st.caption(
            f"{len(candidates)}件の実践を提案します。"
            "気になる実践を開くと、"
            "その場で詳しく質問できます。"
        )

        for candidate in candidates:
            display_practice_card(
                candidate=candidate
            )

    st.divider()

    if st.button(
        "相談内容を最初から入力し直す",
        key="reset_all_button",
        use_container_width=True,
    ):
        reset_all()
        st.rerun()


# ============================================================
# 画面表示
# ============================================================

display_request_form()
display_practice_candidates()