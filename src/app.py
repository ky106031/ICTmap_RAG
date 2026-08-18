import json
import time
from pathlib import Path
from typing import Any

import streamlit as st


# ============================================================
# ページ設定
# ============================================================

st.set_page_config(
    page_title="ICTマップAI検索システム",
    page_icon="🔬",
    layout="centered",
)


# ============================================================
# 基本パス
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

DEMO_DATA_DIR = (
    BASE_DIR
    / "data"
    / "demo_backup_v2"
)

PRACTICE_SEARCH_PATH = (
    DEMO_DATA_DIR
    / "practice_search.json"
)

DOCUMENT_ANSWER_01_PATH = (
    DEMO_DATA_DIR
    / "document_answer_01.json"
)

DOCUMENT_ANSWER_02_PATH = (
    DEMO_DATA_DIR
    / "document_answer_02.json"
)


# ============================================================
# Demo待機時間
#
# 発表時に「処理している感じ」を再現する。
# 必要なら後から調整可能。
# ============================================================

GRAPH_SEARCH_DELAY = 5.5
DOCUMENT_SEARCH_DELAY = 4.5


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
    --primary-soft: #eef7f8;

    --text-main: #192b35;
    --text-sub: #6f7e87;

    --border: #dce5e8;
    --surface: #ffffff;

    --content-width: 900px;
}


/* =========================================================
   Streamlit rerun時の薄い表示を抑える
========================================================= */

[data-stale="true"] {
    opacity: 1 !important;
}


/* =========================================================
   ページ全体
========================================================= */

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
    max-width:
        var(--content-width) !important;

    width:
        calc(100% - 48px) !important;

    margin-left:
        auto !important;

    margin-right:
        auto !important;

    padding-left:
        0 !important;

    padding-right:
        0 !important;

    padding-top:
        1.6rem;

    padding-bottom:
        17rem;
}


p {
    line-height:
        1.7;
}


/* =========================================================
   Header
========================================================= */

.st-key-app_header {
    margin-bottom:
        2.5rem;

    padding:
        1.7rem
        2rem;

    border-radius:
        22px;

    background:
        linear-gradient(
            135deg,
            #164553,
            #176579 58%,
            #268799
        );

    box-shadow:
        0 16px 44px
        rgba(
            22,
            74,
            88,
            .14
        );
}


.st-key-app_header h1 {
    color:
        #ffffff !important;

    font-size:
        2.5rem !important;

    margin-bottom:
        .4rem !important;
}


.st-key-app_header p {
    color:
        rgba(
            255,
            255,
            255,
            .82
        ) !important;
}


/* =========================================================
   実践カード
========================================================= */

div[class*="st-key-practice_card_"] {
    margin-bottom:
        .8rem;
}


div[class*="st-key-practice_card_"]
div[data-testid="stVerticalBlock"] {
    gap:
        .5rem !important;
}


div[data-testid="stVerticalBlockBorderWrapper"] {
    border:
        1px solid
        #dce5e8 !important;

    border-radius:
        16px !important;

    background:
        #ffffff !important;

    box-shadow:
        0 5px 18px
        rgba(
            30,
            60,
            72,
            .04
        );
}


div[class*="st-key-practice_card_"] h3 {
    color:
        #176579 !important;

    font-size:
        1.15rem !important;
}


/* =========================================================
   実践カード内チェック
========================================================= */

div[class*="st-key-practice_card_"]
div[data-testid="stCheckbox"] {
    margin-top:
        .3rem;

    padding:
        .55rem
        .75rem;

    border:
        1px solid
        #d7e7ea;

    border-radius:
        10px;

    background:
        #eef7f8;
}


/* =========================================================
   Chat Message
========================================================= */

div[data-testid="stChatMessage"] {
    box-sizing:
        border-box !important;

    width:
        calc(100% - 24px) !important;

    margin-left:
        12px !important;

    margin-right:
        12px !important;

    margin-bottom:
        .9rem !important;

    padding:
        1.05rem
        1.35rem !important;

    border:
        1px solid
        #e1e8ea;

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
            .025
        );
}


div[data-testid="stChatMessageContent"] {
    padding-left:
        .4rem !important;

    padding-right:
        .4rem !important;
}


div[data-testid="stChatMessage"] p {
    line-height:
        1.8 !important;
}


div[data-testid="stChatMessage"] li {
    line-height:
        1.75 !important;

    margin-bottom:
        .35rem;
}


/* =========================================================
   AI回答内見出し
========================================================= */

div[data-testid="stChatMessage"] h2 {
    color:
        #173b47 !important;

    font-size:
        1.45rem !important;

    line-height:
        1.4 !important;

    margin-top:
        1.5rem !important;

    margin-bottom:
        .7rem !important;
}


div[data-testid="stChatMessage"] h3 {
    color:
        #173b47 !important;

    font-size:
        1.25rem !important;

    line-height:
        1.4 !important;

    margin-top:
        1.35rem !important;

    margin-bottom:
        .6rem !important;
}


/* =========================================================
   Streamlit Bottom
========================================================= */

[data-testid="stBottom"] {
    z-index:
        2000 !important;

    width:
        100% !important;

    left:
        0 !important;

    right:
        0 !important;

    background:
        linear-gradient(
            to top,
            #f8fafb 88%,
            rgba(
                248,
                250,
                251,
                0
            )
        ) !important;
}


[data-testid="stBottom"] > div {
    max-width:
        var(--content-width) !important;

    width:
        calc(100% - 48px) !important;

    margin-left:
        auto !important;

    margin-right:
        auto !important;
}


/* =========================================================
   Chat Input
========================================================= */

div[data-testid="stChatInput"] {
    width:
        100% !important;

    max-width:
        100% !important;

    margin-left:
        auto !important;

    margin-right:
        auto !important;

    position:
        relative !important;

    z-index:
        2001 !important;

    border-radius:
        14px !important;

    pointer-events:
        auto !important;
}


div[data-testid="stChatInput"]
textarea {
    max-height:
        105px !important;

    overflow-y:
        auto !important;

    line-height:
        1.5 !important;
}


/* =========================================================
   固定：参照実践バー
========================================================= */

.st-key-reference_bar {
    box-sizing:
        border-box !important;

    position:
        fixed !important;

    left:
        50% !important;

    transform:
        translateX(-50%) !important;

    bottom:
        142px !important;

    max-width:
        var(--content-width) !important;

    width:
        calc(100% - 48px) !important;

    z-index:
        3000 !important;

    margin:
        0 !important;

    padding:
        .55rem
        .8rem !important;

    border:
        1px solid
        #d4e3e6 !important;

    border-radius:
        13px !important;

    background:
        rgba(
            250,
            252,
            252,
            .99
        ) !important;

    backdrop-filter:
        blur(12px);

    box-shadow:
        0 7px 24px
        rgba(
            23,
            70,
            84,
            .11
        ) !important;

    pointer-events:
        auto !important;
}


.st-key-reference_bar
div[data-testid="stVerticalBlock"] {
    gap:
        .25rem !important;
}


.st-key-reference_bar
div[data-testid="stHorizontalBlock"] {
    align-items:
        center !important;

    gap:
        .7rem !important;
}


.st-key-reference_bar p {
    margin:
        0 !important;

    color:
        #344a55 !important;

    font-size:
        .9rem !important;
}


.st-key-reference_bar button {
    position:
        relative !important;

    z-index:
        3001 !important;

    min-height:
        2.3rem !important;

    border-radius:
        9px !important;

    font-size:
        .83rem !important;

    pointer-events:
        auto !important;
}


/* =========================================================
   Popover
========================================================= */

div[data-testid="stPopover"] {
    position:
        relative !important;

    z-index:
        4000 !important;

    pointer-events:
        auto !important;
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


/* =========================================================
   Divider
========================================================= */

hr {
    margin:
        1.7rem
        0 !important;
}


/* =========================================================
   Mobile
========================================================= */

@media (
    max-width: 760px
) {

    :root {
        --content-width: 100%;
    }


    .block-container {
        width:
            calc(100% - 20px) !important;

        padding-top:
            .9rem;

        padding-bottom:
            18rem;
    }


    .st-key-app_header {
        padding:
            1.4rem
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


    div[data-testid="stChatMessage"] {
        width:
            calc(100% - 8px) !important;

        margin-left:
            4px !important;

        margin-right:
            4px !important;

        padding:
            .9rem
            .9rem !important;
    }


    [data-testid="stBottom"] > div {
        width:
            calc(100% - 20px) !important;
    }


    .st-key-reference_bar {
        width:
            calc(100% - 20px) !important;

        bottom:
            138px !important;

        padding:
            .45rem
            .6rem !important;
    }


    div[data-testid="stChatInput"]
    textarea {
        max-height:
            95px !important;
    }

}

</style>
        """,
        unsafe_allow_html=True,
    )


apply_custom_css()


# ============================================================
# JSON
# ============================================================

def load_json(
    path: Path,
) -> dict[str, Any]:
    """
    Demo用JSONを読み込む。
    """

    if not path.exists():

        raise FileNotFoundError(
            f"Demo用JSONが見つかりません。\n"
            f"{path}"
        )

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as file:

        data = json.load(
            file
        )

    if not isinstance(
        data,
        dict,
    ):

        raise ValueError(
            f"JSONの形式が不正です: {path}"
        )

    return data


# ============================================================
# Session State
# ============================================================

DEFAULT_STATE = {
    "initial_query": "",
    "practice_candidates": [],
    "selected_practice_ids": [],
    "research_messages": [],
    "has_generated_candidates": False,

    # --------------------------------------------
    # Demo処理待ち
    # --------------------------------------------

    "pending_demo_graph": False,
    "pending_demo_document": None,

    # --------------------------------------------
    # 追加質問の回数
    #
    # 0 → document_answer_01
    # 1 → document_answer_02
    # --------------------------------------------

    "document_answer_index": 0,

    "selection_error": None,
}


for key, value in DEFAULT_STATE.items():

    if key not in st.session_state:

        if isinstance(
            value,
            list,
        ):

            st.session_state[
                key
            ] = value.copy()

        else:

            st.session_state[
                key
            ] = value


# ============================================================
# State
# ============================================================

def reset_all() -> None:
    """
    Demoを最初からやり直す。
    """

    for key in list(
        st.session_state.keys()
    ):

        if (
            key.startswith(
                "card_select_"
            )
            or key.startswith(
                "bar_select_"
            )
        ):

            del st.session_state[
                key
            ]

    for key, value in (
        DEFAULT_STATE.items()
    ):

        if isinstance(
            value,
            list,
        ):

            st.session_state[
                key
            ] = value.copy()

        else:

            st.session_state[
                key
            ] = value


def get_selected_candidates() -> list[
    dict[str, Any]
]:
    """
    UI上で選択されている実践を取得する。
    """

    selected_ids = set(
        st.session_state.selected_practice_ids
    )

    return [
        candidate
        for candidate
        in st.session_state.practice_candidates
        if str(
            candidate.get(
                "practice_id",
                "",
            )
        ) in selected_ids
    ]


def update_selected_ids(
    practice_id: str,
    selected: bool,
) -> None:
    """
    選択中のpractice_idを更新する。
    """

    current_ids = set(
        st.session_state.selected_practice_ids
    )

    if selected:

        current_ids.add(
            practice_id
        )

    else:

        current_ids.discard(
            practice_id
        )

    ordered_ids: list[str] = []

    for candidate in (
        st.session_state.practice_candidates
    ):

        candidate_id = str(
            candidate.get(
                "practice_id",
                "",
            )
        )

        if candidate_id in current_ids:

            ordered_ids.append(
                candidate_id
            )

    st.session_state.selected_practice_ids = (
        ordered_ids
    )


def on_card_selection_change(
    practice_id: str,
) -> None:
    """
    実践カード側のチェック変更。
    """

    card_key = (
        f"card_select_{practice_id}"
    )

    selected = bool(
        st.session_state.get(
            card_key,
            False,
        )
    )

    update_selected_ids(
        practice_id=practice_id,
        selected=selected,
    )

    bar_key = (
        f"bar_select_{practice_id}"
    )

    if bar_key in st.session_state:

        st.session_state[
            bar_key
        ] = selected


def on_bar_selection_change(
    practice_id: str,
) -> None:
    """
    固定バー側のチェック変更。
    """

    bar_key = (
        f"bar_select_{practice_id}"
    )

    selected = bool(
        st.session_state.get(
            bar_key,
            False,
        )
    )

    update_selected_ids(
        practice_id=practice_id,
        selected=selected,
    )

    card_key = (
        f"card_select_{practice_id}"
    )

    if card_key in st.session_state:

        st.session_state[
            card_key
        ] = selected


# ============================================================
# Helper
# ============================================================

def join_values(
    values: list[Any],
) -> str:

    normalized = [
        str(value).strip()
        for value in values
        if str(value).strip()
    ]

    return "、".join(
        normalized
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
    ).strip()

    title = str(
        candidate.get(
            "title",
            "タイトル不明",
        )
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
                (
                    f"{year}年"
                    if year
                    else ""
                ),
            ]
        )

        if bibliography:

            st.write(
                bibliography
            )

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

        card_key = (
            f"card_select_{practice_id}"
        )

        if (
            card_key
            not in st.session_state
        ):

            st.session_state[
                card_key
            ] = (
                practice_id
                in st.session_state.selected_practice_ids
            )

        st.checkbox(
            "この実践を参考にする",
            key=card_key,
            on_change=(
                on_card_selection_change
            ),
            args=(
                practice_id,
            ),
        )


# ============================================================
# 固定：参照実践バー
# ============================================================

def display_reference_bar() -> None:

    if not (
        st.session_state.has_generated_candidates
    ):

        return

    candidates = (
        st.session_state.practice_candidates
    )

    selected = (
        get_selected_candidates()
    )

    with st.container(
        key="reference_bar"
    ):

        columns = st.columns(
            [
                3.3,
                1.2,
            ]
        )

        with columns[0]:

            if selected:

                labels = [
                    f"実践{candidate['index']}"
                    for candidate
                    in selected
                ]

                st.markdown(
                    "**参照中：** "
                    + " ・ ".join(
                        labels
                    )
                )

            else:

                st.markdown(
                    "**参照する実践を選択してください**"
                )

        with columns[1]:

            with st.popover(
                "参照実践を変更"
            ):

                st.caption(
                    "質問時に参照する実践を"
                    "選択してください。"
                )

                for candidate in candidates:

                    practice_id = str(
                        candidate.get(
                            "practice_id",
                            "",
                        )
                    )

                    index = candidate.get(
                        "index",
                        "",
                    )

                    title = str(
                        candidate.get(
                            "title",
                            "",
                        )
                    )

                    bar_key = (
                        f"bar_select_{practice_id}"
                    )

                    if (
                        bar_key
                        not in st.session_state
                    ):

                        st.session_state[
                            bar_key
                        ] = (
                            practice_id
                            in st.session_state.selected_practice_ids
                        )

                    st.checkbox(
                        (
                            f"実践{index} "
                            f"{title}"
                        ),
                        key=bar_key,
                        on_change=(
                            on_bar_selection_change
                        ),
                        args=(
                            practice_id,
                        ),
                    )


# ============================================================
# Chat履歴
# ============================================================

def display_research_messages() -> None:

    for message in (
        st.session_state.research_messages
    ):

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

            continue

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
                            f"（本文部分 "
                            f"{chunk_index}）"
                        )


# ============================================================
# Demo Graph処理
# ============================================================

def process_demo_graph() -> None:
    """
    GraphRAGの代わりに
    practice_search.jsonを読み込む。
    """

    if not (
        st.session_state.pending_demo_graph
    ):

        return

    try:

        with st.spinner(
            "ICTマップを探索しています..."
        ):

            time.sleep(
                GRAPH_SEARCH_DELAY
            )

            data = load_json(
                PRACTICE_SEARCH_PATH
            )

        candidates = data.get(
            "practice_candidates",
            [],
        )

        if not isinstance(
            candidates,
            list,
        ):

            raise ValueError(
                "practice_candidatesの形式が不正です。"
            )

        st.session_state.practice_candidates = (
            candidates
        )

        st.session_state.has_generated_candidates = (
            True
        )

        st.session_state.pending_demo_graph = (
            False
        )

        st.rerun()

    except Exception as error:

        st.session_state.pending_demo_graph = (
            False
        )

        st.error(
            "デモ用の実践情報を"
            "読み込めませんでした。"
        )

        with st.expander(
            "エラーの詳細"
        ):

            st.code(
                str(error)
            )


# ============================================================
# Demo Document処理
# ============================================================

def get_demo_answer_path(
    answer_index: int,
) -> Path | None:
    """
    質問回数に対応するJSONを返す。
    """

    if answer_index == 0:

        return (
            DOCUMENT_ANSWER_01_PATH
        )

    if answer_index == 1:

        return (
            DOCUMENT_ANSWER_02_PATH
        )

    return None


def process_demo_document() -> None:
    """
    Document RAGの代わりに
    保存済み回答JSONを読み込む。
    """

    pending = (
        st.session_state.pending_demo_document
    )

    if not pending:

        return

    answer_index = (
        st.session_state.document_answer_index
    )

    answer_path = get_demo_answer_path(
        answer_index
    )

    # --------------------------------------------------------
    # 保存済み回答を使い切った場合
    # --------------------------------------------------------

    if answer_path is None:

        st.session_state.pending_demo_document = (
            None
        )

        st.session_state.research_messages.append(
            {
                "role": "assistant",
                "content": (
                    "このデモで用意されている"
                    "回答は以上です。"
                ),
                "sources": [],
            }
        )

        st.rerun()

        return

    try:

        with st.spinner(
            "選択した研究知見を確認しています..."
        ):

            time.sleep(
                DOCUMENT_SEARCH_DELAY
            )

            data = load_json(
                answer_path
            )

        answer = str(
            data.get(
                "answer",
                "",
            )
        ).strip()

        sources = data.get(
            "sources",
            [],
        )

        if not answer:

            raise ValueError(
                "保存済み回答が空です。"
            )

        if not isinstance(
            sources,
            list,
        ):

            sources = []

        st.session_state.research_messages.append(
            {
                "role": "assistant",
                "content": answer,
                "sources": sources,
            }
        )

        st.session_state.document_answer_index += (
            1
        )

        st.session_state.pending_demo_document = (
            None
        )

        st.rerun()

    except Exception as error:

        st.session_state.pending_demo_document = (
            None
        )

        st.error(
            "デモ用の回答を"
            "読み込めませんでした。"
        )

        with st.expander(
            "エラーの詳細"
        ):

            st.code(
                str(error)
            )


# ============================================================
# 固定UI
# ============================================================

display_reference_bar()


if (
    st.session_state.has_generated_candidates
):

    chat_placeholder = (
        "選択した実践について質問してください"
    )

else:

    chat_placeholder = (
        "授業づくりについて相談してください"
    )


user_input = st.chat_input(
    chat_placeholder
)


# ============================================================
# 入力受付
# ============================================================

if user_input:

    normalized_input = (
        user_input.strip()
    )

    if normalized_input:

        # ----------------------------------------------------
        # 1回目
        # ----------------------------------------------------

        if not (
            st.session_state.has_generated_candidates
        ):

            st.session_state.initial_query = (
                normalized_input
            )

            st.session_state.pending_demo_graph = (
                True
            )

        # ----------------------------------------------------
        # 2回目以降
        # ----------------------------------------------------

        else:

            selected_candidates = (
                get_selected_candidates()
            )

            if not selected_candidates:

                st.session_state.selection_error = (
                    "質問する前に、"
                    "参考にしたい実践を"
                    "1件以上選択してください。"
                )

            else:

                # --------------------------------------------
                # 入力内容はそのまま画面へ表示
                # --------------------------------------------

                st.session_state.research_messages.append(
                    {
                        "role": "user",
                        "content": normalized_input,
                    }
                )

                st.session_state.pending_demo_document = {
                    "query": normalized_input,
                }


# ============================================================
# Main UI
# ============================================================

display_header()


# ============================================================
# 初回画面
# ============================================================

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

    # --------------------------------------------------------
    # 保存済みGraphRAG結果
    # --------------------------------------------------------

    process_demo_graph()


# ============================================================
# 実践検索後
# ============================================================

else:

    # --------------------------------------------------------
    # 初回質問
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # おすすめ実践
    # --------------------------------------------------------

    st.markdown(
        "## おすすめの授業実践"
    )

    st.write(
        f"{len(st.session_state.practice_candidates)}件の"
        "実践が見つかりました。"
        "参考にしたい実践を選択してください。"
    )

    if not (
        st.session_state.practice_candidates
    ):

        st.info(
            "実践情報がありません。"
        )

    else:

        for candidate in (
            st.session_state.practice_candidates
        ):

            display_practice_card(
                candidate
            )

    st.divider()

    # --------------------------------------------------------
    # 研究知見について相談
    # --------------------------------------------------------

    st.markdown(
        "## 研究知見について相談する"
    )

    st.caption(
        "1件の実践の深掘りだけでなく、"
        "複数実践の比較や、"
        "複数の研究知見を組み合わせた"
        "新しい授業案についても質問できます。"
    )

    # --------------------------------------------------------
    # 未選択
    # --------------------------------------------------------

    if (
        st.session_state.selection_error
    ):

        st.warning(
            st.session_state.selection_error
        )

        st.session_state.selection_error = (
            None
        )

    # --------------------------------------------------------
    # Chat履歴
    # --------------------------------------------------------

    display_research_messages()

    # --------------------------------------------------------
    # 保存済みDocument RAG回答
    # --------------------------------------------------------

    process_demo_document()

    st.divider()

    # --------------------------------------------------------
    # Reset
    # --------------------------------------------------------

    if st.button(
        "最初からやり直す"
    ):

        reset_all()

        st.rerun()