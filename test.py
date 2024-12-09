import dotenv
import os
dotenv.load_dotenv()

print(os.getenv("OPENAI_API_KEY"))
