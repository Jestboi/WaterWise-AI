from huggingface_hub import snapshot_download
import os

def download_model():
    # Set the model name
    model_name = "meta-llama/Llama-3.2-3B-Instruct"
    
    try:
        # Download the model
        print(f"Downloading {model_name}...")
        local_dir = snapshot_download(
            repo_id=model_name,
            local_dir="./models/llama3.2-3b",
            token=os.getenv("HUGGING_FACE_HUB_TOKEN")
        )
        print(f"Model downloaded successfully to {local_dir}")
        
    except Exception as e:
        print(f"Error downloading model: {str(e)}")

if __name__ == "__main__":
    download_model()
