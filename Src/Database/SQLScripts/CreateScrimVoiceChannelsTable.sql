CREATE TABLE ScrimVoiceChannels (
    ChannelID INT PRIMARY KEY,
    ChannelTeam INT NOT NULL,
    ParentTextChannel INT NOT NULL,
    FOREIGN KEY (ParentTextChannel) REFERENCES ScrimTextChannels(ChannelID) ON DELETE CASCADE ON UPDATE CASCADE
)