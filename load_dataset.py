from datasets import load_dataset


def main():
    dataset = load_dataset("nir-yar/nba-pbp-to-recap")
    print(dataset)


if __name__ == "__main__":
    main()
