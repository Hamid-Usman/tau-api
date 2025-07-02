
from langchain_ollama import OllamaLLM as Ollama
from langchain.prompts import ChatPromptTemplate
import threading
from core.models import Tag, FoodItem, Rating, ReviewAgent, CartItem, Order, OrderItem


def handle_ai_recommendation(order_data):
    threading.Thread(
        target=ai_recommendation,
        args=(order_data,)
    ).start()

def ai_recommendation(order_data):
    # past_orders = OrderItem.objects.all()
    try:
        llm = Ollama(model="mistral", temperature = 0.7)
        menu = FoodItem.objects.filter(available=True)
        print("Menu items from DB:")
        for item in menu:
            print("-", item.name)
            
        menu_data = "\n".join(
            f"menu: {item}"
            for item in menu
        )
        prompt_template = """
            Look into the database for the FoodItems {menu} and give a recommendation based on the user's previous order history, make sure it is an item available in the menu:
            {formatted_data}
            These are the currently available on the menu: {menu}
            
        Based on the history and menu, recommend ONE item the user is likely to enjoy.
        Only recommend items from the menu. Keep it concise. unless return 0
        """
        formatted_data = "\n".join(
            f"order: {o["food_item__name"]}"
            for o in order_data
        )
        print("working1")
        prompt = ChatPromptTemplate.from_template(prompt_template)
        chain = prompt | llm
        analysis = chain.invoke({"formatted_data": formatted_data, "menu": menu_data})
        print("working", analysis)
    except Exception as e:
        print("failed", e)