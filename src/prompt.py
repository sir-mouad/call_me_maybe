from src.parse import FunctionDefinition


def get_full_prompt(
    functions: list[FunctionDefinition],
    prompt: str,
    msg: str = ""
) -> str:
    """Build the full prompt string to send to the LLM.

    Args:
        functions: List of available function definitions.
        prompt: The user's natural language request.
        msg: Optional continuation text appended at the end.

    Returns:
        The full prompt string.
    """
    full_prompt: str = (
        "You are a function-calling assistant.\n"
        "Your job is to select the correct function and extract"
        " the correct arguments from the user request.\n"
        "Extract values EXACTLY as they appear in the request,"
        " including negative signs, order, and case.\n"
        "Do not reorder, paraphrase, or interpret the values.\n"
        "Available functions:\n"
    )
    for func in functions:
        param: str = ", ".join(
            f"{k} ({v})" for k, v in func.parameters.items()
        )
        full_prompt += (
            f"- {func.name}: {func.description}. | params: {param}\n"
        )
    full_prompt += f"User request: {prompt}\n{msg}"
    return full_prompt
