from src.pipelines.index_comments import make_point_id


def test_point_id_differs_across_videos():
    assert make_point_id("video_a", "c1") != make_point_id("video_b", "c1")


def test_point_id_is_deterministic():
    assert make_point_id("video_a", "c1") == make_point_id("video_a", "c1")


def test_point_id_separator_prevents_ambiguity():
    assert make_point_id("12", "3") != make_point_id("1", "23")
