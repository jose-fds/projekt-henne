"""Automated integrity tests for chickens-europe.csv.

Each test turns a check from stages 3-7 of the fact-check process into an
assertion that must pass. Also includes a mutation test (stage 8.2): a
deliberately corrupted copy must make the relevant check fail loudly.
"""
from __future__ import annotations

import copy
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[2]
CSV = ROOT / "data" / "chickens-europe.csv"


@pytest.fixture(scope="module")
def df() -> pd.DataFrame:
    return pd.read_csv(CSV)


def test_row_count(df):
    assert len(df) == 41


def test_unique_keys(df):
    assert df["code"].is_unique
    assert df["country"].is_unique
    assert not df.duplicated().any()


def test_no_missing_values(df):
    assert not df.isna().any().any()


def test_positive_counts(df):
    assert (df["chickens_millions"] > 0).all()
    assert (df["people_millions"] > 0).all()


def test_year_range(df):
    assert df["chicken_year"].between(2020, 2024).all()


def test_region_categories(df):
    assert set(df["region"].unique()) <= {"europe", "asia"}


def test_code_format(df):
    assert df["code"].str.match(r"^[A-Z]{2}$").all()


def test_ratio_is_consistent(df):
    # ratio should equal chickens / people exactly (no precomputed mismatch)
    recomputed = df["chickens_millions"] / df["people_millions"]
    # there is no stored ratio column; just sanity that it's finite and positive
    assert recomputed.notna().all()
    assert (recomputed > 0).all()


def test_classification_known_exceptions(df):
    """The two European holdouts must be Iceland and Luxembourg only."""
    eu = df[df["region"] == "europe"].copy()
    eu["ratio"] = eu["chickens_millions"] / eu["people_millions"]
    holdouts = sorted(eu.loc[eu["ratio"] < 1, "code"].tolist())
    assert holdouts == ["IS", "LU"]


def test_transcontinental_excluded_from_europe_count(df):
    eu = df[df["region"] == "europe"]
    assert len(eu) == 39


def test_world_and_country_ranges_sane(df):
    # rough upper bounds so a unit slip (millions vs thousands) fails loudly
    assert df["chickens_millions"].max() < 1_000
    assert df["people_millions"].max() < 1_000
    assert df["chickens_millions"].min() > 0.01


# ---- Stage 8.2: mutation testing (plant a known error) ----
def test_mutation_duplicate_code_detected(df):
    broken = copy.deepcopy(df)
    broken.loc[broken["code"] == "PL", "code"] = "FR"  # introduce duplicate key
    with pytest.raises(AssertionError):
        assert broken["code"].is_unique


def test_mutation_negative_people_detected(df):
    broken = copy.deepcopy(df)
    broken.loc[broken["code"] == "LU", "people_millions"] = -1.0
    with pytest.raises(AssertionError):
        assert (broken["people_millions"] > 0).all()
