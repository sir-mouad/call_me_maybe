def get_valid_next_tokens(generated, encoded_options):
    next_tokens = set()
    n = len(generated)
    for token_ids in encoded_options.values():
        if token_ids[:n] == generated:
            next_tokens.add(token_ids[n])
    return next_tokens


def mask_and_pick(logits, next_tokens):
    for i, v in enumerate(logits):
        if i not in next_tokens:
            logits[i] = float("-inf")

    return (logits.index(max(logits)))


def pick_from_options(model, prompt_ids, encoded_options):
    generated = []
    while True:
        logits = model.get_logits_from_input_ids(prompt_ids + generated)
        next_tokens = get_valid_next_tokens(generated, encoded_options)
        next_token = mask_and_pick(logits, next_tokens)
        generated.append(next_token)
        for name, token_ids in encoded_options.items():
            if token_ids == generated:
                return name


def pick_number(model, prompt_ids, number_tokens):
    generated = []
    while True:
        logits = model.get_logits_from_input_ids(prompt_ids + generated)
        next_token = mask_and_pick(logits, number_tokens)
        generated.append(next_token)
        if len(generated) > 20:
            return model.decode(generated)
        try:
            float(model.decode(generated))
        except ValueError:
            generated.pop()
            return model.decode(generated)
        

def pick_string(model, prompt_ids, all_token_ids):
    generated = []
    while True:
        logits = model.get_logits_from_input_ids(prompt_ids + generated)
        next_token = mask_and_pick(logits, all_token_ids)
        generated.append(next_token)
        current = model.decode(generated)
        if current.endswith('"'):
            return current.split('\n')[0].strip().rstrip('"')
        if len(generated) > 50:  # safe
            return current.strip('"')

def pick_value(model, prompt_ids, param_type, number_tokens, all_token_ids):
    if param_type == "number":
        return round(float(pick_number(model, prompt_ids, number_tokens)), 6)
    elif param_type == "integer":
        return int(float(pick_number(model, prompt_ids, number_tokens)))
    elif param_type == "string":
        return (pick_string(model, prompt_ids, all_token_ids))
    elif param_type == "boolean":
        encoded_bools = {
            "true":  model.encode("true").flatten().tolist(),
            "false": model.encode("false").flatten().tolist()}
        result = pick_from_options(model, prompt_ids, encoded_bools)
        return result == "true"
    else:
        raise ValueError(f"unsupported type: {param_type}")
