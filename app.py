import streamlit as st
from main import DataStore, FlashcardApp
import random

DATA_FILE = "data.json"
st.title("O que vamos traduzir hoje?")

def init_session():
    st.session_state.setdefault("cards", [])
    datastore = DataStore(filename=DATA_FILE)
    state = datastore.load()
    if not state.get("cards"):
        datastore.create_file()
    else:
        st.session_state.cards = state["cards"]
        st.session_state.progress = state["progress"]
        
def show_create_card():
    with st.container():
        user_input = st.chat_input("Escreva o texto a ser traduzido")
        if user_input:
            app = FlashcardApp()
            card = app.create_card(user_input)  # retorna card
            st.write(card["output"])
            st.success("Card criado e pronto para revisão!")
            st.session_state.cards.append(card)
        

def next_card(previous_card: dict): 
    """
    Input: Acão do usuário
    Logic: 
    1. Se o usuário clicar no botão
    2. Exibir próximo card aleatório
    Output: Exibir outro card, diferente do anterior
    """
    card = random.choice(st.session_state.cards)
    if len(st.session_state.cards) == 1:
        st.write("Não há mais cards para revisar.")
    else: 
        card["id"] != previous_card["id"]
        return card


def show_review_card():
    if not st.session_state.cards:
        st.write("Nenhum card criado ainda.")
        return
    # escolhe e guarda o card atual
    card = random.choice(st.session_state.cards)
    st.session_state.current_card = card

    progress = st.session_state.progress
    st.write(card["input"]) # Não sendo atualizado ao clicar no botão de enviar, gerando inconsistência entre o output esperado em 
    
    # Exibir quantas vezes o card foi revisado
    for p in progress:
        if p["card_id"] == card["id"]:
            st.write("Revisões:", p["reviews"])
           
    user_output = st.chat_input("Escreva a resposta")
    if user_output:           
        # st.write("Resposta correta:", card["output"])
        app = FlashcardApp()
        review = app.review_card(card=card, user_output=user_output)
        st.write_stream(review)
    # Botão para ir ao próximo card
    if st.button("Próximo Card"):
        # chama a função que seleciona outro card diferente
        next_card(st.session_state.current_card)
        

def main():
    init_session()
    choice = st.sidebar.selectbox("Menu", ["Criar card", "Revisar card"])
    if choice == "Criar card":
        show_create_card()
    else:
        show_review_card()
        
if __name__ == "__main__":
    main()