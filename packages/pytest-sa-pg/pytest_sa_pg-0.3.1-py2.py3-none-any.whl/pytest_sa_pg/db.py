import os
import tempfile
import subprocess
from pathlib import Path


def pcall(cmd, args, env=None):
    try:
        return subprocess.check_call([cmd] + args, env=env)
    except OSError:
        # path might be unset on windows and also debian derivatives
        raise OSError('command %r failed, is it in your PATH ?' % cmd)


def edit_config(confpath, confoptions):
    with confpath.open('ab') as cfg:
        for optname, optvalue in confoptions.items():
            cfg.write('{} = {}\n'.format(optname, optvalue).encode('ascii'))


def ensure_cluster(clusterpath, postgresql_conf_options=None):
    if not clusterpath.exists():
        pcall('initdb', ['-D', clusterpath.as_posix(), '-E', 'utf-8', '--locale=C'])
        if postgresql_conf_options is not None:
            print('Adjusting `{}/postgresql.conf`'.format(clusterpath))
            edit_config(clusterpath / 'postgresql.conf', postgresql_conf_options)



def setup_local_pg_cluster(request, datadir, pgport,
                           postgresql_conf_options=None):
    " create (if missing) a local cluster to use for the tests "
    dbpath = Path(datadir, 'pgdb')
    ensure_cluster(dbpath, postgresql_conf_options)
    env = os.environ.copy()
    sockdir = tempfile.mkdtemp(prefix='pgsocket')
    options = '-k %s -p %s' % (sockdir, pgport)
    options += ' -c fsync=off -c full_page_writes=off'
    options += ' -c synchronous_commit=off'
    pcall('pg_ctl', ['start', '-w', '-D', dbpath.as_posix(), '-o', options], env=env)

    def shutdown_postgres():
        pcall('pg_ctl', ['stop', '-D', dbpath.as_posix(), '-m', 'fast'])
        try:
            os.rmdir(sockdir)
        except OSError:
            pass
    request.addfinalizer(shutdown_postgres)
