from llm_sdk import Small_LLM_Model
from src.parse import get_and_check_inputs, FunctionDefinition, load_json
from src.prompt import get_full_prompt
from src.constrained import pick_from_options, pick_value
import json
import os


def main():
    model = Small_LLM_Model()
    prompts, functions, output_path = get_and_check_inputs()
    vocab = load_json(model.get_path_to_vocab_file())
    all_token_ids = set(vocab.values())
    number_tokens = {v for k, v in vocab.items() if k.strip() in "0123456789.-"}
    encoded_functions = {
        func.name: model.encode(func.name).flatten().tolist()
        for func in functions
    }
    results = []
    for prompt in prompts:
        msg = "Selected function: "
        prompt_ids = model.encode(get_full_prompt(
            functions, prompt, msg)).flatten().tolist()
        fn_name = pick_from_options(model, prompt_ids, encoded_functions)
        func = next(f for f in functions if f.name == fn_name)
        value = {}
        for param in func.parameters:
            msg = f"Selected function: {fn_name}\n"
            for k, v in value.items():
                msg += f"Value of parameter '{k}': {v}\n"
            p_type = func.parameters[param]
            msg += f"Value of parameter '{param}' ({p_type}): \""
            prompt_ids = model.encode(get_full_prompt(
                functions, prompt, msg)).flatten().tolist()
            value[param] = pick_value(
                model, prompt_ids, p_type, number_tokens, all_token_ids)
        results.append({
            "prompt": prompt,
            "name": fn_name,
            "parameters": value})
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)


if __name__ == "__main__":
    main()
