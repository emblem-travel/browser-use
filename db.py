import os
from contextlib import contextmanager
from typing import Dict

import psycopg


def get_db_credentials() -> Dict[str, str]:
	creds = {
		'user': os.getenv('POSTGRES_USER', ''),
		'password': os.getenv('POSTGRES_PASSWORD', ''),
		'host': os.getenv('POSTGRES_HOST', ''),
		'port': os.getenv('POSTGRES_PORT', ''),
		'dbname': os.getenv('POSTGRES_DB', ''),
	}

	missing = [key for key, value in creds.items() if value is None or value == '']
	if missing:
		raise OSError(f'Missing environment variables: {", ".join(missing)}')

	return creds


@contextmanager
def get_db():
	creds = get_db_credentials()
	conn = psycopg.connect(
		dbname=creds['dbname'],
		user=creds['user'],
		password=creds['password'],
		host=creds['host'],
		port=creds['port'],
		sslmode='disable',
	)
	try:
		yield conn
		conn.commit()  # Automatically commit if no exceptions
	except:
		conn.rollback()  # Rollback on exceptions
		raise
	finally:
		conn.close()
