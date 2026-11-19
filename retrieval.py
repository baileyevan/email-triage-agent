from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def _text(e: dict) -> str:
    return f"{e['from']} {e['subject']} {e['body'][:1500]}"


class ExamplePool:
    """Labeled emails we can look up by similarity. Each item needs: id, from, subject, body, label."""

    def __init__(self, labeled: list[dict]):
        self.items = labeled
        self.vec = TfidfVectorizer(sublinear_tf=True, stop_words="english", max_features=20000)
        self.matrix = self.vec.fit_transform([_text(e) for e in labeled])

    def similar(self, email: dict, k: int = 5, exclude_id: str | None = None) -> list[dict]:
        sims = cosine_similarity(self.vec.transform([_text(email)]), self.matrix)[0]
        out = []
        for i in sims.argsort()[::-1]:
            if self.items[i]["id"] == exclude_id:
                continue  # leave-one-out: an email must never retrieve itself
            out.append(self.items[i])
            if len(out) == k:
                break
        return out