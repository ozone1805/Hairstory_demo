import os
import openai

# Load API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPEN_API_KEY not set in environment variables.")

openai.api_key = api_key

# 1. Upload the file
file_path = "fakecatalog.txt"
print("Uploading file...")
uploaded_file = openai.files.create(
    file=open(file_path, "rb"),
    purpose="assistants"
)
file_id = uploaded_file.id
print(f"✅ Uploaded fakecatalog.txt — File ID: {file_id}")

# 2. Create the assistant (no file_ids here)
print("Creating assistant...")
assistant = openai.beta.assistants.create(
    name="Hairstory demo v2",
    instructions="You are a haircare product expert and always refer to the uploaded product catalog when answering questions. If someone asks you something that's not about haircare, then say you don't know but you're happy to help with hair product recommendations.",
    model="gpt-4o-mini",
    tools=[{"type": "file_search"}],
)
assistant_id = assistant.id
print(f"✅ Assistant created — ID: {assistant_id}")

# Output Playground link
print(f"Assistant ID: {assistant_id}")
print(f"File ID: {file_id}")
print(f"🌐 Playground URL: https://platform.openai.com/playground?assistant={assistant_id}")
