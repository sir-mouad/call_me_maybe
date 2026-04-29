import argparse
import json
from pydantic import BaseModel, Field, model_validator, ValidationError
import sys


class request_input(BaseModel):
    prompt: str = Field(min_length=1)
    data: str

    @model_validator(mode='after')
    def check_request(self):
        if self.prompt != "prompt":
            raise ValueError("most the key is prompt")
        return self

class request_diff(BaseModel):
    name: str
    description: str
    parameters: dict[str: str]



def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data

def check_parce_input(data: dict):
    for item in data:
        key = "".join(item.keys())
        try:
            value = item[key]
        except KeyError:
            print("the dict cannot be empty")
            return
        _ = request_input(prompt=key, data=value)
    prompts = []
    for item in data:
        prompts.append(item['prompt'])
    return prompts 

def check_parce_diff(data: dict):
    pass

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--functions_definition")
    parser.add_argument("--input")
    parser.add_argument("--output")
    args = parser.parse_args()
    data_input = load_json(args.input)
    data_diff = load_json(args.functions_definition)
    try:
        prompts = check_parce_input(data_input)
        if prompts is None:
            return
    except Exception as error:
        for e in error.errors():
            print(e['msg'])
            sys.exit(1)
    


if __name__ == "__main__":
    main()
