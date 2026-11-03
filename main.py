import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from GZ_modul import GZDataManager, GZ_today, GZ_validate_date


LIGHT_THEME = False

if LIGHT_THEME:
    BG_PRIMARY = "#f5f6f8"
    BG_SECONDARY = "#ffffff"
    BG_TERTIARY = "#ffffff"
    FG_PRIMARY = "#1f2933"
    FG_SECONDARY = "#6b7280"
    BORDER_COLOR = "#e2e5ea"
    ACCENT_COLOR = "#2563eb"
    HOVER_BG = "#f0f2f5"
    SELECTION_BG = "#e8f0fe"
    ZEBRA_ODD = "#fafbfc"
    ZEBRA_EVEN = "#ffffff"
    STATUS_AVAILABLE = "#10b981"
    STATUS_IN_USE = "#f59e0b"
    STATUS_REPAIR = "#8b5cf6"
    STATUS_DISPOSED = "#ef4444"
    DANGER_COLOR = "#ef4444"
    WARNING_BG = "#fef2f2"
else:
    BG_PRIMARY = "#1f2125"
    BG_SECONDARY = "#292c31"
    BG_TERTIARY = "#292c31"
    FG_PRIMARY = "#e5e7eb"
    FG_SECONDARY = "#9ca3af"
    BORDER_COLOR = "#3a3e45"
    ACCENT_COLOR = "#2563eb"
    HOVER_BG = "#374151"
    SELECTION_BG = "#3b82f6"
    ZEBRA_ODD = "#292c31"
    ZEBRA_EVEN = "#1f2125"
    STATUS_AVAILABLE = "#10b981"
    STATUS_IN_USE = "#f59e0b"
    STATUS_REPAIR = "#8b5cf6"
    STATUS_DISPOSED = "#ef4444"
    DANGER_COLOR = "#ef4444"
    WARNING_BG = "#450a0a"

FONT_NORMAL = ('Segoe UI', 10)
FONT_BOLD = ('Segoe UI', 10, 'bold')
FONT_TITLE = ('Segoe UI', 12, 'bold')

STATUS_MSG_DURATION = 2000

PAD_SMALL = 8
PAD_MEDIUM = 12


class CustomCombobox(tk.Frame):

    def __init__(self, master, values=[], width=15, on_select=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(bg=BG_SECONDARY)

        self.values = values
        self.on_select = on_select
        self.dropdown = None
        self._global_bind_id = None
        self._window_bind_id = None
        self.selected_value = tk.StringVar()
        self.entry = tk.Entry(
            self,
            textvariable=self.selected_value,
            bg=BG_TERTIARY,
            fg=FG_PRIMARY,
            insertbackground=FG_PRIMARY,
            font=FONT_NORMAL,
            bd=1,
            relief=tk.SOLID,
            highlightthickness=0,
            highlightbackground=BORDER_COLOR
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.button = CustomButton(
            self,
            text="▼",
            is_primary=False,
            is_danger=False,
            width=2,
            command=self.toggle_dropdown
        )
        self.button.pack(side=tk.RIGHT)

        self.entry.bind("<FocusIn>", lambda e: self.highlight_border())
        self.entry.bind("<FocusOut>", lambda e: self.normal_border())
        self.entry.bind("<KeyRelease>", lambda e: self.on_key_release())
        self.entry.bind("<Down>", lambda e: self.open_dropdown(self.values))
        self.entry.bind("<Escape>", lambda e: self.close_dropdown())

    def highlight_border(self):
        self.entry.config(bd=1, highlightbackground=ACCENT_COLOR, highlightthickness=1)

    def normal_border(self):
        self.entry.config(bd=1, highlightbackground=BORDER_COLOR, highlightthickness=0)

    def on_key_release(self, event=None):
        current_text = self.selected_value.get()
        if not current_text:
            self.close_dropdown()
            return
        matching = [v for v in self.values if current_text.lower() in v.lower()]
        if matching:
            self.open_dropdown(matching)
        else:
            self.close_dropdown()

    def _dropdown_item(self, parent, value):
        btn = tk.Button(
            parent,
            text=value,
            bg=BG_SECONDARY,
            fg=FG_PRIMARY,
            activebackground=HOVER_BG,
            activeforeground=FG_PRIMARY,
            bd=0,
            relief=tk.FLAT,
            font=FONT_NORMAL,
            anchor=tk.W,
            justify=tk.LEFT,
            command=lambda v=value: self.select_value(v)
        )
        btn.pack(fill=tk.X, padx=0, pady=0)
        btn.bind("<Enter>", lambda e, b=btn: b.config(bg=HOVER_BG))
        btn.bind("<Leave>", lambda e, b=btn: b.config(bg=BG_SECONDARY))

    def open_dropdown(self, values=None):
        if values is None:
            values = self.values
        self.close_dropdown()
        if not values:
            return

        dropdown = tk.Toplevel(self)
        dropdown.wm_overrideredirect(True)
        dropdown.wm_attributes("-topmost", True)
        dropdown.configure(bg=BG_SECONDARY, bd=1, relief=tk.SOLID)

        for value in values:
            self._dropdown_item(dropdown, value)

        x = self.entry.winfo_rootx()
        y = self.entry.winfo_rooty() + self.entry.winfo_height()
        dropdown.geometry(f"+{x}+{y}")
        dropdown.deiconify()
        dropdown.update_idletasks()
        width = max(self.entry.winfo_width() or 150, dropdown.winfo_reqwidth())
        dropdown.geometry(f"{width}x{dropdown.winfo_reqheight()}+{x}+{y}")
        dropdown.lift()

        self.dropdown = dropdown

        self._global_bind_id = self.winfo_toplevel().bind("<Button-1>", self._on_global_click, add="+")
        self._window_bind_id = self.winfo_toplevel().bind("<Configure>", self._on_window_configure, add="+")

    def _on_window_configure(self, event=None):
        dropdown = self.dropdown
        if not dropdown or not dropdown.winfo_exists():
            return
        try:
            if not self.entry.winfo_ismapped():
                self.close_dropdown()
                return
            x = self.entry.winfo_rootx()
            y = self.entry.winfo_rooty() + self.entry.winfo_height()
            width = max(self.entry.winfo_width() or 150, dropdown.winfo_reqwidth())
            dropdown.geometry(f"{width}x{dropdown.winfo_reqheight()}+{x}+{y}")
        except tk.TclError:
            self.close_dropdown()

    def _on_global_click(self, event):
        if not self.dropdown:
            return
        widget = str(event.widget)
        if widget.startswith(str(self.dropdown)) or widget.startswith(str(self)):
            return
        self.close_dropdown()

    def toggle_dropdown(self, event=None):
        if self.dropdown and self.dropdown.winfo_exists():
            self.close_dropdown()
        else:
            self.open_dropdown(self.values)

    def close_dropdown(self):
        if self._global_bind_id:
            try:
                self.winfo_toplevel().unbind("<Button-1>", self._global_bind_id)
            except Exception:
                pass
            self._global_bind_id = None
        if self._window_bind_id:
            try:
                self.winfo_toplevel().unbind("<Configure>", self._window_bind_id)
            except Exception:
                pass
            self._window_bind_id = None
        if self.dropdown and self.dropdown.winfo_exists():
            self.dropdown.destroy()
        self.dropdown = None

    def select_value(self, value):
        self.close_dropdown()
        self.selected_value.set(value)
        if self.on_select:
            self.on_select()

    def get(self):
        return self.selected_value.get()

    def set(self, value):
        self.selected_value.set(value)


class CustomButton(tk.Button):

    def __init__(self, master, text="", is_primary=True, is_danger=False, **kwargs):
        self.is_primary = is_primary
        self.is_danger = is_danger

        if is_primary:
            bg = ACCENT_COLOR
            fg = "white"
            active_bg = "#1d4ed8"
            border_color = ACCENT_COLOR
            relief_type = tk.RAISED
        elif is_danger:
            bg = BG_SECONDARY
            fg = DANGER_COLOR
            active_bg = WARNING_BG
            border_color = DANGER_COLOR
            relief_type = tk.RAISED
        else:
            bg = BG_SECONDARY
            fg = FG_PRIMARY
            active_bg = HOVER_BG
            border_color = BORDER_COLOR
            relief_type = tk.RAISED

        super().__init__(
            master,
            text=text,
            bg=bg,
            fg=fg,
            activebackground=active_bg,
            activeforeground=fg,
            bd=1,
            relief=relief_type,
            highlightthickness=0,
            highlightbackground=border_color,
            font=FONT_NORMAL,
            **kwargs
        )

        self.default_bg = bg
        self.hover_bg = active_bg
        self.default_fg = fg
        self.default_border = border_color

        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        self.config(bg=self.hover_bg, relief=tk.SUNKEN)

    def on_leave(self, event):
        self.config(bg=self.default_bg, relief=self.default_relief if hasattr(self, 'default_relief') else tk.RAISED)


class CustomMenuBar(tk.Frame):

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(bg=BG_SECONDARY, padx=PAD_MEDIUM, pady=PAD_SMALL)

        self.menu_items = []
        self.active_menu = None
        self._menu_bind_id = None
        self._menu_window_bind_id = None

    def add_menu(self, label, items):
        menu_btn = CustomButton(self, text=label, is_primary=False, is_danger=False)
        menu_btn.pack(side=tk.LEFT, padx=(0, PAD_MEDIUM))
        menu_btn.bind("<Enter>", lambda e: self.highlight_menu(menu_btn))
        menu_btn.bind("<Leave>", lambda e: self.unhighlight_menu())
        menu_btn.bind("<Button-1>", lambda e: self.toggle_menu(menu_btn, items))

        self.menu_items.append({
            "button": menu_btn,
            "label": label,
            "items": items,
            "dropdown": None
        })

    def highlight_menu(self, btn):
        self.unhighlight_menu()
        btn.config(bg=HOVER_BG)

    def unhighlight_menu(self):
        for item in self.menu_items:
            item["button"].config(bg=BG_SECONDARY)

    def toggle_menu(self, btn, items):
        if self.active_menu and self.active_menu != btn:
            self.close_all_menus()

        for item in self.menu_items:
            if item["button"] == btn:
                if item["dropdown"] and item["dropdown"].winfo_exists():
                    self.close_all_menus()
                else:
                    self.close_all_menus()
                    self.create_dropdown(item, btn)
                    self.active_menu = btn
                break

    def create_dropdown(self, menu_item, parent_btn):
        self.close_all_menus()

        dropdown = tk.Toplevel(self)
        dropdown.wm_overrideredirect(True)
        dropdown.wm_attributes("-topmost", True)
        dropdown.configure(bg=BG_SECONDARY, bd=1, relief=tk.SOLID)

        for label, cmd in menu_item["items"]:
            if label == "":
                sep = tk.Frame(dropdown, bg=BORDER_COLOR, height=2)
                sep.pack(fill=tk.X, padx=PAD_MEDIUM, pady=2)
                continue
            btn = CustomButton(dropdown, text=label, is_primary=False, is_danger=False, padx=PAD_MEDIUM, anchor="w", justify=tk.LEFT)
            btn.pack(fill=tk.X, padx=2, pady=2)
            btn.bind("<Button-1>", lambda e, c=cmd: self.execute_and_close(c))

        x = parent_btn.winfo_rootx()
        y = parent_btn.winfo_rooty() + parent_btn.winfo_height()
        dropdown.geometry(f"+{x}+{y}")
        dropdown.deiconify()
        dropdown.update_idletasks()
        dropdown.geometry(f"{dropdown.winfo_reqwidth()}x{dropdown.winfo_reqheight()}+{x}+{y}")
        dropdown.lift()

        menu_item["dropdown"] = dropdown

        self._menu_bind_id = self.winfo_toplevel().bind("<Button-1>", self._on_global_click, add="+")
        self._menu_window_bind_id = self.winfo_toplevel().bind("<Configure>", self._on_window_configure, add="+")

    def _on_window_configure(self, event=None):
        for item in self.menu_items:
            dropdown = item.get("dropdown")
            if not (dropdown and dropdown.winfo_exists()):
                continue
            try:
                btn = item["button"]
                if not btn.winfo_ismapped():
                    self.close_all_menus()
                    return
                x = btn.winfo_rootx()
                y = btn.winfo_rooty() + btn.winfo_height()
                dropdown.geometry(f"{dropdown.winfo_reqwidth()}x{dropdown.winfo_reqheight()}+{x}+{y}")
            except tk.TclError:
                self.close_all_menus()
                return

    def _on_global_click(self, event):
        widget = str(event.widget)
        if widget.startswith(str(self)):
            return
        self.close_all_menus()

    def execute_and_close(self, cmd):
        self.close_all_menus()
        if cmd:
            cmd()

    def close_all_menus(self):
        if self._menu_bind_id:
            try:
                self.winfo_toplevel().unbind("<Button-1>", self._menu_bind_id)
            except Exception:
                pass
            self._menu_bind_id = None
        if self._menu_window_bind_id:
            try:
                self.winfo_toplevel().unbind("<Configure>", self._menu_window_bind_id)
            except Exception:
                pass
            self._menu_window_bind_id = None
        for item in self.menu_items:
            if item["dropdown"] and item["dropdown"].winfo_exists():
                item["dropdown"].destroy()
            item["dropdown"] = None
        self.active_menu = None


class StatusBar(tk.Frame):

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(bg=BG_SECONDARY, height=30, padx=PAD_MEDIUM, pady=PAD_SMALL)

        self.status_label = tk.Label(self, text="", bg=BG_SECONDARY, fg=FG_SECONDARY, font=FONT_NORMAL)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def show_message(self, text, is_error=False):
        self.status_label.configure(text=text)
        if is_error:
            self.status_label.configure(fg=DANGER_COLOR)
        else:
            self.status_label.configure(fg=FG_PRIMARY)

        self.after(STATUS_MSG_DURATION, lambda: self.status_label.configure(text="", fg=FG_SECONDARY))


class GZApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("IT Asset Manager")
        self.geometry("1000x700")
        self.minsize(800, 500)
        self.configure(bg=BG_PRIMARY)

        self.db = GZDataManager()

        self.configure_theme()

        self.main_container = tk.Frame(self, bg=BG_PRIMARY)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        self.create_menu_bar()

        self.content_frame = tk.Frame(self.main_container, bg=BG_SECONDARY)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=PAD_MEDIUM, pady=PAD_MEDIUM)

        self.current_view = None
        self.computers_tree = None
        self.computers_search_entry = None
        self.computers_status_combo = None

        self.status_bar = StatusBar(self.main_container)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        self.show_computers_view()

    def configure_theme(self):
        style = ttk.Style()
        style.theme_use('clam')

        style.configure('.', background=BG_SECONDARY, foreground=FG_PRIMARY, font=FONT_NORMAL)
        style.configure('TFrame', background=BG_SECONDARY)
        style.configure('TLabel', background=BG_SECONDARY, foreground=FG_PRIMARY, font=FONT_NORMAL)
        style.configure('Header.TLabel', background=BG_SECONDARY, foreground=FG_PRIMARY, font=FONT_TITLE)

        style.configure('Treeview',
            background=BG_TERTIARY, foreground=FG_PRIMARY,
            fieldbackground=BG_TERTIARY,
            borderwidth=0, font=FONT_NORMAL,
            rowheight=30)
        style.configure('Treeview.Heading',
            background=BG_SECONDARY, foreground=FG_PRIMARY,
            font=FONT_BOLD, borderwidth=0,
            relief=tk.FLAT)
        style.map('Treeview',
            background=[("selected", SELECTION_BG)],
            foreground=[("selected", FG_PRIMARY)])
        style.map('Treeview.Heading',
            background=[("active", BG_SECONDARY), ("hover", BG_SECONDARY), ("pressed", BG_SECONDARY)],
            foreground=[("active", FG_PRIMARY), ("hover", FG_PRIMARY), ("pressed", FG_PRIMARY)],
            relief=[("pressed", tk.FLAT), ("active", tk.FLAT)])

        style.configure('TScrollbar',
            background=BG_SECONDARY, troughcolor=BG_TERTIARY,
            bordercolor=BG_SECONDARY, arrowcolor=FG_SECONDARY)
        style.map('TScrollbar',
            background=[("active", HOVER_BG), ("hover", HOVER_BG), ("pressed", SELECTION_BG)],
            arrowcolor=[("active", FG_PRIMARY), ("pressed", FG_PRIMARY)])

    def create_menu_bar(self):
        self.menu_bar = CustomMenuBar(self.main_container)
        self.menu_bar.pack(fill=tk.X, side=tk.TOP)

        self.menu_bar.add_menu("Számítógépek", [
            ("Számítógépek listája", self.show_computers_view),
            ("Új számítógép", self.show_add_computer_dialog),
            ("", None),
            ("Selejtezések", self.show_disposals_view),
        ])

        self.menu_bar.add_menu("Kiadások", [
            ("Aktív kiadások", lambda: self.show_assignments_view(active_only=True)),
            ("Összes kiadás", lambda: self.show_assignments_view(active_only=False)),
        ])

    def clear_view(self):
        if self.current_view:
            self.current_view.destroy()
            self.current_view = None

    def generate_random_data(self, tree):
        import random
        from datetime import datetime, timedelta

        manufacturers = ["Dell", "HP", "Lenovo", "Asus", "Acer", "MSI"]
        models = ["OptiPlex", "EliteDesk", "ThinkCentre", "ProDesk", "Vivo", "Precision"]
        processors = ["Intel i3", "Intel i5", "Intel i7", "Intel i9", "AMD Ryzen 5", "AMD Ryzen 7"]
        statuses = ["Elérhető", "Használatban", "Javítás alatt"]
        os_list = ["Windows 10", "Windows 11", "Ubuntu 22.04", "Linux Mint", "Debian"]

        existing_tags = {comp.get("asset_tag") for comp in self.db.list_computers()}
        added = 0
        attempts = 0
        while added < 10 and attempts < 100:
            attempts += 1
            asset_tag = f"PC-{random.randint(100, 999):03d}"
            if asset_tag in existing_tags:
                continue

            purchase_date = (datetime.now() - timedelta(days=random.randint(30, 365*5))).strftime("%Y-%m-%d")
            status = random.choice(statuses)
            notes = random.choice(["", "Jó állapot", "Garancia alatt", "Frissítve", "Régóta szolgálatban"])

            computer = {
                "asset_tag": asset_tag,
                "name": f"Gép {random.randint(1, 100)}",
                "manufacturer": random.choice(manufacturers),
                "model": random.choice(models),
                "serial_number": f"S{random.randint(100000, 999999)}",
                "processor": random.choice(processors),
                "ram": f"{random.choice([4, 8, 16, 32, 64])}GB",
                "storage": f"{random.choice([128, 256, 512, 1024])}GB SSD",
                "operating_system": random.choice(os_list),
                "purchase_date": purchase_date,
                "status": status,
                "notes": notes
            }

            try:
                self.db.add_computer(computer)
                existing_tags.add(asset_tag)
                added += 1
            except ValueError as e:
                self.status_bar.show_message(f"Érvénytelen tesztadat: {e}", is_error=True)
            except sqlite3.Error as e:
                self.status_bar.show_message(f"Adatbázis-hiba a tesztgép felvételekor: {e}", is_error=True)

        self.load_computers_table(tree)
        if added == 10:
            self.status_bar.show_message("10 random számítógép hozzáadva!")
        elif added:
            self.status_bar.show_message(f"{added}/10 tesztgép felvéve – a többi nem fért bele a próbálkozások száma miatt (leltári szám készlet fogytán).", is_error=True)
        else:
            self.status_bar.show_message("Nem sikerült tesztgépet felvenni! Lehet, hogy kimerült a leltári szám készlet.", is_error=True)

    def show_computers_view(self):
        self.clear_view()

        frame = tk.Frame(self.content_frame, bg=BG_SECONDARY)
        frame.pack(fill=tk.BOTH, expand=True)
        self.current_view = frame

        header = tk.Frame(frame, bg=BG_SECONDARY)
        header.pack(fill=tk.X, pady=(0, PAD_MEDIUM))
        ttk.Label(header, text="Számítógépek", style="Header.TLabel").pack(side=tk.LEFT)

        search_frame = tk.Frame(frame, bg=BG_SECONDARY)
        search_frame.pack(fill=tk.X, pady=(0, PAD_MEDIUM))

        search_label = ttk.Label(search_frame, text="Keresés:")
        search_label.pack(side=tk.LEFT, padx=(0, PAD_SMALL))

        search_entry = ttk.Entry(search_frame, width=30)
        search_entry.pack(side=tk.LEFT, padx=(0, PAD_MEDIUM), fill=tk.X, expand=True)
        search_entry.insert(0, "Keresés név vagy leltári szám alapján...")
        search_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(search_entry, "Keresés név vagy leltári szám alapján..."))
        search_entry.bind("<FocusOut>", lambda e: self.restore_placeholder(search_entry, "Keresés név vagy leltári szám alapján..."))

        status_label = ttk.Label(search_frame, text="Státusz:")
        status_label.pack(side=tk.LEFT, padx=(0, PAD_SMALL))

        status_combo = CustomCombobox(
            search_frame,
            values=["Összes", "Elérhető", "Használatban", "Javítás alatt", "Selejtezett"],
            width=15
        )
        status_combo.set("Összes")
        status_combo.pack(side=tk.LEFT, padx=(0, PAD_MEDIUM))

        def refresh():
            self.load_computers_table(
                tree,
                search_entry.get() if search_entry.get() != "Keresés név vagy leltári szám alapján..." else "",
                "" if status_combo.get() == "Összes" else status_combo.get()
            )

        search_entry.bind("<KeyRelease>", lambda e: refresh())
        search_entry.bind("<Return>", lambda e: refresh())
        status_combo.entry.bind("<KeyRelease>", lambda e: refresh())
        status_combo.entry.bind("<Return>", lambda e: refresh())
        status_combo.on_select = refresh

        tree_frame = tk.Frame(frame, bg=BG_SECONDARY)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        tree = ttk.Treeview(tree_frame, columns=("id", "asset_tag", "name", "manufacturer", "model", "processor", "ram", "storage", "os", "purchase_date", "status"), show="headings")

        columns = [
            ("id", "ID", 45),
            ("asset_tag", "Leltári szám", 85),
            ("name", "Név", 110),
            ("manufacturer", "Gyártó", 80),
            ("model", "Modell", 90),
            ("processor", "Processzor", 95),
            ("ram", "RAM", 60),
            ("storage", "Tárhely", 95),
            ("os", "OS", 100),
            ("purchase_date", "Vételi dátum", 95),
            ("status", "Státusz", 110),
        ]

        for col_id, col_text, col_width in columns:
            tree.heading(col_id, text=col_text, anchor=tk.W, command="")
            tree.column(col_id, width=col_width, anchor=tk.W, stretch=False)

        tree.column("status", stretch=True)

        tree.tag_configure("status_available", foreground=STATUS_AVAILABLE)
        tree.tag_configure("status_in_use", foreground=STATUS_IN_USE)
        tree.tag_configure("status_repair", foreground=STATUS_REPAIR)
        tree.tag_configure("status_disposed", foreground=STATUS_DISPOSED)
        tree.tag_configure('odd', background=ZEBRA_ODD)
        tree.tag_configure('even', background=ZEBRA_EVEN)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        hscrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        hscrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        tree.configure(yscrollcommand=scrollbar.set, xscrollcommand=hscrollbar.set)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.load_computers_table(tree, "", "")

        button_frame = tk.Frame(frame, bg=BG_SECONDARY)
        button_frame.pack(fill=tk.X, pady=(PAD_MEDIUM, 0))

        CustomButton(button_frame, text="Random adatok", is_primary=True, command=lambda: self.generate_random_data(tree)).pack(side=tk.LEFT, padx=(0, PAD_SMALL))
        CustomButton(button_frame, text="Új számítógép", is_primary=True, command=self.show_add_computer_dialog).pack(side=tk.LEFT, padx=PAD_SMALL)
        CustomButton(button_frame, text="Szerkesztés", is_primary=False, command=lambda: self.edit_computer(tree)).pack(side=tk.LEFT, padx=PAD_SMALL)
        CustomButton(button_frame, text="Kiadás", is_primary=False, command=lambda: self.assign_computer_from_table(tree)).pack(side=tk.LEFT, padx=PAD_SMALL)
        CustomButton(button_frame, text="Selejtezés", is_primary=False, is_danger=True, command=lambda: self.dispose_computer_from_table(tree)).pack(side=tk.LEFT, padx=PAD_SMALL)

        tree.bind("<Double-1>", lambda e: self.edit_computer(tree))

        self.computers_tree = tree
        self.computers_search_entry = search_entry
        self.computers_status_combo = status_combo

    def clear_placeholder(self, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)

    def restore_placeholder(self, entry, placeholder):
        if entry.get() == "":
            entry.insert(0, placeholder)

    STATUS_TAGS = {
        "Elérhető": "status_available",
        "Használatban": "status_in_use",
        "Javítás alatt": "status_repair",
        "Selejtezett": "status_disposed",
    }

    def load_computers_table(self, tree, search="", status_filter=""):
        for item in tree.get_children():
            tree.delete(item)

        computers = self.db.list_computers(search=search, status=status_filter)
        for i, comp in enumerate(computers):
            tag = 'odd' if i % 2 else 'even'
            comp_status = comp.get("status", "Elérhető")
            tags = (tag, self.STATUS_TAGS.get(comp_status, tag))

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
                comp_status,
            ), tags=tags)

    def refresh_computers_view(self):
        if not (self.computers_tree and self.computers_tree.winfo_exists()):
            return
        search = self.computers_search_entry.get()
        if search == "Keresés név vagy leltári szám alapján...":
            search = ""
        status = self.computers_status_combo.get() if self.computers_status_combo else ""
        status = "" if status == "Összes" else status
        self.load_computers_table(self.computers_tree, search, status)

    def show_add_computer_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Új számítógép")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(bg=BG_SECONDARY, padx=PAD_MEDIUM, pady=PAD_MEDIUM)

        form = tk.Frame(dialog, bg=BG_SECONDARY)
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
            ("notes", "Megjegyzés:", False),
        ]

        entries = {}
        for i, (field, label, required) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=i, column=0, sticky=tk.W, pady=PAD_SMALL, padx=PAD_SMALL)
            entry = ttk.Entry(form)
            entry.grid(row=i, column=1, sticky=tk.EW, pady=PAD_SMALL, padx=PAD_SMALL)
            entries[field] = entry

        button_frame = tk.Frame(form, bg=BG_SECONDARY)
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=PAD_MEDIUM)

        def save():
            computer = {}
            for field, widget in entries.items():
                value = widget.get()
                if value:
                    computer[field] = value

            if not computer.get("asset_tag") or not computer.get("name"):
                self.status_bar.show_message("A leltári szám és a név kötelező!", is_error=True)
                return

            if computer.get("purchase_date") and not GZ_validate_date(computer.get("purchase_date")):
                self.status_bar.show_message("Érvénytelen dátum formátum! YYYY-MM-DD", is_error=True)
                return

            try:
                self.db.add_computer(computer)
                self.status_bar.show_message("Számítógép sikeresen hozzáadva!")
                dialog.destroy()
                self.refresh_computers_view()
            except Exception as e:
                self.status_bar.show_message(f"Hiba: {str(e)}", is_error=True)

        CustomButton(button_frame, text="Mentés", is_primary=True, command=save).pack(side=tk.LEFT, padx=PAD_SMALL)
        CustomButton(button_frame, text="Mégse", is_primary=False, command=dialog.destroy).pack(side=tk.LEFT, padx=PAD_SMALL)

    def edit_computer(self, tree):
        selected = tree.selection()
        if not selected:
            self.status_bar.show_message("Válassz ki egy számítógépet!", is_error=True)
            return

        item = tree.item(selected[0])
        computer_id = item['values'][0]
        computer = self.db.get_computer_by_id(computer_id)
        if not computer:
            self.status_bar.show_message("Számítógép nem található!", is_error=True)
            return

        dialog = tk.Toplevel(self)
        dialog.title(f"Szerkesztés: {computer.get('asset_tag')}")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(bg=BG_SECONDARY, padx=PAD_MEDIUM, pady=PAD_MEDIUM)

        form = tk.Frame(dialog, bg=BG_SECONDARY)
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
            ("notes", "Megjegyzés:", computer.get("notes", "")),
        ]

        entries = {}
        for i, (field, label, default) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=i, column=0, sticky=tk.W, pady=PAD_SMALL, padx=PAD_SMALL)
            entry = ttk.Entry(form)
            entry.grid(row=i, column=1, sticky=tk.EW, pady=PAD_SMALL, padx=PAD_SMALL)
            entry.insert(0, default)
            entries[field] = entry

        def save():
            updates = {}
            for field, widget in entries.items():
                updates[field] = widget.get()

            if not updates.get("asset_tag") or not updates.get("name"):
                self.status_bar.show_message("A leltári szám és a név kötelező!", is_error=True)
                return

            if updates.get("purchase_date") and not GZ_validate_date(updates.get("purchase_date")):
                self.status_bar.show_message("Érvénytelen dátum!", is_error=True)
                return

            try:
                self.db.update_computer(computer_id, updates)
                self.status_bar.show_message("Számítógép sikeresen frissítve!")
                dialog.destroy()
                self.refresh_computers_view()
            except Exception as e:
                self.status_bar.show_message(f"Hiba: {str(e)}", is_error=True)

        button_frame = tk.Frame(form, bg=BG_SECONDARY)
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=PAD_MEDIUM)
        CustomButton(button_frame, text="Mentés", is_primary=True, command=save).pack(side=tk.LEFT, padx=PAD_SMALL)
        CustomButton(button_frame, text="Mégse", is_primary=False, command=dialog.destroy).pack(side=tk.LEFT, padx=PAD_SMALL)

    def assign_computer_from_table(self, tree):
        selected = tree.selection()
        if not selected:
            self.status_bar.show_message("Válassz ki egy számítógépet!", is_error=True)
            return

        item = tree.item(selected[0])
        computer_id = item['values'][0]
        computer = self.db.get_computer_by_id(computer_id)

        if computer.get("status") != "Elérhető":
            self.status_bar.show_message(f"Ez a gép nem elérhető (státusz: {computer.get('status')})!", is_error=True)
            return

        self.show_assign_dialog(computer_id)

    def show_assign_dialog(self, computer_id):
        computer = self.db.get_computer_by_id(computer_id)

        dialog = tk.Toplevel(self)
        dialog.title(f"Kiadás: {computer.get('asset_tag')}")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(bg=BG_SECONDARY, padx=PAD_MEDIUM, pady=PAD_MEDIUM)

        form = tk.Frame(dialog, bg=BG_SECONDARY)
        form.pack(fill=tk.BOTH, expand=True)

        ttk.Label(form, text=f"Számítógép: {computer.get('asset_tag')} - {computer.get('name')}", font=FONT_BOLD).grid(row=0, column=0, columnspan=2, pady=PAD_MEDIUM)

        ttk.Label(form, text="Felhasználó név:").grid(row=1, column=0, sticky=tk.W, pady=PAD_SMALL, padx=PAD_SMALL)
        user_entry = ttk.Entry(form)
        user_entry.grid(row=1, column=1, sticky=tk.EW, pady=PAD_SMALL, padx=PAD_SMALL)
        user_entry.insert(0, "Felhasználó név (pl: Nagy Péter)")
        user_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(user_entry, "Felhasználó név (pl: Nagy Péter)"))
        user_entry.bind("<FocusOut>", lambda e: self.restore_placeholder(user_entry, "Felhasználó név (pl: Nagy Péter)"))

        ttk.Label(form, text="Kiadás dátuma:").grid(row=2, column=0, sticky=tk.W, pady=PAD_SMALL, padx=PAD_SMALL)
        date_entry = ttk.Entry(form)
        date_entry.grid(row=2, column=1, sticky=tk.EW, pady=PAD_SMALL, padx=PAD_SMALL)
        date_entry.insert(0, GZ_today())

        def save():
            user_name = user_entry.get()
            if not user_name or user_name == "Felhasználó név (pl: Nagy Péter)":
                self.status_bar.show_message("Adja meg a felhasználó nevét!", is_error=True)
                return

            assigned_at = date_entry.get()

            if not GZ_validate_date(assigned_at):
                self.status_bar.show_message("Érvénytelen dátum!", is_error=True)
                return

            try:
                self.db.assign_computer_by_name(computer_id, user_name, assigned_at)
                self.status_bar.show_message("Számítógép sikeresen kiadva!")
                dialog.destroy()
                self.refresh_computers_view()
            except Exception as e:
                self.status_bar.show_message(f"Hiba: {str(e)}", is_error=True)

        button_frame = tk.Frame(form, bg=BG_SECONDARY)
        button_frame.grid(row=3, column=0, columnspan=2, pady=PAD_MEDIUM)
        CustomButton(button_frame, text="Kiadás", is_primary=True, command=save).pack(side=tk.LEFT, padx=PAD_SMALL)
        CustomButton(button_frame, text="Mégse", is_primary=False, command=dialog.destroy).pack(side=tk.LEFT, padx=PAD_SMALL)

    def dispose_computer_from_table(self, tree):
        selected = tree.selection()
        if not selected:
            self.status_bar.show_message("Válassz ki egy számítógépet!", is_error=True)
            return

        item = tree.item(selected[0])
        computer_id = item['values'][0]
        computer = self.db.get_computer_by_id(computer_id)

        if computer.get("status") != "Elérhető":
            self.status_bar.show_message(f"Csak elérhető gépeket lehet selejtezni (státusz: {computer.get('status')})!", is_error=True)
            return

        self.show_dispose_dialog(computer_id)

    def show_dispose_dialog(self, computer_id):
        computer = self.db.get_computer_by_id(computer_id)

        dialog = tk.Toplevel(self)
        dialog.title(f"Selejtezés: {computer.get('asset_tag')}")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(bg=BG_SECONDARY, padx=PAD_MEDIUM, pady=PAD_MEDIUM)

        form = tk.Frame(dialog, bg=BG_SECONDARY)
        form.pack(fill=tk.BOTH, expand=True)

        ttk.Label(form, text=f"Számítógép: {computer.get('asset_tag')} - {computer.get('name')}", font=FONT_BOLD).grid(row=0, column=0, columnspan=2, pady=PAD_MEDIUM)

        ttk.Label(form, text="Selejtezés oka:").grid(row=1, column=0, sticky=tk.W, pady=PAD_SMALL, padx=PAD_SMALL)
        reason_entry = ttk.Entry(form)
        reason_entry.grid(row=1, column=1, sticky=tk.EW, pady=PAD_SMALL, padx=PAD_SMALL)

        ttk.Label(form, text="Selejtezés dátuma:").grid(row=2, column=0, sticky=tk.W, pady=PAD_SMALL, padx=PAD_SMALL)
        date_entry = ttk.Entry(form)
        date_entry.grid(row=2, column=1, sticky=tk.EW, pady=PAD_SMALL, padx=PAD_SMALL)
        date_entry.insert(0, GZ_today())

        ttk.Label(form, text="Megjegyzés:").grid(row=3, column=0, sticky=tk.W, pady=PAD_SMALL, padx=PAD_SMALL)
        notes_entry = ttk.Entry(form)
        notes_entry.grid(row=3, column=1, sticky=tk.EW, pady=PAD_SMALL, padx=PAD_SMALL)

        def save():
            reason = reason_entry.get()
            disposal_date = date_entry.get()
            notes = notes_entry.get()

            if not reason:
                self.status_bar.show_message("Az ok megadása kötelező!", is_error=True)
                return

            if not GZ_validate_date(disposal_date):
                self.status_bar.show_message("Érvénytelen dátum!", is_error=True)
                return

            try:
                self.db.add_disposal(computer_id, disposal_date, reason, notes)
                self.status_bar.show_message("Számítógép sikeresen selejtezve!")
                dialog.destroy()
                self.refresh_computers_view()
            except Exception as e:
                self.status_bar.show_message(f"Hiba: {str(e)}", is_error=True)

        button_frame = tk.Frame(form, bg=BG_SECONDARY)
        button_frame.grid(row=4, column=0, columnspan=2, pady=PAD_MEDIUM)
        CustomButton(button_frame, text="Selejtezés", is_primary=False, is_danger=True, command=save).pack(side=tk.LEFT, padx=PAD_SMALL)
        CustomButton(button_frame, text="Mégse", is_primary=False, command=dialog.destroy).pack(side=tk.LEFT, padx=PAD_SMALL)

    def show_disposals_view(self):
        self.clear_view()

        frame = tk.Frame(self.content_frame, bg=BG_SECONDARY)
        frame.pack(fill=tk.BOTH, expand=True)
        self.current_view = frame

        header = tk.Frame(frame, bg=BG_SECONDARY)
        header.pack(fill=tk.X, pady=(0, PAD_MEDIUM))
        ttk.Label(header, text="Selejtezések", style="Header.TLabel").pack(side=tk.LEFT)

        tree_frame = tk.Frame(frame, bg=BG_SECONDARY)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        tree = ttk.Treeview(tree_frame, columns=("id", "computer_id", "asset_tag", "disposal_date", "reason", "notes"), show="headings")

        columns = [
            ("id", "ID", 50),
            ("computer_id", "Gép ID", 60),
            ("asset_tag", "Leltári szám", 100),
            ("disposal_date", "Selejtezés dátuma", 120),
            ("reason", "Ok", 150),
            ("notes", "Megjegyzés", 200),
        ]

        for col_id, col_text, col_width in columns:
            tree.heading(col_id, text=col_text, anchor=tk.W, command="")
            tree.column(col_id, width=col_width, anchor=tk.W)

        tree.tag_configure('odd', background=ZEBRA_ODD)
        tree.tag_configure('even', background=ZEBRA_EVEN)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=scrollbar.set)

        self.load_disposals_table(tree)

    def load_disposals_table(self, tree):
        for item in tree.get_children():
            tree.delete(item)

        disposals = self.db.list_disposals()
        for i, disposal in enumerate(disposals):
            tag = 'odd' if i % 2 else 'even'
            computer = self.db.get_computer_by_id(disposal.get("computer_id"))
            asset_tag = computer.get("asset_tag", "Ismeretlen") if computer else "Ismeretlen"
            tree.insert("", tk.END, values=(
                disposal.get("id"),
                disposal.get("computer_id"),
                asset_tag,
                disposal.get("disposal_date"),
                disposal.get("reason", ""),
                disposal.get("notes", "")
            ), tags=(tag,))

    def show_assignments_view(self, active_only=False):
        self.clear_view()

        frame = tk.Frame(self.content_frame, bg=BG_SECONDARY)
        frame.pack(fill=tk.BOTH, expand=True)
        self.current_view = frame

        title = "Aktív kiadások" if active_only else "Összes kiadás"
        header = tk.Frame(frame, bg=BG_SECONDARY)
        header.pack(fill=tk.X, pady=(0, PAD_MEDIUM))
        ttk.Label(header, text=title, style="Header.TLabel").pack(side=tk.LEFT)

        tree_frame = tk.Frame(frame, bg=BG_SECONDARY)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        tree = ttk.Treeview(tree_frame, columns=("id", "computer_id", "asset_tag", "user_id", "user_name", "assigned_at", "returned_at"), show="headings")

        columns = [
            ("id", "ID", 50),
            ("computer_id", "Gép ID", 60),
            ("asset_tag", "Leltári szám", 100),
            ("user_id", "Felhasználó ID", 80),
            ("user_name", "Felhasználó", 150),
            ("assigned_at", "Kiadás dátuma", 120),
            ("returned_at", "Visszavétel dátuma", 120),
        ]

        for col_id, col_text, col_width in columns:
            tree.heading(col_id, text=col_text, anchor=tk.W, command="")
            tree.column(col_id, width=col_width, anchor=tk.W)

        tree.tag_configure('odd', background=ZEBRA_ODD)
        tree.tag_configure('even', background=ZEBRA_EVEN)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=scrollbar.set)

        self.load_assignments_table(tree, active_only)

        if active_only:
            button_frame = tk.Frame(frame, bg=BG_SECONDARY)
            button_frame.pack(fill=tk.X, pady=(PAD_MEDIUM, 0))
            CustomButton(button_frame, text="Visszavétel", is_primary=True, command=lambda: self.return_computer_from_table(tree)).pack(side=tk.LEFT, padx=(0, PAD_SMALL))

    def load_assignments_table(self, tree, active_only=False):
        for item in tree.get_children():
            tree.delete(item)

        assignments = self.db.list_assignments(active_only=active_only)
        for i, assignment in enumerate(assignments):
            tag = 'odd' if i % 2 else 'even'
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
            ), tags=(tag,))

    def return_computer_from_table(self, tree):
        selected = tree.selection()
        if not selected:
            self.status_bar.show_message("Válassz ki egy kiadást!", is_error=True)
            return

        item = tree.item(selected[0])
        assignment_id = item['values'][0]

        if messagebox.askyesno("Visszavétel", "Biztosan vissza veszed ezt a számítógépet?"):
            try:
                self.db.return_computer(assignment_id)
                self.status_bar.show_message("Számítógép sikeresen visszavéve!")
                self.load_assignments_table(tree, active_only=True)
                self.refresh_computers_view()
            except Exception as e:
                self.status_bar.show_message(f"Hiba: {str(e)}", is_error=True)


if __name__ == "__main__":
    app = GZApp()
    app.mainloop()
