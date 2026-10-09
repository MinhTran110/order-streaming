CREATE TABLE IF NOT EXISTS predictions (
  order_id   VARCHAR(32) PRIMARY KEY,
  score      DOUBLE PRECISION,
  flagged    BOOLEAN,
  scored_at  TIMESTAMP DEFAULT NOW()
);

