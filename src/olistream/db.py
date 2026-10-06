import psycopg2
from olistream.config import PG, RW


def _connect(cfg):
    conn = psycopg2.connect(**cfg)
    conn.autocommit = True
    return conn


def pg_conn():
    return _connect(PG)


def rw_conn():
    return _connect(RW)