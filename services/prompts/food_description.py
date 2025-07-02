
from langchain_ollama import OllamaLLM as Ollama
from langchain.prompts import ChatPromptTemplate
import threading
from core.models import Tag, FoodItem, Rating, ReviewAgent, CartItem, Order, OrderItem

def handle_description_generation(food_item_id):
    threading.Thread(
        target=generate_and_update_description,
        args=(food_item_id,)
    ).start()

def generate_and_update_description(food_item_id):
    print("processing")
    food_item =FoodItem.objects.get(id=food_item_id)
    try:
    
        llm = Ollama(model="mistral", temperature=0.7)
        prompt_template = """
            You are a professional food critic and menu description writer. 
            Create an brief 2 sentence description for this menu item and inspect the images to help in your description:
            
            food: {name}
            tags: {tags}
        """
        
        context = {
            "name": food_item.name,
            "image": food_item.image,
            "tags": " ,".join([tag.tag for tag in food_item.tags.all()]) if food_item.tags.exists() else ""
        }
        
        prompt = ChatPromptTemplate.from_template(prompt_template)
        chain = prompt | llm
        description = chain.invoke(context)
        
        food_item.description = description
        food_item.description_generated = True
        food_item.save()
        print("Done!")
    except Exception as e:
        print("Didn't work, deleting created food" )
        food_item.delete()
    