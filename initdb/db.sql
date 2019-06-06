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
    execution_time  INT NOT NULL,
    score           FLOAT NOT NULL,
    created_at      DATETIME NOT NULL,
    FOREIGN KEY (submission_id) REFERENCES submissions(id)
);


-- workaround for https://github.com/kosakkun/Endless-Marathon/issues/14
INSERT INTO problems (
    id,  name, statement, created_at
) VALUES (
   1, 'tsp', 'nyanchu', '2019-01-01 00:00:00'
);
INSERT INTO languages (
    id, name, how_to_compile, how_to_execute, created_at
) VALUES (
    1, 'cpp', 'nyanchu', 'nyanchu', '2019-01-01 00:00:00'
);
