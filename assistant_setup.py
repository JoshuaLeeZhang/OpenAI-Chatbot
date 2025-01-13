from openai import OpenAI
import os

client = OpenAI()

# Step 1: Create the Assistant
def create_assistant(name, instructions, model="gpt-4o"):
    return client.beta.assistants.create(
        name=name,
        instructions=instructions,
        model=model,
        tools=[{"type": "file_search"}],
    )

# Step 2: Create a Vector Store
def create_vector_store(name):
    return client.beta.vector_stores.create(name=name)

# Step 3: Upload Files to the Vector Store
def upload_files_to_vector_store(vector_store_id, file_paths):
    file_streams = [open(path, "rb") for path in file_paths]
    
    file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id = vector_store_id, files=file_streams
        )

# Step 4: Update the Assistant with Vector Store
def update_assistant_with_vector_store(assistant_id, vector_store_id):
    return client.beta.assistants.update(
        assistant_id=assistant_id,
        tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}},
    )

def setup_assistant(
    assistant_name,
    assistant_instructions,
    model="gpt-4o",
    vector_store_name="default_vector_store"
):
    # Step 1: Create Assistant
    assistant = create_assistant(
        name=assistant_name,
        instructions=assistant_instructions,
        model=model,
    )
    print(f"Assistant '{assistant_name}' created with ID: {assistant.id}")
    
    # Step 2: Create Vector Store
    vector_store = create_vector_store(name=vector_store_name)
    print(f"Vector Store '{vector_store_name}' created with ID: {vector_store.id}")
    
    # Step 3: Upload Files
    file_paths = []
    for root, dirs, files in os.walk('info_folder'):
        for file in files:
            file_paths.append(os.path.join(root, file))

    upload_files_to_vector_store(vector_store_id=vector_store.id, file_paths=file_paths)
    print(f"Files uploaded to Vector Store '{vector_store_name}'.")
    
    # Step 4: Update Assistant
    updated_assistant = update_assistant_with_vector_store(
        assistant_id=assistant.id, vector_store_id=vector_store.id
    )
    print(f"Assistant '{assistant_name}' updated with Vector Store '{vector_store_name}'.")
    return updated_assistant

# SET UP ASSISTANT HERE

setup_assistant(assistant_name = "default_name", assistant_instructions = "default_instructions", model = "gpt-4o", vector_store_name = "default_vector_store")