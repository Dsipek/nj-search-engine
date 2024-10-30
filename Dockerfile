FROM python:3.10

WORKDIR /app

COPY app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

RUN pip install --no-cache-dir fastapi uvicorn

RUN python ranking.py

EXPOSE 8000

# Define environment variable
ENV PORT 8000

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]