CREATE TABLE repositories
(
    name     String,
    owner    String,
    stars    Int32,
    watchers Int32,
    forks    Int32,
    language String,
    updated  datetime
) ENGINE = ReplacingMergeTree(updated)
      ORDER BY name;

CREATE TABLE repositories_authors_commits
(
    date        date,
    repo        String,
    author      String,
    commits_num Int32
) ENGINE = ReplacingMergeTree
      ORDER BY (date, repo, author);

CREATE TABLE repositories_positions
(
    date     date,
    repo     String,
    position UInt32
) ENGINE = ReplacingMergeTree
      ORDER BY (date, repo);
