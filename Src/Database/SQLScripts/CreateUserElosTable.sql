CREATE TABLE UserElos (
    Snowflake INT,
    Game VARCHAR(32) NOT NULL,
    Elo INT NOT NULL,
    FOREIGN KEY (Game) REFERENCES Games(Name),
    PRIMARY KEY (Snowflake, Game)
)