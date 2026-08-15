default: lock install lint rag_prepare rag_chunk rag_embedding rag_vectorstore

setup:
    brew update
    brew install pyenv uv
    brew upgrade pyenv uv

python version:
    if ! pyenv versions --bare | grep -qx "{{version}}"; then \
        pyenv install {{version}}; \
    fi
    pyenv local {{version}}
    pyenv rehash

    uv python pin {{version}}
    uv venv --python {{version}} --clear

lock:
    uv lock --upgrade

install:
    uv sync --frozen --all-extras --no-install-project --all-groups
    . ./.venv/bin/activate

lint:
    uv run auto-typing-final .
    uv run ruff format
    uv run ruff check --fix
    uv run ty check

rag_prepare:
    uv run python -m rag prepare

rag_chunk:
    uv run python -m rag chunk

rag_embedding:
    uv run python -m rag embedding

rag_vectorstore:
    uv run python -m rag vector_store

pipeline:
    uv run python -m rag prepare
    uv run python -m rag chunk
    uv run python -m rag embedding
    uv run python -m rag vector_store

evaluate question:
    uv run python -m evaluation run -q "{{question}}"

evaluate_test:
    uv run python -m evaluation test