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
DROP TABLE IF EXISTS tournaments;
DROP TABLE IF EXISTS players_tournaments;

CREATE TABLE IF NOT EXISTS players (
    id serial primary key,
    name text
);

CREATE TABLE IF NOT EXISTS tournaments (
    id serial primary key,
    name text
);

CREATE TABLE IF NOT EXISTS matches (
    player1_id int references players(id),
    player2_id int references players(id),
    winner int references players(id),
    tournaments_id int references tournaments(id)
);

CREATE TABLE IF NOT EXISTS players_tournaments (
    player_id int references players(id),
    tournaments_id int references tournaments(id)
);

CREATE VIEW total_matches_of_players AS SELECT id, players.name, count(matches.player1_id) AS matches FROM players LEFT JOIN matches ON matches.player1_id = players.id OR matches.player2_id = players.id GROUP BY players.id;

CREATE VIEW total_wins_of_players AS SELECT id, players.name, count(matches.winner) AS wins FROM players LEFT JOIN matches ON matches.winner = players.id GROUP BY players.id;

CREATE VIEW bye_round_of_players AS SELECT id, name, count(matches.player1_id) as num FROM players LEFT JOIN (SELECT player1_id FROM matches WHERE player2_id IS NULL) AS matches ON matches.player1_id = players.id GROUP BY players.id;

CREATE VIEW standing AS SELECT players.id, players.name, match2.wins, match1.matches as bye_round from players
LEFT JOIN (SELECT * from total_matches_of_players) as match1
ON players.id = match1.id
LEFT JOIN (SELECT * from total_wins_of_players) as match2
ON players.id = match2.id
ORDER BY wins DESC;
