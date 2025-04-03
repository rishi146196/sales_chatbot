from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import os
from langchain_huggingface import HuggingFaceEndpoint

# Initialize FastAPI app
app = FastAPI(
    title="Supply Chain Chatbot API",
    description="An interactive chatbot to manage inventory and orders.",
    version="1.2"
)

# Database setup
conn = sqlite3.connect("supply_chain.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS inventory (id INTEGER PRIMARY KEY, product_name TEXT, stock INTEGER, price REAL)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, order_id TEXT, product_name TEXT, status TEXT)''')
conn.commit()

# Set up Hugging Face API key
huggingface_api_key = os.getenv("HUGGINGFACEHUB_API_TOKEN")

if not huggingface_api_key:
    raise RuntimeError("Hugging Face API key is missing. Set it using 'export HUGGINGFACEHUB_API_TOKEN=your_api_key'")

# Initialize Hugging Face model
try:
    hf_model = HuggingFaceEndpoint(
        endpoint_url="https://api-inference.huggingface.co/models/facebook/opt-1.3b",
        huggingfacehub_api_token=huggingface_api_key
    )
except Exception as e:
    raise RuntimeError(f"Failed to initialize Hugging Face model: {str(e)}")

# Request model
class QueryRequest(BaseModel):
    query: str

@app.get("/")
async def welcome():
    """Welcome message for users."""
    return {"message": "Welcome to the Supply Chain Chatbot API! 🎉"}

@app.post("/chatbot/")
async def chatbot_response(request: QueryRequest):
    """
    Get AI-powered chatbot responses for supply chain queries.
    """
    user_query = request.query.lower()

    try:
        with sqlite3.connect("supply_chain.db") as conn:
            cursor = conn.cursor()

            # Handle highest stock product query
            if "highest stock" in user_query or "most stock" in user_query:
                cursor.execute("SELECT product_name, stock FROM inventory ORDER BY stock DESC LIMIT 1")
                data = cursor.fetchone()
                if data:
                    return {"response": f"📦 The product with the highest stock is {data[0]} with {data[1]} units."}
                return {"response": "No stock data available."}

            # Check for specific stock availability
            elif "stock" in user_query or "available" in user_query:
                words = user_query.split()
                product_name = next((word for word in words if word.lower() in [
                    "laptop", "printer", "smartphone", "mouse", "tablet",
                    "monitor", "keyboard", "headphones", "speaker", "smartwatch"
                ]), None)

                if product_name:
                    cursor.execute("SELECT product_name, stock FROM inventory WHERE LOWER(product_name) LIKE ?", ('%' + product_name.lower() + '%',))
                else:
                    cursor.execute("SELECT product_name, stock FROM inventory WHERE stock > 0")

                data = cursor.fetchall()

                if not data:
                    return {"response": f"No available stock for {product_name if product_name else 'any product'} at the moment."}

                return {"response": "Stock Availability:\n" + "\n".join([f"{item[0]}: {item[1]} units" for item in data])}

            # Check order status
            elif ("order" in user_query and "status" in user_query) or "orders" in user_query:
                words = user_query.split()
                order_id = next((word.lower() for word in words if word.lower().startswith("ord")), None)

                if order_id:
                    cursor.execute("SELECT order_id, product_name, status FROM orders WHERE LOWER(order_id) = ?", (order_id,))
                    data = cursor.fetchone()
                    if data:
                        return {"response": f"📦 Order {data[0]} - {data[1]}: {data[2]}"}
                    return {"response": "❌ No matching order found."}
                
                # Show all orders if no specific order ID is provided
                cursor.execute("SELECT order_id, product_name, status FROM orders")
                data = cursor.fetchall()
                
                if not data:
                    return {"response": "❌ No orders found in the system."}
                
                return {"response": "📦 Order Statuses:\n" + "\n".join([f"🔹 Order {item[0]} - {item[1]}: {item[2]}" for item in data])}

            # Check pricing
            elif "price" in user_query or "cost" in user_query:
                cursor.execute("SELECT product_name, price FROM inventory")
                data = cursor.fetchall()

                if not data:
                    return {"response": "No pricing data available."}

                return {"response": "Pricing Information:\n" + "\n".join([f"💰 {item[0]}: ${item[1]:.2f}" for item in data])}

            # Default AI-powered response using Hugging Face Model
            else:
                ai_response = hf_model.invoke(user_query)
                return {"response": ai_response}

    except Exception as e:
        return {"response": f"⚠️ An error occurred: {str(e)}"}

# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
