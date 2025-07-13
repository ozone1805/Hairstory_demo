import os
import openai
import requests
import time
import sys

# Constants
API_BASE_URL = "https://api.openai.com/v1"
FILE_PATH = "product_catalogue.txt"
ASSISTANT_NAME = "Hairstory demo v6"
VECTOR_STORE_NAME = "Hairstory Product Catalog"
MAX_RETRIES = 30
POLL_INTERVAL = 2

def load_api_key():
    """Load and validate OpenAI API key from environment."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set in environment variables.")
    return api_key

def get_headers(api_key):
    """Get headers for API requests."""
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "OpenAI-Beta": "assistants=v2"
    }

def upload_file(api_key):
    """Upload the catalog file and return file ID."""
    print("Uploading file...")
    openai.api_key = api_key
    
    uploaded_file = openai.files.create(
        file=open(FILE_PATH, "rb"),
        purpose="assistants"
    )
    file_id = uploaded_file.id
    print(f"✅ Uploaded {FILE_PATH} — File ID: {file_id}")
    return file_id

def create_vector_store(api_key, headers):
    """Create a vector store and return its ID."""
    print("Creating vector store...")
    
    vector_store_data = {
        "name": VECTOR_STORE_NAME,
        "expires_after": {
            "anchor": "last_active_at",
            "days": 30
        }
    }
    
    response = requests.post(
        f"{API_BASE_URL}/vector_stores",
        headers=headers,
        json=vector_store_data
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to create vector store: {response.status_code} - {response.text}")
        sys.exit(1)
    
    vector_store = response.json()
    vector_store_id = vector_store["id"]
    print(f"✅ Vector store created — ID: {vector_store_id}")
    return vector_store_id

def add_file_to_vector_store(api_key, headers, vector_store_id, file_id):
    """Add file to vector store and return batch ID."""
    print("Adding file to vector store...")
    
    file_batch_data = {"file_ids": [file_id]}
    
    response = requests.post(
        f"{API_BASE_URL}/vector_stores/{vector_store_id}/file_batches",
        headers=headers,
        json=file_batch_data
    )
    
    if response.status_code not in (200, 202):
        print(f"❌ Failed to add file to vector store: {response.status_code} - {response.text}")
        sys.exit(1)
    
    file_batch = response.json()
    file_batch_id = file_batch["id"]
    print(f"✅ File batch created — ID: {file_batch_id}")
    return file_batch_id

def wait_for_batch_completion(api_key, headers, vector_store_id, file_batch_id):
    """Wait for file batch to complete processing."""
    print("Waiting for file batch to complete...")
    
    for attempt in range(MAX_RETRIES):
        response = requests.get(
            f"{API_BASE_URL}/vector_stores/{vector_store_id}/file_batches/{file_batch_id}",
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to check file batch status: {response.status_code} - {response.text}")
            sys.exit(1)
        
        batch_status = response.json()
        status = batch_status["status"]
        
        if status == "completed":
            print("✅ File batch completed successfully")
            return
        elif status == "failed":
            error_msg = batch_status.get('error', 'Unknown error')
            print(f"❌ File batch failed: {error_msg}")
            sys.exit(1)
        else:
            print(f"⏳ File batch status: {status} (attempt {attempt + 1}/{MAX_RETRIES})")
            time.sleep(POLL_INTERVAL)
    
    print(f"❌ File batch did not complete within {MAX_RETRIES * POLL_INTERVAL} seconds")
    sys.exit(1)

def create_assistant(api_key, vector_store_id):
    """Create assistant with vector store for file search."""
    print("Creating assistant...")
    openai.api_key = api_key
    
    assistant = openai.beta.assistants.create(
        name=ASSISTANT_NAME,
        instructions="""Begin every statement with bananas! and say bananas! before the user asks any questions. You are a haircare product expert and always refer to the uploaded product catalog when answering questions. If someone asks you something that's not about haircare, then say you don't know but you're happy to help with hair product recommendations. For now, the link formatting is not supported, so please use the product name instead. First try to reccommend singleton products, but if the user asks for a bundle, or the products your recommend are in a bundle, then recommend the bundle.""",
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
    return assistant_id

def print_summary(assistant_id, file_id, vector_store_id, file_batch_id):
    """Print summary of created resources."""
    print(f"\n📋 Summary:")
    print(f"Assistant ID: {assistant_id}")
    print(f"File ID: {file_id}")
    print(f"Vector Store ID: {vector_store_id}")
    print(f"File Batch ID: {file_batch_id}")
    print(f"🌐 Playground URL: https://platform.openai.com/playground/assistants?assistant={assistant_id}&mode=assistant")

def main():
    """Main function to orchestrate the assistant creation process."""
    try:
        # Load API key
        api_key = load_api_key()
        headers = get_headers(api_key)
        
        # Step 1: Upload file
        file_id = upload_file(api_key)
        
        # Step 2: Create vector store
        vector_store_id = create_vector_store(api_key, headers)
        
        # Step 3: Add file to vector store
        file_batch_id = add_file_to_vector_store(api_key, headers, vector_store_id, file_id)
        
        # Step 4: Wait for batch completion
        wait_for_batch_completion(api_key, headers, vector_store_id, file_batch_id)
        
        # Step 5: Create assistant
        assistant_id = create_assistant(api_key, vector_store_id)
        
        # Step 6: Print summary
        print_summary(assistant_id, file_id, vector_store_id, file_batch_id)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
