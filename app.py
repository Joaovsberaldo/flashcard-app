import streamlit as st
from main import DataStore, FlashcardApp
import random

DATA_FILE = "data.json"
st.title("Flashcard App")

def init_session():
    st.session_state.setdefault("cards", [])
    datastore = DataStore(filename=DATA_FILE)
    state = datastore.load()
    if not state.get("cards"):
        datastore.create_file()
    else:
        st.session_state.cards = state["cards"]
        
def show_create_card():
    user_input = st.text_input("Texto original")
    if st.button("Traduzir"):
        card = FlashcardApp.create_card(user_input)  # retorna card
        # Exibir o resultado na tela
        st.write(card["output"])
        st.session_state.cards.append(card)


def show_review_card():
    if not st.session_state.cards:
        st.write("Nenhum card criado ainda.")
        return
    card = random.choice(st.session_state.cards)
    st.write("Texto:")
    st.write(card["input"])
    user_output = st.text_input("Escreva a resposta")
    if st.button("Revisar"):            
        st.write("Resposta correta:", card["output"])
        app = FlashcardApp()
        feedback = app.review_card(card=card, user_output=user_output)
        st.write_stream(feedback)


def main():
    init_session()
    choice = st.sidebar.selectbox("Menu", ["Criar card", "Revisar card"])
    if choice == "Criar card":
        show_create_card()
    else:
        show_review_card()
        
if __name__ == "__main__":
    main()