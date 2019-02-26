DROP TABLE IF EXISTS submissions;
CREATE TABLE submissions (
    code_id         BIGINT NOT NULL PRIMARY KEY,
    user_id         VARCHAR(255) NOT NULL,
    problem_id      VARCHAR(255) NOT NULL,
    language        VARCHAR(255) NOT NULL,
    code            TEXT NOT NULL,
    code_length     INT NOT NULL,
    execution_time  INT NOT NULL,
    score           FLOAT NOT NULL,   
    time_stamp      DATETIME NOT NULL
);
