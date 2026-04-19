# Dockerfile — generate SUMD.md inside a container
# Build: docker build -t sumd-gen .
# Run:   docker run --rm -v "$PWD:/project" sumd-gen

FROM python:3.12-slim

RUN pip install --no-cache-dir sumd

WORKDIR /project

ENTRYPOINT ["sumd"]
CMD ["scan", ".", "--fix", "--profile", "rich"]
