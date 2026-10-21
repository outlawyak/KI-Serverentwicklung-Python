-- Database schema and test data (T0.7).
-- Run: docker exec -i ai-server-db psql -U app -d games -v ON_ERROR_STOP=1 < db/schema.sql
-- The script can be re-run: it drops and recreates all tables (data is lost).

BEGIN;

DROP TABLE IF EXISTS review;
DROP TABLE IF EXISTS game_details;
DROP TABLE IF EXISTS game;

CREATE TABLE game (
    id           integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title        varchar(200) NOT NULL,
    genre        varchar(50)  NOT NULL,
    release_date date,
    -- optimistic locking: incremented on every update
    version      integer      NOT NULL DEFAULT 0
);

-- 1:1 with game (unique FK)
CREATE TABLE game_details (
    id          integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    game_id     integer NOT NULL UNIQUE REFERENCES game (id) ON DELETE CASCADE,
    description text,
    developer   varchar(100),
    publisher   varchar(100)
);

-- 1:N with game
CREATE TABLE review (
    id         integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    game_id    integer     NOT NULL REFERENCES game (id) ON DELETE CASCADE,
    rating     smallint    NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment    text,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX review_game_id_idx ON review (game_id);

-- Test data. Explicit ids are not allowed with GENERATED ALWAYS, so the
-- rows rely on insertion order: games get ids 1-3.
INSERT INTO game (title, genre, release_date) VALUES
    ('The Legend of Zelda: Breath of the Wild', 'Action-Adventure', '2017-03-03'),
    ('Stardew Valley',                          'Simulation',       '2016-02-26'),
    ('Hades',                                   'Roguelike',        '2020-09-17');

INSERT INTO game_details (game_id, description, developer, publisher) VALUES
    (1, 'Open-world adventure in the kingdom of Hyrule.', 'Nintendo EPD',      'Nintendo'),
    (2, 'Farming and life simulation in Pelican Town.',   'ConcernedApe',      'ConcernedApe'),
    (3, 'Escape the underworld in this action roguelike.', 'Supergiant Games', 'Supergiant Games');

INSERT INTO review (game_id, rating, comment) VALUES
    (1, 5, 'A masterpiece of open-world design.'),
    (1, 4, 'Great, but weapon durability is annoying.'),
    (2, 5, 'Relaxing and endlessly charming.'),
    (3, 5, 'Tight combat and a great story.'),
    (3, 3, 'Fun, but gets repetitive after a while.');

COMMIT;
