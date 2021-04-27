CREATE TABLE ServerAdministrators (
    ServerID INT,
    UserID INT,
    FOREIGN KEY (ServerID) REFERENCES Servers(Snowflake),
    PRIMARY KEY(ServerID, UserID)
)