from dotenv import load_dotenv
import os

env_path = "D:\\watchdog n1\\.env"

print("File exists:", os.path.exists(env_path))

load_dotenv(dotenv_path=env_path)

print("DATABASE_URL =", os.getenv("DATABASE_URL"))
print("OPENAI =", os.getenv("OPENAI_API_KEY"))