import libs.database as db

if __name__ == "__main__":
    con = db.connect("./muziek.db")

    print("DB CONNECTÉE")

    db.disconnect(con)