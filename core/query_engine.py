"""Template -> query generation engine (PRD §5.2, §5.4.2).

Placeholders use the ``{column_name}`` syntax and are case-sensitive. Each
generated query is the Cartesian product of (coin row x selected template).
"""
from __future__ import annotations

import re
from typing import Any

import pandas as pd

PLACEHOLDER_RE = re.compile(r"\{([^{}]+)\}")


def extract_placeholders(template_text: str) -> list[str]:
    """Return the ordered, unique placeholder names used in a template."""
    seen: list[str] = []
    for name in PLACEHOLDER_RE.findall(template_text):
        if name not in seen:
            seen.append(name)
    return seen


def read_coin_list(file_like) -> pd.DataFrame:
    """Read the uploaded coin XLSX (first sheet) as strings."""
    df = pd.read_excel(file_like, sheet_name=0, dtype=str)
    df = df.fillna("")
    df.columns = [str(c).strip() for c in df.columns]
    return df


def generate_queries(
    coins: pd.DataFrame,
    templates: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[str]]:
    """Resolve templates against every coin row.

    Returns ``(queries, warnings)``. A combination is skipped (with a warning)
    when the template references a placeholder absent from the coin columns
    (PRD §8: "Template placeholder not in coin list -> skip + log warning").
    """
    queries: list[dict[str, Any]] = []
    warnings: list[str] = []
    columns = set(coins.columns)

    for tpl in templates:
        text = tpl["text"]
        placeholders = extract_placeholders(text)
        missing = [p for p in placeholders if p not in columns]
        if missing:
            warnings.append(
                f"Template '{text}' skipped — missing column(s): "
                + ", ".join("{" + m + "}" for m in missing)
            )
            continue

        for _, coin in coins.iterrows():
            query = text
            for col in coins.columns:
                query = query.replace("{" + col + "}", str(coin[col]))
            queries.append(
                {
                    "query": query.strip(),
                    "template": text,
                    "fa_name": coin.get("fa_name", ""),
                    "en_name": coin.get("en_name", ""),
                    "symbol": coin.get("symbol", ""),
                }
            )

    return queries, warnings
