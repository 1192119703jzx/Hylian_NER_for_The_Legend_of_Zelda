from typing import Sequence, NamedTuple
from mention import Mention

class ScoringCounts(NamedTuple):
    """Immutable counts for computing precision and recall."""

    true_positives: int
    false_positives: int
    false_negatives: int

def score_mentions(
    reference: Sequence[Mention], predictions: Sequence[Mention]
) -> ScoringCounts:
    true_positive_set = set(reference).intersection(set(predictions))
    false_positive_set = set(predictions) - true_positive_set
    false_negative_set = set(reference) - true_positive_set
    return ScoringCounts(len(true_positive_set), len(false_positive_set), len(false_negative_set))
