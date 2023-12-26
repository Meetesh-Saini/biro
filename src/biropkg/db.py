import sqlite3


def pre_db(birohome):
    con = sqlite3.connect(f"{birohome}/index.db")
    cur = con.cursor()

    cur.executescript(
        """
        -- Table for Packages
        CREATE TABLE IF NOT EXISTS Packages (
            name TEXT PRIMARY KEY,
            description TEXT,
            readme_file_path TEXT,
            version TEXT,
            fetch_url TEXT UNIQUE,
            authors TEXT
        );
        """
    )

    con.commit()
    con.close()
