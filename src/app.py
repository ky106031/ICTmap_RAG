import html
import json
import time
from pathlib import Path
from textwrap import dedent
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
            "error"
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
# HTML表示ヘルパー
# ============================================================

def render_html(
    content: str,
) -> None:
    """
    HTMLのインデントを除去してからStreamlitへ描画する。

    MarkdownがHTMLをコードブロックとして認識する問題を防ぐ。
    """
    st.markdown(
        dedent(content).strip(),
        unsafe_allow_html=True,
    )


def escape_text(
    value: Any,
) -> str:
    return html.escape(
        str(value)
    )


# ============================================================
# カスタムCSS
# ============================================================

def apply_custom_css() -> None:

    render_html(
        """
        <style>

        /* ============================================
           全体
        ============================================ */

        .stApp {
            background:
                linear-gradient(
                    180deg,
                    #f1f6f8 0%,
                    #f7f9fb 320px,
                    #f7f9fb 100%
                );
        }

        .block-container {
            max-width: 1120px;
            padding-top: 2rem;
            padding-bottom: 5rem;
        }

        html,
        body,
        [class*="css"] {
            color: #182630;
        }

        p {
            line-height: 1.75;
        }


        /* ============================================
           ヒーロー
        ============================================ */

        .app-hero {
            position: relative;
            overflow: hidden;

            padding:
                2.35rem
                2.5rem
                2.3rem
                2.5rem;

            margin-bottom: 2.4rem;

            border-radius: 24px;

            background:
                linear-gradient(
                    135deg,
                    #123d4b 0%,
                    #17647a 58%,
                    #27899b 100%
                );

            box-shadow:
                0 20px 55px
                rgba(24, 70, 87, 0.17);
        }

        .app-hero::after {
            content: "";

            position: absolute;
            right: -50px;
            top: -75px;

            width: 230px;
            height: 230px;

            border-radius: 50%;

            background:
                rgba(
                    255,
                    255,
                    255,
                    0.08
                );
        }

        .app-hero::before {
            content: "";

            position: absolute;
            right: 110px;
            bottom: -130px;

            width: 230px;
            height: 230px;

            border-radius: 50%;

            background:
                rgba(
                    255,
                    255,
                    255,
                    0.055
                );
        }

        .hero-badge {
            position: relative;
            z-index: 2;

            display: inline-flex;
            align-items: center;
            gap: 0.45rem;

            padding:
                0.38rem
                0.8rem;

            margin-bottom: 0.95rem;

            border:
                1px solid
                rgba(
                    255,
                    255,
                    255,
                    0.23
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
                    0.93
                );

            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.055em;
        }

        .hero-title {
            position: relative;
            z-index: 2;

            margin: 0;

            color: #ffffff;

            font-size:
                clamp(
                    2.05rem,
                    4.6vw,
                    3.25rem
                );

            font-weight: 780;
            line-height: 1.18;
            letter-spacing: -0.045em;
        }

        .hero-description {
            position: relative;
            z-index: 2;

            max-width: 770px;

            margin-top: 0.95rem;
            margin-bottom: 0;

            color:
                rgba(
                    255,
                    255,
                    255,
                    0.82
                );

            font-size: 0.98rem;
            line-height: 1.8;
        }


        /* ============================================
           セクション
        ============================================ */

        .section-header {
            margin-top: 0.25rem;
            margin-bottom: 1.2rem;
        }

        .section-eyebrow {
            margin-bottom: 0.28rem;

            color: #258095;

            font-size: 0.73rem;
            font-weight: 760;

            letter-spacing: 0.11em;
        }

        .section-title {
            margin: 0;

            color: #182733;

            font-size: 1.95rem;
            font-weight: 770;

            line-height: 1.3;
            letter-spacing: -0.035em;
        }

        .section-description {
            margin-top: 0.45rem;

            color: #70808b;

            font-size: 0.94rem;
            line-height: 1.7;
        }


        /* ============================================
           フォーム
        ============================================ */

        div[data-testid="stForm"] {
            padding:
                1.45rem
                1.5rem
                1.35rem;

            border:
                1px solid
                #dce6ea;

            border-radius: 18px;

            background:
                rgba(
                    255,
                    255,
                    255,
                    0.96
                );

            box-shadow:
                0 8px 32px
                rgba(
                    31,
                    64,
                    79,
                    0.06
                );
        }

        div[data-testid="stTextArea"] label {
            color: #334650 !important;

            font-weight: 680 !important;
            font-size: 0.9rem !important;
        }

        div[data-testid="stTextArea"] textarea {
            min-height: 135px !important;

            padding:
                1rem
                1.05rem !important;

            border:
                1px solid
                #d8e3e7 !important;

            border-radius: 13px !important;

            background:
                #f8fafb !important;

            color:
                #1d2d37 !important;

            font-size: 1rem !important;
            line-height: 1.65 !important;

            box-shadow: none !important;
        }

        div[data-testid="stTextArea"] textarea:focus {
            border-color:
                #28859a !important;

            background:
                #ffffff !important;

            box-shadow:
                0 0 0 4px
                rgba(
                    40,
                    133,
                    154,
                    0.10
                ) !important;
        }


        /* ============================================
           ボタン
        ============================================ */

        .stButton > button,
        .stFormSubmitButton > button {
            min-height: 3rem;

            border-radius: 11px !important;

            font-size: 0.95rem !important;
            font-weight: 680 !important;

            transition:
                transform 0.16s ease,
                box-shadow 0.16s ease,
                background 0.16s ease,
                border-color 0.16s ease !important;
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
                #f2f9fa !important;

            color:
                #155c6d !important;

            box-shadow:
                0 5px 15px
                rgba(
                    25,
                    95,
                    115,
                    0.08
                ) !important;
        }

        .stFormSubmitButton > button {
            border:
                1px solid
                #17677c !important;

            background:
                linear-gradient(
                    135deg,
                    #17647a,
                    #27889a
                )
                !important;

            color:
                #ffffff !important;

            box-shadow:
                0 8px 22px
                rgba(
                    23,
                    100,
                    122,
                    0.17
                )
                !important;
        }

        .stFormSubmitButton > button:hover {
            transform:
                translateY(-1px);

            background:
                linear-gradient(
                    135deg,
                    #13576b,
                    #21788a
                )
                !important;

            color:
                #ffffff !important;
        }


        /* ============================================
           実践カード
        ============================================ */

        div[data-testid="stVerticalBlockBorderWrapper"] {
            overflow: hidden;

            border:
                1px solid
                #dce6ea !important;

            border-radius:
                19px !important;

            background:
                rgba(
                    255,
                    255,
                    255,
                    0.98
                ) !important;

            box-shadow:
                0 9px 32px
                rgba(
                    28,
                    60,
                    75,
                    0.055
                );

            transition:
                border-color 0.18s ease,
                box-shadow 0.18s ease;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:hover {
            border-color:
                #c8dade !important;

            box-shadow:
                0 13px 38px
                rgba(
                    28,
                    60,
                    75,
                    0.085
                );
        }

        .practice-kicker {
            display: inline-flex;

            padding:
                0.28rem
                0.7rem;

            margin-bottom: 0.75rem;

            border-radius: 999px;

            background:
                #e9f5f7;

            color:
                #17647a;

            font-size: 0.72rem;
            font-weight: 760;

            letter-spacing: 0.075em;
        }

        .practice-title {
            margin:
                0
                0
                0.45rem
                0;

            color:
                #172733;

            font-size: 1.28rem;
            font-weight: 740;

            line-height: 1.55;
            letter-spacing: -0.02em;
        }

        .practice-biblio {
            margin-bottom: 1rem;

            color:
                #7a8993;

            font-size: 0.87rem;
        }


        /* ============================================
           メタ情報
        ============================================ */

        .meta-grid {
            display: grid;

            grid-template-columns:
                repeat(
                    3,
                    minmax(0, 1fr)
                );

            gap: 0.7rem;

            margin:
                0.9rem
                0
                1rem;
        }

        .meta-box {
            padding:
                0.8rem
                0.9rem;

            border:
                1px solid
                #e4ebee;

            border-radius: 11px;

            background:
                #f8fafb;
        }

        .meta-label {
            margin-bottom: 0.25rem;

            color:
                #81919a;

            font-size: 0.7rem;
            font-weight: 720;

            letter-spacing: 0.06em;
        }

        .meta-value {
            color:
                #263945;

            font-size: 0.91rem;
            font-weight: 640;

            line-height: 1.5;
        }


        /* ============================================
           ICT情報
        ============================================ */

        .info-row {
            display: flex;
            align-items: flex-start;

            gap: 0.75rem;

            margin:
                0.9rem
                0;

            padding:
                0.8rem
                0.95rem;

            border-radius:
                11px;

            background:
                #f7fafb;
        }

        .info-icon {
            min-width: 1.7rem;

            font-size: 1.05rem;
        }

        .info-body {
            flex: 1;
        }

        .info-label {
            margin-bottom: 0.15rem;

            color:
                #697b85;

            font-size: 0.73rem;
            font-weight: 720;
        }

        .info-value {
            color:
                #263945;

            font-size: 0.93rem;
            line-height: 1.6;
        }


        /* ============================================
           教育効果
        ============================================ */

        .effect-box {
            margin:
                0.95rem
                0
                1rem;

            padding:
                0.85rem
                0.95rem;

            border-left:
                4px solid
                #31889b;

            border-radius:
                0
                11px
                11px
                0;

            background:
                #f1f8f9;
        }

        .effect-title {
            margin-bottom:
                0.4rem;

            color:
                #34616d;

            font-size:
                0.75rem;

            font-weight:
                750;
        }

        .effect-item {
            position: relative;

            padding-left:
                1.15rem;

            margin-top:
                0.32rem;

            color:
                #283d47;

            font-size:
                0.92rem;

            line-height:
                1.6;
        }

        .effect-item::before {
            content: "✓";

            position: absolute;
            left: 0;

            color:
                #247c8f;

            font-weight:
                800;
        }


        /* ============================================
           チャット
        ============================================ */

        div[data-testid="stChatMessage"] {
            margin-bottom:
                0.7rem;

            padding:
                0.85rem
                0.95rem;

            border:
                1px solid
                #e2e9ec;

            border-radius:
                15px;

            background:
                #ffffff;
        }

        div[data-testid="stChatMessage"] p {
            line-height:
                1.8;
        }

        div[data-testid="stChatInput"] {
            border-radius:
                14px;
        }


        /* ============================================
           Expander
        ============================================ */

        div[data-testid="stExpander"] {
            border:
                1px solid
                #e1e8eb !important;

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


        /* ============================================
           Streamlit alert
        ============================================ */

        div[data-testid="stAlert"] {
            border-radius:
                12px !important;
        }


        /* ============================================
           Divider
        ============================================ */

        hr {
            margin-top:
                2rem !important;

            margin-bottom:
                2rem !important;

            border-color:
                #e3e9ec !important;
        }


        /* ============================================
           モバイル
        ============================================ */

        @media (
            max-width: 760px
        ) {

            .block-container {
                padding-top:
                    1rem;

                padding-left:
                    1rem;

                padding-right:
                    1rem;
            }

            .app-hero {
                padding:
                    1.7rem
                    1.4rem;

                border-radius:
                    19px;
            }

            .hero-title {
                font-size:
                    2rem;
            }

            .meta-grid {
                grid-template-columns:
                    1fr;
            }

            .section-title {
                font-size:
                    1.6rem;
            }
        }

        </style>
        """
    )


apply_custom_css()


# ============================================================
# ヘッダー
# ============================================================

def display_header() -> None:

    render_html(
        """
        <div class="app-hero">

            <div class="hero-badge">
                🔬 SCIENCE × ICT
            </div>

            <div class="hero-title">
                理科ICT授業支援システム
            </div>

            <p class="hero-description">
                理科教育研究に蓄積されたICT活用実践をもとに、
                授業づくりの参考となる事例を提案します。
                気になる実践については、
                論文本文をもとに詳しく質問できます。
            </p>

        </div>
        """
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

    grade = escape_text(
        candidate.get(
            "grade"
        )
        or "記載なし"
    )

    field = escape_text(
        candidate.get(
            "field"
        )
        or "記載なし"
    )

    unit = escape_text(
        candidate.get(
            "unit"
        )
        or "記載なし"
    )

    render_html(
        f"""
        <div class="meta-grid">

            <div class="meta-box">
                <div class="meta-label">
                    学年
                </div>

                <div class="meta-value">
                    {grade}
                </div>
            </div>

            <div class="meta-box">
                <div class="meta-label">
                    領域
                </div>

                <div class="meta-value">
                    {field}
                </div>
            </div>

            <div class="meta-box">
                <div class="meta-label">
                    単元
                </div>

                <div class="meta-value">
                    {unit}
                </div>
            </div>

        </div>
        """
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

    render_html(
        """
        <div class="section-header">

            <div class="section-eyebrow">
                PAPER ASSISTANT
            </div>

            <div class="section-title">
                この実践について質問する
            </div>

            <div class="section-description">
                選択した実践の論文本文をもとに回答します。
                研究知見を別の学年や単元へ応用する相談もできます。
            </div>

        </div>
        """
    )

    if (
        not messages
        and not pending_query
    ):
        st.info(
            "「授業展開は？」"
            "「ICTをどのように活用しましたか？」"
            "「別の学年へ応用するとしたら？」"
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
    # 回答生成
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
        border=True
    ):

        render_html(
            f"""
            <div class="practice-kicker">
                PRACTICE {escape_text(index)}
            </div>

            <div class="practice-title">
                {escape_text(title)}
            </div>
            """
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

            render_html(
                f"""
                <div class="practice-biblio">
                    {escape_text(bibliographic_text)}
                </div>
                """
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

            render_html(
                f"""
                <div class="info-row">

                    <div class="info-icon">
                        💻
                    </div>

                    <div class="info-body">

                        <div class="info-label">
                            使用したICT
                        </div>

                        <div class="info-value">
                            {escape_text(ict_text)}
                        </div>

                    </div>

                </div>
                """
            )

        if effects:

            effect_html = ""

            for effect in effects:

                effect_html += (
                    '<div class="effect-item">'
                    f"{escape_text(effect)}"
                    "</div>"
                )

            render_html(
                f"""
                <div class="effect-box">

                    <div class="effect-title">
                        この実践で確認されたこと
                    </div>

                    {effect_html}

                </div>
                """
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

    render_html(
        """
        <div class="section-header">

            <div class="section-eyebrow">
                LESSON DESIGN
            </div>

            <div class="section-title">
                授業づくりについて相談する
            </div>

            <div class="section-description">
                学年・単元・使いたいICT・期待する学習効果などを、
                自由な文章で入力してください。
            </div>

        </div>
        """
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
            height=130,
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

    render_html(
        f"""
        <div class="section-header">

            <div class="section-eyebrow">
                RECOMMENDED PRACTICES
            </div>

            <div class="section-title">
                おすすめの授業実践
            </div>

            <div class="section-description">
                {len(candidates)}件の実践を提案します。
                気になる実践を開くと、
                論文本文をもとに詳しく質問できます。
            </div>

        </div>
        """
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