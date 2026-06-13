from llm_sdk import Small_LLM_Model  # type: ignore
from src.parse import get_and_check_inputs, load_json
from src.pydantic_model import FunctionDefinition
from src.prompt import get_full_prompt
from src.constrained import pick_from_options, pick_value
import json
import os


def main() -> None:
    """Entry point for the function calling pipeline.

    Loads the model, parses inputs, runs constrained decoding for each prompt,
    and writes the results to the output file.
    """
    prompts: list[str]
    functions: list[FunctionDefinition]
    output_path: str
    prompts, functions, output_path = get_and_check_inputs()
    model: Small_LLM_Model = Small_LLM_Model()

    vocab: dict[str, int] = load_json(model.get_path_to_vocab_file())
    all_token_ids: set[int] = set(vocab.values())
    number_tokens: set[int] = set()

    for k, v in vocab.items():
        if k.strip() in "0123456789.-":
            number_tokens.add(v)

    encoded_functions: dict[str, list[int]] = {}
    for func in functions:
        encoded = model.encode(func.name).flatten().tolist()
        encoded_functions[func.name] = encoded

    results: list[dict[str, object]] = []
    for prompt in prompts:
        msg: str = "Selected function: "
        prompt_ids: list[int] = model.encode(
            get_full_prompt(functions, prompt, msg)).flatten().tolist()
        fn_name: str = pick_from_options(model, prompt_ids, encoded_functions)
        if fn_name == "add function definition (ಠ_ಠ)":
            break
        for f in functions:
            if f.name == fn_name:
                func = f
                break
        value: dict[str, float | int | str | bool] = {}
        for param in func.parameters:
            if fn_name == "add function definition (ಠ_ಠ)":
                value[param] = "!?"
                continue
            msg = f"Selected function: {fn_name}\n"
            for k, val in value.items():
                msg += f"Value of parameter '{k}': {val}\n"
            p_type: str = func.parameters[param]
            if p_type == "string":
                msg += f"Value of parameter '{param}' ({p_type}): \""
            else:
                msg += f"Value of parameter '{param}' ({p_type}), "
                msg += "extract exactly as it appears including sign: "
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
    with open(output_path, "w") as file:
        json.dump(results, file, indent=2)


if __name__ == "__main__":
    main()
