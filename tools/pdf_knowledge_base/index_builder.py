def build_figure_index(figures: list[dict]) -> dict:
    by_category: dict[str, list[str]] = {}
    by_importance: dict[str, list[str]] = {}
    by_tag: dict[str, list[str]] = {}
    for fig in figures:
        fig_id = fig["id"]
        by_category.setdefault(fig.get("category", "unknown"), []).append(fig_id)
        by_importance.setdefault(fig.get("importance", "medium"), []).append(fig_id)
        for tag in fig.get("tags", []):
            by_tag.setdefault(tag, []).append(fig_id)
    return {
        "figures": figures,
        "index": {"by_category": by_category, "by_importance": by_importance, "by_tag": by_tag},
        "filter_presets": {
            "key_figures": {"importance": ["high"]},
            "all_results": {"category": ["result", "experiment"]},
            "overview_only": {"category": ["overview"]},
        },
    }

def filter_figures(index: dict, category: list[str] | None = None, importance: list[str] | None = None, tags: list[str] | None = None) -> list[str]:
    all_ids = {fig["id"] for fig in index["figures"]}
    result = all_ids
    if category:
        cat_ids = set()
        for cat in category:
            cat_ids.update(index["index"]["by_category"].get(cat, []))
        result &= cat_ids
    if importance:
        imp_ids = set()
        for imp in importance:
            imp_ids.update(index["index"]["by_importance"].get(imp, []))
        result &= imp_ids
    if tags:
        tag_ids = set()
        for tag in tags:
            tag_ids.update(index["index"]["by_tag"].get(tag, []))
        result &= tag_ids
    return [fig["id"] for fig in index["figures"] if fig["id"] in result]
