import pytest
from pydantic import ValidationError

from src.api.schemas.comments import AudienceReport, CommentItem, TopicItem


def test_topic_validation():
    # Test that TopicItem validation works correctly.
    topic = TopicItem(
        title="Praise for author",
        sentiment="positive",
        percentage=45.0,
        key_takeaway="Viewers enjoyed the content.",
    )
    assert topic.title == "Praise for author"
    assert topic.sentiment == "positive"
    assert topic.percentage == 45.0


def test_topic_item_invalid_sentiment():
    # Test that invalid sentiment raises a ValidationError.
    with pytest.raises(ValidationError):
        TopicItem(
            title="Criticism of content",
            sentiment="neutral",  # Invalid sentiment
            percentage=30.0,
            key_takeaway="Viewers had mixed feelings.",
        )


def test_audience_report_from_json():
    # Test that AudienceReport can be created from JSON.
    raw_json = """
    {
        "executive_summary": "Overall positive reception.",
        "topics": [
            {
                "title": "Positive feedback",
                "sentiment": "positive",
                "percentage": 80.0,
                "key_takeaway": "Great video!"
            }
        ]
    }
    """
    report = AudienceReport.model_validate_json(raw_json)
    assert report.executive_summary == "Overall positive reception."
    assert len(report.topics) == 1
    assert report.topics[0].sentiment == "positive"


def test_comment_item_default_votes():
    # Verify that if no likes are provided, the default value is 0.
    comment = CommentItem(comment_id=1, text="Test comment")
    assert comment.votes == 0
