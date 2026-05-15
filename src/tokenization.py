from src.parse import load_json

def load_vocab(model):
    return load_json(model.get_path_to_vocabulary_json())