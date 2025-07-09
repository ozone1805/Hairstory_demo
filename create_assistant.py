import os
import openai
import requests
import time

# Load API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not set in environment variables.")

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

# 2. Create a vector store using direct API calls
print("Creating vector store...")
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "OpenAI-Beta": "assistants=v2"
}

# Create vector store
vector_store_data = {
    "name": "Hairstory Product Catalog",
    "expires_after": {
        "anchor": "last_active_at",
        "days": 30
    }
}

response = requests.post(
    "https://api.openai.com/v1/vector_stores",
    headers=headers,
    json=vector_store_data
)

if response.status_code != 200:
    print(f"❌ Failed to create vector store: {response.status_code} - {response.text}")
    exit(1)

vector_store = response.json()
vector_store_id = vector_store["id"]
print(f"✅ Vector store created — ID: {vector_store_id}")

# 3. Add the file to the vector store
print("Adding file to vector store...")
file_batch_data = {
    "file_ids": [file_id]
}

response = requests.post(
    f"https://api.openai.com/v1/vector_stores/{vector_store_id}/file_batches",
    headers=headers,
    json=file_batch_data
)

if response.status_code not in (200, 202):
    print(f"❌ Failed to add file to vector store: {response.status_code} - {response.text}")
    exit(1)

file_batch = response.json()
file_batch_id = file_batch["id"]
print(f"✅ File batch created — ID: {file_batch_id}")

# 4. Wait for the file batch to complete
print("Waiting for file batch to complete...")
while True:
    response = requests.get(
        f"https://api.openai.com/v1/vector_stores/{vector_store_id}/file_batches/{file_batch_id}",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to check file batch status: {response.status_code} - {response.text}")
        exit(1)
    
    batch_status = response.json()
    status = batch_status["status"]
    
    if status == "completed":
        print("✅ File batch completed successfully")
        break
    elif status == "failed":
        print(f"❌ File batch failed: {batch_status.get('error', 'Unknown error')}")
        exit(1)
    else:
        print(f"⏳ File batch status: {status}")
        time.sleep(2)

# 5. Create the assistant with the new vector store
print("Creating assistant...")
assistant = openai.beta.assistants.create(
    name="Hairstory demo v3",
    instructions="You are a haircare product expert and always refer to the uploaded product catalog when answering questions. If someone asks you something that's not about haircare, then say you don't know but you're happy to help with hair product recommendations.",
    model="gpt-4o-mini",
    tools=[{"type": "file_search"}],
    tool_resources={
        "file_search": {
            "vector_store_ids": [vector_store_id]
        }
    }
)
assistant_id = assistant.id
print(f"✅ Assistant created — ID: {assistant_id}")

# Output Playground link
print(f"\n📋 Summary:")
print(f"Assistant ID: {assistant_id}")
print(f"File ID: {file_id}")
print(f"Vector Store ID: {vector_store_id}")
print(f"File Batch ID: {file_batch_id}")
print(f"🌐 Playground URL: https://platform.openai.com/playground?assistant={assistant_id}")
