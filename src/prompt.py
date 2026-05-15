def get_full_prompt(functions, prompt, msg=""):
    full_prompt = ("You are a function-calling assistant.\n"
                   "Your job is to select the correct function and extract"
                   " the correct arguments from the user request.\n"
                   "Extract values EXACTLY as they appear in the request,"
                   " including negative signs, order, and case.\n"
                   "Do not reorder, paraphrase, or interpret the values.\n"
                   "Available functions:\n")
    for func in functions:
        param = ", ".join(f"{k} ({v})" for k, v in func.parameters.items())
        full_prompt += (f"- {func.name}: {func.description}. "
                        "| params: "f"{param}\n")
    full_prompt += f"User request: {prompt}\n{msg}"
    return (full_prompt)
