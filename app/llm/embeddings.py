from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np

# Load model (can be replaced with Mistral / Llama embeddings model)
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME)


def mean_pooling(model_output, attention_mask):
    """
    Perform mean pooling on token embeddings
    """
    token_embeddings = model_output[0]  # First element of output tuple
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)


def get_embedding(text: str) -> list[float]:
    """
    Generate embedding vector for a given text
    """
    encoded_input = tokenizer(text, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        model_output = model(**encoded_input)
    embedding = mean_pooling(model_output, encoded_input["attention_mask"])
    return embedding.squeeze().cpu().numpy().tolist()
