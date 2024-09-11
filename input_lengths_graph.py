import json
from datasets import load_dataset
from transformers import AutoTokenizer
from tqdm import tqdm
import matplotlib.pyplot as plt


def split_into_buckets(lengths):
    bucket_size = 100
    maximum = (int(max(lengths) / bucket_size)) * bucket_size
    bucket_dict = {}
    for i in range(bucket_size, maximum + 2 * bucket_size, bucket_size):
        bucket_dict[i] = 0

    for num in lengths:
        bucket = (int(num / bucket_size) + 1) * bucket_size
        bucket_dict[bucket] += 1

    return bucket_dict


def collect_data():
    dataset = load_dataset("nir-yar/nba-pbp-to-recap", cache_dir="cache")
    tokenizer = AutoTokenizer.from_pretrained(
        "meta-llama/Meta-Llama-3.1-8B-Instruct",
        trust_remote_code=True,
        cache_dir="cache"
    )
    all_samples = [*dataset["train"], *dataset["test"], *dataset["validation"]]
    tokens = []
    for sample in tqdm(all_samples):
        embedded = tokenizer(sample["input"], return_tensors="pt", return_attention_mask=False)
        tokens.append(embedded["input_ids"].size(1))

    print(f"Average: {sum(tokens) / len(tokens)}")
    with open("graphs/lengths.json", "w") as f:
        f.write(json.dumps(tokens))


def graph():
    with open("graphs/lengths.json", 'r') as f:
        lengths = json.loads(f.read())

    bucket_dict = split_into_buckets(lengths)
    x = list(bucket_dict.keys())
    y = list(bucket_dict.values())

    plt.bar(x[140:230], y[140:230], width=80)
    plt.xlabel('Play-by-play length (Tokens)')
    plt.ylabel('Samples')
    plt.title('Play-by-play length distribution')
    plt.xticks(rotation=45, ha='right', fontsize=8)
    plt.tight_layout()
    plt.savefig('graphs/input_length.png')


if __name__ == "__main__":
    # collect_data()
    graph()
