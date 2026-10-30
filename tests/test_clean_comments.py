import pandas as pd

from src.pipelines.clean_comments import clean_comments_pipeline


def test_clean_comments_removes_spam_and_duplicates():
    data = {
        "author": ["user1", "user2", "user3", "user4"],
        "text": ["Отличное видео!", "Отличное видео!", "https://spam.com", "ок"],
        "votes": [10, 5, 0, 0],
    }

    df = pd.DataFrame(data)

    result = clean_comments_pipeline(df)

    assert len(result) == 1
    assert result.iloc[0]["author"] == "user1"
