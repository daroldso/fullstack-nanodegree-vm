-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

DROP DATABASE IF EXISTS tournament;
CREATE DATABASE tournament;
\c tournament;

DROP TABLE IF EXISTS matches;
DROP TABLE IF EXISTS players;

CREATE TABLE IF NOT EXISTS players (
    id serial primary key,
    name text
);

CREATE TABLE IF NOT EXISTS matches (
    player1_id int references players(id),
    player2_id int references players(id),
    winner int references players(id)
);

CREATE VIEW total_matches_of_players AS SELECT id, count(matches.player1_id) AS matches FROM players LEFT JOIN matches ON matches.player1_id = players.id OR matches.player2_id = players.id GROUP BY players.id;

CREATE VIEW total_wins_of_players AS SELECT id, count(matches.winner) AS wins FROM players LEFT JOIN matches ON matches.winner = players.id GROUP BY players.id;

CREATE VIEW standing AS SELECT players.id, name, match2.wins, match1.matches from players
LEFT JOIN (SELECT * from total_matches_of_players) as match1
ON players.id = match1.id
LEFT JOIN (SELECT * from total_wins_of_players) as match2
ON players.id = match2.id
ORDER BY wins DESC;
