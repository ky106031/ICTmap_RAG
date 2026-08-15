import html
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

# 保存済みデータを読み込む際の待機時間
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

        /* ============================================
           全体
        ============================================ */

        .stApp {
            background:
                linear-gradient(
                    180deg,
                    #f4f8fa 0%,
                    #f7f9fb 280px,
                    #f7f9fb 100%
                );
        }

        .block-container {
            max-width: 1120px;
            padding-top: 2.4rem;
            padding-bottom: 5rem;
        }

        html,
        body,
        [class*="css"] {
            color: #18212b;
        }

        p {
            line-height: 1.75;
        }

        /* ============================================
           通常見出し
        ============================================ */

        h1,
        h2,
        h3 {
            color: #172432;
            letter-spacing: -0.025em;
        }

        h2 {
            font-size: 2rem !important;
            font-weight: 750 !important;
            margin-top: 1.6rem !important;
            margin-bottom: 0.35rem !important;
        }

        h3 {
            font-size: 1.35rem !important;
            font-weight: 700 !important;
        }

        /* ============================================
           ヒーローヘッダー
        ============================================ */

        .app-hero {
            position: relative;
            overflow: hidden;
            padding: 2.25rem 2.4rem 2.15rem 2.4rem;
            margin-bottom: 2.15rem;
            border-radius: 24px;

            background:
                linear-gradient(
                    135deg,
                    #123c4a 0%,
                    #176077 56%,
                    #247f91 100%
                );

            box-shadow:
                0 18px 50px rgba(25, 65, 82, 0.15);
        }

        .app-hero::after {
            content: "";
            position: absolute;
            right: -55px;
            top: -75px;
            width: 220px;
            height: 220px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.08);
        }

        .app-hero::before {
            content: "";
            position: absolute;
            right: 90px;
            bottom: -110px;
            width: 190px;
            height: 190px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.05);
        }

        .hero-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            padding: 0.38rem 0.78rem;
            margin-bottom: 0.85rem;

            border-radius: 999px;
            border: 1px solid rgba(255,255,255,0.22);

            background: rgba(255,255,255,0.10);

            color: rgba(255,255,255,0.90);
            font-size: 0.82rem;
            font-weight: 650;
            letter-spacing: 0.04em;
        }

        .hero-title {
            position: relative;
            z-index: 2;

            margin: 0;
            color: #ffffff;
            font-size: clamp(2rem, 4.4vw, 3.25rem);
            font-weight: 780;
            line-height: 1.16;
            letter-spacing: -0.04em;
        }

        .hero-description {
            position: relative;
            z-index: 2;

            max-width: 760px;
            margin-top: 0.85rem;
            margin-bottom: 0;

            color: rgba(255,255,255,0.82);
            font-size: 1rem;
            line-height: 1.75;
        }

        /* ============================================
           セクション見出し
        ============================================ */

        .section-header {
            margin-top: 0.4rem;
            margin-bottom: 1.05rem;
        }

        .section-eyebrow {
            color: #227589;
            font-size: 0.78rem;
            font-weight: 750;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            margin-bottom: 0.25rem;
        }

        .section-title {
            margin: 0;
            color: #172432;
            font-size: 1.9rem;
            font-weight: 760;
            letter-spacing: -0.035em;
        }

        .section-description {
            margin-top: 0.4rem;
            color: #6f7d89;
            font-size: 0.95rem;
            line-height: 1.65;
        }

        /* ============================================
           フォーム
        ============================================ */

        div[data-testid="stForm"] {
            padding: 1.35rem 1.45rem 1.3rem;
            border: 1px solid #dce6ea;
            border-radius: 18px;
            background: rgba(255,255,255,0.92);

            box-shadow:
                0 7px 30px rgba(31, 64, 79, 0.055);
        }

        div[data-testid="stTextArea"] label {
            color: #33424f !important;
            font-weight: 680 !important;
            font-size: 0.9rem !important;
        }

        div[data-testid="stTextArea"] textarea {
            min-height: 130px !important;

            border: 1px solid #d8e2e7 !important;
            border-radius: 14px !important;

            background: #f8fafb !important;

            padding: 1rem 1rem !important;

            color: #1c2933 !important;
            font-size: 1rem !important;
            line-height: 1.65 !important;

            box-shadow: none !important;

            transition:
                border-color 0.2s ease,
                box-shadow 0.2s ease,
                background 0.2s ease;
        }

        div[data-testid="stTextArea"] textarea:focus {
            border-color: #29859a !important;
            background: #ffffff !important;

            box-shadow:
                0 0 0 4px rgba(41,133,154,0.10)
                !important;
        }

        /* ============================================
           ボタン
        ============================================ */

        .stButton > button,
        .stFormSubmitButton > button {
            min-height: 3rem;

            border-radius: 12px !important;
            border: 1px solid #cad9df !important;

            background: #ffffff !important;
            color: #20313d !important;

            font-weight: 680 !important;
            font-size: 0.96rem !important;

            box-shadow: none !important;

            transition:
                transform 0.16s ease,
                border-color 0.16s ease,
                background 0.16s ease,
                color 0.16s ease,
                box-shadow 0.16s ease;
        }

        .stButton > button:hover,
        .stFormSubmitButton > button:hover {
            transform: translateY(-1px);

            border-color: #22798d !important;

            background: #f2f9fa !important;
            color: #15596b !important;

            box-shadow:
                0 6px 15px rgba(23,96,119,0.08)
                !important;
        }

        .stFormSubmitButton > button {
            border: 1px solid #176077 !important;

            background:
                linear-gradient(
                    135deg,
                    #176077,
                    #247f91
                )
                !important;

            color: #ffffff !important;

            box-shadow:
                0 8px 22px rgba(23,96,119,0.16)
                !important;
        }

        .stFormSubmitButton > button:hover {
            border-color: #124e62 !important;

            background:
                linear-gradient(
                    135deg,
                    #135569,
                    #1e7183
                )
                !important;

            color: #ffffff !important;
        }

        /* ============================================
           実践カード
        ============================================ */

        div[data-testid="stVerticalBlockBorderWrapper"] {
            border: 1px solid #dde6ea !important;
            border-radius: 19px !important;

            background: rgba(255,255,255,0.96) !important;

            box-shadow:
                0 8px 30px rgba(28, 60, 75, 0.055);

            overflow: hidden;

            transition:
                transform 0.18s ease,
                box-shadow 0.18s ease,
                border-color 0.18s ease;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:hover {
            border-color: #c8dadd !important;

            box-shadow:
                0 12px 38px rgba(28, 60, 75, 0.085);
        }

        .practice-kicker {
            display: inline-flex;
            align-items: center;

            padding: 0.27rem 0.68rem;
            margin-bottom: 0.7rem;

            border-radius: 999px;

            background: #e9f5f7;
            color: #176077;

            font-size: 0.76rem;
            font-weight: 760;
            letter-spacing: 0.06em;
        }

        .practice-title {
            margin: 0 0 0.45rem 0;

            color: #172432;
            font-size: 1.27rem;
            font-weight: 740;
            line-height: 1.55;

            letter-spacing: -0.018em;
        }

        .practice-biblio {
            margin-bottom: 1rem;

            color: #7a8791;
            font-size: 0.88rem;
        }

        /* ============================================
           メタデータ
        ============================================ */

        .meta-grid {
            display: grid;
            grid-template-columns:
                repeat(3, minmax(0, 1fr));

            gap: 0.75rem;

            margin-top: 0.9rem;
            margin-bottom: 1rem;
        }

        .meta-box {
            padding: 0.8rem 0.88rem;

            border: 1px solid #e4ebee;
            border-radius: 12px;

            background: #f8fafb;
        }

        .meta-label {
            margin-bottom: 0.28rem;

            color: #81909a;
            font-size: 0.73rem;
            font-weight: 700;
            letter-spacing: 0.05em;
        }

        .meta-value {
            color: #263744;
            font-size: 0.92rem;
            font-weight: 630;
            line-height: 1.45;
        }

        .info-row {
            display: flex;
            gap: 0.7rem;
            align-items: flex-start;

            margin: 0.95rem 0;
            padding: 0.78rem 0.9rem;

            border-radius: 12px;

            background: #f8fafb;
        }

        .info-icon {
            min-width: 1.8rem;
            font-size: 1.05rem;
        }

        .info-body {
            flex: 1;
        }

        .info-label {
            margin-bottom: 0.2rem;

            color: #596a76;
            font-size: 0.78rem;
            font-weight: 720;
        }

        .info-value {
            color: #253641;
            font-size: 0.94rem;
            line-height: 1.6;
        }

        .effect-box {
            margin-top: 0.9rem;
            margin-bottom: 1rem;

            padding: 0.85rem 0.95rem;

            border-left: 4px solid #2c899c;
            border-radius: 0 12px 12px 0;

            background: #f2f8f9;
        }

        .effect-title {
            margin-bottom: 0.45rem;

            color: #32616d;
            font-size: 0.78rem;
            font-weight: 750;
        }

        .effect-item {
            position: relative;

            padding-left: 1.1rem;
            margin-top: 0.35rem;

            color: #273b45;
            font-size: 0.93rem;
            line-height: 1.55;
        }

        .effect-item::before {
            content: "✓";

            position: absolute;
            left: 0;

            color: #237b8d;
            font-weight: 800;
        }

        /* ============================================
           Chat
        ============================================ */

        div[data-testid="stChatMessage"] {
            padding: 0.8rem 0.9rem;
            margin-bottom: 0.65rem;

            border: 1px solid #e4eaed;
            border-radius: 15px;

            background: #ffffff;
        }

        div[data-testid="stChatMessage"] p {
            line-height: 1.78;
        }

        div[data-testid="stChatInput"] {
            border-radius: 14px;
        }

        div[data-testid="stChatInput"] textarea {
            border-radius: 14px !important;
        }

        /* ============================================
           Expander
        ============================================ */

        div[data-testid="stExpander"] {
            border: 1px solid #e1e8eb !important;
            border-radius: 12px !important;

            background: #fafcfc !important;
        }

        div[data-testid="stExpander"] summary {
            color: #50636f;
            font-weight: 620;
        }

        /* ============================================
           Info / Warning
        ============================================ */

        div[data-testid="stAlert"] {
            border-radius: 13px !important;
        }

        /* ============================================
           Divider
        ============================================ */

        hr {
            border-color: #e5eaed !important;
            margin-top: 2rem !important;
            margin-bottom: 2rem !important;
        }

        /* ============================================
           スピナー
        ============================================ */

        div[data-testid="stSpinner"] {
            color: #176077;
        }

        /* ============================================
           モバイル
        ============================================ */

        @media (max-width: 760px) {

            .block-container {
                padding-top: 1.2rem;
                padding-left: 1rem;
                padding-right: 1rem;
            }

            .app-hero {
                padding: 1.7rem 1.35rem;
                border-radius: 19px;
            }

            .hero-title {
                font-size: 2rem;
            }

            .meta-grid {
                grid-template-columns: 1fr;
            }

            .section-title {
                font-size: 1.6rem;
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
    st.markdown(
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
                授業づくりに参考となる事例を提案します。
                気になる実践については、論文本文をもとに詳しく質問できます。
            </p>
        </div>
        """,
        unsafe_allow_html=True,
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


def escape_text(
    value: Any,
) -> str:
    return html.escape(
        str(value)
    )


def display_basic_information(
    candidate: dict[str, Any],
) -> None:
    """
    学年・領域・単元をカード形式で表示する。
    """
    grade = escape_text(
        candidate.get("grade")
        or "記載なし"
    )

    field = escape_text(
        candidate.get("field")
        or "記載なし"
    )

    unit = escape_text(
        candidate.get("unit")
        or "記載なし"
    )

    st.markdown(
        f"""
        <div class="meta-grid">

            <div class="meta-box">
                <div class="meta-label">学年</div>
                <div class="meta-value">{grade}</div>
            </div>

            <div class="meta-box">
                <div class="meta-label">領域</div>
                <div class="meta-value">{field}</div>
            </div>

            <div class="meta-box">
                <div class="meta-label">単元</div>
                <div class="meta-value">{unit}</div>
            </div>

        </div>
        """,
        unsafe_allow_html=True,
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
        """,
        unsafe_allow_html=True,
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
            f"""
            <div class="practice-kicker">
                PRACTICE {escape_text(index)}
            </div>

            <div class="practice-title">
                {escape_text(title)}
            </div>
            """,
            unsafe_allow_html=True,
        )

        bibliographic_values = [
            author,
            f"{year}年" if year else "",
        ]

        bibliographic_text = join_values(
            bibliographic_values
        )

        if bibliographic_text:
            st.markdown(
                f"""
                <div class="practice-biblio">
                    {escape_text(bibliographic_text)}
                </div>
                """,
                unsafe_allow_html=True,
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
                """,
                unsafe_allow_html=True,
            )

        if effects:
            effect_html = ""

            for effect in effects:
                effect_html += (
                    '<div class="effect-item">'
                    f"{escape_text(effect)}"
                    "</div>"
                )

            st.markdown(
                f"""
                <div class="effect-box">

                    <div class="effect-title">
                        この実践で確認されたこと
                    </div>

                    {effect_html}

                </div>
                """,
                unsafe_allow_html=True,
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

    st.markdown(
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
        """,
        unsafe_allow_html=True,
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

        submitted = st.form_submit_button(
            "参考になる実践を探す",
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
            "ICT活用実践を探索しています..."
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
                気になる実践を開くと、論文本文をもとに詳しく質問できます。
            </div>

        </div>
        """,
        unsafe_allow_html=True,
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