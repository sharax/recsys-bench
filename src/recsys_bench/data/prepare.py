"""Raw MovieLens -> filtered, densely-indexed, deterministic parquet."""

import argparse

import polars as pl

from recsys_bench.config import DATASETS, POSITIVE_THRESHOLD, PROC, Dataset

SCHEMA = {
    "user_id": pl.Int32,
    "item_id": pl.Int32,
    "rating": pl.Float32,
    "timestamp": pl.Int64,
}


def _read_raw(ds: Dataset) -> pl.DataFrame:
    """Read either format into one schema.

    ml-1m is '::'-delimited with no header; polars has no multi-char
    separator, so we read each line whole (using a separator byte that
    cannot occur in the file) and split it ourselves.
    """
    if ds.separator == "::":
        raw = pl.read_csv(
            ds.ratings_path,
            has_header=False,
            separator="\x01",
            new_columns=["line"],
            quote_char=None,
        )
        return (
            raw.with_columns(pl.col("line").str.split_exact("::", 3).alias("f"))
            .unnest("f")
            .rename({f"field_{i}": c for i, c in enumerate(SCHEMA)})
            .cast(SCHEMA)
        )

    raw = pl.read_csv(ds.ratings_path)
    return raw.rename(dict(zip(raw.columns, SCHEMA, strict=True))).cast(SCHEMA)


def densify(df: pl.DataFrame, col: str) -> tuple[pl.DataFrame, pl.DataFrame]:
    """Remap `col` to a contiguous 0..n-1 range. Returns (df, mapping)."""
    mapping = (
        df.select(pl.col(col).unique().sort())
        .with_row_index(name=f"{col}_dense")
        .cast({f"{col}_dense": pl.Int32})
    )
    out = df.join(mapping, on=col, how="inner").drop(col).rename({f"{col}_dense": col})
    return out, mapping


def validate(df: pl.DataFrame) -> None:
    """Assert the shape of the data before anything downstream trusts it."""
    assert df.height > 0, "no rows survived preparation"
    assert df.null_count().sum_horizontal().item() == 0, "nulls in prepared data"
    for col, dtype in [("user_id", pl.Int32), ("item_id", pl.Int32)]:
        assert df.schema[col] == dtype, f"{col} has dtype {df.schema[col]}"
        assert df[col].min() == 0, f"{col} is not 0-indexed"
        assert df[col].max() == df[col].n_unique() - 1, f"{col} is not dense"


def prepare(ds: Dataset) -> pl.DataFrame:
    raw = _read_raw(ds)
    assert raw.height == ds.expected_raw_rows, (
        f"{ds.name}: expected {ds.expected_raw_rows:,} raw rows, "
        f"got {raw.height:,} -- the source file changed"
    )

    df = raw.filter(pl.col("rating") >= POSITIVE_THRESHOLD).drop("rating")
    kept = df.height / raw.height

    df, user_map = densify(df, "user_id")
    df, item_map = densify(df, "item_id")

    # Deterministic row order: joins above are not order-preserving, and a
    # byte-stable parquet means a checksum of it is meaningful.
    df = df.sort(["user_id", "timestamp", "item_id"])

    validate(df)

    PROC.mkdir(parents=True, exist_ok=True)
    df.write_parquet(PROC / f"{ds.name}-interactions.parquet")
    user_map.write_parquet(PROC / f"{ds.name}-user-map.parquet")
    item_map.write_parquet(PROC / f"{ds.name}-item-map.parquet")

    print(
        f"{ds.name}: {raw.height:,} raw -> {df.height:,} positives ({kept:.1%} kept) | "
        f"users {raw['user_id'].n_unique():,} -> {df['user_id'].n_unique():,} | "
        f"items {raw['item_id'].n_unique():,} -> {df['item_id'].n_unique():,}"
    )
    return df


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", default="all", choices=[*DATASETS, "all"])
    args = p.parse_args()
    targets = DATASETS.values() if args.dataset == "all" else [DATASETS[args.dataset]]
    for ds in targets:
        prepare(ds)


if __name__ == "__main__":
    main()
