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
   全体
========================================================= */

.stApp {
    background:
        linear-gradient(
            180deg,
            #f3f7f9 0px,
            #f7f9fb 340px,
            #f7f9fb 100%
        );
}

.block-container {
    max-width: 1080px;
    padding-top: 2rem;
    padding-bottom: 5rem;
}

html,
body,
[class*="css"] {
    color: #1d2b34;
}

p {
    line-height: 1.7;
}


/* =========================================================
   ヘッダーコンテナ
========================================================= */

.st-key-app_header {
    position: relative;

    margin-bottom: 2.4rem;

    padding:
        2rem
        2.25rem
        2.05rem
        2.25rem;

    border-radius: 24px;

    background:
        linear-gradient(
            135deg,
            #143f4d 0%,
            #17667b 55%,
            #2a899a 100%
        );

    box-shadow:
        0 18px 48px
        rgba(23, 70, 86, 0.16);
}

.st-key-app_header h1 {
    margin-bottom: 0.45rem !important;

    color: #ffffff !important;

    font-size: 2.8rem !important;
    font-weight: 760 !important;

    line-height: 1.22 !important;

    letter-spacing: -0.045em !important;
}

.st-key-app_header p {
    max-width: 760px;

    margin-bottom: 0 !important;

    color:
        rgba(
            255,
            255,
            255,
            0.82
        ) !important;

    font-size: 0.98rem;
    line-height: 1.75;
}

.st-key-app_header div[data-testid="stCaptionContainer"] {
    margin-bottom: 0.3rem;
}

.st-key-app_header div[data-testid="stCaptionContainer"] p {
    display: inline-block;

    width: auto;

    padding:
        0.3rem
        0.72rem;

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
            0.10
        );

    color:
        rgba(
            255,
            255,
            255,
            0.92
        ) !important;

    font-size: 0.75rem !important;
    font-weight: 700;

    letter-spacing: 0.06em;
}


/* =========================================================
   セクション
========================================================= */

.st-key-request_section,
.st-key-results_header {
    margin-bottom: 1rem;
}

.st-key-request_section h2,
.st-key-results_header h2 {
    margin-top: 0 !important;
    margin-bottom: 0.25rem !important;

    color: #172832 !important;

    font-size: 1.95rem !important;
    font-weight: 750 !important;

    letter-spacing: -0.035em !important;
}

.st-key-request_section p,
.st-key-results_header p {
    color: #72818b !important;

    font-size: 0.94rem !important;
}


/* =========================================================
   入力フォーム
========================================================= */

div[data-testid="stForm"] {
    padding:
        1.4rem
        1.45rem
        1.35rem;

    border:
        1px solid
        #dae5e9;

    border-radius: 18px;

    background:
        rgba(
            255,
            255,
            255,
            0.97
        );

    box-shadow:
        0 8px 28px
        rgba(
            31,
            64,
            79,
            0.055
        );
}

div[data-testid="stTextArea"] label {
    color: #344752 !important;

    font-size: 0.9rem !important;
    font-weight: 680 !important;
}

div[data-testid="stTextArea"] textarea {
    min-height: 132px !important;

    padding:
        1rem
        1.05rem !important;

    border:
        1px solid
        #d8e3e7 !important;

    border-radius: 13px !important;

    background:
        #f7f9fa !important;

    color:
        #1e2e38 !important;

    font-size: 1rem !important;
    line-height: 1.65 !important;

    box-shadow:
        none !important;
}

div[data-testid="stTextArea"] textarea:focus {
    border-color:
        #298397 !important;

    background:
        #ffffff !important;

    box-shadow:
        0 0 0 4px
        rgba(
            41,
            131,
            151,
            0.10
        ) !important;
}


/* =========================================================
   ボタン
========================================================= */

.stButton > button,
.stFormSubmitButton > button {
    min-height: 3rem;

    border-radius:
        11px !important;

    font-size:
        0.95rem !important;

    font-weight:
        680 !important;

    transition:
        transform 0.15s ease,
        box-shadow 0.15s ease,
        background 0.15s ease,
        border-color 0.15s ease !important;
}

.stFormSubmitButton > button {
    border:
        1px solid
        #17677c !important;

    background:
        linear-gradient(
            135deg,
            #17647a,
            #28899b
        ) !important;

    color:
        #ffffff !important;

    box-shadow:
        0 7px 20px
        rgba(
            23,
            100,
            122,
            0.15
        ) !important;
}

.stFormSubmitButton > button:hover {
    transform:
        translateY(-1px);

    background:
        linear-gradient(
            135deg,
            #13586c,
            #237b8d
        ) !important;

    color:
        #ffffff !important;
}

.stButton > button {
    border:
        1px solid
        #ccd9df !important;

    background:
        #ffffff !important;

    color:
        #283b46 !important;
}

.stButton > button:hover {
    transform:
        translateY(-1px);

    border-color:
        #2a8296 !important;

    background:
        #f2f8fa !important;

    color:
        #155d6e !important;

    box-shadow:
        0 5px 15px
        rgba(
            25,
            95,
            115,
            0.07
        ) !important;
}


/* =========================================================
   実践カード
========================================================= */

div[data-testid="stVerticalBlockBorderWrapper"] {
    overflow: hidden;

    border:
        1px solid
        #dae5e9 !important;

    border-radius:
        18px !important;

    background:
        rgba(
            255,
            255,
            255,
            0.98
        ) !important;

    box-shadow:
        0 8px 30px
        rgba(
            28,
            60,
            75,
            0.052
        );

    transition:
        border-color 0.16s ease,
        box-shadow 0.16s ease;
}

div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color:
        #c6dade !important;

    box-shadow:
        0 12px 38px
        rgba(
            28,
            60,
            75,
            0.08
        );
}


/* 実践番号 */

div[class*="st-key-practice_card_"] h3 {
    margin-bottom:
        0.35rem !important;

    color:
        #17667b !important;

    font-size:
        0.88rem !important;

    font-weight:
        780 !important;

    letter-spacing:
        0.06em !important;
}


/* 論文タイトル */

div[class*="st-key-practice_card_"] h4 {
    margin-top:
        0 !important;

    margin-bottom:
        0.2rem !important;

    color:
        #172832 !important;

    font-size:
        1.25rem !important;

    font-weight:
        720 !important;

    line-height:
        1.5 !important;
}


/* Caption */

div[class*="st-key-practice_card_"]
div[data-testid="stCaptionContainer"] p {
    color:
        #7b8993 !important;

    font-size:
        0.86rem !important;
}


/* =========================================================
   学年・領域・単元
========================================================= */

div[class*="st-key-practice_card_"]
div[data-testid="stHorizontalBlock"] {
    gap: 0.7rem;
}

div[class*="st-key-practice_card_"]
div[data-testid="column"] {
    padding:
        0.72rem
        0.8rem;

    border:
        1px solid
        #e4ebee;

    border-radius:
        11px;

    background:
        #f8fafb;
}

div[class*="st-key-practice_card_"]
div[data-testid="column"] strong {
    color:
        #7c8d96;

    font-size:
        0.75rem;
}

div[class*="st-key-practice_card_"]
div[data-testid="column"] p {
    margin-bottom:
        0 !important;

    color:
        #293b46;

    font-size:
        0.92rem;
}


/* =========================================================
   チャット
========================================================= */

div[data-testid="stChatMessage"] {
    padding:
        0.85rem
        0.95rem;

    margin-bottom:
        0.7rem;

    border:
        1px solid
        #e1e8eb;

    border-radius:
        15px;

    background:
        #ffffff;
}

div[data-testid="stChatMessage"] p {
    line-height:
        1.78;
}


/* =========================================================
   Expander
========================================================= */

div[data-testid="stExpander"] {
    border:
        1px solid
        #e0e8eb !important;

    border-radius:
        12px !important;

    background:
        #fafcfc !important;
}

div[data-testid="stExpander"] summary {
    color:
        #53656f;

    font-weight:
        620;
}


/* =========================================================
   Alert
========================================================= */

div[data-testid="stAlert"] {
    border-radius:
        12px !important;
}


/* =========================================================
   Divider
========================================================= */

hr {
    margin-top:
        2.1rem !important;

    margin-bottom:
        2.1rem !important;

    border-color:
        #e2e9ec !important;
}


/* =========================================================
   モバイル
========================================================= */

@media (
    max-width: 760px
) {

    .block-container {
        padding-top: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .st-key-app_header {
        padding:
            1.55rem
            1.3rem;

        border-radius:
            18px;
    }

    .st-key-app_header h1 {
        font-size:
            2rem !important;
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
            "🔬 SCIENCE × ICT"
        )

        st.title(
            "理科ICT授業支援システム"
        )

        st.write(
            "理科教育研究に蓄積されたICT活用実践をもとに、"
            "授業づくりの参考となる事例を提案します。"
            "気になる実践については、"
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
# 表示用ヘルパー
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
                f"**💻 使用したICT**  \n"
                f"{ict_text}"
            )

        if effects:

            st.markdown(
                "**✓ この実践で確認されたこと**"
            )

            for effect in effects:

                st.markdown(
                    f"- {effect}"
                )

        button_text = (
            "閉じる"
            if is_expanded
            else "この実践を詳しく見る →"
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

    with st.container(
        key="request_section"
    ):

        st.markdown(
            "## 授業づくりについて相談する"
        )

        st.write(
            "学年・単元・使いたいICT・期待する学習効果などを、"
            "自由な文章で入力してください。"
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
                height=130,
            )
        )

        submitted = (
            st.form_submit_button(
                "参考になる実践を探す",
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
            f"{len(candidates)}件の実践を提案します。"
            "気になる実践を開くと、"
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

display_header()
display_request_form()
display_practice_candidates()