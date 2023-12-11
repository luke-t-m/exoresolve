
PLANNING:\
\
exoresolve repo:\
	src\
		killhand (dir)\
		exoresolve.py\
		exoresolve_cli.py\
		setup (dir)\
			resolv.conf\
\
	encrypted lists (dir)\
		never.list\
		always.list\
		sometimes.list\
	setup.py\
	update_lists.py\
\
\
\
/usr/local/exoresolve:\
	exoresolve.py\
	exores (exoresolve_cli.py)\
	killhand.ko\
	lists (dir)\
		never.list\
		always.list\
		sometimes.list\
	encryption_key	\
\
\
what setup does:\
mkdir /usr/local/exoresolve\
cp exoresolve.py, exoresolve_cli.py -> exores\
make killhand\
cp killhand.ko\
mkdir lists\
unencrypt encrypted_lists to lists\
\
\
\
TO-DO:\
make cli.\
fork off into private(r) repo for more secure url lists/ settings.
