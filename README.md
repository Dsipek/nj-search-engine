# NJ Search Engine

This project is a lightweight, fast, and scalable search engine built with FastAPI, Redis for caching, and NLTK for tokenization and stemming. The app provides an API for uploading documents, calculating TF-IDF scores, and performing search queries with ranked results. It supports three main ways to run: in a Docker Compose setup for horizontal scalability, as a standalone Docker container, and locally.

## Features

- **Upload and Search**: Add text documents and perform efficient search queries.
- **TF-IDF Calculation**: Computes TF-IDF scores for search term relevance.
- **Caching with Redis**: Optional caching layer for fast query responses.
- **Scalable**: Built to scale horizontally with Docker Compose.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- Python 3.8+ (for local development)

## Getting Started

### Project Structure

- **`app/`**: Contains the FastAPI application code.
- **`data/`**: Directory to store document files.
- **`requirements.txt`**: Lists Python dependencies.
- **`Dockerfile`**: Defines the container image.
- **`docker-compose.yml`**: Sets up the app, Redis, and optional scaling in Docker Compose.

---

## Installation and Running Options

### 1. Run with Docker Compose (Recommended)

Docker Compose setup runs the app along with Redis in a networked, horizontally-scalable configuration.

1. **Set up and start services**: 
NOTE: If you do not wish to build the docker image yourself the image could be obtained by:
   ```bash
   docker pull sipedom/nj-search-engine
   ```
Run Docker Compose with the following command:
   ```bash
   docker-compose up --scale app=3 --build
   ```
Here --scale app=3 scales the application to three instances. You can adjust the number for your needs.

1. **Access the app**: 
 - The API will be available at http://localhost:80
 - Redis runs on port 6379 internally within Docker network

### 2. Run as a standalone Docker container
You can run the search engine as a single container with an optional Redis container for caching:

1. **Build the Docker image**:
   ```bash
   docker build -t nj-search-engine .
   ```
Or alternatively pull the existing docker image from the docker hub at `sipedom/nj-search-engine`.

2. **Run with Redis (optional)**:
- **Start Redis**:
    ```bash
    docker run -d --name redis redis
    ```
- **Run the app with Redis**
    ```bash
    docker run -p 8000:8000 --link redis:redis -e REDIS_HOST=redis nj-search-engine
    ```
3. **Run without Redis**:
    ```bash
    docker run -p 8000:8000 nj-search-engine
    ```
4. **Access the app**:
Open `http://localhost:8000` in your browser.

### 3. Run as a standalone Docker container
For development or testing purposes, you may want to run the app directly on your local machine. 

1. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
2. **Start the Redis server (optional)**:
    ```
    redis-server
    ```
    NOTICE: Running the Redis server is not neccessary for the app to operate in this setup

3. **Run the app**:
Make sure you are located in the directory where app.py is located at.
    ```bash
    uvicorn app:app --host 0.0.0.0 --port 8000 
    ```

4. **Access the app**:  
Open `http://localhost:8000` in your browser.

## Usage
The app provides two main API endpoints:

1. **Upload a document**:
    - `POST /add-document`
    - Use this endpoint to upload text files for indexing or search.
    - Supports only **.txt** files.
    - **Sample request**:
        ```bash
        curl -X POST "http://localhost:8000/add-document" -F "file=@yourfile.txt"
        ```
        NOTICE: replace port `:8000` with `:80` if running with docker-compose


2. **Search for a Query**:
    - `POST /search`
    - Sends a search query to get ranked results based on TF-IDF scores.
    - **Sample request**:
        ```bash
        curl -X POST "http://localhost:8000/search" -H "Content-Type: application/json" -d '{"query": "your search term"}'
        ```
        NOTICE: replace port `:8000` with `:80` if running with docker-compose

## Scaling and Performance
Using Docker Compose, you can scale horizontally by adding more app instances, which will help distribute the load. Redis caching further improves performance by storing frequently-used query results.
