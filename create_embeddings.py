import os
import tiktoken
from openai import OpenAI
import numpy as np
import json

client = OpenAI()


def return_embedding(text, model = "text-embedding-3-large"):
    """
    Generates an embedding for a given text using OpenAI's API.
    """
    try:
        response = client.embeddings.create(input=text, model=model)
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding for text: {text[:30]}...: {e}")
        return None

def return_token_size(text):
    """
    Calculates the token size of a given text using tiktoken.
    """
    encoding = tiktoken.get_encoding("cl100k_base")
    num_tokens = len(encoding.encode(text))

    return num_tokens

# max input is 8191
    
def create_embeddings_for_json(data_list):
    """
    Creates embeddings for a list of strings and aggregates them into a single embedding.
    """

    embeddings_array = []
    
    for element in data_list:
        embedding = return_embedding(element)
        if embedding is not None:
            embeddings_array.append(embedding)

    if not embeddings_array:
        print("No valid embeddings generated.")
        return None
        
    aggregated_embeddings = aggregate_embeddings(embeddings_array)
    
    return aggregated_embeddings
        
def aggregate_embeddings(embeddings_array):
    """
    Aggregates an array of embeddings by calculating the mean across all embeddings.
    """

    embeddings_array = np.array(embeddings_array)

    embeddings_averaged = np.mean(embeddings_array, axis=0)

    return embeddings_averaged.tolist()

def create_embeddings_for_products(info_folder="info_folder", output_file="embeddings.json"):
    """
    Reads all JSON files from the specified folder, generates embeddings, and saves the result to a JSON file.
    """

    if not os.path.exists(info_folder):
        print(f"Folder not found: {info_folder}")
        return

    try:
        for file_name in os.listdir(info_folder):
            file_path = os.path.join(info_folder, file_name)

            if file_name.endswith(".json"):
                with open(file_path, 'r') as f:
                    data = json.load(f)
            else:
                print(f"Unsupported file format: {file_name}. Skipping.")
                continue

            # Generate embeddings for this file
            embeddings = create_embeddings_for_json(data)

        # Save all embeddings to a single JSON file
        with open(output_file, 'w') as f:
            json.dump(embeddings, f)
        print(f"Embeddings saved to {output_file}")
    except Exception as e:
        print(f"Error processing folder {info_folder}: {e}")

create_embeddings_for_products()

