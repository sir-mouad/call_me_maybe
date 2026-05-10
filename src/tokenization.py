from llm_sdk import Small_LLM_Model
import json
from .parse import get_and_check_inputs


def prompts_to_tokens_id():
    model = Small_LLM_Model()
    prompts, _ = get_and_check_inputs()
    tokens_id = []
    for p in prompts:
        tokens_id.append(model.encode(p).flatten().tolist())
    return tokens_id
        
# prompt = "What is the square root of 16?"

# model = Small_LLM_Model()
# tokens_id = model.encode(prompt)
# # lest = tokens_id.tolist()
# # print(tokens_id)
# # print(model.decode(tokens_id))
# tokens_id = tokens_id.flatten().tolist()
# logits = model.get_logits_from_input_ids(tokens_id)
# # print(type(logits))
# # print(model.decode(logits))
# # token_id = logits.max().item() 

# # token_id = logits.index()
# # print(token_id)
# # print(model.decode([token_id]))

# # token_id = 151508
# # print(token_id, model.decode([token_id]))
# path = model.get_path_to_vocab_file()
# with open(path, "r") as f:
#     vocab = json.load(f)
# id_to_token = {v: k for k, v in vocab.items()}
# print((id_to_token[1542]))
