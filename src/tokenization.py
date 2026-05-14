from src.parse import load_json

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
