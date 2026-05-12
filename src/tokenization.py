from llm_sdk import Small_LLM_Model
import json
from src.parse import load_json


def get_full_prompt(functions, prompt, msg=""):
    # model = Small_LLM_Model()
    full_prompt = ("You are a function-calling assistant.\n"
                   "Your job is to select the correct function and extract"
                   " the correct arguments from the user request.\n"
                   "Available functions:\n")
    for func in functions:
        param = ", ".join(f"{k} ({v})" for k, v in func.parameters.items())
        full_prompt += (f"- {func.name}: {func.description}. | params: "f"{param}\n")
    full_prompt += f"User request: {prompt}\n{msg}"
    return (full_prompt)


def tokenize(model, text):
    return model.encode(text).flatten().tolist()

def load_vocab(model):
    return load_json(model.get_path_to_vocabulary_json())


# You are a function-calling assistant.
# Your job is to select the correct function and extract the correct arguments from the user request.

# Available functions:
# - fn_add_numbers: Add two numbers together and return their sum. | params: a (number), b (number)
# - fn_greet: Generate a greeting message for a person by name. | params: name (string)
# - fn_reverse_string: Reverse a string and return the reversed result. | params: s (string)

# User request: What is the sum of 2 and 3?

# Selected function:
# ----------------------------------------------------------------------------------
# You are a function-calling assistant.
# Your job is to select the correct function and extract the correct arguments from the user request.

# Available functions:
# - fn_add_numbers: Add two numbers together and return their sum. | params: a (number), b (number)
# - fn_greet: Generate a greeting message for a person by name. | params: name (string)
# - fn_reverse_string: Reverse a string and return the reversed result. | params: s (string)

# User request: What is the sum of 2 and 3?
# Selected function: fn_add_numbers

# Value of parameter 'a' (number)
