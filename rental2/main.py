import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import mysql.connector

class CarRentalApp(tk.Tk): #okno aplikacji używamy biblioteki tkinter
    def __init__(self, db):
        super().__init__()
        self.title("Wypożyczalnia samochodów")
        self.db = db
        self.cursor = db.cursor()

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.login_page = LoginPage(self.notebook, self.db, self.cursor, self.show_main_window)
        self.notebook.add(self.login_page, text="Logowanie")


    def show_main_window(self):
        self.notebook.forget(0)  # Forget the login page
        self.main_window = MainWindow(self.notebook, self.db, self.cursor)
        self.notebook.add(self.main_window, text="Strona główna")

class MainWindow(ttk.Frame):
    def __init__(self, notebook, db, cursor):
        super().__init__(notebook)
        self.db = db
        self.cursor = cursor

        # Tworzenie widżetu ttk.Notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Dodawanie zakładek do widżetu ttk.Notebook
        self.add_tab1()
        self.add_tab2()
        self.add_tab3()

    def add_tab1(self):
        tab1 = ttk.Frame(self.notebook)

        self.users_page = UsersPage(self.notebook, self.db, self.cursor)
        self.notebook.add(self.users_page, text="Klienci")

    def add_tab2(self):
        tab2 = ttk.Frame(self.notebook)

        self.cars_page = CarsPage(self.notebook, self.db, self.cursor)
        self.notebook.add(self.cars_page, text="Samochody")

    def add_tab3(self):
        tab3 = ttk.Frame(self.notebook)

        self.rentals_page = RentalsPage(self.notebook, self.db, self.cursor)
        self.notebook.add(self.rentals_page, text="Wypożyczenia")


class UsersPage(ttk.Frame): #strona klientów
    def __init__(self, notebook, db, cursor):
        super().__init__(notebook)
        self.db = db
        self.cursor = cursor

        label = ttk.Label(self, text='Przeglądaj klientów')
        label.pack()

        self.users_treeview = ttk.Treeview(self)
        self.users_treeview.pack()

        self.users_treeview["columns"] = ("customer_id", "first_name", "last_name", "email", "phone_number")
        self.users_treeview.column("#0", width=0, stretch=tk.NO)
        self.users_treeview.column("customer_id", anchor=tk.W, width=70)
        self.users_treeview.column("first_name", anchor=tk.W, width=100)
        self.users_treeview.column("last_name", anchor=tk.W, width=100)
        self.users_treeview.column("email", anchor=tk.W, width=200)
        self.users_treeview.column("phone_number", anchor=tk.W, width=100)

        self.users_treeview.heading("#0", text="", anchor=tk.W)
        self.users_treeview.heading("customer_id", text="ID", anchor=tk.W)
        self.users_treeview.heading("first_name", text="Imię", anchor=tk.W)
        self.users_treeview.heading("last_name", text="Nazwisko", anchor=tk.W)
        self.users_treeview.heading("email", text="Email", anchor=tk.W)
        self.users_treeview.heading("phone_number", text="Numer telefonu", anchor=tk.W)

        self.load_users()

        add_user_button = ttk.Button(self, text="Dodaj klienta", command=self.add_user)
        add_user_button.pack()
        delete_user_button = ttk.Button(self, text="Usuń klienta", command=self.delete_user)
        delete_user_button.pack()

    def load_users(self):
        self.users_treeview.delete(*self.users_treeview.get_children())
        self.cursor.execute("SELECT * FROM users")
        users = self.cursor.fetchall()
        for user in users:
            self.users_treeview.insert("", tk.END, text="", values=user)

    def add_user(self):
        add_user_window = AddUserWindow(self.db, self.cursor, self.load_users)

    def delete_user(self):  #usuwanie uzytkowników. Nie da isę usunąć jeśli są powiązani z tableą rental. Trzeba dodać komunikat o tym
        selected_item = self.users_treeview.focus()
        if selected_item:
            user_id = self.users_treeview.item(selected_item)["values"][0]
            query = "DELETE FROM users WHERE customer_id = %s"
            values = (user_id,)
            self.cursor.execute(query, values)
            self.db.commit()
            self.load_users()

class AddUserWindow(tk.Toplevel):
    def __init__(self, db, cursor, callback):
        super().__init__()
        self.db = db
        self.cursor = cursor
        self.callback = callback

        self.title("Dodaj użytkownika")

        label_first_name = ttk.Label(self, text="Imię:")
        label_first_name.grid(row=0, column=0, sticky=tk.E)
        self.entry_first_name = ttk.Entry(self)
        self.entry_first_name.grid(row=0, column=1)

        label_last_name = ttk.Label(self, text="Nazwisko:")
        label_last_name.grid(row=1, column=0, sticky=tk.E)
        self.entry_last_name = ttk.Entry(self)
        self.entry_last_name.grid(row=1, column=1)

        label_email = ttk.Label(self, text="Email:")
        label_email.grid(row=2, column=0, sticky=tk.E)
        self.entry_email = ttk.Entry(self)
        self.entry_email.grid(row=2, column=1)

        label_phone_number = ttk.Label(self, text="Numer telefonu:")
        label_phone_number.grid(row=3, column=0, sticky=tk.E)
        self.entry_phone_number = ttk.Entry(self)
        self.entry_phone_number.grid(row=3, column=1)

        save_button = ttk.Button(self, text="Zapisz", command=self.save_user)
        save_button.grid(row=4, column=0, columnspan=2)

    def save_user(self):
        first_name = self.entry_first_name.get()
        last_name = self.entry_last_name.get()
        email = self.entry_email.get()
        phone_number = self.entry_phone_number.get()

        query = "INSERT INTO users (first_name, last_name, email, phone_number) VALUES (%s, %s, %s, %s)"
        values = (first_name, last_name, email, phone_number)

        self.cursor.execute(query, values)
        self.db.commit()

        self.callback()
        self.destroy()

class CarsPage(ttk.Frame):
    def __init__(self, notebook, db, cursor):
        super().__init__(notebook)
        self.db = db
        self.cursor = cursor

        label = ttk.Label(self, text='Przeglądaj samochody')
        label.pack()

        self.cars_treeview = ttk.Treeview(self)
        self.cars_treeview.pack()

        self.cars_treeview["columns"] = ("car_id", "brand", "model", "year", "color", "price", "available")
        self.cars_treeview.column("#0", width=0, stretch=tk.NO)
        self.cars_treeview.column("car_id", anchor=tk.W, width=70)
        self.cars_treeview.column("brand", anchor=tk.W, width=100)
        self.cars_treeview.column("model", anchor=tk.W, width=100)
        self.cars_treeview.column("year", anchor=tk.W, width=70)
        self.cars_treeview.column("color", anchor=tk.W, width=100)
        self.cars_treeview.column("price", anchor=tk.W, width=70)
        self.cars_treeview.column("available", anchor=tk.W, width=70)

        self.cars_treeview.heading("#0", text="", anchor=tk.W)
        self.cars_treeview.heading("car_id", text="ID", anchor=tk.W)
        self.cars_treeview.heading("brand", text="Marka", anchor=tk.W)
        self.cars_treeview.heading("model", text="Model", anchor=tk.W)
        self.cars_treeview.heading("year", text="Rok", anchor=tk.W)
        self.cars_treeview.heading("color", text="Kolor", anchor=tk.W)
        self.cars_treeview.heading("price", text="Cena", anchor=tk.W)
        self.cars_treeview.heading("available", text="Dostępny", anchor=tk.W)

        self.load_cars()

        add_car_button = ttk.Button(self, text="Dodaj samochód", command=self.add_car)
        add_car_button.pack()
        delete_car_button = ttk.Button(self, text="Usuń samochód", command=self.delete_car)
        delete_car_button.pack()

    def load_cars(self):
        self.cars_treeview.delete(*self.cars_treeview.get_children())
        self.cursor.execute("SELECT * FROM carlist")
        cars = self.cursor.fetchall()
        for car in cars:
            self.cars_treeview.insert("", tk.END, text="", values=car)

    def add_car(self):
        add_car_window = AddCarWindow(self.db, self.cursor, self.load_cars)

    def delete_car(self):
        selected_item = self.cars_treeview.focus()
        if selected_item:
            car_id = self.cars_treeview.item(selected_item)["values"][0]
            query = "DELETE FROM carlist WHERE id = %s"
            values = (car_id,)
            self.cursor.execute(query, values)
            self.db.commit()
            self.load_cars()

class AddCarWindow(tk.Toplevel):
    def __init__(self, db, cursor, callback):
        super().__init__()
        self.db = db
        self.cursor = cursor
        self.callback = callback

        self.title("Dodaj samochód")

        label_brand = ttk.Label(self, text="Marka:")
        label_brand.grid(row=0, column=0, sticky=tk.E)
        self.entry_brand = ttk.Entry(self)
        self.entry_brand.grid(row=0, column=1)

        label_model = ttk.Label(self, text="Model:")
        label_model.grid(row=1, column=0, sticky=tk.E)
        self.entry_model = ttk.Entry(self)
        self.entry_model.grid(row=1, column=1)

        label_year = ttk.Label(self, text="Rok:")
        label_year.grid(row=2, column=0, sticky=tk.E)
        self.entry_year = ttk.Entry(self)
        self.entry_year.grid(row=2, column=1)

        label_color = ttk.Label(self, text="Kolor:")
        label_color.grid(row=3, column=0, sticky=tk.E)
        self.entry_color = ttk.Entry(self)
        self.entry_color.grid(row=3, column=1)

        label_price = ttk.Label(self, text="Cena:")
        label_price.grid(row=4, column=0, sticky=tk.E)
        self.entry_price = ttk.Entry(self)
        self.entry_price.grid(row=4, column=1)

        label_available = ttk.Label(self, text="Dostępny:")
        label_available.grid(row=5, column=0, sticky=tk.E)
        self.entry_available = ttk.Entry(self)
        self.entry_available.grid(row=5, column=1)

        save_button = ttk.Button(self, text="Zapisz", command=self.save_car)
        save_button.grid(row=6, column=0, columnspan=2)

    def save_car(self):
        brand = self.entry_brand.get()
        model = self.entry_model.get()
        year = self.entry_year.get()
        color = self.entry_color.get()
        price = self.entry_price.get()
        available = self.entry_available.get()

        query = "INSERT INTO carlist (brand, model, year, color, price, available) VALUES (%s, %s, %s, %s, %s, %s)"
        values = (brand, model, year, color, price, available)

        self.cursor.execute(query, values)
        self.db.commit()

        self.callback()
        self.destroy()

class RentalsPage(ttk.Frame):
    def __init__(self, notebook, db, cursor):
        super().__init__(notebook)
        self.db = db
        self.cursor = cursor

        label = ttk.Label(self, text='Przeglądaj wypożyczenia')
        label.pack()

        self.rentals_treeview = ttk.Treeview(self)
        self.rentals_treeview.pack()

        self.rentals_treeview["columns"] = ( "rental_date", "user_id", "car_id", "return_date")
        self.rentals_treeview.column("#0", width=0, stretch=tk.NO)
        #self.rentals_treeview.column("rental_id", anchor=tk.W, width=70) to jest raczej niepotrzebne ale zostawiam na wszelki wypadek. zeby działało poprawnie trzeba do bazy danych dodać ten atrybut i zmienić w kodzie pare rzeczy
        self.rentals_treeview.column("rental_date", anchor=tk.W, width=100)
        self.rentals_treeview.column("user_id", anchor=tk.W, width=70)
        self.rentals_treeview.column("car_id", anchor=tk.W, width=70)
        self.rentals_treeview.column("return_date", anchor=tk.W, width=100)

        self.rentals_treeview.heading("#0", text="", anchor=tk.W)
        #self.rentals_treeview.heading("rental_id", text="ID", anchor=tk.W)
        self.rentals_treeview.heading("rental_date", text="Data wypożyczenia", anchor=tk.W)
        self.rentals_treeview.heading("user_id", text="ID użytkownika", anchor=tk.W)
        self.rentals_treeview.heading("car_id", text="ID samochodu", anchor=tk.W)
        self.rentals_treeview.heading("return_date", text="Data zwrotu", anchor=tk.W)

        self.load_rentals()

        add_rental_button = ttk.Button(self, text="Dodaj wypożyczenie", command=self.add_rental)
        add_rental_button.pack()

    def load_rentals(self):
        self.rentals_treeview.delete(*self.rentals_treeview.get_children())
        self.cursor.execute("SELECT * FROM rental")
        rentals = self.cursor.fetchall()
        for rental in rentals:
            self.rentals_treeview.insert("", tk.END, text="", values=rental)

    def add_rental(self):
        add_rental_window = AddRentalWindow(self.db, self.cursor, self.load_rentals)

class AddRentalWindow(tk.Toplevel):
    def __init__(self, db, cursor, callback):
        super().__init__()
        self.db = db
        self.cursor = cursor
        self.callback = callback

        self.title("Dodaj wypożyczenie")

        label_rental_date = ttk.Label(self, text="Data wypożyczenia:")
        label_rental_date.grid(row=0, column=0, sticky=tk.E)
        self.entry_rental_date = ttk.Entry(self)
        self.entry_rental_date.grid(row=0, column=1)

        label_user_id = ttk.Label(self, text="Wybierz klienta:")
        label_user_id.grid(row=1, column=0, sticky=tk.E)
        self.user_id_var = tk.StringVar()
        self.combo_user_id = ttk.Combobox(self, textvariable=self.user_id_var)
        self.combo_user_id.grid(row=1, column=1)
        self.load_users()

        label_car_id = ttk.Label(self, text="Wybierz samochód:")
        label_car_id.grid(row=2, column=0, sticky=tk.E)
        self.car_id_var = tk.StringVar()
        self.combo_car_id = ttk.Combobox(self, textvariable=self.car_id_var)
        self.combo_car_id.grid(row=2, column=1)
        self.load_cars()

        label_return_date = ttk.Label(self, text="Data zwrotu:")
        label_return_date.grid(row=3, column=0, sticky=tk.E)
        self.entry_return_date = ttk.Entry(self)
        self.entry_return_date.grid(row=3, column=1)

        save_button = ttk.Button(self, text="Zapisz", command=self.save_rental)
        save_button.grid(row=4, column=0, columnspan=2)

    def load_users(self):
        self.combo_user_id['values'] = []
        self.cursor.execute("SELECT customer_id, first_name, last_name FROM users")
        users = self.cursor.fetchall()
        user_options = []
        for user in users:
            user_options.append(f"{user[0]} - {user[1]} {user[2]}")
        self.combo_user_id['values'] = user_options

    def load_cars(self):
        self.combo_car_id['values'] = []
        self.cursor.execute("SELECT id, brand, model FROM carlist WHERE available = '1'") #available jest zapisane jako tinyint gdzie 1 to dostępne a 0 niedostępne
        cars = self.cursor.fetchall()
        car_options = []
        for car in cars:
            car_options.append(f"{car[0]} - {car[1]} {car[2]}")
        self.combo_car_id['values'] = car_options

    def save_rental(self):
        rental_date = self.entry_rental_date.get()
        user_id = self.user_id_var.get().split()[0]
        car_id = self.car_id_var.get().split()[0]
        return_date = self.entry_return_date.get()

        # Sprawdzanie dostępności samochodu na podaną datę. Ale chyba nie działa poprawnie. Do tego może być potrzebna biblioteka time
        query = "SELECT * FROM rental WHERE car_id = %s AND rental_date = %s"
        values = (car_id, rental_date)
        self.cursor.execute(query, values)
        existing_rentals = self.cursor.fetchall()

        if existing_rentals:
            messagebox.showerror("Błąd", "Samochód jest już zarezerwowany na tę datę.")
        else:
            query = "INSERT INTO rental (rental_date, user_id, car_id, return_date) VALUES (%s, %s, %s, %s)"
            values = (rental_date, user_id, car_id, return_date)

            self.cursor.execute(query, values)
            self.db.commit()

            self.callback()
            self.destroy()

class LoginPage(ttk.Frame):
    def __init__(self, notebook, db, cursor, login_callback):
        super().__init__(notebook)
        self.db = db
        self.cursor = cursor
        self.login_callback = login_callback

        label_username = ttk.Label(self, text="Nazwa użytkownika:")
        label_username.pack()
        self.entry_username = ttk.Entry(self)
        self.entry_username.pack()

        label_password = ttk.Label(self, text="Hasło:")
        label_password.pack()
        self.entry_password = ttk.Entry(self, show="*")
        self.entry_password.pack()

        login_button = ttk.Button(self, text="Zaloguj", command=self.login)
        login_button.pack()

    def login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        query = "SELECT * FROM admins WHERE username = %s AND password = %s"
        values = (username, password)
        self.cursor.execute(query, values)
        user = self.cursor.fetchone()

        if user:
            self.login_callback()
        else:
            tk.messagebox.showerror("Błąd logowania", "Nieprawidłowa nazwa użytkownika lub hasło")


# Połączenie z bazą danych. Wpisać usera i hasło. Trzeba stworzyć bazę w SQLu, tablice są w polecenia sql
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="kotek1",
    database="carinventory"
)

app = CarRentalApp(db)
app.mainloop()
