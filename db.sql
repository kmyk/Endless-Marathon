DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id              BIGINT NOT NULL PRIMARY KEY,
    name            VARCHAR(255) NOT NULL,
    secret_value    VARCHAR(255) NOT NULL,
    created_at      DATETIME NOT NULL
);

DROP TABLE IF EXISTS problems;
CREATE TABLE problems (
    id              BIGINT NOT NULL PRIMARY KEY,
    name            VARCHAR(255) NOT NULL,
    statement       TEXT NOT NULL,
    created_at      DATETIME NOT NULL
);

DROP TABLE IF EXISTS testcases;
CREATE TABLE testcases (
    id              BIGINT NOT NULL PRIMARY KEY,
    problem_id      BIGINT NOT NULL PRIMARY KEY,
    name            VARCHAR(255) NOT NULL,
    input           TEXT NOT NULL,
    created_at      DATETIME NOT NULL,
    FOREIGN KEY (problem_id) REFERENCES problems(id)
);

DROP TABLE IF EXISTS languages;
CREATE TABLE languages (
    id              BIGINT NOT NULL PRIMARY KEY,
    name            VARCHAR(255) NOT NULL,
    how_to_compile  TEXT NOT NULL,
    how_to_execute  TEXT NOT NULL,
    created_at      DATETIME NOT NULL
);

DROP TABLE IF EXISTS submissions;
CREATE TABLE submissions (
    id              BIGINT NOT NULL PRIMARY KEY,
    user_id         BIGINT NOT NULL,
    problem_id      BIGINT NOT NULL,
    language_id     BIGINT NOT NULL,
    code            TEXT NOT NULL,
    created_at      DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (problem_id) REFERENCES problems(id),
    FOREIGN KEY (language_id) REFERENCES languages(id)
);

DROP TABLE IF EXISTS submission_results;
CREATE TABLE submission_results (
    id              BIGINT NOT NULL PRIMARY KEY,
    submission_id   BIGINT NOT NULL,
    testcase_id     BIGINT NOT NULL,
    execution_time  INT NOT NULL,
    score           FLOAT NOT NULL,
    created_at      DATETIME NOT NULL,
    FOREIGN KEY (submission_id) REFERENCES submissions(id),
    FOREIGN KEY (testcase_id) REFERENCES testcases(id)
);
