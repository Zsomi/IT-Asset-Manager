import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from GZ_modul import GZDataManager, GZ_today, GZ_validate_date


class GZApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("IT Asset Manager")
        self.geometry("1000x700")
        self.minsize(800, 500)
        self.configure(bg="#1e1e2e")
        self.db = GZDataManager()
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        self.main_frame = ttk.Frame(self, padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.create_menu()
        self.current_view = None
        self.show_computers_view()

    def configure_styles(self):
        """Stílusok beállítása a GUI-hoz."""
        bg_color = "#1e1e2e"
        fg_color = "#d4d4d8"

        self.style.configure('TFrame', background=bg_color)
        self.style.configure('TLabel', background=bg_color, foreground=fg_color, font=('Segoe UI', 10))
        self.style.configure('TButton', background="#313244", foreground=fg_color, font=('Segoe UI', 10), borderwidth=1)
        self.style.map('TButton', background=[('active', '#45475a')])
        self.style.configure('TEntry', fieldbackground="#313244", foreground=fg_color, insertcolor=fg_color)
        self.style.configure('Treeview', background="#313244", foreground=fg_color, fieldbackground="#313244")
        self.style.configure('Treeview.Heading', background="#45475a", foreground=fg_color, font=('Segoe UI', 10, 'bold'))
        self.style.configure('TScrollbar', background=bg_color, troughcolor="#313244")

    def create_menu(self):
        """Menü sáv létrehozása."""
        menu_bar = tk.Menu(self, bg="#1e1e2e", fg="#d4d4d8", activebackground="#45475a", activeforeground="#d4d4d8")
        self.config(menu=menu_bar)

        computers_menu = tk.Menu(menu_bar, tearoff=0, bg="#1e1e2e", fg="#d4d4d8")
        computers_menu.add_command(label="Számítógépek listája", command=self.show_computers_view)
        computers_menu.add_command(label="Új számítógép", command=self.show_add_computer_dialog)
        computers_menu.add_separator()
        computers_menu.add_command(label="Selejtezések", command=self.show_disposals_view)
        menu_bar.add_cascade(label="Számítógépek", menu=computers_menu)

        users_menu = tk.Menu(menu_bar, tearoff=0, bg="#1e1e2e", fg="#d4d4d8")
        users_menu.add_command(label="Felhasználók listája", command=self.show_users_view)
        users_menu.add_command(label="Új felhasználó", command=self.show_add_user_dialog)
        menu_bar.add_cascade(label="Felhasználók", menu=users_menu)

        assignments_menu = tk.Menu(menu_bar, tearoff=0, bg="#1e1e2e", fg="#d4d4d8")
        assignments_menu.add_command(label="Aktív kiadások", command=lambda: self.show_assignments_view(active_only=True))
        assignments_menu.add_command(label="Összes kiadás", command=lambda: self.show_assignments_view(active_only=False))
        menu_bar.add_cascade(label="Kiadások", menu=assignments_menu)

    def clear_view(self):
        """Aktuális nézet törlése."""
        if self.current_view:
            self.current_view.destroy()
            self.current_view = None

    def show_computers_view(self):
        """Számítógépek listázása táblázatban."""
        self.clear_view()

        frame = ttk.Frame(self.main_frame)
        frame.pack(fill=tk.BOTH, expand=True)
        self.current_view = frame

        search_frame = ttk.Frame(frame)
        search_frame.pack(fill=tk.X, pady=5)

        ttk.Label(search_frame, text="Keresés:").pack(side=tk.LEFT, padx=5)
        search_entry = ttk.Entry(search_frame, width=30)
        search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        status_label = ttk.Label(search_frame, text="Státusz:")
        status_label.pack(side=tk.LEFT, padx=5)
        status_combo = ttk.Combobox(search_frame, values=["", "Elérhető", "Használatban", "Javítás alatt", "Selejtezett"], width=15)
        status_combo.pack(side=tk.LEFT, padx=5)

        def refresh_computers():
            self.load_computers_table(tree, search_entry.get(), status_combo.get())

        ttk.Button(search_frame, text="Keresés", command=refresh_computers).pack(side=tk.LEFT, padx=5)

        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        tree = ttk.Treeview(tree_frame, columns=("id", "asset_tag", "name", "manufacturer", "model", "processor", "ram", "storage", "os", "purchase_date", "status", "notes"), show="headings")

        tree.heading("id", text="ID", anchor=tk.W)
        tree.heading("asset_tag", text="Leltári szám", anchor=tk.W)
        tree.heading("name", text="Név", anchor=tk.W)
        tree.heading("manufacturer", text="Gyártó", anchor=tk.W)
        tree.heading("model", text="Modell", anchor=tk.W)
        tree.heading("processor", text="Processzor", anchor=tk.W)
        tree.heading("ram", text="RAM", anchor=tk.W)
        tree.heading("storage", text="Tárhely", anchor=tk.W)
        tree.heading("os", text="Operációs rendszer", anchor=tk.W)
        tree.heading("purchase_date", text="Vételi dátum", anchor=tk.W)
        tree.heading("status", text="Státusz", anchor=tk.W)
        tree.heading("notes", text="Megjegyzés", anchor=tk.W)

        tree.column("id", width=50, anchor=tk.W)
        tree.column("asset_tag", width=100, anchor=tk.W)
        tree.column("name", width=150, anchor=tk.W)
        tree.column("manufacturer", width=100, anchor=tk.W)
        tree.column("model", width=100, anchor=tk.W)
        tree.column("processor", width=100, anchor=tk.W)
        tree.column("ram", width=80, anchor=tk.W)
        tree.column("storage", width=80, anchor=tk.W)
        tree.column("os", width=120, anchor=tk.W)
        tree.column("purchase_date", width=100, anchor=tk.W)
        tree.column("status", width=100, anchor=tk.W)
        tree.column("notes", width=150, anchor=tk.W)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=scrollbar.set)

        # Adatok betöltése
        self.load_computers_table(tree, "", "")

        # Gombok
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=5)

        ttk.Button(button_frame, text="Új számítógép", command=self.show_add_computer_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Szerkesztés", command=lambda: self.edit_computer(tree)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Kiadás", command=lambda: self.assign_computer_from_table(tree)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Selejtezés", command=lambda: self.dispose_computer_from_table(tree)).pack(side=tk.LEFT, padx=5)
        tree.bind("<Double-1>", lambda e: self.edit_computer(tree))

    def load_computers_table(self, tree, search="", status=""):
        """Számítógépek betöltése a táblázatba."""
        for item in tree.get_children():
            tree.delete(item)

        computers = self.db.list_computers(search=search, status=status)
        for comp in computers:
            tree.insert("", tk.END, values=(
                comp.get("id"),
                comp.get("asset_tag"),
                comp.get("name"),
                comp.get("manufacturer"),
                comp.get("model"),
                comp.get("processor"),
                comp.get("ram"),
                comp.get("storage"),
                comp.get("operating_system"),
                comp.get("purchase_date"),
                comp.get("status"),
                comp.get("notes")
            ))

    def show_add_computer_dialog(self):
        """Új számítógép hozzáadása."""
        dialog = tk.Toplevel(self)
        dialog.title("Új számítógép")
        dialog.transient(self)
        dialog.grab_set()

        form = ttk.Frame(dialog, padding=10)
        form.pack(fill=tk.BOTH, expand=True)

        fields = [
            ("asset_tag", "Leltári szám:", True),
            ("name", "Név:", True),
            ("manufacturer", "Gyártó:", False),
            ("model", "Modell:", False),
            ("serial_number", "Sorozatszám:", False),
            ("processor", "Processzor:", False),
            ("ram", "RAM:", False),
            ("storage", "Tárhely:", False),
            ("operating_system", "Operációs rendszer:", False),
            ("purchase_date", "Vételi dátum (YYYY-MM-DD):", False),
            ("status", "Státusz:", False),
            ("notes", "Megjegyzés:", False),
        ]

        entries = {}
        for i, (field, label, required) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=i, column=0, sticky=tk.W, pady=2)
            if field == "status":
                combo = ttk.Combobox(form, values=["Elérhető", "Használatban", "Javítás alatt", "Selejtezett"])
                combo.grid(row=i, column=1, sticky=tk.EW, pady=2, padx=5)
                combo.set("Elérhető")
                entries[field] = combo
            else:
                entry = ttk.Entry(form)
                entry.grid(row=i, column=1, sticky=tk.EW, pady=2, padx=5)
                entries[field] = entry

        button_frame = ttk.Frame(form)
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)

        def save():
            computer = {}
            for field, widget in entries.items():
                value = widget.get() if isinstance(widget, ttk.Entry) else widget.get()
                if value:
                    computer[field] = value

            if not computer.get("asset_tag") or not computer.get("name"):
                messagebox.showerror("Hiba", "A leltári szám és a név kötelező!")
                return

            if computer.get("purchase_date") and not GZ_validate_date(computer.get("purchase_date")):
                messagebox.showerror("Hiba", "Érvénytelen dátum formátum! Használj YYYY-MM-DD formátumot.")
                return

            try:
                self.db.add_computer(computer)
                messagebox.showinfo("Siker", "Számítógép sikeresen hozzáadva!")
                dialog.destroy()
                if self.current_view:
                    for widget in self.current_view.winfo_children():
                        if isinstance(widget, ttk.Treeview):
                            self.load_computers_table(widget)
                            break
            except Exception as e:
                messagebox.showerror("Hiba", str(e))

        ttk.Button(button_frame, text="Mentés", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Mégse", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def edit_computer(self, tree):
        """Számítógép szerkesztése."""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Figyelmeztetés", "Válassz ki egy számítógépet!")
            return

        item = tree.item(selected[0])
        computer_id = item['values'][0]
        computer = self.db.get_computer_by_id(computer_id)
        if not computer:
            messagebox.showerror("Hiba", "Számítógép nem található!")
            return

        dialog = tk.Toplevel(self)
        dialog.title(f"Szerkesztés: {computer.get('asset_tag')}")
        dialog.transient(self)
        dialog.grab_set()

        form = ttk.Frame(dialog, padding=10)
        form.pack(fill=tk.BOTH, expand=True)

        fields = [
            ("asset_tag", "Leltári szám:", computer.get("asset_tag")),
            ("name", "Név:", computer.get("name")),
            ("manufacturer", "Gyártó:", computer.get("manufacturer", "")),
            ("model", "Modell:", computer.get("model", "")),
            ("serial_number", "Sorozatszám:", computer.get("serial_number", "")),
            ("processor", "Processzor:", computer.get("processor", "")),
            ("ram", "RAM:", computer.get("ram", "")),
            ("storage", "Tárhely:", computer.get("storage", "")),
            ("operating_system", "Operációs rendszer:", computer.get("operating_system", "")),
            ("purchase_date", "Vételi dátum:", computer.get("purchase_date", "")),
            ("status", "Státusz:", computer.get("status", "Elérhető")),
            ("notes", "Megjegyzés:", computer.get("notes", "")),
        ]

        entries = {}
        for i, (field, label, default) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=i, column=0, sticky=tk.W, pady=2)
            if field == "status":
                combo = ttk.Combobox(form, values=["Elérhető", "Használatban", "Javítás alatt", "Selejtezett"])
                combo.grid(row=i, column=1, sticky=tk.EW, pady=2, padx=5)
                combo.set(default)
                entries[field] = combo
            else:
                entry = ttk.Entry(form)
                entry.grid(row=i, column=1, sticky=tk.EW, pady=2, padx=5)
                entry.insert(0, default)
                entries[field] = entry

        def save():
            updates = {}
            for field, widget in entries.items():
                value = widget.get() if isinstance(widget, ttk.Entry) else widget.get()
                if value:
                    updates[field] = value

            if not updates.get("asset_tag") or not updates.get("name"):
                messagebox.showerror("Hiba", "A leltári szám és a név kötelező!")
                return

            if updates.get("purchase_date") and not GZ_validate_date(updates.get("purchase_date")):
                messagebox.showerror("Hiba", "Érvénytelen dátum formátum!")
                return

            updates["id"] = computer_id
            try:
                # TODO: update_computer metódus implementálása
                messagebox.showinfo("Siker", "Számítógép sikeresen frissítve!")
                dialog.destroy()
                if self.current_view:
                    for widget in self.current_view.winfo_children():
                        if isinstance(widget, ttk.Treeview):
                            self.load_computers_table(widget)
                            break
            except Exception as e:
                messagebox.showerror("Hiba", str(e))

        button_frame = ttk.Frame(form)
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)
        ttk.Button(button_frame, text="Mentés", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Mégse", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def assign_computer_from_table(self, tree):
        """Számítógép kiadása a táblázatból."""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Figyelmeztetés", "Válassz ki egy számítógépet!")
            return

        item = tree.item(selected[0])
        computer_id = item['values'][0]
        computer = self.db.get_computer_by_id(computer_id)

        if computer.get("status") != "Elérhető":
            messagebox.showwarning("Figyelmeztetés", f"Ez a gép nem elérhető (státusz: {computer.get('status')})!")
            return

        self.show_assign_dialog(computer_id)

    def show_assign_dialog(self, computer_id):
        """Kiadás dialógus."""
        computer = self.db.get_computer_by_id(computer_id)
        users = self.db.list_users()

        if not users:
            messagebox.showwarning("Figyelmeztetés", "Nincsenek felhasználók az adatbázisban!")
            return

        dialog = tk.Toplevel(self)
        dialog.title(f"Kiadás: {computer.get('asset_tag')}")
        dialog.transient(self)
        dialog.grab_set()

        form = ttk.Frame(dialog, padding=10)
        form.pack(fill=tk.BOTH, expand=True)

        ttk.Label(form, text=f"Számítógép: {computer.get('asset_tag')} - {computer.get('name')}").grid(row=0, column=0, columnspan=2, pady=5)

        ttk.Label(form, text="Felhasználó:").grid(row=1, column=0, sticky=tk.W, pady=2)
        user_combo = ttk.Combobox(form, values=[f"{u['id']}: {u['name']} ({u.get('department', '')})" for u in users])
        user_combo.grid(row=1, column=1, sticky=tk.EW, pady=2, padx=5)

        ttk.Label(form, text="Kiadás dátuma:").grid(row=2, column=0, sticky=tk.W, pady=2)
        date_entry = ttk.Entry(form)
        date_entry.grid(row=2, column=1, sticky=tk.EW, pady=2, padx=5)
        date_entry.insert(0, GZ_today())

        def save():
            user_str = user_combo.get()
            if not user_str:
                messagebox.showerror("Hiba", "Válassz felhasználót!")
                return

            user_id = int(user_str.split(":")[0])
            assigned_at = date_entry.get()

            if not GZ_validate_date(assigned_at):
                messagebox.showerror("Hiba", "Érvénytelen dátum!")
                return

            try:
                self.db.assign_computer(computer_id, user_id, assigned_at)
                messagebox.showinfo("Siker", "Számítógép sikeresen kiadva!")
                dialog.destroy()
                if self.current_view:
                    for widget in self.current_view.winfo_children():
                        if isinstance(widget, ttk.Treeview):
                            self.load_computers_table(widget)
                            break
            except Exception as e:
                messagebox.showerror("Hiba", str(e))

        button_frame = ttk.Frame(form)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(button_frame, text="Kiadás", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Mégse", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def dispose_computer_from_table(self, tree):
        """Számítógép selejtezése a táblázatból."""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Figyelmeztetés", "Válassz ki egy számítógépet!")
            return

        item = tree.item(selected[0])
        computer_id = item['values'][0]
        computer = self.db.get_computer_by_id(computer_id)

        if computer.get("status") != "Elérhető":
            messagebox.showwarning("Figyelmeztetés", f"Csak elérhető gépeket lehet selejtezni (státusz: {computer.get('status')})!")
            return

        self.show_dispose_dialog(computer_id)

    def show_dispose_dialog(self, computer_id):
        """Selejtezés dialógus."""
        computer = self.db.get_computer_by_id(computer_id)

        dialog = tk.Toplevel(self)
        dialog.title(f"Selejtezés: {computer.get('asset_tag')}")
        dialog.transient(self)
        dialog.grab_set()

        form = ttk.Frame(dialog, padding=10)
        form.pack(fill=tk.BOTH, expand=True)

        ttk.Label(form, text=f"Számítógép: {computer.get('asset_tag')} - {computer.get('name')}").grid(row=0, column=0, columnspan=2, pady=5)

        ttk.Label(form, text="Selejtezés oka:").grid(row=1, column=0, sticky=tk.W, pady=2)
        reason_entry = ttk.Entry(form)
        reason_entry.grid(row=1, column=1, sticky=tk.EW, pady=2, padx=5)

        ttk.Label(form, text="Selejtezés dátuma:").grid(row=2, column=0, sticky=tk.W, pady=2)
        date_entry = ttk.Entry(form)
        date_entry.grid(row=2, column=1, sticky=tk.EW, pady=2, padx=5)
        date_entry.insert(0, GZ_today())

        ttk.Label(form, text="Megjegyzés:").grid(row=3, column=0, sticky=tk.W, pady=2)
        notes_entry = ttk.Entry(form)
        notes_entry.grid(row=3, column=1, sticky=tk.EW, pady=2, padx=5)

        def save():
            reason = reason_entry.get()
            disposal_date = date_entry.get()
            notes = notes_entry.get()

            if not reason:
                messagebox.showerror("Hiba", "Az ok megadása kötelező!")
                return

            if not GZ_validate_date(disposal_date):
                messagebox.showerror("Hiba", "Érvénytelen dátum!")
                return

            try:
                self.db.add_disposal(computer_id, disposal_date, reason, notes)
                messagebox.showinfo("Siker", "Számítógép sikeresen selejtezve!")
                dialog.destroy()
                if self.current_view:
                    for widget in self.current_view.winfo_children():
                        if isinstance(widget, ttk.Treeview):
                            self.load_computers_table(widget)
                            break
            except Exception as e:
                messagebox.showerror("Hiba", str(e))

        button_frame = ttk.Frame(form)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        ttk.Button(button_frame, text="Selejtezés", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Mégse", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def show_users_view(self):
        """Felhasználók listázása."""
        self.clear_view()

        frame = ttk.Frame(self.main_frame)
        frame.pack(fill=tk.BOTH, expand=True)
        self.current_view = frame

        # Kereső
        search_frame = ttk.Frame(frame)
        search_frame.pack(fill=tk.X, pady=5)

        ttk.Label(search_frame, text="Keresés:").pack(side=tk.LEFT, padx=5)
        search_entry = ttk.Entry(search_frame, width=30)
        search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        dept_label = ttk.Label(search_frame, text="Osztály:")
        dept_label.pack(side=tk.LEFT, padx=5)
        dept_entry = ttk.Entry(search_frame, width=15)
        dept_entry.pack(side=tk.LEFT, padx=5)

        def refresh_users():
            self.load_users_table(tree, search_entry.get(), dept_entry.get())

        ttk.Button(search_frame, text="Keresés", command=refresh_users).pack(side=tk.LEFT, padx=5)

        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        tree = ttk.Treeview(tree_frame, columns=("id", "name", "department", "email", "phone", "notes"), show="headings")
        tree.heading("id", text="ID", anchor=tk.W)
        tree.heading("name", text="Név", anchor=tk.W)
        tree.heading("department", text="Osztály", anchor=tk.W)
        tree.heading("email", text="Email", anchor=tk.W)
        tree.heading("phone", text="Telefon", anchor=tk.W)
        tree.heading("notes", text="Megjegyzés", anchor=tk.W)

        tree.column("id", width=50)
        tree.column("name", width=150)
        tree.column("department", width=120)
        tree.column("email", width=150)
        tree.column("phone", width=100)
        tree.column("notes", width=200)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=scrollbar.set)

        self.load_users_table(tree, "", "")

        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=5)
        ttk.Button(button_frame, text="Új felhasználó", command=self.show_add_user_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Szerkesztés", command=lambda: self.edit_user(tree)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Törlés", command=lambda: self.delete_user_from_table(tree)).pack(side=tk.LEFT, padx=5)

    def load_users_table(self, tree, search="", department=""):
        """Felhasználók betöltése."""
        for item in tree.get_children():
            tree.delete(item)

        users = self.db.list_users(search=search, department=department)
        for user in users:
            tree.insert("", tk.END, values=(
                user.get("id"),
                user.get("name"),
                user.get("department", ""),
                user.get("email", ""),
                user.get("phone", ""),
                user.get("notes", "")
            ))

    def show_add_user_dialog(self):
        """Új felhasználó hozzáadása."""
        dialog = tk.Toplevel(self)
        dialog.title("Új felhasználó")
        dialog.transient(self)
        dialog.grab_set()

        form = ttk.Frame(dialog, padding=10)
        form.pack(fill=tk.BOTH, expand=True)

        fields = [
            ("name", "Név:", True),
            ("department", "Osztály:", False),
            ("email", "Email:", False),
            ("phone", "Telefon:", False),
            ("notes", "Megjegyzés:", False),
        ]

        entries = {}
        for i, (field, label, required) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=i, column=0, sticky=tk.W, pady=2)
            entry = ttk.Entry(form)
            entry.grid(row=i, column=1, sticky=tk.EW, pady=2, padx=5)
            entries[field] = entry

        def save():
            user = {}
            for field, widget in entries.items():
                value = widget.get()
                if value:
                    user[field] = value

            if not user.get("name"):
                messagebox.showerror("Hiba", "A név kötelező!")
                return

            try:
                self.db.add_user(user)
                messagebox.showinfo("Siker", "Felhasználó sikeresen hozzáadva!")
                dialog.destroy()
                if self.current_view:
                    for widget in self.current_view.winfo_children():
                        if isinstance(widget, ttk.Treeview):
                            self.load_users_table(widget)
                            break
            except Exception as e:
                messagebox.showerror("Hiba", str(e))

        button_frame = ttk.Frame(form)
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)
        ttk.Button(button_frame, text="Mentés", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Mégse", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def edit_user(self, tree):
        """Felhasználó szerkesztése."""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Figyelmeztetés", "Válassz ki egy felhasználót!")
            return

        item = tree.item(selected[0])
        user_id = item['values'][0]
        user = self.db.get_user_by_id(user_id)
        if not user:
            messagebox.showerror("Hiba", "Felhasználó nem található!")
            return

        dialog = tk.Toplevel(self)
        dialog.title(f"Szerkesztés: {user.get('name')}")
        dialog.transient(self)
        dialog.grab_set()

        form = ttk.Frame(dialog, padding=10)
        form.pack(fill=tk.BOTH, expand=True)

        fields = [
            ("name", "Név:", user.get("name", "")),
            ("department", "Osztály:", user.get("department", "")),
            ("email", "Email:", user.get("email", "")),
            ("phone", "Telefon:", user.get("phone", "")),
            ("notes", "Megjegyzés:", user.get("notes", "")),
        ]

        entries = {}
        for i, (field, label, default) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=i, column=0, sticky=tk.W, pady=2)
            entry = ttk.Entry(form)
            entry.grid(row=i, column=1, sticky=tk.EW, pady=2, padx=5)
            entry.insert(0, default)
            entries[field] = entry

        def save():
            updates = {}
            for field, widget in entries.items():
                value = widget.get()
                if value:
                    updates[field] = value

            if not updates.get("name"):
                messagebox.showerror("Hiba", "A név kötelező!")
                return

            try:
                self.db.update_user(user_id, updates)
                messagebox.showinfo("Siker", "Felhasználó sikeresen frissítve!")
                dialog.destroy()
                if self.current_view:
                    for widget in self.current_view.winfo_children():
                        if isinstance(widget, ttk.Treeview):
                            self.load_users_table(widget)
                            break
            except Exception as e:
                messagebox.showerror("Hiba", str(e))

        button_frame = ttk.Frame(form)
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)
        ttk.Button(button_frame, text="Mentés", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Mégse", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def delete_user_from_table(self, tree):
        """Felhasználó törlése."""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Figyelmeztetés", "Válassz ki egy felhasználót!")
            return

        item = tree.item(selected[0])
        user_id = item['values'][0]
        user = self.db.get_user_by_id(user_id)

        if messagebox.askyesno("Törlés", f"Biztosan törölöd a(z) {user.get('name')} felhasználót?"):
            try:
                self.db.delete_user(user_id)
                messagebox.showinfo("Siker", "Felhasználó sikeresen törölve!")
                if self.current_view:
                    for widget in self.current_view.winfo_children():
                        if isinstance(widget, ttk.Treeview):
                            self.load_users_table(widget)
                            break
            except Exception as e:
                messagebox.showerror("Hiba", str(e))

    def show_disposals_view(self):
        """Selejtezések listázása."""
        self.clear_view()

        frame = ttk.Frame(self.main_frame)
        frame.pack(fill=tk.BOTH, expand=True)
        self.current_view = frame

        # Táblázat
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        tree = ttk.Treeview(tree_frame, columns=("id", "computer_id", "asset_tag", "disposal_date", "reason", "notes"), show="headings")
        tree.heading("id", text="ID", anchor=tk.W)
        tree.heading("computer_id", text="Gép ID", anchor=tk.W)
        tree.heading("asset_tag", text="Leltári szám", anchor=tk.W)
        tree.heading("disposal_date", text="Selejtezés dátuma", anchor=tk.W)
        tree.heading("reason", text="Ok", anchor=tk.W)
        tree.heading("notes", text="Megjegyzés", anchor=tk.W)

        tree.column("id", width=50)
        tree.column("computer_id", width=60)
        tree.column("asset_tag", width=100)
        tree.column("disposal_date", width=120)
        tree.column("reason", width=150)
        tree.column("notes", width=200)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=scrollbar.set)

        # Adatok betöltése
        self.load_disposals_table(tree)

    def load_disposals_table(self, tree):
        """Selejtezések betöltése."""
        for item in tree.get_children():
            tree.delete(item)

        disposals = self.db.list_disposals()
        for disposal in disposals:
            computer = self.db.get_computer_by_id(disposal.get("computer_id"))
            asset_tag = computer.get("asset_tag", "Ismeretlen") if computer else "Ismeretlen"
            tree.insert("", tk.END, values=(
                disposal.get("id"),
                disposal.get("computer_id"),
                asset_tag,
                disposal.get("disposal_date"),
                disposal.get("reason", ""),
                disposal.get("notes", "")
            ))

    def show_assignments_view(self, active_only=False):
        """Kiadások listázása."""
        self.clear_view()

        frame = ttk.Frame(self.main_frame)
        frame.pack(fill=tk.BOTH, expand=True)
        self.current_view = frame

        title = "Aktív kiadások" if active_only else "Összes kiadás"
        ttk.Label(frame, text=title, font=('Segoe UI', 12, 'bold')).pack(pady=5)

        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        tree = ttk.Treeview(tree_frame, columns=("id", "computer_id", "asset_tag", "user_id", "user_name", "assigned_at", "returned_at"), show="headings")
        tree.heading("id", text="ID", anchor=tk.W)
        tree.heading("computer_id", text="Gép ID", anchor=tk.W)
        tree.heading("asset_tag", text="Leltári szám", anchor=tk.W)
        tree.heading("user_id", text="Felhasználó ID", anchor=tk.W)
        tree.heading("user_name", text="Felhasználó", anchor=tk.W)
        tree.heading("assigned_at", text="Kiadás dátuma", anchor=tk.W)
        tree.heading("returned_at", text="Visszavétel dátuma", anchor=tk.W)

        tree.column("id", width=50)
        tree.column("computer_id", width=60)
        tree.column("asset_tag", width=100)
        tree.column("user_id", width=80)
        tree.column("user_name", width=150)
        tree.column("assigned_at", width=120)
        tree.column("returned_at", width=120)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=scrollbar.set)

        self.load_assignments_table(tree, active_only)

        if active_only:
            button_frame = ttk.Frame(frame)
            button_frame.pack(fill=tk.X, pady=5)
            ttk.Button(button_frame, text="Visszavétel", command=lambda: self.return_computer_from_table(tree)).pack(side=tk.LEFT, padx=5)

    def load_assignments_table(self, tree, active_only=False):
        """Kiadások betöltése."""
        for item in tree.get_children():
            tree.delete(item)

        assignments = self.db.list_assignments(active_only=active_only)
        for assignment in assignments:
            computer = self.db.get_computer_by_id(assignment.get("computer_id"))
            user = self.db.get_user_by_id(assignment.get("user_id"))

            asset_tag = computer.get("asset_tag", "Ismeretlen") if computer else "Ismeretlen"
            user_name = user.get("name", "Ismeretlen") if user else "Ismeretlen"

            tree.insert("", tk.END, values=(
                assignment.get("id"),
                assignment.get("computer_id"),
                asset_tag,
                assignment.get("user_id"),
                user_name,
                assignment.get("assigned_at"),
                assignment.get("returned_at", "") or ""
            ))

    def return_computer_from_table(self, tree):
        """Számítógép visszavétele a táblázatból."""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Figyelmeztetés", "Válassz ki egy kiadást!")
            return

        item = tree.item(selected[0])
        assignment_id = item['values'][0]

        if messagebox.askyesno("Visszavétel", "Biztosan vissza veszed ezt a számítógépet?"):
            try:
                self.db.return_computer(assignment_id)
                messagebox.showinfo("Siker", "Számítógép sikeresen visszavéve!")
                if self.current_view:
                    for widget in self.current_view.winfo_children():
                        if isinstance(widget, ttk.Treeview):
                            self.load_assignments_table(widget, active_only=True)
                            break
            except Exception as e:
                messagebox.showerror("Hiba", str(e))

if __name__ == "__main__":
    app = GZApp()
    app.mainloop()
