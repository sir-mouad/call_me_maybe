from typing import Any


def get_valid_next_tokens(
    generated: list[int],
    encoded_options: dict[str, list[int]]
) -> set[int]:
    """Return valid next token ids given what has been generated so far.

    Args:
        generated: List of token ids generated so far.
        encoded_options: Dict mapping option names to their token id sequences.

    Returns:
        Set of valid next token ids.
    """
    next_tokens: set[int] = set()
    n: int = len(generated)
    for token_ids in encoded_options.values():
        if len(token_ids) > n and token_ids[:n] == generated:
            next_tokens.add(token_ids[n])
    return next_tokens


def mask_and_pick(logits: list[float], next_tokens: set[int]) -> int:
    """Mask invalid tokens and return the token id with the highest score.

    Args:
        logits: List of logit scores for every token in the vocabulary.
        next_tokens: Set of valid token ids to keep unmasked.

    Returns:
        Token id with the highest score among valid tokens.
    """
    for i in range(len(logits)):
        if i not in next_tokens:
            logits[i] = float("-inf")
    return logits.index(max(logits))


def pick_from_options(
    model: Any,
    prompt_ids: list[int],
    encoded_options: dict[str, list[int]]
) -> str:
    """Generate token by token and return the first fully matched option name.

    Args:
        model: The LLM model instance.
        prompt_ids: Tokenized prompt as a list of token ids.
        encoded_options: Dict mapping option names to their token id sequences.

    Returns:
        The name of the matched option.
    """
    generated: list[int] = []
    while True:
        logits: list[float] = model.get_logits_from_input_ids(
            prompt_ids + generated)
        next_tokens: set[int] = get_valid_next_tokens(
            generated, encoded_options)
        if not next_tokens:
            break
        next_token: int = mask_and_pick(logits, next_tokens)
        generated.append(next_token)
        for name, token_ids in encoded_options.items():
            if token_ids == generated:
                return name
    return "add function definition (ಠ_ಠ)"


def pick_number(
    model: Any,
    prompt_ids: list[int],
    number_tokens: set[int]
) -> str:
    """Generate a number value token by token using constrained decoding.

    Args:
        model: The LLM model instance.
        prompt_ids: Tokenized prompt as a list of token ids.
        number_tokens: Set of valid digit/dot/minus token ids.

    Returns:
        The generated number as a string.
    """
    generated: list[int] = []
    while True:
        logits: list[float] = model.get_logits_from_input_ids(
            prompt_ids + generated)
        next_token: int = mask_and_pick(logits, number_tokens)
        generated.append(next_token)
        if len(generated) > 20:
            return str(model.decode(generated))
        try:
            float(model.decode(generated))
        except ValueError:
            generated.pop()
            result: str = str(model.decode(generated))
            return result if result else "0"


def pick_string(
    model: Any,
    prompt_ids: list[int],
    all_token_ids: set[int]
) -> str:
    """Generate a string value token by token until a closing quote is found.

    Args:
        model: The LLM model instance.
        prompt_ids: Tokenized prompt as a list of token ids.
        all_token_ids: Set of all valid token ids.

    Returns:
        The generated string value without surrounding quotes.
    """
    generated: list[int] = []
    while True:
        logits: list[float] = model.get_logits_from_input_ids(
            prompt_ids + generated)
        next_token: int = mask_and_pick(logits, all_token_ids)
        generated.append(next_token)
        current: str = str(model.decode(generated))
        if current.endswith('"'):
            return current.rstrip('"').strip()
        if '"' in current:
            return current.split('"')[0].strip()
        if len(generated) > 100:
            return current.strip()


def pick_value(
    model: Any,
    prompt_ids: list[int],
    param_type: str,
    number_tokens: set[int],
    all_token_ids: set[int]
) -> float | int | str | bool:
    """Route to the correct pick function based on parameter type.

    Args:
        model: The LLM model instance.
        prompt_ids: Tokenized prompt as a list of token ids.
        param_type: The type of the parameter
          (number, string, boolean, integer).
        number_tokens: Set of valid digit/dot/minus token ids.
        all_token_ids: Set of all valid token ids.

    Returns:
        The extracted value cast to the correct Python type.

    Raises:
        ValueError: If the parameter type is not supported.
    """
    if param_type == "number" or param_type == "float":
        return round(float(pick_number(model, prompt_ids, number_tokens)), 6)
    elif param_type == "string":
        return pick_string(model, prompt_ids, all_token_ids)
    elif param_type == "integer":
        return int(float(pick_number(model, prompt_ids, number_tokens)))
    elif param_type == "boolean":
        encoded_bools: dict[str, list[int]] = {
            "true": model.encode("true").flatten().tolist(),
            "false": model.encode("false").flatten().tolist()
        }
        result: str = pick_from_options(model, prompt_ids, encoded_bools)
        return result == "true"
    else:
        raise ValueError(f"unsupported type: {param_type}")
