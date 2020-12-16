from ..database import DBMuziek
from .main_window import MainWindow


def run(db: DBMuziek):
    MainWindow(db).run()
