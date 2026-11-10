import pandas as pd


def clean_comments_pipeline(
    df: pd.DataFrame, max_comments_per_author: int = 2, min_text_len: int = 3
) -> pd.DataFrame:
    df = df.copy()
    url_pattern = r"https?://\S+|t\.me/\S+"
    df["has_url"] = df["text"].str.contains(url_pattern, regex=True, na=False)
    df["is_duplicate"] = df["text"].duplicated()
    df["text_len"] = df["text"].str.len()
    df = df[(df["text_len"] >= min_text_len) & (~df["has_url"]) & (~df["is_duplicate"])]
    if "author" in df.columns:
        is_anon = df["author"].isna() | (df["author"] == "anonymous")
        group_key = df["author"].where(~is_anon, other="anon_" + df.index.astype(str))
        df = (
            df.sort_values("votes", ascending=False)
            .groupby(group_key)
            .head(max_comments_per_author)
        )
    df["text"] = df["text"].str.replace(r"@\S+", "", regex=True).str.strip()
    df = df.reset_index(drop=True)
    return df


if __name__ == "__main__":
    data_path = r"data/raw/youtube_comments_1000.csv"
    df = pd.read_csv(data_path)
    print(f"Number of comments before cleaning: {len(df)}")
    df = clean_comments_pipeline(df)
    print(f"Number of comments after cleaning: {len(df)}")
