from typing import Any

import streamlit as st

from document_pipeline import run_document_rag
from rag_pipeline import run_pipeline


# ============================================================
# ページ設定
# ============================================================

st.set_page_config(
    page_title="理科ICT授業実践アシスタント",
    page_icon="🔬",
    layout="centered",
)

st.title("理科ICT授業実践アシスタント")

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
    # practice_idごとに会話履歴を保持する
    st.session_state.document_messages = {}

if "document_pending_queries" not in st.session_state:
    # practice_idごとに回答生成待ちの質問を保持する
    st.session_state.document_pending_queries = {}

if "has_generated_candidates" not in st.session_state:
    st.session_state.has_generated_candidates = False


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
    st.session_state.has_generated_candidates = False


def initialize_document_state(
    practice_id: str,
) -> None:
    """
    practice_idごとのDocument RAG用状態を初期化する。
    """
    if practice_id not in st.session_state.document_messages:
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


def toggle_practice(practice_id: str) -> None:
    """
    実践カードの展開・閉じるを切り替える。

    別の実践を開いた場合は、
    それまで開いていた実践を閉じる。
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

def display_processing_error(
    error: Exception,
    process_name: str,
) -> None:
    """
    APIエラーなどを利用者向けの表現で表示する。
    """
    error_text = str(error)

    if (
        "429" in error_text
        or "RESOURCE_EXHAUSTED" in error_text
    ):
        st.warning(
            "現在、AIの利用回数が一時的な上限に達しています。"
            "時間を空けてから、もう一度お試しください。"
        )

    elif (
        "503" in error_text
        or "UNAVAILABLE" in error_text
    ):
        st.warning(
            "現在、AIへのアクセスが混み合っています。"
            "少し時間を空けてから、もう一度お試しください。"
        )

    elif (
        "404" in error_text
        or "NOT_FOUND" in error_text
    ):
        st.error(
            "現在、AIモデルを利用できません。"
            "管理者に設定の確認を依頼してください。"
        )

    else:
        st.error(
            f"{process_name}の途中で"
            "エラーが発生しました。"
        )

    # 開発中の詳細確認用
    with st.expander("エラーの詳細"):
        st.code(error_text)


# ============================================================
# 表示用ヘルパー
# ============================================================

def join_values(values: list[Any]) -> str:
    """
    空の値を除外して「、」で連結する。
    """
    normalized_values = [
        str(value).strip()
        for value in values
        if str(value).strip()
    ]

    return "、".join(normalized_values)


def display_basic_information(
    candidate: dict[str, Any],
) -> None:
    """
    学年・領域・単元を3列で表示する。
    """
    columns = st.columns(3)

    with columns[0]:
        st.markdown("**学年**")
        st.write(
            candidate.get("grade")
            or "記載なし"
        )

    with columns[1]:
        st.markdown("**領域**")
        st.write(
            candidate.get("field")
            or "記載なし"
        )

    with columns[2]:
        st.markdown("**単元**")
        st.write(
            candidate.get("unit")
            or "記載なし"
        )


def display_document_message(
    message: dict[str, Any],
) -> None:
    """
    Document RAGの会話メッセージを表示する。
    """
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

    with st.chat_message(role):
        st.markdown(content)

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
# 論文本文への質問欄
# ============================================================

def display_document_conversation(
    candidate: dict[str, Any],
) -> None:
    """
    展開された実践カード内に、
    論文本文を対象としたチャット欄を表示する。

    表示順:
        1. 過去の会話履歴
        2. 新しく送信されたユーザー質問
        3. AIの回答または回答生成中の表示
        4. 次の質問を入力するチャット入力欄

    質問送信後は一度再描画し、
    ユーザーの質問を画面へ先に表示してから
    回答生成を開始する。
    """
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

    messages = st.session_state.document_messages[
        practice_id
    ]

    pending_query = (
        st.session_state.document_pending_queries[
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

    # 会話開始前だけ質問例を表示する
    if not messages and not pending_query:
        st.info(
            "例えば、"
            "「生徒はどのような活動をしましたか？」"
            "「ICTをどのように活用しましたか？」"
            "「別の学年へ応用するとしたら、"
            "どのような授業が考えられますか？」"
            "などと質問できます。"
        )

    # --------------------------------------------------------
    # 保存済みの会話履歴を表示
    # --------------------------------------------------------

    for message in messages:
        display_document_message(
            message=message
        )

    # --------------------------------------------------------
    # 回答待ちの質問があれば回答を生成
    # --------------------------------------------------------

    if pending_query:
        try:
            # AIのメッセージ領域には、
            # 回答生成中はスピナーだけを表示する
            with st.chat_message("assistant"):
                with st.spinner(""):
                    result = run_document_rag(
                        query=pending_query,
                        paper_ids=[paper_id],
                        top_k=5,
                    )

            assistant_message = {
                "role": "assistant",
                "content": result["answer"],
                "sources": result.get(
                    "sources",
                    [],
                ),
            }

            messages.append(
                assistant_message
            )

            st.session_state.document_pending_queries[
                practice_id
            ] = None

            # 完成した回答を会話履歴として再描画し、
            # その下に入力欄を表示する
            st.rerun()

        except Exception as error:
            st.session_state.document_pending_queries[
                practice_id
            ] = None

            display_processing_error(
                error=error,
                process_name="回答の作成",
            )

            # エラー後も次の質問を入力できるようにするため、
            # ここではreturnしない

    # --------------------------------------------------------
    # チャット入力欄を会話履歴の一番下に表示
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

    # --------------------------------------------------------
    # 質問を履歴へ追加し、回答待ち状態にする
    # --------------------------------------------------------

    messages.append(
        {
            "role": "user",
            "content": normalized_question,
        }
    )

    st.session_state.document_pending_queries[
        practice_id
    ] = normalized_question

    # 次の再描画でユーザー質問を先に表示し、
    # その下で回答を生成する
    st.rerun()


# ============================================================
# 実践カード
# ============================================================

def display_practice_card(
    candidate: dict[str, Any],
) -> None:
    """
    実践の概要と展開ボタンを表示する。
    """
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
        candidate.get("title")
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

    with st.container(border=True):
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
            key=f"toggle_{practice_id}",
            disabled=not bool(paper_id),
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
# 相談内容の入力
# ============================================================

def display_request_form() -> None:
    """
    授業づくりについての相談内容を入力する。
    """
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
            value=st.session_state.user_request,
            placeholder=(
                "例：高校3年生の生物でInstagramを活用し、"
                "観察への意欲を高めたいです。"
                "参考になる実践を教えてください。"
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
            "条件に合う実践を考えています..."
        ):
            result = run_pipeline(
                user_query=normalized_request
            )

        st.session_state.user_request = (
            normalized_request
        )

        st.session_state.practice_candidates = (
            result.get(
                "practice_candidates",
                [],
            )
        )

        st.session_state.expanded_practice_id = None

        st.session_state.document_messages = {}

        st.session_state.document_pending_queries = {}

        st.session_state.has_generated_candidates = True

        st.rerun()

    except Exception as error:
        display_processing_error(
            error=error,
            process_name="実践の提案",
        )


# ============================================================
# 提案結果
# ============================================================

def display_practice_candidates() -> None:
    """
    提案された実践をカード形式で表示する。
    """
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
            "条件に合う実践を提案できませんでした。"
            "条件を少し変えて、もう一度お試しください。"
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