
from langchain_ollama import OllamaLLM as Ollama
from langchain.prompts import ChatPromptTemplate
import threading
from ...core.models import Tag, FoodItem, Rating, ReviewAgent, CartItem, Order, OrderItem


def handle_ai_recommendation(order_data):
    threading.Thread(
        target=ai_recommendation,
        args=(order_data,)
    ).start()

def ai_recommendation(order_data):
    # past_orders = OrderItem.objects.all()
    try:
        llm = Ollama(model="mistral", temperature = 0.7)
        menu = FoodItem.objects.all()
        prompt_template = """
            Make a recommendation from the menu {menu} based on the for the user previous orders, make sure it is an item available in the menu:
            {formatted_data}
        """
        formatted_data = {
            "\n".join(
            f"order: {o["food_item__name"]}"
            for o in order_data
        )}
        print("working1")
        prompt = ChatPromptTemplate.from_template(prompt_template)
        chain = prompt | llm
        analysis = chain.invoke({"formatted_data": formatted_data, "menu": menu})
        print("working", analysis)
    except Exception as e:
        print("failed", e)