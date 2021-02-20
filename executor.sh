docker build -t dash .
docker run -p 8050:8050 -v "$(pwd)"/app:/app --rm dash