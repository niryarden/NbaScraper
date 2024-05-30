from datasets import load_dataset
from transformers import AutoTokenizer


def main():
    dataset = load_dataset("nir-yar/nba-pbp-to-recap")
    tokenizer = AutoTokenizer.from_pretrained("microsoft/phi-2", trust_remote_code=True)
    input_ex = dataset["train"][0]["input"]
    res = tokenizer(input_ex, return_tensors="pt", return_attention_mask=False)
    print(res.data["input_ids"].shape[1])


if __name__ == "__main__":
    main()
