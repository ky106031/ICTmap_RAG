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
    --primary-soft: #eef7f8;

    --text-main: #192b35;
    --text-sub: #6f7e87;

    --border: #dce5e8;
    --surface: #ffffff;

    /*
    本文・参照バー・Chat Inputで
    共通して使う最大幅
    */
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


/*
通常本文の中央基準も900pxへ統一
*/

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

    /*
    固定UIの下に本文が隠れないよう
    十分な余白を確保
    */
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

/*
左右を完全に均等にする。
本文幅の中でさらに少し余白を確保。
*/

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


/*
メッセージ内部も左右対称
*/

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
   Streamlit Bottom領域
========================================================= */

/*
Bottomそのものは画面幅いっぱいでよい。

その内部だけを900px中央配置にする。
*/

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


/*
stBottom直下のラッパーを
明示的に中央揃え
*/

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


/*
入力が長くなりすぎても
際限なく上へ伸びないようにする。

3～4行程度で内部スクロールへ移行。
*/

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

/*
Chat Inputと全く同じ

    width: 900px
    left: 50%
    translateX(-50%)

を使う。

これにより中央基準を統一。
*/

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


/* =========================================================
   参照バー内部
========================================================= */

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
    画面・選択・会話履歴を初期化する。
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
    選択中の実践候補を返す。
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
    選択中practice_idを更新する。
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
# Error
# ============================================================

def display_processing_error(
    error: Exception,
    process_name: str,
) -> None:

    error_text = str(
        error
    )

    if (
        "429" in error_text
        or "RESOURCE_EXHAUSTED"
        in error_text
    ):

        st.warning(
            "現在、AIの利用が混み合っています。"
            "少し時間を空けてから"
            "もう一度お試しください。"
        )

    elif (
        "503" in error_text
        or "UNAVAILABLE"
        in error_text
    ):

        st.warning(
            "現在、AIへのアクセスが"
            "混み合っています。"
            "少し時間を空けてから"
            "もう一度お試しください。"
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
            error_text
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
        # 初回質問 → GraphRAG
        # ----------------------------------------------------

        if not (
            st.session_state.has_generated_candidates
        ):

            st.session_state.initial_query = (
                normalized_input
            )

            st.session_state.pending_graph_query = (
                normalized_input
            )

        # ----------------------------------------------------
        # 追加質問 → Document RAG
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
                        f"実践"
                        f"{candidate['index']}："
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

    # --------------------------------------------------------
    # ユーザー入力
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

    # --------------------------------------------------------
    # GraphRAG
    # --------------------------------------------------------

    if (
        st.session_state.pending_graph_query
    ):

        pending_query = (
            st.session_state.pending_graph_query
        )

        try:

            with st.spinner(
                "ICTマップを探索しています..."
            ):

                result = run_pipeline(
                    user_query=pending_query
                )

            st.session_state.practice_candidates = (
                result.get(
                    "practice_candidates",
                    [],
                )
            )

            st.session_state.has_generated_candidates = (
                True
            )

            st.session_state.pending_graph_query = (
                None
            )

            st.rerun()

        except Exception as error:

            st.session_state.pending_graph_query = (
                None
            )

            display_processing_error(
                error=error,
                process_name="実践の検索",
            )


# ============================================================
# GraphRAG検索後
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
            "条件に合う実践を提案できませんでした。"
            "条件を変えて、もう一度お試しください。"
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
    # 未選択エラー
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
    # Document RAG
    # --------------------------------------------------------

    if (
        st.session_state.pending_document_query
    ):

        pending = (
            st.session_state.pending_document_query
        )

        try:

            with st.spinner(
                "選択した研究知見を確認しています..."
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

            st.session_state.pending_document_query = (
                None
            )

            st.rerun()

        except Exception as error:

            st.session_state.pending_document_query = (
                None
            )

            display_processing_error(
                error=error,
                process_name="回答の作成",
            )

    st.divider()

    # --------------------------------------------------------
    # Reset
    # --------------------------------------------------------

    if st.button(
        "最初からやり直す"
    ):

        reset_all()

        st.rerun()