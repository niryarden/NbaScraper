import json
from datasets import load_dataset
from transformers import AutoTokenizer
from tqdm import tqdm
import matplotlib.pyplot as plt


def split_into_buckets(lst, maximum):
    bucket_size = 1000
    bucket_dict = {}
    for i in range(bucket_size, maximum + 2 * bucket_size, bucket_size):
        bucket_dict[i] = 0

    for num in lst:
        bucket = (int(num / 1000) + 1) * 1000
        bucket_dict[bucket] += 1

    return bucket_dict


def collect_data():
    dataset = load_dataset("nir-yar/nba-pbp-to-recap", cache_dir="cache")
    tokenizer = AutoTokenizer.from_pretrained(
        "meta-llama/Meta-Llama-3.1-8B-Instruct",
        trust_remote_code=True,
        cache_dir="cache"
    )
    all_samples = [*dataset["train"], *dataset["test"], *dataset["validation"], *dataset["unsupervised"]]
    tokens = []
    for sample in tqdm(all_samples):
        embedded = tokenizer(sample["input"], return_tensors="pt", return_attention_mask=False)
        tokens.append(embedded["input_ids"].size(1))

    print(sum(tokens) / len(tokens))
    maximum = (int(max(tokens) / 1000)) * 1000
    bucket_dict = split_into_buckets(tokens, maximum)
    with open("buckets.json", "w") as f:
        json.dump(bucket_dict, f)


def graph():
    with open("buckets.json", 'r') as f:
        data = json.loads(f.read())
    x = list(data.keys())
    y = list(data.values())

    plt.bar(x[12:], y[12:])
    plt.xlabel('Play-by-play length (Tokens)')
    plt.ylabel('Samples')
    plt.title('Play-by-play length distribution')
    plt.xticks(rotation=45, ha='right', fontsize=8)
    plt.tight_layout()
    # plt.show()
    plt.savefig('buckets.png')


if __name__ == "__main__":
    collect_data()
    graph()
