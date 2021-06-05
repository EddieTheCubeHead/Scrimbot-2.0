CREATE TABLE Participants (
    MatchID INT,
    ParticipantID INT NOT NULL,
    Game VARCHAR(32) NOT NULL,
    Team SMALLINT NOT NULL,
    FrozenElo INT,
    FOREIGN KEY (MatchID) REFERENCES Matches(MatchID),
    FOREIGN KEY (ParticipantID, Game) REFERENCES UserElos(Snowflake, Game),
    PRIMARY KEY(MatchID, ParticipantID)
)