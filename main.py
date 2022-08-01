import sqlite3

def get_address():
    conn = sqlite3.connect("settings.db")
    cur = conn.cursor()
    settings = cur.execute("SELECT * FROM settings").fetchone()
    print(settings)
    conn.close()


if __name__ == '__main__':
    get_address()
