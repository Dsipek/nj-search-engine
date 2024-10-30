import json
import os
from collections import defaultdict
from typing import Any, Dict, List, Optional

import redis
from fastapi import FastAPI, File, HTTPException, UploadFile
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from pydantic import BaseModel

# Initialize FastAPI
app = FastAPI()

# Redis client
redis_client: Optional[redis.Redis] = None
try:
    redis_client = redis.Redis(host="redis", port=6379, db=0)
    # Test the connection
    redis_client.ping()
except (redis.ConnectionError, redis.exceptions.BusyLoadingError):
    redis_client = None
    print("Redis is not available, running without caching.")

# Initialize stemmer
stemmer = PorterStemmer()


def load_json(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)


# Atomic json saving in case the process is interupted half way
def save_json(data, filepath: str):
    tmp_path = f"{filepath}.tmp"
    with open(tmp_path, "w") as f:
        json.dump(data, f)
    os.replace(tmp_path, filepath)


inverted_index: Dict[str, List[int]] = load_json("inverted_index.json")

term_frequencies: Dict[int, Dict[str, int]] = load_json("term_frequencies.json")


# Function to tokenize text
def tokenize(text: str) -> List[str]:
    tokens = word_tokenize(text.lower())
    return [stemmer.stem(token) for token in tokens]


# Function to calculate TF-IDF scores
def calculate_tfidf(query: str) -> List[float]:
    # Check for cached query
    if redis_client:
        cache_key = f"tfidf:{query}"
        cached_result = redis_client.get(cache_key)

        if cached_result:
            return json.loads(cached_result)

    query_tokens = tokenize(query)
    doc_scores: List[float] = [0] * len(term_frequencies)

    for token in query_tokens:
        if token in inverted_index:
            for doc_id in inverted_index[token]:
                tf = term_frequencies[str(doc_id)].get(token, 0)
                idf = 1 / len(inverted_index[token])
                doc_scores[doc_id] += tf * idf

    if redis_client:
        redis_client.set(
            cache_key, json.dumps(doc_scores), ex=3600
        )  # Caching for one hour
    return doc_scores


class SearchRequest(BaseModel):
    query: str


@app.post("/search")
async def search(search_request: SearchRequest) -> Dict[str, Any]:
    query = search_request.query

    # Calculate TF-IDF scores for the query
    scores = calculate_tfidf(query)

    # Rank documents by score
    ranked_docs = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)

    # Return the ranked documents
    return {
        "results": [
            {"document_id": doc_id, "score": score} for doc_id, score in ranked_docs
        ]
    }


@app.post("/add-document")
async def add_document(file: UploadFile = File(...)) -> Dict[str, Any]:
    # Ensure the uploaded file is a .txt file
    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files are allowed.")

    # Read the content of the file
    content = await file.read()
    content = content.decode("utf-8")  # Decode bytes to string

    # Tokenize the new document
    tokens = tokenize(content)
    doc_id = len(
        term_frequencies
    )  # New document ID is the current length of term_frequencies

    # Update the term frequencies
    term_frequencies[doc_id] = defaultdict(int)
    for token in tokens:
        term_frequencies[doc_id][token] += 1
        if token not in inverted_index:
            inverted_index[token] = []
        inverted_index[token].append(doc_id)

    # Save updated inverted index and term frequencies to JSON files
    save_json(inverted_index, "inverted_index.json")
    save_json(term_frequencies, "term_frequencies.json")

    return {"message": "Document added successfully", "document_id": doc_id}
