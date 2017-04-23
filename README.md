## Quotes Posting Model ##

Quotes posting modeling.

It is just a practice project. So the description is provided only in Russian. [Link](https://vasilesk.ru/static/files/extra/quotes_posting.pdf)


### Dependencies ###

* PyQt5
* psycopg2

### DB schema###

DB schema can be found in **extra/db.sql**

### Configuration ###

Set variable

    SSH_ON = True

in **main.py** if you need ssh tunnel for DB connection.

Configuration files are stored in **config** folder.

DB configuration is in **db.json** or in **tunnel.py** and **db_over_ssh.json** for **SSH_ON** mode (host must be set *localhost* for this mode)
