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
   Streamlit再実行時の白っぽいフェードを抑える
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

    /*
    下部固定の
    選択実践バー + chat input
    と本文が重ならないようにする
    */
    padding-bottom: 11rem;
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
        rgba(22, 74, 88, .14);
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
   Chat
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
   固定：選択中の実践バー
========================================================= */

.st-key-reference_bar {

    position:
        fixed;

    left:
        50%;

    bottom:
        76px;

    transform:
        translateX(-50%);

    width:
        min(
            930px,
            calc(100vw - 32px)
        );

    z-index:
        999;

    padding:
        .55rem
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
            .97
        );

    backdrop-filter:
        blur(10px);

    box-shadow:
        0 8px 28px
        rgba(
            23,
            70,
            84,
            .12
        );
}


/*
固定バー内部の余白をコンパクトに
*/

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


/*
選択中テキスト
*/

.st-key-reference_bar p {

    margin:
        0 !important;

    font-size:
        .88rem !important;

    color:
        #344a55 !important;
}


/*
「参照する実践を変更」ボタン
*/

.st-key-reference_bar
button {

    min-height:
        2.25rem !important;

    border-radius:
        9px !important;

    font-size:
        .82rem !important;
}


/* =========================================================
   Chat input
========================================================= */

div[data-testid="stChatInput"] {
    border-radius:
        14px !important;
}


/*
chat input周辺を自然につなぐ
*/

[data-testid="stBottom"] {

    background:
        linear-gradient(
            to top,
            #f8fafb 78%,
            rgba(
                248,
                250,
                251,
                0
            )
        );
}


/* =========================================================
   処理中表示
========================================================= */

.st-key-processing_message {

    margin:
        .2rem 0
        1.1rem;

    padding:
        .55rem
        .8rem;

    border-radius:
        10px;

    background:
        #eef7f8;
}

.st-key-processing_message p {

    margin:
        0 !important;

    color:
        #176579 !important;

    font-size:
        .9rem !important;

    font-weight:
        650 !important;
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

    .st-key-reference_bar {

        bottom:
            72px;

        width:
            calc(
                100vw - 20px
            );
    }

    .block-container {

        padding-bottom:
            12rem;
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

    # 実践選択widgetのstateを削除
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

    # 実践カード順になるよう並べ直す
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

    # 下部固定バー側も同期
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

    # 実践カード側も同期
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
# 固定：選択中の実践
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

                    index = (
                        candidate.get(
                            "index",
                            "",
                        )
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

    for message in (
        st.session_state.research_messages
    ):

        role = message.get(
            "role",
            "assistant",
        )

        with st.chat_message(
            role
        ):

            st.markdown(
                message.get(
                    "content",
                    "",
                )
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
# 固定UIを先に生成
#
# chat_inputを先に宣言することで、
# submitされた値を本文描画前にstateへ反映できる。
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
# 入力をまずStateへ登録
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

                # 入力した瞬間に会話履歴へ追加
                # → Gemini処理中でも質問が画面に残る
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
    # 入力した質問を必ず表示
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
    # 質問の直下でGraphRAG処理
    # --------------------------------------------------------

    if (
        st.session_state.pending_graph_query
    ):

        pending_query = (
            st.session_state.pending_graph_query
        )

        with st.container(
            key="processing_message"
        ):

            st.markdown(
                "🔎 ICTマップを探索しています..."
            )

        try:

            with st.spinner(
                "関連する研究知見を確認しています..."
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

    for candidate in (
        st.session_state.practice_candidates
    ):

        display_practice_card(
            candidate
        )

    st.divider()

    # --------------------------------------------------------
    # Document RAG Chat
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
    # これまでの会話
    # --------------------------------------------------------

    display_research_messages()

    # --------------------------------------------------------
    # 新しい質問の直下でDocument RAG処理
    # --------------------------------------------------------

    if (
        st.session_state.pending_document_query
    ):

        pending = (
            st.session_state.pending_document_query
        )

        with st.container(
            key="processing_message"
        ):

            st.markdown(
                "📚 選択した研究知見を"
                "確認しています..."
            )

        try:

            with st.spinner(
                "論文本文を横断して確認しています..."
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

    if st.button(
        "最初からやり直す"
    ):

        reset_all()

        st.rerun()