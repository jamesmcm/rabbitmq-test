UPDATE
  crowdsourcer_karma_distribution,
  (
    SELECT
      v.cs_id,
      s.severity,
      s.karma
    FROM
      vulnerability v
      LEFT JOIN severity s ON v.sev_id = s.id
    WHERE
      v.id = %(vuln_id) s
  ) row
SET
  crowdsourcer_karma_distribution.minor_sum = crowdsourcer_karma_distribution.minor_sum + CASE WHEN row.severity = 'minor' THEN row.karma ELSE 0 end,
  crowdsourcer_karma_distribution.medium_sum = crowdsourcer_karma_distribution.medium_sum + CASE WHEN row.severity = 'medium' THEN row.karma ELSE 0 end,
  crowdsourcer_karma_distribution.high_sum = crowdsourcer_karma_distribution.high_sum + CASE WHEN row.severity = 'high' THEN row.karma ELSE 0 end,
  crowdsourcer_karma_distribution.critical_sum = crowdsourcer_karma_distribution.critical_sum + CASE WHEN row.severity = 'critical' THEN row.karma ELSE 0 end
WHERE
  crowdsourcer_karma_distribution.cs_id = row.cs_id;