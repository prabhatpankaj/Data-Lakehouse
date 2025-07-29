DO
$$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_database
      WHERE datname = 'superset'
   ) THEN
      CREATE DATABASE superset;
   END IF;
END
$$;