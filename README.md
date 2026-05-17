*This project has been created as part of the 42 curriculum by mhadir.*

# Call Me Maybe — Introduction to Function Calling in LLMs

## Description

This project implements a **function calling tool** that translates natural language prompts into structured function calls using a small language model (Qwen/Qwen3-0.6B).

Given a prompt like `"What is the sum of 2 and 3?"`, the system does not answer `5`. Instead it returns:

```json
{
  "prompt": "What is the sum of 2 and 3?",
  "name": "fn_add_numbers",
  "parameters": {"a": 2.0, "b": 3.0}
}
```

The core technique is **Greedy Constrained Decoding** — a method that guides the model token-by-token to guarantee 100% valid and structured output, even with a 0.6B parameter model that would otherwise fail 70% of the time.

---

## Instructions

### Installation

```bash
uv sync
```

### Running

```bash
uv run python -m src
```

With custom paths:

```bash
uv run python -m src \
  --functions_definition data/input/functions_definition.json \
  --input data/input/function_calling_tests.json \
  --output data/output/function_calling_results.json
```

### Makefile commands

```bash
make install     # install dependencies
make run         # run the program
make debug       # run with pdb debugger
make clean       # remove caches
make lint        # run flake8 and mypy
make lint-strict # run mypy with --strict
```

---

## Algorithm Explanation

The system uses **Greedy Constrained Decoding**, broken into three phases per prompt:

### Phase 1 — Function Selection

The prompt is built with all available function descriptions. The LLM is asked to complete `"Selected function: "`. At each token step:

1. The model produces logits (scores) for every token in the vocabulary
2. `get_valid_next_tokens` computes which tokens can legally come next based on the known function names
3. All other tokens are masked to `-inf`
4. The highest scoring valid token is picked (greedy)
5. This repeats until a full function name is matched

### Phase 2 — Parameter Extraction

For each parameter, a new prompt is built with the full context including previously extracted values. The LLM is constrained based on the parameter type:

- **number / integer** → only digit, dot, and minus tokens are allowed. Generation stops when `float()` conversion fails.
- **string** → all tokens are allowed. Generation stops at a closing `"`.
- **boolean** → treated like function selection with only `"true"` and `"false"` as options.

### Phase 3 — Assembly

The JSON result is assembled entirely by the code — not by the LLM. This guarantees 100% valid JSON output.

---

## Design Decisions

- **Separate LLM calls per parameter** — simpler than full JSON generation, easier to constrain, more reliable
- **Greedy decoding over sampling** — deterministic and reliable for function calling
- **Pydantic for all validation** — catches bad input early with clear error messages
- **Prompt grows with context** — each parameter prompt includes previously extracted values so the LLM has full context
- **String delimiter** — prompt ends with `"` for string parameters so the LLM knows it is inside a string and will close it

---

## Performance Analysis

Tested on the provided function set with 11 prompts:

```
Score:           10/11 (90.9%)
JSON validity:   100% — every output is parseable
Speed:           under 5 minutes for all prompts on CPU
```

The one failure was a string containing inner quotes (`Say "hello" to {name}`) — the closing quote detection split on the inner quote. This is a known edge case of the string delimiter approach.

---

## Challenges Faced

- **Vocab structure** — the vocabulary JSON maps token strings to ids, not ids to strings. Required flipping the lookup direction.
- **String stop condition** — strings containing `"` inside them cause early stopping. Solved partially with length safety and strip logic.
- **Number precision** — floating point gives `3.000000000000001` instead of `3.0`. Fixed with `round(..., 6)`.
- **Infinite loops** — early versions had no safety on string/number generation. Added max length guards.
- **Type errors** — `model.decode()` returns `Any` which conflicts with mypy strict mode. Fixed with explicit `str()` casts.

---

## Testing Strategy

Tested with:

1. **Basic prompts** — sum, greet, reverse, square root
2. **Edge cases** — zero values, negative numbers, uppercase strings, strings with spaces
3. **Multiple parameters** — regex substitution with 3 string params
4. **Ambiguous prompts** — "Add five and ten", "Flip the string"
5. **Unknown functions** — prompts with no matching function
6. **Invalid input files** — missing files, malformed JSON
7. **Moulinette** — official grader with private test set

---

## Example Usage

```bash
# run with default paths
uv run python -m src

# run with custom paths
uv run python -m src \
  --functions_definition data/input/functions_definition.json \
  --input data/input/function_calling_tests.json \
  --output data/output/function_calling_results.json
```

Example output:

```json
[
  {
    "prompt": "What is the sum of 2 and 3?",
    "name": "fn_add_numbers",
    "parameters": {"a": 2.0, "b": 3.0}
  },
  {
    "prompt": "Greet shrek",
    "name": "fn_greet",
    "parameters": {"name": "shrek"}
  }
]
```

---

## Resources

- [3Blue1Brown — Large Language Models Playlist](https://youtube.com/playlist?list=PLZHQObOWTQDM4E-dwvbnQTiyKDO-y9T2t&si=GVxWlLjXHd6DT10S) — watched to understand how LLMs work internally, covering tokenization, transformers, and attention mechanisms
- [3Blue1Brown — Neural Networks Playlist](https://www.youtube.com/playlist?list=PLZHQObOWTQDNU6R1_67000Dx_ZCJB-3pi) — watched to understand how LLMs and neural networks work internally
- [Constrained Decoding — outlines library concepts](https://github.com/outlines-dev/outlines)
- [Pydantic Documentation](https://docs.pydantic.dev)

### AI Usage

- Ask questions about concepts like constrained decoding, tokenization, and attention mechanisms to better understand the theory before implementing
- Get explanations of error messages and debug hints when stuck, then fixing the code myself
- Review my implementation and point out potential edge cases to test
- Help structure the README after the project was complete

All AI suggestions were reviewed, tested, and understood before being included.