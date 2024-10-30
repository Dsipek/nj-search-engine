import json
import os
from collections import Counter, defaultdict

import nltk
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

# Dowloading the tokenizer model
nltk.download("punkt_tab")

DATASET_DIR = "./20_newsgroups"

# Initialize stemmer for root word analysis
stemmer = PorterStemmer()


# Load dataset from local directory
def load_documents_from_directory(directory):
    documents = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                documents.append(f.read())
    return documents


def tokenize(text):
    tokens = word_tokenize(text.lower())
    return [stemmer.stem(token) for token in tokens]


def create_inverted_index(docs):
    inverted_index = defaultdict(list)
    term_frequencies = {}

    for doc_id, doc in enumerate(docs):
        tokens = tokenize(doc)
        term_count = Counter(tokens)

        for token, count in term_count.items():
            inverted_index[token].append(doc_id)

        # Store term frequencies per document
        term_frequencies[doc_id] = {
            token: count / len(tokens) for token, count in term_count.items()
        }
    # Save the inverted index and term frequencies for later use
    with open("inverted_index.json", "w") as f:
        json.dump(inverted_index, f)

    with open("term_frequencies.json", "w") as f:
        json.dump(term_frequencies, f)


if __name__ == "__main__":
    # Load documents and create the index
    docs = load_documents_from_directory(DATASET_DIR)
    create_inverted_index(docs)
