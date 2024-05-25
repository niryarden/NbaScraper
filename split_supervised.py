import random


def main():
    all_samples = []
    for year in range(2019, 2024):
        with open(f"data/dataset/{year}/{year}_samples.jsonl", "r") as f:
            all_samples.extend(f.read().splitlines())
    random.shuffle(all_samples)
    n = len(all_samples)
    train = all_samples[:int(0.8 * n)]
    test = all_samples[int(0.8 * n):int(0.9 * n)]
    dev = all_samples[int(0.9 * n):]

    with open(f"data/dataset/supervised/train.jsonl", "w") as f:
        f.write("\n".join(train))
    with open(f"data/dataset/supervised/test.jsonl", "w") as f:
        f.write("\n".join(test))
    with open(f"data/dataset/supervised/dev.jsonl", "w") as f:
        f.write("\n".join(dev))


if __name__ == "__main__":
    main()
