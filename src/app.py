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
}


/* =========================================================
   Streamlit再実行時の薄い表示を抑える
========================================================= */

[data-stale="true"] {
    opacity: 1 !important;
}


/* =========================================================
   基本
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
    max-width: 980px;
    padding-top: 1.6rem;

    /*
    固定された
    参照実践バー + チャット入力欄
    と本文が重ならないようにする
    */
    padding-bottom: 13rem;
}

p {
    line-height: 1.7;
}


/* =========================================================
   Header
========================================================= */

.st-key-app_header {
    margin-bottom: 2.5rem;

    padding:
        1.7rem
        2rem;

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
   カード内チェックボックス
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

    margin-bottom:
        .7rem;

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


/* =========================================================
   AI回答内見出し
========================================================= */

div[data-testid="stChatMessage"] h2 {

    color:
        #173b47 !important;

    font-size:
        1.45rem !important;
}

div[data-testid="stChatMessage"] h3 {

    color:
        #173b47 !important;

    font-size:
        1.25rem !important;
}


/* =========================================================
   固定：参照中の実践バー
========================================================= */

.st-key-reference_bar {

    position:
        fixed;

    left:
        50%;

    /*
    Streamlitのchat_inputより
    十分上に配置する
    */
    bottom:
        105px;

    transform:
        translateX(-50%);

    width:
        min(
            930px,
            calc(100vw - 32px)
        );

    z-index:
        1000;

    padding:
        .45rem
        .75rem;

    border:
        1px solid
        #d4e3e6;

    border-radius:
        13px;

    background:
        rgba(
            250,
            252,
            252,
            .98
        );

    backdrop-filter:
        blur(10px);

    box-shadow:
        0 7px 24px
        rgba(
            23,
            70,
            84,
            .10
        );
}


/* 固定バー内部 */

.st-key-reference_bar
div[data-testid="stVerticalBlock"] {

    gap:
        .3rem !important;
}


.st-key-reference_bar
div[data-testid="stHorizontalBlock"] {

    align-items:
        center;

    gap:
        .6rem;
}


.st-key-reference_bar p {

    margin:
        0 !important;

    font-size:
        .88rem !important;

    color:
        #344a55 !important;
}


.st-key-reference_bar button {

    min-height:
        2.25rem !important;

    border-radius:
        9px !important;

    font-size:
        .82rem !important;
}


/* =========================================================
   固定チャット入力
========================================================= */

[data-testid="stBottom"] {

    z-index:
        1001 !important;

    background:
        linear-gradient(
            to top,
            #f8fafb 82%,
            rgba(
                248,
                250,
                251,
                0
            )
        ) !important;
}


div[data-testid="stChatInput"] {

    position:
        relative;

    z-index:
        1002 !important;

    border-radius:
        14px !important;
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
        1.7rem 0 !important;
}


/* =========================================================
   Mobile
========================================================= */

@media (
    max-width: 760px
) {

    .block-container {

        padding-top:
            .9rem;

        padding-left:
            1rem;

        padding-right:
            1rem;

        padding-bottom:
            14rem;
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


    .st-key-reference_bar {

        bottom:
            100px;

        width:
            calc(
                100vw - 20px
            );

        padding:
            .4rem
            .55rem;
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
# State操作
# ============================================================

def reset_all() -> None:
    """
    システム全体を初期状態へ戻す。
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
    現在選択されている実践候補を取得する。
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
    実践の選択状態を更新する。
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

    # 実践カードの表示順を維持する
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

    # 固定バー側と同期
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

    # カード側と同期
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
    """
    空の値を除外して「、」で連結する。
    """

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
    """
    APIエラーなどをユーザー向けに表示する。
    """

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
    """
    ページ上部のヘッダー。
    """

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
# 実践カード
# ============================================================

def display_practice_card(
    candidate: dict[str, Any],
) -> None:
    """
    GraphRAGで取得した実践をカード表示する。
    """

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
            f"card_select_"
            f"{practice_id}"
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
# 固定：参照中の実践バー
# ============================================================

def display_reference_bar() -> None:
    """
    チャット入力欄の上に、
    現在参照している実践を固定表示する。

    popoverからいつでも選択変更可能。
    """

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
                        f"bar_select_"
                        f"{practice_id}"
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
    """
    Document RAGでの会話履歴を表示する。
    """

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
#
# st.chat_inputをトップレベルで使用することで、
# Streamlit標準の画面下固定入力欄として表示する。
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
# 入力をStateへ即時登録
# ============================================================

if user_input:

    normalized_input = (
        user_input.strip()
    )

    if normalized_input:

        # ----------------------------------------------------
        # 初回質問
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
        # 追加質問
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

                # 入力直後に履歴へ追加するため、
                # AI処理中でも質問が消えない
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
    # ユーザーが入力した質問
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
    #
    # spinnerは1つだけ。
    # 質問の直下に表示される。
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
    # 最初のユーザー質問
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
    # 実践候補
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
    # Document RAG
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
    # 会話履歴
    # --------------------------------------------------------

    display_research_messages()

    # --------------------------------------------------------
    # 新しい質問への回答生成
    #
    # ユーザー質問はすでに
    # research_messagesに入っているので、
    # AI処理中も画面から消えない。
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