CREATE TABLE Aliases (
    GameName VARCHAR(32),
    Alias VARCHAR(32),
    FOREIGN KEY (GameName) REFERENCES Games(Name),
    PRIMARY KEY (GameName, Alias)
)