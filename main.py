from dotenv import load_dotenv
from google import genai 
import time
import os
load_dotenv(".env")

google_api_key = os.getenv("GOOGLE_API_KEY")

client = genai.Client(api_key=google_api_key)

def create_card(user_input: str) -> list[dict]:
    # Capture the input
     
    # Gerenate the output
    response = client.models.generate_content_stream(
        model="gemini-2.0-flash",
        contents=[(
            "You are an translator for an flashcard app. You are responsible to translate user inputs to portuguese from Brazil."
            "Example: "
            "Input: Hello, world"
            "Output: Olá, mundo!"
            f"Generate a translation for the following input: {user_input}"
        )]
    )
    text = []
    for chunk in response:
        text.append(chunk.text)
        print(chunk.text, end="")
    output = " ".join(text)
    
    card = {
        "input": user_input,
        "output": output
    }
    cards = []
    cards.append(card)
    print("Card created!")
    return cards

def check_card(card: dict, user_output: str):         
    
    if user_output.lower() == card["output"].lower():
        return "Sua resposta está correta!"
    else:
        response = client.models.generate_content_stream(
            model="gemini-2.0-flash",
            contents=[(
                "</General instructions"
                "You are an translator assistant for a flashcard app. You goal is to check if the user translation for a text is correct.\<"
                
                ">/Task:"
                "Check the following input/output pair." 
                "To do this, use your knowledge to judge the user output given the input and compare it with the target output."
                f"Input: {card['input']}"
                f"User output: {user_output}"
                f"Target Output: {card['output']}"
                "Your answer needs to be concise and less than 50 words."
                "You answer should have 2 paragraphs: The first is to classify the user output and the second is to give a feedback on the user output."
                "As a feedback you can analyze the correcteness, fluency and coherence of the user output."
                "Always answer in Portuguese from Brazil."
                "Always answer in second person.\<"
                
                ">/Example 1:"
                "Your answer is correct."
                "Your translation is accurate and reads naturally in Portuguese. There are no issues with grammar or vocabulary."
                "Example 2:"
                "Your translation is correct but it's not fluent. The words Y and X could be switch to Z and W, because is more natural for this situation in Portuguese.\<"  
            )]
        )
        
        for chunk in response:
            yield chunk.text + ""
            time.sleep(0.03)
    
    

def main():
    print("Hello from flashcard-app!")

if __name__ == "__main__":
    main()
    create_card
    check_card
