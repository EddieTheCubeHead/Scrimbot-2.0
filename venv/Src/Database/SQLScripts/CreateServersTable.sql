CREATE TABLE Servers (
    Snowflake INT PRIMARY KEY,
    Prefix VARCHAR(5) DEFAULT "/",
    ScrimTimeout INT DEFAULT 15,
    EnablePings SMALLINT DEFAULT 0,
    ReactionMessage INT
)