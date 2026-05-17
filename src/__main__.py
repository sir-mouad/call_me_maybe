from llm_sdk import Small_LLM_Model  # type: ignore
from src.parse import get_and_check_inputs, FunctionDefinition, load_json
from src.prompt import get_full_prompt
from src.constrained import pick_from_options, pick_value
import json
import os


def main() -> None:
    """Entry point for the function calling pipeline.

    Loads the model, parses inputs, runs constrained decoding for each prompt,
    and writes the results to the output file.
    """
    model: Small_LLM_Model = Small_LLM_Model()
    prompts: list[str]
    functions: list[FunctionDefinition]
    output_path: str
    prompts, functions, output_path = get_and_check_inputs()

    vocab: dict[str, int] = load_json(model.get_path_to_vocab_file())
    all_token_ids: set[int] = set(vocab.values())
    number_tokens: set[int] = {
        v for k, v in vocab.items() if k.strip() in "0123456789.-"
    }
    encoded_functions: dict[str, list[int]] = {
        func.name: model.encode(func.name).flatten().tolist()
        for func in functions
    }

    results: list[dict[str, object]] = []
    for prompt in prompts:
        msg: str = "Selected function: "
        prompt_ids: list[int] = model.encode(
            get_full_prompt(functions, prompt, msg)).flatten().tolist()
        fn_name: str = pick_from_options(model, prompt_ids, encoded_functions)
        func: FunctionDefinition = next(
            f for f in functions if f.name == fn_name)
        value: dict[str, float | int | str | bool] = {}
        for param in func.parameters:
            msg = f"Selected function: {fn_name}\n"
            for k, v in value.items():
                msg += f"Value of parameter '{k}': {v}\n"
            p_type: str = func.parameters[param]
            if p_type == "string":
                msg += f"Value of parameter '{param}' ({p_type}): \""
            else:
                msg += f"Value of parameter '{param}' ({p_type}): "
            prompt_ids = model.encode(
                get_full_prompt(functions, prompt, msg)).flatten().tolist()
            value[param] = pick_value(
                model, prompt_ids, p_type, number_tokens, all_token_ids)
        results.append({
            "prompt": prompt,
            "name": fn_name,
            "parameters": value
        })

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)


if __name__ == "__main__":
    main()
