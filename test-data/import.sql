COPY site(id, city, country, latitude, longitude, name, note, region, street, timezone, url)
FROM '/sites.csv'
DELIMITER ','
QUOTE '"'
CSV HEADER;

COPY token(site_id, value, expired, created)
FROM '/tokens.csv'
DELIMITER ','
QUOTE '"'
CSV HEADER;

COPY "user"(email, full_name, disabled, password)
FROM '/users.csv'
DELIMITER ','
QUOTE '"'
CSV HEADER;

COPY site_data(site_id, allocated_machines, deployed_machines, ready_machines, error_machines, last_seen)
FROM '/site_data.csv'
DELIMITER ','
QUOTE '"'
CSV HEADER;
