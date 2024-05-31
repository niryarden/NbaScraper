import random
import zipfile


def split_supervised():
    all_samples = []
    for year in range(2019, 2024):
        with open(f"data/dataset/{year}/{year}_samples.jsonl", "r") as f:
            all_samples.extend(f.read().splitlines())
    random.shuffle(all_samples)
    n = len(all_samples)
    train = all_samples[:int(0.8 * n)]
    test = all_samples[int(0.8 * n):int(0.9 * n)]
    validation = all_samples[int(0.9 * n):]

    with open(f"data/dataset/to_upload/uncompressed/train.jsonl", "w") as f:
        f.write("\n".join(train))
    with zipfile.ZipFile("data/dataset/to_upload/compressed/train.zip", "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.write("data/dataset/to_upload/uncompressed/train.jsonl")

    with open(f"data/dataset/to_upload/uncompressed/test.jsonl", "w") as f:
        f.write("\n".join(test))
    with zipfile.ZipFile("data/dataset/to_upload/compressed/test.zip", "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.write("data/dataset/to_upload/uncompressed/test.jsonl")

    with open(f"data/dataset/to_upload/uncompressed/validation.jsonl", "w") as f:
        f.write("\n".join(validation))
    with zipfile.ZipFile("data/dataset/to_upload/compressed/validation.zip", "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.write("data/dataset/to_upload/uncompressed/validation.jsonl")


def gather_unsupervised():
    all_samples = []
    for year in range(1996, 2019):
        with open(f"data/dataset/{year}/{year}_samples.jsonl", "r") as f:
            all_samples.extend(f.read().splitlines())
    random.shuffle(all_samples)

    with open(f"data/dataset/to_upload/uncompressed/unsupervised.jsonl", "w") as f:
        f.write("\n".join(all_samples))
    with zipfile.ZipFile("data/dataset/to_upload/compressed/unsupervised.zip", "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.write("data/dataset/to_upload/uncompressed/unsupervised.jsonl")


if __name__ == "__main__":
    split_supervised()
    gather_unsupervised()
