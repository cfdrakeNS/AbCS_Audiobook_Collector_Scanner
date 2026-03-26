import sys
from PySide6.QtWidgets import QApplication
from src.ui.web_metadata import WebMetadataWindow
from src.database import DatabaseManager, Book
from src.accessibility.scaling import UIScaler
from src.accessibility.theme_manager import ThemeManager


def test_web_metadata_window():
    app = QApplication(sys.argv)
    scaler = UIScaler(app)
    theme_manager = ThemeManager(app)
    db = None  # Use None for DB in test
    # Create a dummy book with minimal fields
    book = Book(
        title="Test Title",
        author_name="Test Author",
        comments="Test plot",
        year=2022,
        series_name="Test Series",
        genre_name="Test Genre"
    )
    win = WebMetadataWindow(db=db, book=book, scaler=scaler, theme_manager=theme_manager)
    win.show()
    print("WebMetadataWindow opened successfully.")
    return app.exec()

if __name__ == "__main__":
    sys.exit(test_web_metadata_window())
