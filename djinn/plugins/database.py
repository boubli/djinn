"""
Database Plugins - Database command generators for all major databases.
"""


class MySQLPlugin:
    """MySQL/MariaDB commands."""
    
    SYSTEM_PROMPT = """You are a MySQL expert. Generate MySQL commands.
Output only the command."""
    
    TEMPLATES = {
        "connect": "mysql -u {user} -p -h {host} {database}",
        "dump": "mysqldump -u {user} -p {database} > {file}.sql",
        "restore": "mysql -u {user} -p {database} < {file}.sql",
        "create_db": "mysql -u {user} -p -e 'CREATE DATABASE {database}'",
        "drop_db": "mysql -u {user} -p -e 'DROP DATABASE {database}'",
        "show_dbs": "mysql -u {user} -p -e 'SHOW DATABASES'",
        "show_tables": "mysql -u {user} -p -e 'SHOW TABLES' {database}",
        "create_user": "mysql -u root -p -e \"CREATE USER '{user}'@'localhost' IDENTIFIED BY '{password}'\"",
        "grant_all": "mysql -u root -p -e \"GRANT ALL PRIVILEGES ON {database}.* TO '{user}'@'localhost'\"",
        "slow_queries": "mysqldumpslow /var/log/mysql/mysql-slow.log",
    }


class PostgresPlugin:
    """PostgreSQL commands."""
    
    SYSTEM_PROMPT = """You are a PostgreSQL expert. Generate psql commands.
Output only the command."""
    
    TEMPLATES = {
        "connect": "psql -U {user} -h {host} -d {database}",
        "dump": "pg_dump -U {user} -h {host} {database} > {file}.sql",
        "dump_data": "pg_dump -U {user} --data-only {database} > {file}.sql",
        "restore": "psql -U {user} -h {host} {database} < {file}.sql",
        "create_db": "createdb -U {user} {database}",
        "drop_db": "dropdb -U {user} {database}",
        "list_dbs": "psql -U {user} -c '\\l'",
        "list_tables": "psql -U {user} -d {database} -c '\\dt'",
        "vacuum": "psql -U {user} -d {database} -c 'VACUUM ANALYZE'",
        "reindex": "psql -U {user} -d {database} -c 'REINDEX DATABASE {database}'",
    }


class MongoDBPlugin:
    """MongoDB commands."""
    
    SYSTEM_PROMPT = """You are a MongoDB expert. Generate mongosh commands.
Output only the command."""
    
    TEMPLATES = {
        "connect": "mongosh mongodb://{user}:{password}@{host}:27017/{database}",
        "dump": "mongodump --uri='mongodb://{host}:27017/{database}' --out={directory}",
        "restore": "mongorestore --uri='mongodb://{host}:27017' {directory}",
        "export": "mongoexport --uri='mongodb://{host}:27017/{database}' --collection={collection} --out={file}.json",
        "import": "mongoimport --uri='mongodb://{host}:27017/{database}' --collection={collection} --file={file}.json",
        "show_dbs": "mongosh --eval 'show dbs'",
        "show_collections": "mongosh {database} --eval 'show collections'",
        "stats": "mongosh {database} --eval 'db.stats()'",
    }


class RedisPlugin:
    """Redis commands."""
    
    SYSTEM_PROMPT = """You are a Redis expert. Generate redis-cli commands.
Output only the command."""
    
    TEMPLATES = {
        "connect": "redis-cli -h {host} -p {port} -a {password}",
        "ping": "redis-cli ping",
        "info": "redis-cli info",
        "keys": "redis-cli keys '*{pattern}*'",
        "get": "redis-cli get {key}",
        "set": "redis-cli set {key} '{value}'",
        "del": "redis-cli del {key}",
        "flushall": "redis-cli flushall",
        "save": "redis-cli bgsave",
        "monitor": "redis-cli monitor",
    }


class SQLitePlugin:
    """SQLite commands."""
    
    TEMPLATES = {
        "open": "sqlite3 {database}",
        "dump": "sqlite3 {database} .dump > {file}.sql",
        "import": "sqlite3 {database} < {file}.sql",
        "tables": "sqlite3 {database} '.tables'",
        "schema": "sqlite3 {database} '.schema {table}'",
        "vacuum": "sqlite3 {database} 'VACUUM'",
    }


class ElasticsearchPlugin:
    """Elasticsearch commands."""
    
    TEMPLATES = {
        "health": "curl -X GET 'localhost:9200/_cluster/health?pretty'",
        "indices": "curl -X GET 'localhost:9200/_cat/indices?v'",
        "create_index": "curl -X PUT 'localhost:9200/{index}'",
        "delete_index": "curl -X DELETE 'localhost:9200/{index}'",
        "search": "curl -X GET 'localhost:9200/{index}/_search?q={query}&pretty'",
        "bulk": "curl -X POST 'localhost:9200/_bulk' -H 'Content-Type: application/json' --data-binary @{file}.json",
    }


class CassandraPlugin:
    """Cassandra commands."""
    
    TEMPLATES = {
        "connect": "cqlsh {host}",
        "describe": "cqlsh -e 'DESCRIBE KEYSPACES'",
        "nodetool_status": "nodetool status",
        "nodetool_repair": "nodetool repair",
    }


class InfluxDBPlugin:
    """InfluxDB commands."""
    
    TEMPLATES = {
        "query": "influx query 'from(bucket:\"{bucket}\") |> range(start: -{time})'",
        "write": "influx write -b {bucket} '{measurement} {field}={value}'",
        "backup": "influx backup {directory}",
        "restore": "influx restore {directory}",
    }
