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

    return load_json(
        PRACTICE_SEARCH_PATH
    )


def load_document_answer(
    turn: int,
) -> dict[str, Any]:

    if turn == 1:
        path = DOCUMENT_ANSWER_01_PATH

    elif turn == 2:
        path = DOCUMENT_ANSWER_02_PATH

    else:
        raise ValueError(
            "保存済み回答は2回分までです。"
        )

    return load_json(
        path
    )


# ============================================================
# ページ設定
# ============================================================

st.set_page_config(
    page_title="理科ICT授業支援システム",
    page_icon="🔬",
    layout="centered",
)


# ============================================================
# カスタムCSS
# ============================================================

def apply_custom_css() -> None:

    st.markdown(
        """
<style>

/* =========================================================
   基本
========================================================= */

:root {
    --primary: #176579;
    --primary-dark: #124b5a;
    --primary-soft: #edf6f7;

    --text-main: #192b35;
    --text-sub: #6f7e87;

    --border: #dce5e8;
    --surface: #ffffff;
    --surface-soft: #f7f9fa;
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
    padding-bottom: 5rem;
}

html,
body,
[class*="css"] {
    color: var(--text-main);
}

p {
    line-height: 1.72;
}


/* =========================================================
   上部ヘッダー
========================================================= */

.st-key-app_header {
    margin-bottom: 3rem;

    padding:
        1.75rem
        2rem
        1.8rem
        2rem;

    border-radius: 22px;

    background:
        linear-gradient(
            135deg,
            #164553 0%,
            #176579 58%,
            #268799 100%
        );

    box-shadow:
        0 16px 44px
        rgba(22, 74, 88, 0.14);
}

.st-key-app_header h1 {
    margin-top: 0.45rem !important;
    margin-bottom: 0.45rem !important;

    color: #ffffff !important;

    font-size: 2.55rem !important;
    font-weight: 760 !important;

    line-height: 1.2 !important;
    letter-spacing: -0.045em !important;
}

.st-key-app_header p {
    max-width: 720px;

    margin-bottom: 0 !important;

    color:
        rgba(
            255,
            255,
            255,
            0.82
        ) !important;

    font-size: 0.95rem !important;
    line-height: 1.7;
}

.st-key-app_header
div[data-testid="stCaptionContainer"] p {
    display: inline-block;

    width: auto;

    margin: 0 !important;

    padding:
        0.28rem
        0.7rem;

    border:
        1px solid
        rgba(
            255,
            255,
            255,
            0.22
        );

    border-radius: 999px;

    background:
        rgba(
            255,
            255,
            255,
            0.09
        );

    color:
        rgba(
            255,
            255,
            255,
            0.92
        ) !important;

    font-size: 0.72rem !important;
    font-weight: 700;

    letter-spacing: 0.045em;
}


/* =========================================================
   セクション見出し
========================================================= */

.st-key-request_section {
    margin-bottom: 1.15rem;
}

.st-key-request_section h2,
.st-key-results_header h2 {
    margin-top: 0 !important;
    margin-bottom: 0.3rem !important;

    color: var(--text-main) !important;

    font-size: 1.8rem !important;
    font-weight: 740 !important;

    line-height: 1.3 !important;
    letter-spacing: -0.035em !important;
}

.st-key-request_section p,
.st-key-results_header p {
    margin-bottom: 0 !important;

    color: var(--text-sub) !important;

    font-size: 0.92rem !important;
}


/* =========================================================
   入力フォーム
========================================================= */

div[data-testid="stForm"] {
    padding:
        1.25rem
        1.3rem
        1.2rem;

    border:
        1px solid var(--border);

    border-radius: 17px;

    background:
        rgba(
            255,
            255,
            255,
            0.98
        );

    box-shadow:
        0 7px 26px
        rgba(
            27,
            60,
            73,
            0.045
        );
}

div[data-testid="stTextArea"] label {
    color: #40525c !important;

    font-size: 0.86rem !important;
    font-weight: 670 !important;
}

div[data-testid="stTextArea"] textarea {
    min-height: 126px !important;

    padding:
        0.95rem
        1rem !important;

    border:
        1px solid
        #d9e2e6 !important;

    border-radius:
        12px !important;

    background:
        #f8fafb !important;

    color:
        #1e3039 !important;

    font-size:
        0.98rem !important;

    line-height:
        1.65 !important;

    box-shadow:
        none !important;

    transition:
        border-color 0.15s ease,
        box-shadow 0.15s ease,
        background 0.15s ease;
}

div[data-testid="stTextArea"] textarea:focus {
    border-color:
        #268096 !important;

    background:
        #ffffff !important;

    box-shadow:
        0 0 0 3px
        rgba(
            38,
            128,
            150,
            0.09
        ) !important;
}


/* =========================================================
   フォーム送信ボタン
========================================================= */

.st-key-submit_area {
    margin-top: 0.15rem;
}

.stFormSubmitButton > button {
    min-height: 2.85rem;

    border:
        1px solid
        #176579 !important;

    border-radius:
        10px !important;

    background:
        linear-gradient(
            135deg,
            #176579,
            #268799
        ) !important;

    color:
        #ffffff !important;

    font-size:
        0.9rem !important;

    font-weight:
        680 !important;

    box-shadow:
        0 6px 17px
        rgba(
            23,
            101,
            121,
            0.15
        ) !important;

    transition:
        transform 0.15s ease,
        box-shadow 0.15s ease !important;
}

.stFormSubmitButton > button:hover {
    transform:
        translateY(-1px);

    background:
        linear-gradient(
            135deg,
            #14586a,
            #217b8d
        ) !important;

    color:
        #ffffff !important;

    box-shadow:
        0 8px 20px
        rgba(
            23,
            101,
            121,
            0.19
        ) !important;
}


/* =========================================================
   通常ボタン
========================================================= */

.stButton > button {
    min-height: 2.8rem;

    border:
        1px solid
        #ccd9dd !important;

    border-radius:
        10px !important;

    background:
        #ffffff !important;

    color:
        #2c414b !important;

    font-size:
        0.9rem !important;

    font-weight:
        650 !important;

    box-shadow:
        none !important;

    transition:
        transform 0.15s ease,
        border-color 0.15s ease,
        background 0.15s ease,
        box-shadow 0.15s ease !important;
}

.stButton > button:hover {
    transform:
        translateY(-1px);

    border-color:
        #278397 !important;

    background:
        #f3f9fa !important;

    color:
        #155a6b !important;

    box-shadow:
        0 5px 14px
        rgba(
            25,
            95,
            115,
            0.06
        ) !important;
}


/* =========================================================
   結果見出し
========================================================= */

.st-key-results_header {
    margin-bottom: 1.1rem;
}


/* =========================================================
   実践カード
========================================================= */

div[data-testid="stVerticalBlockBorderWrapper"] {
    overflow: hidden;

    border:
        1px solid
        #dde6e9 !important;

    border-radius:
        17px !important;

    background:
        #ffffff !important;

    box-shadow:
        0 7px 26px
        rgba(
            27,
            60,
            73,
            0.045
        );

    transition:
        border-color 0.16s ease,
        transform 0.16s ease,
        box-shadow 0.16s ease;
}

div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    transform:
        translateY(-1px);

    border-color:
        #c7dadd !important;

    box-shadow:
        0 12px 32px
        rgba(
            27,
            60,
            73,
            0.075
        );
}


/* 実践番号 */

div[class*="st-key-practice_card_"] h3 {
    margin-bottom:
        0.35rem !important;

    color:
        #22788b !important;

    font-size:
        0.76rem !important;

    font-weight:
        760 !important;

    letter-spacing:
        0.08em !important;

    text-transform:
        uppercase;
}


/* 論文タイトル */

div[class*="st-key-practice_card_"] h4 {
    margin-top:
        0 !important;

    margin-bottom:
        0.15rem !important;

    color:
        #172a34 !important;

    font-size:
        1.16rem !important;

    font-weight:
        710 !important;

    line-height:
        1.48 !important;

    letter-spacing:
        -0.015em !important;
}


/* 著者 */

div[class*="st-key-practice_card_"]
div[data-testid="stCaptionContainer"] p {
    color:
        #819099 !important;

    font-size:
        0.82rem !important;
}


/* =========================================================
   学年・領域・単元
========================================================= */

div[class*="st-key-practice_card_"]
div[data-testid="stHorizontalBlock"] {
    gap:
        0.6rem;
}

div[class*="st-key-practice_card_"]
div[data-testid="column"] {
    padding:
        0.62rem
        0.72rem;

    border:
        1px solid
        #e5ebed;

    border-radius:
        10px;

    background:
        #f8fafb;
}

div[class*="st-key-practice_card_"]
div[data-testid="column"] strong {
    color:
        #83929a;

    font-size:
        0.7rem;

    font-weight:
        700;
}

div[class*="st-key-practice_card_"]
div[data-testid="column"] p {
    margin-bottom:
        0 !important;

    color:
        #293c46;

    font-size:
        0.88rem;
}


/* =========================================================
   ICT・教育効果
========================================================= */

div[class*="st-key-practice_card_"]
p strong {
    color:
        #314852;
}


/* =========================================================
   詳細エリア
========================================================= */

.st-key-document_section {
    margin-top: 1rem;
}

.st-key-document_section h3 {
    margin-bottom:
        0.25rem !important;

    color:
        var(--text-main);

    font-size:
        1.48rem !important;

    font-weight:
        720 !important;

    letter-spacing:
        -0.025em !important;
}

.st-key-document_section
div[data-testid="stCaptionContainer"] p {
    color:
        var(--text-sub) !important;

    font-size:
        0.88rem !important;
}


/* =========================================================
   チャット
========================================================= */

div[data-testid="stChatMessage"] {
    padding:
        0.82rem
        0.92rem;

    margin-bottom:
        0.65rem;

    border:
        1px solid
        #e2e9eb;

    border-radius:
        14px;

    background:
        #ffffff;

    box-shadow:
        0 2px 8px
        rgba(
            30,
            60,
            72,
            0.025
        );
}

div[data-testid="stChatMessage"] p {
    line-height:
        1.75;
}

div[data-testid="stChatInput"] {
    border-radius:
        13px;
}


/* =========================================================
   Expander
========================================================= */

div[data-testid="stExpander"] {
    border:
        1px solid
        #e1e8ea !important;

    border-radius:
        11px !important;

    background:
        #fafcfc !important;
}

div[data-testid="stExpander"] summary {
    color:
        #576871;

    font-size:
        0.87rem;

    font-weight:
        620;
}


/* =========================================================
   Alert
========================================================= */

div[data-testid="stAlert"] {
    border-radius:
        11px !important;
}


/* =========================================================
   Divider
========================================================= */

hr {
    margin-top:
        2.4rem !important;

    margin-bottom:
        2.4rem !important;

    border-color:
        #e4eaec !important;
}


/* =========================================================
   Reset
========================================================= */

.st-key-reset_area {
    margin-top:
        0.3rem;
}


/* =========================================================
   モバイル
========================================================= */

@media (
    max-width: 760px
) {

    .block-container {
        padding-top:
            0.9rem;

        padding-left:
            1rem;

        padding-right:
            1rem;
    }

    .st-key-app_header {
        padding:
            1.45rem
            1.3rem;

        margin-bottom:
            2rem;

        border-radius:
            17px;
    }

    .st-key-app_header h1 {
        font-size:
            1.9rem !important;
    }

}

</style>
        """,
        unsafe_allow_html=True,
    )


apply_custom_css()


# ============================================================
# ヘッダー
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
            "ICTを活用した理科教育研究の知見から、"
            "授業づくりの参考となる実践を提案します。"
            "選択した実践については、"
            "論文本文をもとに詳しく質問できます。"
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
# 表示ヘルパー
# ============================================================

def join_values(
    values: list[Any],
) -> str:

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

    columns = st.columns(
        3
    )

    with columns[0]:

        st.markdown(
            "**学年**"
        )

        st.write(
            candidate.get(
                "grade"
            )
            or "記載なし"
        )

    with columns[1]:

        st.markdown(
            "**領域**"
        )

        st.write(
            candidate.get(
                "field"
            )
            or "記載なし"
        )

    with columns[2]:

        st.markdown(
            "**単元**"
        )

        st.write(
            candidate.get(
                "unit"
            )
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

                    chunk_index = (
                        source.get(
                            "chunk_index",
                            "",
                        )
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

    with st.container(
        key="document_section"
    ):

        st.markdown(
            "### この実践について質問する"
        )

        st.caption(
            "選択した実践の論文本文をもとに回答します。"
            "研究知見を別の学年や単元へ応用する相談もできます。"
        )

    if (
        not messages
        and not pending_query
    ):

        st.info(
            "例えば、"
            "「授業展開は？」"
            "「ICTをどのように活用しましたか？」"
            "「別の学年へ応用するとしたら、"
            "どのような授業が考えられますか？」"
            "などと質問できます。"
        )

    # --------------------------------------------------------
    # 会話履歴
    # --------------------------------------------------------

    for message in messages:

        display_document_message(
            message=message
        )

    # --------------------------------------------------------
    # 回答
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

                return

            with st.chat_message(
                "assistant"
            ):

                with st.spinner(
                    "論文本文を確認しています..."
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

            sources = (
                demo_data.get(
                    "sources",
                    [],
                )
            )

            if not answer:

                raise RuntimeError(
                    "保存済み回答が空です。"
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
    # 質問入力
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
        border=True,
        key=(
            f"practice_card_{practice_id}"
        ),
    ):

        st.markdown(
            f"### 実践 {index}"
        )

        st.markdown(
            f"#### {title}"
        )

        bibliographic_values = [
            author,
            f"{year}年"
            if year
            else "",
        ]

        bibliographic_text = (
            join_values(
                bibliographic_values
            )
        )

        if bibliographic_text:

            st.caption(
                bibliographic_text
            )

        display_basic_information(
            candidate
        )

        st.write("")

        ict_values = [
            *hardware,
            *software,
        ]

        ict_text = (
            join_values(
                ict_values
            )
        )

        if ict_text:

            st.markdown(
                "**ICT**"
            )

            st.caption(
                ict_text
            )

        if effects:

            st.markdown(
                "**この実践で確認されたこと**"
            )

            for effect in effects:

                st.markdown(
                    f"✓ {effect}"
                )

        button_text = (
            "閉じる"
            if is_expanded
            else "詳しく見る →"
        )

        button_columns = st.columns(
            [
                2.4,
                1,
            ]
        )

        with button_columns[1]:

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

    with st.container(
        key="request_section"
    ):

        st.markdown(
            "## 授業づくりについて相談する"
        )

        st.write(
            "授業で実現したいことを、自由な文章で入力してください。"
        )

    with st.form(
        key="practice_request_form",
        clear_on_submit=False,
    ):

        user_request = (
            st.text_area(
                "相談内容",
                value=(
                    st.session_state.user_request
                ),
                placeholder=(
                    "例：観察に意欲的に取り組めるような"
                    "授業にしたいです。"
                ),
                height=125,
            )
        )

        submit_columns = st.columns(
            [
                2.1,
                1,
            ]
        )

        with submit_columns[1]:

            submitted = (
                st.form_submit_button(
                    "実践を探す →",
                    use_container_width=True,
                )
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
            "ICT活用実践を探索しています..."
        ):

            time.sleep(
                PRACTICE_LOADING_SECONDS
            )

            demo_data = (
                load_practice_search()
            )

        result = (
            demo_data.get(
                "result",
                {},
            )
        )

        practice_candidates = (
            result.get(
                "practice_candidates",
                [],
            )
        )

        if not practice_candidates:

            raise RuntimeError(
                "実践候補を読み込めませんでした。"
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

    with st.container(
        key="results_header"
    ):

        st.markdown(
            "## おすすめの授業実践"
        )

        st.write(
            f"{len(candidates)}件の実践が見つかりました。"
            "気になる実践を選ぶと、"
            "論文本文をもとに詳しく質問できます。"
        )

    if not candidates:

        st.info(
            "実践候補を表示できませんでした。"
        )

    else:

        for candidate in candidates:

            display_practice_card(
                candidate=candidate
            )

    st.divider()

    with st.container(
        key="reset_area"
    ):

        reset_columns = st.columns(
            [
                2.4,
                1,
            ]
        )

        with reset_columns[1]:

            if st.button(
                "最初からやり直す",
                key="reset_all_button",
                use_container_width=True,
            ):

                reset_all()

                st.rerun()


# ============================================================
# 画面表示
# ============================================================

display_header()
display_request_form()
display_practice_candidates()