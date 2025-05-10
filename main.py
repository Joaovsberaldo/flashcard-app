from dotenv import load_dotenv
from google import genai 
import time, os, json, uuid, random
from typing import Dict, List, Union, Optional, Generator
load_dotenv(".env")

DATA_FILE = "data.json"

google_api_key = os.getenv("GOOGLE_API_KEY")

class DataStore:
    """Handles loading and saving flashcard data."""
    def __init__(self, filename: str = DATA_FILE) -> None:
        self.filename = filename
        
    def load(self) -> Dict[str, Union[List[dict], Dict[str, dict]]]:
        """Load data from the JSON file."""
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {"cards": [], "progress": {}}
        
    def save(self, data: Dict[str, Union[List[dict], Dict[str, dict]]]) -> None:
        """Save data to the JSON file."""
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def create_file(self) -> None:
        """Create a new data file with empty cards and progress dict."""
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump({"cards": [], "progress": {}}, f, ensure_ascii=False, indent=2)

class FlashcardApp:
    """Flashcard application handling card creation and review."""
    def __init__(self, client: Optional[genai.Client] = None, datastore: Optional[DataStore] = None):
        if client is None:
            client = genai.Client(api_key=google_api_key)
        self.client = client
        if datastore is None:
            datastore = DataStore(filename=DATA_FILE)
        self.datastore = datastore

    def create_card(self, user_input: str) -> dict:
        """
        Create a new flashcard by generating a Portuguese translation.

        Args:
            user_input: The text to translate.

        Returns:
            The new card dictionary with id, input, and output.
        """
        prompt = (
                "You are an translator for an flashcard app. You are responsible to translate user inputs to portuguese from Brazil."
                "Example: "
                "Input: Hello, world"
                "Output: Olá, mundo!"
                f"Generate a translation for the following input: {user_input}"
            )
        response = self.client.models.generate_content_stream(
            model="gemini-2.0-flash",
            contents=[prompt]
        )
        text = []
        for chunk in response:
            text.append(chunk.text)
            print(chunk.text, end="")
        output = " ".join(text)
        
        new_card = {
                "id": str(uuid.uuid4()),
                "input": user_input,
                "output": output,
        }

        new_progress = {
            "card_id": new_card["id"],
            "reviews": 0,
        }
        
        state = self.datastore.load()
        cards = state["cards"]
        progress = state["progress"]
        
        cards.append(new_card)
        progress.append(new_progress)
        new_state = {"cards": cards, "progress": progress}
        self.datastore.save(new_state)
        print("Card created!")
        return new_card
    
    def review_card(self, card: dict, user_output: str) -> Union[str, Generator[str, None, None]]:
        """
        Review a random card by comparing user output with the stored translation.

        Args:
            user_output: The user's translation attempt.

        Returns:
            If the answer is correct, returns a success message string.
            If incorrect, returns a generator yielding feedback text chunks.
        """
        state = self.datastore.load()  
        cards = state.get("cards", [])
        if not cards:
            return "No cards available to review."
        
        target_output = card["output"]
        
        # Valida se a resposta do usuário é idêntica a resposta alvo
        if user_output.lower() == target_output.lower():
            progress = state.get("progress")
            for p in progress:
                if p["card_id"] == card["id"]:
                    p["reviews"] += 1
                    state["progress"] = progress
                    self.datastore.save(state)
                return "The answer is correct!"
            
        else:
            prompt = (
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
            )
            response = self.client.models.generate_content_stream(
                model="gemini-2.0-flash",
                contents=[prompt]
            )
            # Salva o progresso
            progress = state.get("progress")
            for p in progress:
                if p["card_id"] == card["id"]:
                    p["reviews"] += 1
                    state["progress"] = progress
                    self.datastore.save(state)
                    break
                
            # Imprime a resposta
            for chunk in response:
                print(chunk.text, end="")
                yield chunk.text + ""
                time.sleep(0.05)
                

# def main():
#     print("Hello from flashcard-app!")

# if __name__ == "__main__":
#     main()
#     create_card
#     review_card
