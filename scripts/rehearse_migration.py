"""Restore a private logical backup into a disposable *_rehearsal database.

Never writes to production: the target database name must end in _rehearsal.
Run with POSTGRES_URL targeting that local database and backup path as argv[1].
"""
import asyncio
import gzip
import json
import os
from pathlib import Path
import sys
from urllib.parse import urlsplit
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import asyncpg
from infra.db import postgres


def ident(value):
    return '"'+value.replace('"', '""')+'"'


async def main():
    url = os.environ['POSTGRES_URL'].replace('postgresql+asyncpg://', 'postgresql://')
    if not urlsplit(url).path.endswith('_rehearsal'):
        raise SystemExit('Refusing to restore into a database without _rehearsal suffix')
    snapshot = json.loads(gzip.decompress(Path(sys.argv[1]).read_bytes()))
    conn = await asyncpg.connect(url)
    try:
        assert not await conn.fetchval("SELECT count(*) FROM pg_tables WHERE schemaname='public'"), 'Target must be empty'
        async with conn.transaction():
            for seq in snapshot['sequences']:
                await conn.execute(f"CREATE SEQUENCE public.{ident(seq['sequencename'])} START {seq['start_value']} INCREMENT {seq['increment_by']} MINVALUE {seq['min_value']} MAXVALUE {seq['max_value']} CACHE {seq['cache_size']} {'CYCLE' if seq['cycle'] else 'NO CYCLE'}")
            for name, table in snapshot['tables'].items():
                columns = []
                for col in table['columns']:
                    columns.append(ident(col['name'])+' '+col['type']+(' NOT NULL' if col['not_null'] else '')+
                                   (' DEFAULT '+col['default_expr'] if col['default_expr'] else ''))
                await conn.execute('CREATE TABLE public.'+ident(name)+' ('+', '.join(columns)+')')
                # PostgreSQL parses its own JSON representation, preserving exact types.
                await conn.executemany('INSERT INTO public.'+ident(name)+' SELECT * FROM json_populate_record(NULL::public.'+ident(name)+', $1::json)',
                                       [(row,) for row in table['rows']])
            constraints = [(name,c) for name,t in snapshot['tables'].items() for c in t['constraints'] if not c['definition'].startswith('NOT NULL')]
            for name, c in sorted(constraints, key=lambda pair: pair[1]['definition'].startswith('FOREIGN KEY')):
                await conn.execute('ALTER TABLE public.'+ident(name)+' ADD CONSTRAINT '+ident(c['name'])+' '+c['definition'])
            for name, table in snapshot['tables'].items():
                names = {c['name'] for c in table['constraints']}
                for index in table['indexes']:
                    if index['name'] not in names:
                        await conn.execute(index['definition'])
            for seq in snapshot['sequences']:
                await conn.execute('SELECT setval($1::regclass,$2,$3)', 'public.'+ident(seq['sequencename']),
                                   seq['last_value'] or seq['start_value'], seq['last_value'] is not None)
        await postgres.create_tables()
        await postgres.verify_and_migrate_schema()
        await postgres.verify_and_migrate_schema()
        for name, table in snapshot['tables'].items():
            restored = await conn.fetch('SELECT row_to_json(t)::text AS data FROM public.'+ident(name)+' t')
            normalize = lambda rows: sorted(json.dumps(json.loads(row), sort_keys=True, ensure_ascii=False) for row in rows)
            assert normalize([r['data'] for r in restored]) == normalize(table['rows']), 'Migration changed rows in '+name
        print('Restore + repeated startup migration verified; all original rows preserved:', sum(len(t['rows']) for t in snapshot['tables'].values()))
    finally:
        await conn.close()
        await postgres.engine.dispose()

if __name__ == '__main__':
    asyncio.run(main())
