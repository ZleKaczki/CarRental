import unittest
from unittest.mock import MagicMock, patch
import mysql.connector
from CarRentalApp import CarRentalApp, LoginPage, MainWindow


class TestLoginPage(unittest.TestCase):
    def setUp(self):
        self.db = mysql.connector.connect(host="localhost", user="root", password="", database="carinventory")
        self.cursor = self.db.cursor()

    def tearDown(self):
        self.db.close()

    def test_login_success(self):
        app = CarRentalApp(self.db)
        login_page = LoginPage(app.notebook, MagicMock(), MagicMock(), MagicMock(), MagicMock())
        login_page.show_main_window = MagicMock(return_value=None)  # Mock metody show_main_window

        # Wprowadź dane logowania
        login_page.username_entry.insert(0, "milu")
        login_page.password_entry.insert(0, "password")

        # Wywołaj metodę logowania
        login_page.login()

        # Sprawdź, czy metoda show_main_window została wywołana dokładnie raz
        self.assertEqual(login_page.show_main_window.call_count, 1)

    def test_login_failure(self):
        app = CarRentalApp(self.db)
        login_page = LoginPage(app.notebook, MagicMock(), MagicMock(), MagicMock(), MagicMock())

        with patch("tkinter.messagebox.showerror") as mock_showerror:
            # Wprowadź nieprawidłowe dane logowania
            login_page.username_entry.insert(0, "tesas")
            login_page.password_entry.insert(0, "wrongpassword")

            # Wywołaj metodę logowania
            login_page.login()

            # Sprawdź, czy messagebox.showerror został wywołany raz z odpowiednimi argumentami
            mock_showerror.assert_called_once_with("Błąd logowania", "Nieprawidłowe dane logowania.")

    def test_show_main_window(self):
        app = CarRentalApp(self.db)
        app.show_main_window()

        # Sprawdź, czy główne okno zostało utworzone
        self.assertIsInstance(app.main_window, MainWindow)


if __name__ == "__main__":
    unittest.main()
