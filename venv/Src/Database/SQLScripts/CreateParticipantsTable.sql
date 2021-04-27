CREATE TABLE Participants (
    MatchID INT,
    ParticipantID INT,
    Team SMALLINT NOT NULL,
    FrozenElo INT,
    FOREIGN KEY (MatchID) REFERENCES Matches(MatchID),
    FOREIGN KEY (ParticipantID) REFERENCES UserElos(Snowflake),
    PRIMARY KEY(MatchID, ParticipantID)
)