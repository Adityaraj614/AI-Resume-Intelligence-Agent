from core.embeddings.embedder import generate_embeddings


texts = [
    "Built NLP system",
    "Created ML pipeline",
    "Built NLP system"
]


embeddings = generate_embeddings(texts)

print("Shape:", embeddings.shape)