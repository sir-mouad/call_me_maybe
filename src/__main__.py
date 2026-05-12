from llm_sdk import Small_LLM_Model
from src.parse import get_and_check_inputs, FunctionDefinition, load_json
from src.prompt import get_full_prompt
from src.constrained import pick_from_options, pick_value


def main():
    model = Small_LLM_Model()
    prompts, functions, output_path = get_and_check_inputs()
    vocab = load_json(model.get_path_to_vocabulary_json())
    number_tokens = [int(k) for k, v in vocab.items()
        if v.strip() in "0123456789.-"]
    all_token_ids = [int(k) for k in vocab.keys()]
    encoded_functions = {
        func.name: model.encode(func.name).flatten().tolist()
        for func in functions
    }
    results = []
    for prompt in prompts:
        msg = "Selected function: "
        prompt_ids = model.encode(get_full_prompt(prompts, msg)).flatten().tolist()
        

