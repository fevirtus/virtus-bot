"""Read-only logical snapshot. Run in the existing pod; stdout is private gzip.

Exports public tables, PostgreSQL JSON rows (preserving numeric precision),
column definitions, constraints, indexes and sequences in one repeatable-read
transaction. No database writes or extra credentials are needed.
"""
import asyncio
import gzip
import json
import os
import sys
import asyncpg


def ident(value):
    return '"'+value.replace('"', '""')+'"'


async def main():
    url = os.getenv('POSTGRES_URL')
    if url:
        conn = await asyncpg.connect(url.replace('postgresql+asyncpg://', 'postgresql://'), timeout=15)
    else:
        conn = await asyncpg.connect(host=os.environ['POSTGRES_HOST'], port=int(os.getenv('POSTGRES_PORT', '5432')),
                                     user=os.environ['POSTGRES_USER'], password=os.environ['POSTGRES_PASSWORD'],
                                     database=os.environ['POSTGRES_DB'], timeout=15)
    try:
        async with conn.transaction(isolation='repeatable_read', readonly=True):
            tables = await conn.fetch("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename")
            snapshot = {'format': 1, 'server': await conn.fetchval('SHOW server_version'), 'tables': {}}
            for table in tables:
                name = table['tablename']
                columns = await conn.fetch('''SELECT a.attname AS name, format_type(a.atttypid,a.atttypmod) AS type,
                    a.attnotnull AS not_null, a.attidentity AS identity, pg_get_expr(d.adbin,d.adrelid) AS default_expr
                    FROM pg_attribute a LEFT JOIN pg_attrdef d ON d.adrelid=a.attrelid AND d.adnum=a.attnum
                    WHERE a.attrelid=to_regclass($1) AND a.attnum>0 AND NOT a.attisdropped ORDER BY a.attnum''', 'public.'+ident(name))
                constraints = await conn.fetch('SELECT conname AS name, pg_get_constraintdef(oid) AS definition FROM pg_constraint WHERE conrelid=to_regclass($1)', 'public.'+ident(name))
                indexes = await conn.fetch('SELECT indexname AS name,indexdef AS definition FROM pg_indexes WHERE schemaname=$1 AND tablename=$2', 'public', name)
                rows = await conn.fetch('SELECT row_to_json(t)::text AS data FROM public.'+ident(name)+' t')
                snapshot['tables'][name] = {'columns': [dict(x) for x in columns], 'constraints': [dict(x) for x in constraints],
                                            'indexes': [dict(x) for x in indexes], 'rows': [x['data'] for x in rows]}
            sequences = await conn.fetch("SELECT sequencename,start_value,min_value,max_value,increment_by,cycle,cache_size,last_value FROM pg_sequences WHERE schemaname='public'")
            snapshot['sequences'] = [dict(x) for x in sequences]
        sys.stdout.buffer.write(gzip.compress(json.dumps(snapshot, default=lambda value: value.decode() if isinstance(value, bytes) else str(value)).encode()))
    finally:
        await conn.close()

if __name__ == '__main__':
    asyncio.run(main())
