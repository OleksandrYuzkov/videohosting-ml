import re
import zlib
from collections import Counter

from qdrant_client.http import models


def compute_sparse_vector(text: str) -> models.SparseVector:
    words = re.findall(r"\w{2,}", text.lower())

    tokens = []
    for word in words:
        tokens.append(word)
        if len(word) >= 5:
            ngrams = [word[i : i + 4] for i in range(len(word) - 3)]
            tokens.extend(ngrams)

    counts = Counter(tokens)

    indices = []
    values = []
    for token, count in counts.items():
        token_id = zlib.crc32(token.encode("utf-8"))
        indices.append(token_id)
        values.append(float(count))

    return models.SparseVector(indices=indices, values=values)
