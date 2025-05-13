import streamlit as st
import pandas as pd
import json
import datetime
import plotly.graph_objs as go

def read_jsonl(file_path: str):
    with open(file_path, "r") as f:
        data = [json.loads(line) for line in f]
    return data

# ---------- Inicialização ----------
if "cards" not in st.session_state:
    st.session_state.cards = []
    data = read_jsonl("flashcards.jsonl")
    st.session_state.cards.extend(data)     
if "review_index" not in st.session_state:
    st.session_state.review_index = 0
if "flipped" not in st.session_state:
    st.session_state.flipped = False
if "stats" not in st.session_state:
    st.session_state.stats = {}
if "total_reviewed" not in st.session_state:
    st.session_state.total_reviewed = 0
if "total_correct" not in st.session_state:
    st.session_state.total_correct = 0

def get_today():
    return datetime.date.today().isoformat()

# --------- Navegação lateral ------------

st.sidebar.title("📝 Flashcards")
sidebar_choice = st.sidebar.radio("Navegar", ["Review", "Search", "Stats", "Create"])

# -------- Funções de Revisão e Estatística --------
def do_flip():
    st.session_state.flipped = not st.session_state.flipped
    
def marcar_revisao(acertou=False):
    hj = get_today()
    if hj not in st.session_state.stats:
        st.session_state.stats[hj] = {"reviewed": 0, "correct": 0}
    st.session_state.total_reviewed += 1
    st.session_state.stats[hj]["reviewed"] += 1
    if acertou:
        st.session_state.total_correct += 1
        st.session_state.stats[hj]["correct"] += 1

def avancar(offset):
    n = len(st.session_state.cards)
    st.session_state.review_index = (st.session_state.review_index + offset) % n
    st.session_state.flipped = False

# --------- Interface de Revisão ----------
if sidebar_choice == "Review":
    st.header("🔄 Flashcard Review")
    cards = st.session_state.cards
    idx = st.session_state.review_index

    if not cards:
        st.info("Nenhum flashcard cadastrado! Use a aba Create para adicionar.")
    else:
        card = cards[idx]
        st.write(f"Card {idx+1} / {len(cards)}")

        # 1) Botão de Flip sempre visível e processado ANTES de renderizar o cartão
        flip_label = "↩️ Desvirar" if st.session_state.flipped else "👁️ Virar"
        st.button(flip_label, on_click=do_flip, key="btn_flip")

        # 2) Renderiza o cartão de acordo com o estado flipped atualizado
        if st.session_state.flipped:
            st.markdown(
                f"""
                <div style="margin:1em 0;padding:2em;
                            text-align:center;
                            background:linear-gradient(90deg,#e4f7fa,#c8d5fc);
                            font-size:2em;border-radius:1em;
                            border:2px solid #a5c4fb;
                            box-shadow:0 2px 17px #afcbeb36;">
                  <b>{card['back']}</b>
                </div>
                """,
                unsafe_allow_html=True,
            )
            # Botões de “Acertou” e “Próximo” só quando virado
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ Acertou", on_click=do_flip, key="btn_acertou"):
                    marcar_revisao(True)
                    st.session_state.flipped = False
                    avancar(1)
            with c2:
                if st.button("➡️ Próximo", on_click=do_flip, key="btn_prox"):
                    marcar_revisao(False)
                    st.session_state.flipped = False
                    avancar(1)
        else:
            st.markdown(
                f"""
                <div style="margin:1em 0;padding:2em;
                            text-align:center;
                            background:linear-gradient(90deg,#456bc2,#c2e1fa);
                            color:white;font-size:2em;
                            border-radius:1em;
                            border:2px solid #668efd;
                            box-shadow:0 2px 17px #a3a9ec36;">
                  <b>{card['front']}</b>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # 3) Navegação “Anterior” / “Próximo (pular)”
        nav1, nav2 = st.columns(2)
        with nav1:
            if st.button("⬅️ Anterior", key="btn_ant"):
                st.session_state.flipped = False
                avancar(-1)
        with nav2:
            if st.button("➡️ Pular", key="btn_skip"):
                st.session_state.flipped = False
                avancar(1)

    st.write("Dica: use o mesmo botão para virar e desvirar, e marque ‘Acertou’ ou ‘Próximo’ após ver o verso.")
    
# ----------- Interface de Pesquisa ---------
elif sidebar_choice == "Search":
    st.header("🔍 Search Cards")
    search = st.text_input("Buscar cartões (Português ou Inglês):")
    filtered = [
        c for c in st.session_state.cards
        if search.strip().lower() in c["front"].lower() or search.strip().lower() in c["back"].lower()
    ]
    st.markdown(f"Exibindo {len(filtered)} resultado(s).")
    for c in filtered:
        st.markdown(
            f"""<div style="margin:1em 0;padding:1em 1.5em;background:#eef5ff;border-radius:8px;font-size:1.2em;">
                <b style="color:#29508A;">{c['front']}</b>
                <span style="color:#3c7;">→</span>
                <b style="color:#329657;">{c['back']}</b>
            </div>""",
            unsafe_allow_html=True,
        )
    if not filtered:
        st.warning("Nenhum cartão encontrado.")

# ---------- Interface de Estatísticas ----------
elif sidebar_choice == "Stats":
    st.header("📈 Estatísticas de Revisão")
    st.write(f"Total de cartões: **{len(st.session_state.cards)}**")
    st.write(f"Total revisões: **{st.session_state.total_reviewed}**")
    acertos = st.session_state.total_correct
    total = st.session_state.total_reviewed
    pct = int(100.0 * acertos / total) if total>0 else 0
    st.write(f"Percentual de acerto: **{pct}%**")

    statsdf = (
        pd.DataFrame(st.session_state.stats).T.sort_index()
        if st.session_state.stats else
        pd.DataFrame(columns=["reviewed","correct"])
    )
    ultimosdias = [
        (datetime.date.today()-datetime.timedelta(days=d)).isoformat()
        for d in reversed(range(14))
    ]
    statsdf = statsdf.reindex(ultimosdias, fill_value=0)
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=statsdf.index,
            y=statsdf["reviewed"],
            name="Revisados",
            marker_color="#29508A"
        )
    )
    fig.add_trace(
        go.Bar(
            x=statsdf.index,
            y=statsdf["correct"],
            name="Acertos",
            marker_color="#39B67B"
        )
    )
    fig.update_layout(
        barmode='group',
        xaxis_title="Dia",
        yaxis_title="Quantidade",
        title="Histórico (14 últimos dias)",
        height=350,
        margin=dict(l=20,r=30,t=55,b=10)
    )
    st.plotly_chart(fig,use_container_width=True)

# ----------- Interface de Criação de Cards ------------
elif sidebar_choice == "Create":
    st.header("➕ Criar Novo Flashcard")
    with st.form(key="flashform", clear_on_submit=True):
        front = st.text_input("Frente:", max_chars=64)
        back = st.text_input("Verso:", max_chars=64)
        submit = st.form_submit_button("Adicionar Flashcard")
        if submit and front.strip() and back.strip():
            st.session_state.cards.append({"front": front.strip(), "back": back.strip()})
            st.success("Flashcard adicionado com sucesso!")


# ------- Rodapé -------
st.sidebar.markdown("---")
st.sidebar.caption("Feito com Streamlit\n\nPortuguês ↔ English Flashcards\n\npor ChatGPT")