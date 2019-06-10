CREATE KEYSPACE rmqtest
WITH replication = {'class': 'SimpleStrategy', 'replication_factor' : 1};

USE rmqtest;

CREATE TABLE crowdsourcer (
  id int PRIMARY KEY,
  name TEXT
);
COPY crowdsourcer (id,name) FROM '/input/crowdsourcer.csv' WITH DELIMITER=',' AND HEADER = FALSE;

CREATE TABLE severity (
  id int PRIMARY KEY,
  severity TEXT,
  karma int
);
COPY severity (id,severity,karma) FROM '/input/severity.csv' WITH DELIMITER=',' AND HEADER = FALSE;

CREATE TABLE vulnerability (
  id int PRIMARY KEY,
  cs_id int,
  sev_id int
);
COPY vulnerability (id,cs_id,sev_id) FROM '/input/vulnerability.csv' WITH DELIMITER=',' AND HEADER = FALSE;


CREATE TABLE crowdsourcer_karma_distribution (
  cs_id int,
  cs_name text,
  minor_sum counter,
  medium_sum counter,
  high_sum counter,
  critical_sum counter,
  PRIMARY KEY((cs_id,cs_name))
);


