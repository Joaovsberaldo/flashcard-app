# 3 buttons: send the input, save the card and check the card

# 2 forms: input, output

# 2 screens: create card and check card 

import streamlit as st
from main import create_card, check_card
import random

st.title("Flashcard App")

if "cards" not in st.session_state:
    st.session_state.cards = []

choice = st.sidebar.selectbox("Menu", ["Criar card", "Checar card"])

if choice == "Criar card":
    user_input = st.text_input("Texto original")
    if st.button("Traduzir"):
        cards = create_card(user_input)  # retorna lista com 1 card
        # Exibir o resultado na tela
        st.write(cards[-1]["output"])
        st.session_state.cards += cards
       
        
else:
    if not st.session_state.cards:
        st.warning("Crie pelo menos um card!")
    else:
        card = random.choice(st.session_state.cards)
        st.write("Texto:")
        st.write(card["input"])
        ans = st.text_input("Escreva a resposta")
        if st.button("Checar"):
            # você precisaria adaptar check_card para retornar resultado em vez de print
            st.write("Resposta correta:", card["output"])
            feedback = check_card(card, ans)
            st.write_stream(feedback)