.PHONY: lint test data split eval all

lint:  ; uv run ruff check . && uv run ruff format --check .
test:  ; uv run pytest
data:  ; uv run python -m recsys_bench.data.prepare
split: ; uv run python -m recsys_bench.data.split
eval:  ; uv run python -m recsys_bench.eval.run
all: data split eval
