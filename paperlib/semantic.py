from __future__ import annotations


def semantic_search(rows: list[dict], query: str, limit: int = 10) -> list[dict]:
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
    except ImportError as exc:
        raise RuntimeError("Install semantic support with: pip install 'paper-library[semantic]'") from exc
    texts = [" ".join([r.get("title", ""), r.get("abstract", ""), r.get("keywords", "")]) for r in rows]
    if not texts:
        return []
    matrix = TfidfVectorizer(stop_words="english").fit_transform(texts + [query])
    scores = cosine_similarity(matrix[-1], matrix[:-1]).ravel()
    ranked = scores.argsort()[::-1][:limit]
    result=[]
    for i in ranked:
        row=dict(rows[i]); row["score"]=float(scores[i]); result.append(row)
    return result
