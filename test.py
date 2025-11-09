import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

print("Loading .env file...")
load_dotenv()

print("Attempting to initialize ChatGoogleGenerativeAI...")
api_key= os.getenv("API_KEY")

if not api_key:
    raise ValueError("API_KEY not found in environment variables.")
try:
    llm = ChatGoogleGenerativeAI(api_key= api_key, model="gemini-2.5-pro", temperature=0)
    print("✅ Success! Model initialized automatically.")
    
    # 3. Run a simple test invoke to confirm it works
    print("Sending test prompt...")
    response = llm.invoke("In one paragraph, say 'success'")
    
    print(f"Model response: {response.content}")

except Exception as e:
    print("\n--- ❌ TEST FAILED ---")
    print(f"An error occurred: {e}")