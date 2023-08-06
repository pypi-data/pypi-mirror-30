from typing import Tuple, List

from .intent_precision_score_with_threshold import intent_precision_score_with_threshold
from .intent_recall_score_with_threshold import intent_recall_score_with_threshold


def intent_precision_recall(
        intent_predictions: List[float],
        y_trues: List[float],
        thresholds: List[float],
        sample_weight: List[float],
    ) -> Tuple[List[float], List[float]]:
    """Calculate Intent and

    Args:
        intent_predictions (list of list of dicts):
            A list of intent_prediction which can contains all possible
            intent sorted by score.
        y_trues (list of strings): A list of ground truth (correct) intents.
        thresholds (list of float):
            A threshold which limits the efficacy of top1
            predicted intent if its score is less than threshold.
        sample_weight (list of float):
            Sample weights.

    Returns:
        recall:
            The fraction of correctly classified samples, if
            ``normalize == True``. Otherwise, the number of correctly
            classified sample.
        precision:


    Examples:
        >>> from ynlu.sdk.evaluation import intent_precision_recall
        >>> intent_precision_recall(
                intent_predictions=[
                    [{"intent": "a", "score": 0.7}],
                    [{"intent": "b", "score": 0.3}],
                ],
                y_trues=["a", "b"],
            )
        >>> 0.5
    """
