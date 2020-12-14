from ..database import DBMuziek
from .main_window import MainWindow


def run(db: DBMuziek):
    print(db.connection)
    MainWindow(db).run()
