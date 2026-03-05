import pytest
from app.services.emotion_service import EmotionService


@pytest.fixture
def emotion_svc():
    # Use service without corpus (no CSV in test env)
    return EmotionService(cvaw_path="./nonexistent.csv")


def test_emotion_no_trigger_early(emotion_svc):
    """Should not trigger before min_turns."""
    _, _, _, _, turns, trigger = emotion_svc.analyze(
        text="我今天很累很焦慮",
        valence_history=[],
        arousal_history=[],
        conversation_turns=0,
        trigger_min_turns=6,
        arousal_low=4.7,
        arousal_high=5.4,
    )
    assert not trigger
    assert turns == 1


def test_emotion_increments_turns(emotion_svc):
    """Turn counter increments on each call."""
    v_hist, a_hist = [], []
    turns = 0
    for _ in range(5):
        _, _, v_hist, a_hist, turns, _ = emotion_svc.analyze(
            text="測試",
            valence_history=v_hist,
            arousal_history=a_hist,
            conversation_turns=turns,
        )
    assert turns == 5


def test_emotion_window_trim(emotion_svc):
    """Valence history window respects the window size."""
    v_hist = [3.0, 4.0, 5.0, 6.0, 7.0]
    a_hist = [3.0, 4.0, 5.0, 6.0, 7.0]
    _, _, new_v, new_a, _, _ = emotion_svc.analyze(
        text="",
        valence_history=v_hist,
        arousal_history=a_hist,
        conversation_turns=0,
        window=3,
    )
    assert len(new_v) <= 3
    assert len(new_a) <= 3
