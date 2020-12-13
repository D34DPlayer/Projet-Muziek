from .main_window import MainWindow
from ..database import DBMuziek


def run(db: DBMuziek):
    print(db.connection)
    MainWindow().run()
