import os, textwrap
from .queries import QUERIES

def generate_database(name, db_type='mysql'):
	path = f'skeleton/{name}'
	os.makedirs(path, exist_ok=True)

	query_data = QUERIES.get(db_type.lower(), None)
	if query_data is None:
		raise ValueError(f"Unsupported database type: {db_type}. Supported types are: {', '.join(QUERIES.keys())}")
	with open(os.path.join(path, query_data['file__name']), 'w') as f:
		f.write(textwrap.dedent(query_data['query']))
		if db_type.lower() == 'elasticsearch':
			# Make the script executable
			os.chmod(os.path.join(path, 'init-es.sh'), 0o755)