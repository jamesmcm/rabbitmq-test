CREATE TABLE crowdsourcer (
  id INTEGER PRIMARY KEY,
  name VARCHAR(256)
);
LOAD DATA INFILE '/var/lib/mysql-files/crowdsourcer.csv' INTO TABLE crowdsourcer FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n';
CREATE TABLE severity (
  id INTEGER PRIMARY KEY,
  severity VARCHAR(16),
  karma INTEGER
);
LOAD DATA INFILE '/var/lib/mysql-files/severity.csv' INTO TABLE severity FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n';
CREATE TABLE vulnerability (
  id INTEGER PRIMARY KEY,
  cs_id INTEGER,
  sev_id INTEGER,
  FOREIGN KEY (cs_id) REFERENCES crowdsourcer (id),
  FOREIGN KEY (sev_id) REFERENCES severity (id)
);
LOAD DATA INFILE '/var/lib/mysql-files/vulnerability.csv' INTO TABLE vulnerability FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n';
CREATE TABLE crowdsourcer_karma_distribution (
  cs_id INTEGER PRIMARY KEY,
  cs_name VARCHAR(256),
  minor_sum BIGINT,
  medium_sum BIGINT,
  high_sum BIGINT,
  critical_sum BIGINT,
  FOREIGN KEY (cs_id) REFERENCES crowdsourcer (id)
);
INSERT INTO crowdsourcer_karma_distribution (
  SELECT
    c.id AS cs_id,
    c.name AS cs_name,
    0 AS minor_sum,
    0 AS medium_sum,
    0 AS high_sum,
    0 AS critical_sum
  FROM
    crowdsourcer c
);
