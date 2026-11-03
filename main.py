import tkinter as tk


class GZApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("IT Asset Manager")
        self.geometry("900x600")
        self.minsize(760, 480)
        self.configure(bg="#1e1e2e")


if __name__ == "__main__":
    app = GZApp()
    app.mainloop()
