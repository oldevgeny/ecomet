"""ClickHouse queries for Task 4."""


def get_phrase_views_by_hour_query(campaign_id: int) -> str:
    """
    Build query for phrase views by hour.

    Args:
        campaign_id: Campaign ID (validated as integer)

    Returns:
        SQL query with campaign_id interpolated

    Note:
        aiochclient only supports parameter binding for INSERT queries.
        For SELECT queries, we use safe string formatting with integer validation.
    """
    if not isinstance(campaign_id, int):
        msg = f"campaign_id must be an integer, got {type(campaign_id)}"
        raise TypeError(msg)

    return f"""
WITH hourly_views AS (
    SELECT
        phrase,
        toHour(dt) as hour,
        argMax(views, dt) as max_views
    FROM phrases_views
    WHERE campaign_id = {campaign_id}
      AND toDate(dt) = today()
    GROUP BY phrase, hour
),
views_deltas AS (
    SELECT
        phrase,
        hour,
        max_views - lagInFrame(max_views, 1, 0) OVER (
            PARTITION BY phrase ORDER BY hour
        ) as delta
    FROM hourly_views
)
SELECT
    phrase,
    arrayReverse(groupArray((hour, delta))) as views_by_hour
FROM views_deltas
WHERE delta > 0
GROUP BY phrase
ORDER BY phrase
"""  # noqa: S608 - campaign_id is validated as integer, safe from SQL injection
