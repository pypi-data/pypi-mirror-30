--  playlists
CREATE TABLE IF NOT EXISTS `playlists` (`id` INTEGER UNSIGNED PRIMARY KEY AUTO_INCREMENT, `priority` DOUBLE NOT NULL, `name` VARCHAR(255), `repeat` INTEGER UNSIGNED NULL, `delay` INTEGER UNSIGNED NULL, `track_delay` INTEGER UNSIGNED NULL, `hours` VARCHAR(255) NULL, `days` VARCHAR(255) NULL, last_played INTEGER UNSIGNED, `labels` VARCHAR(1024) NULL, `weight` VARCHAR(1024) NULL);
CREATE INDEX `IDX_playlists_last_played` ON `playlists` (`last_played`);
CREATE INDEX `IDX_playlists_priority` ON `playlists` (`priority`);

--  tracks
CREATE TABLE IF NOT EXISTS `tracks` (`id` INTEGER UNSIGNED PRIMARY KEY AUTO_INCREMENT, `owner` VARCHAR(255), `filename` VARCHAR(1024), `artist` VARCHAR(255), `title` VARCHAR(255), `length` INTEGER UNSIGNED, `weight` NUMERIC(10,4), `real_weight` NUMERIC(10,4), `count` INTEGER UNSIGNED, `last_played` INTEGER UNSIGNED, `image` VARCHAR(1024), `download` VARCHAR(1024));
CREATE INDEX IDX_tracks_last ON tracks (last_played);
CREATE INDEX IDX_tracks_count ON tracks (count);
CREATE INDEX IDX_tracks_weight ON tracks (weight);
CREATE INDEX IDX_tracks_real_weight ON tracks (real_weight);

-- queue
CREATE TABLE IF NOT EXISTS queue (id INTEGER UNSIGNED PRIMARY KEY AUTO_INCREMENT, track_id INTEGER UNSIGNED, owner VARCHAR(255));

--  urgent (manual) playlist
CREATE TABLE IF NOT EXISTS urgent_playlists (labels VARCHAR(1024), expires INTEGER UNSIGNED);
CREATE INDEX IDX_urgent_playlists_expires ON urgent_playlists (expires);

--  labels
CREATE TABLE IF NOT EXISTS labels (track_id INTEGER UNSIGNED NOT NULL, email VARCHAR(255) NOT NULL, label VARCHAR(255) NOT NULL);
CREATE INDEX IDX_labels_track_id ON labels (track_id);
CREATE INDEX IDX_labels_email ON labels (email);
CREATE INDEX IDX_labels_label ON labels (label);

--  voting
CREATE TABLE IF NOT EXISTS votes (track_id INTEGER UNSIGNED NOT NULL, email VARCHAR(255) NOT NULL, vote INTEGER, weight NUMERIC(10,4), ts INTEGER UNSIGNED);
CREATE INDEX IDX_votes_track_id ON votes (track_id);
CREATE INDEX IDX_votes_email ON votes (email);
CREATE INDEX IDX_votes_ts ON votes (ts);

--  karma
CREATE TABLE IF NOT EXISTS karma (email VARCHAR(255), weight NUMERIC(10,4));
CREATE INDEX IDX_karma_email ON karma (email);

--  play log
CREATE TABLE IF NOT EXISTS playlog (ts INTEGER UNSIGNED NOT NULL, track_id INTEGER UNSIGNED NOT NULL, listeners INTEGER UNSIGNED NOT NULL, lastfm TINYINT UNSIGNED NOT NULL DEFAULT 0, librefm TINYINT UNSIGNED NOT NULL DEFAULT 0);
CREATE INDEX IDX_playlog_ts ON playlog (ts);
CREATE INDEX IDX_playlog_track_id ON playlog (track_id);

-- background tasks
CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTO_INCREMENT, run_after INTEGER UNSIGNED NOT NULL, task VARCHAR(1024));
CREATE INDEX IDX_tasks_run_after ON tasks (run_after);
CREATE INDEX IDX_tasks_task ON tasks (task);
