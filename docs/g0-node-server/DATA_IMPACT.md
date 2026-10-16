# Data Impact

No real users, tenants, customer files, finance or database. Disposable files contain public/secret marker strings only. Loopback server port is ephemeral; temporary directories and sockets are cleaned in finally hooks. No backups or compensation needed because persistent data is untouched.
