import tkinter as tk
from tkinter import ttk, messagebox
import csv
from collections import defaultdict

class MainMenuFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Center frame for content
        center_frame = tk.Frame(self)
        center_frame.pack(expand=True, pady=50)
        
        tk.Label(center_frame, text="Yu-Gi-Oh! Limited Tool (Name STILL Pending)", font=("Helvetica", 18)).pack(pady=20)

        button_frame = tk.Frame(center_frame)
        button_frame.pack()
        
        tk.Button(button_frame, text="Collection Manager", 
                 command=lambda: controller.show_frame("CollectionManager"),
                 width=20, height=2).pack(pady=10)
        tk.Button(button_frame, text="Option 2", 
                 command=lambda: controller.show_frame("Option2Frame"),
                 width=20, height=2).pack(pady=10)
        tk.Button(button_frame, text="Option 3", 
                 command=lambda: controller.show_frame("Option3Frame"),
                 width=20, height=2).pack(pady=10)
        tk.Button(button_frame, text="Option 4", 
                 command=lambda: controller.show_frame("Option4Frame"),
                 width=20, height=2).pack(pady=10)
        
class SearchableDropdown(tk.Frame):
    def __init__(self, parent, options, callback=None):
        super().__init__(parent)
        self.options = options
        self.callback = callback
        self.filtered = options

        self.entry = tk.Entry(self)
        self.entry.pack(fill="x")
        self.entry.bind("<KeyRelease>", self.update_list)
        self.entry.bind("<Down>", self.move_down)
        self.entry.bind("<Tab>", self.move_down)  # Tab moves down too
        self.entry.bind("<FocusOut>", self.on_focus_out)

        self.dropdown_window = tk.Toplevel(self)
        self.hide_dropdown()
        self.dropdown_window.overrideredirect(True)
        self.dropdown_window.lift(aboveThis=self)

        self.listbox = tk.Listbox(self.dropdown_window, height=6)
        self.listbox.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(self.dropdown_window, command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)

        self.listbox.bind("<<ListboxSelect>>", self.on_select)
        self.listbox.bind("<Return>", self.on_select)
        self.entry.bind("<KeyRelease-Escape>", lambda e: self.hide_dropdown())
        #self.listbox.bind("<Escape>", lambda e: self.hide_dropdown())
        self.listbox.bind("<Up>", self.move_up)
        self.listbox.bind("<Down>", self.move_down)
        self.listbox.bind("<Tab>", self.move_down)

    def update_list(self, event=None):
        value = self.entry.get().lower()
        self.filtered = [opt for opt in self.options if value in opt.lower()]

        self.listbox.delete(0, tk.END)
        for opt in self.filtered:
            self.listbox.insert(tk.END, opt)

        if self.filtered:
            self.show_listbox()
        else:
            self.hide_dropdown()

    def show_listbox(self):
        x = self.entry.winfo_rootx()
        y = self.entry.winfo_rooty() + self.entry.winfo_height()
        width = self.entry.winfo_width()

        self.dropdown_window.geometry(f"{width}x120+{x}+{y}")
        self.dropdown_window.deiconify()

        # Bind global click
        self.bind_all("<Button-1>", self.global_click_handler, add="+")


    def move_down(self, event=None):
        if not self.filtered:
            return "break"
        try:
            index = self.listbox.curselection()[0]
        except IndexError:
            index = -1
        self.listbox.selection_clear(0, tk.END)
        new_index = (index + 1) % len(self.filtered)
        self.listbox.selection_set(new_index)
        self.listbox.activate(new_index)
        self.listbox.see(new_index)
        self.listbox.focus_set()
        return "break"

    def move_up(self, event=None):
        if not self.filtered:
            return "break"
        try:
            index = self.listbox.curselection()[0]
        except IndexError:
            index = 0
        self.listbox.selection_clear(0, tk.END)
        new_index = (index - 1) % len(self.filtered)
        self.listbox.selection_set(new_index)
        self.listbox.activate(new_index)
        self.listbox.see(new_index)
        self.listbox.focus_set()
        return "break"

    def on_select(self, event=None):
        if not self.listbox.curselection():
            return
        index = self.listbox.curselection()[0]
        selected = self.filtered[index]
        self.entry.delete(0, tk.END)
        self.entry.insert(0, selected)
        self.hide_dropdown()
        if self.callback:
            self.callback(selected)

    def on_focus_out(self, event=None):
        # Delay to allow clicking listbox without closing it immediately
        self.after(100, self._conditionally_hide)

    def _conditionally_hide(self):
        try:
            focused_widget = self.entry.winfo_toplevel().focus_get()
        except (tk.TclError, KeyError):
            focused_widget = None

        if focused_widget not in (self.entry, self.listbox) and not (focused_widget and str(focused_widget).startswith(str(self.dropdown_window))):
            self.hide_dropdown()

    def global_click_handler(self, event):
        widgets = [self.entry, self.listbox]
        clicked_widget = event.widget

        if clicked_widget not in widgets and not str(clicked_widget).startswith(str(self.dropdown_window)):
            self.hide_dropdown()

    def hide_dropdown(self):
        self.dropdown_window.withdraw()
        self.unbind_all("<Button-1>")


class CollectionManager(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.card_data = defaultdict(lambda: defaultdict(int))  # cardname -> {cardset: quantity}

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.center_frame = tk.Frame(self)
        self.center_frame.grid(row=0, column=0, sticky="nsew")
        self.center_frame.grid_rowconfigure(3, weight=1)
        self.center_frame.grid_columnconfigure(0, weight=1)

        tk.Label(self.center_frame, text="Collection Manager", font=("Helvetica", 18)).grid(row=0, column=0, pady=10)

        # Search box for filtering Treeview cards
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.update_list)
        search_entry = tk.Entry(self.center_frame, textvariable=self.search_var, width=40)
        search_entry.grid(row=1, column=0, pady=5, sticky="ew")
        search_entry.focus()

        # Treeview for showing collection
        tree_frame = tk.Frame(self.center_frame)
        tree_frame.grid(row=2, column=0, sticky="nsew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        columns = ("cardname", "total", "sets")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        self.tree.heading("cardname", text="Card Name")
        self.tree.heading("total", text="Total Quantity")
        self.tree.heading("sets", text="Set Breakdown")

        self.tree.column("cardname", anchor="w", stretch=True)
        self.tree.column("total", anchor="center", width=100, stretch=False)
        self.tree.column("sets", anchor="w", stretch=True)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

        # Frame for dropdown + quantity + set
        dropdown_frame = tk.Frame(self.center_frame)
        dropdown_frame.grid(row=3, column=0, pady=(10, 5), sticky="ew")
        dropdown_frame.grid_columnconfigure(1, weight=1)

        tk.Label(dropdown_frame, text="Card Name:").grid(row=0, column=0, padx=(0, 5), sticky="w")

        # SearchableDropdown initialized with empty list for now
        self.dropdown = SearchableDropdown(dropdown_frame, [], callback=self.card_selected)
        self.dropdown.grid(row=0, column=1, sticky="ew")

        # Quantity Combobox
        tk.Label(dropdown_frame, text="Quantity:").grid(row=1, column=0, padx=(0, 5), sticky="w", pady=(5, 0))
        self.quantity_var = tk.StringVar(value="1")
        self.quantity_combo = ttk.Combobox(dropdown_frame, textvariable=self.quantity_var, values=["1", "2", "3"], state="readonly", width=5)
        self.quantity_combo.grid(row=1, column=1, sticky="w", pady=(5, 0))

        # Set Name Combobox
        tk.Label(dropdown_frame, text="Set Name:").grid(row=2, column=0, sticky="w", pady=(5, 0))
        self.set_name_var = tk.StringVar()
        self.set_name_combo = ttk.Combobox(dropdown_frame, textvariable=self.set_name_var, values=[], state="readonly", width=20)
        self.set_name_combo.grid(row=2, column=1, sticky="w", pady=(5, 0))

        # Back button
        tk.Button(self.center_frame, text="Back to Menu",
                  command=lambda: controller.show_frame("MainMenuFrame")).grid(row=4, column=0, pady=10)

        # Load data from files
        self.load_cards()
        self.load_dropdown_names()
        self.update_list()
        self.load_cards_catalog()

    def load_cards(self):
        self.card_data.clear()
        try:
            with open("pulled_cards.csv", newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    cardname = row["cardname"].strip()
                    cardset = row["cardset"].strip()
                    quantity = int(row["cardq"])
                    self.card_data[cardname][cardset] += quantity
        except FileNotFoundError:
            messagebox.showerror("Error", "pulled_cards.csv not found.")

    def load_dropdown_names(self):
        try:
            with open("cards.csv", newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                cardnames = sorted(set(row["cardname"].strip() for row in reader if "cardname" in row))
                self.dropdown.options = cardnames
                self.dropdown.update_list()
        except FileNotFoundError:
            messagebox.showerror("Error", "cards.csv not found.")

    def update_list(self, *args):
        query = self.search_var.get().lower()
        self.tree.delete(*self.tree.get_children())

        for cardname, sets in sorted(self.card_data.items()):
            if query in cardname.lower():
                total = sum(sets.values())
                set_breakdown = ", ".join(f"{s}:{q}" for s, q in sets.items())
                self.tree.insert("", "end", values=(cardname, total, set_breakdown))

    def card_selected(self, selected_name):
        if not selected_name:
            return
        self.quantity_var.set("1")

        # Get possible sets for the card from the catalog, not from pulled_cards
        sets = self.card_sets_map.get(selected_name, [])
        self.set_name_combo['values'] = sets
        if sets:
            self.set_name_var.set(sets[0])
        else:
            self.set_name_var.set("")

    def load_cards_catalog(self):
        """Load mapping from cardname -> list of sets from cards.csv"""
        self.card_sets_map = defaultdict(set)  # cardname -> set of sets
        try:
            with open("cards.csv", newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    cardname = row["cardname"].strip()
                    raw_sets = row["cardset"].strip()
                    if raw_sets:
                        split_sets = [s.strip() for s in raw_sets.split(';')]
                        for s in split_sets:
                            self.card_sets_map[cardname].add(s)
                    self.card_sets_map[cardname].add("Crafted Card")
            # Convert sets to sorted lists for convenience
            for card in self.card_sets_map:
                self.card_sets_map[card] = sorted(self.card_sets_map[card])
        except FileNotFoundError:
            messagebox.showerror("Error", "cards.csv not found.")

class Option2Frame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        center_frame = tk.Frame(self)
        center_frame.pack(expand=True, pady=50)
        
        tk.Label(center_frame, text="Option 2 Screen", font=("Helvetica", 18)).pack(pady=20)
        tk.Button(center_frame, text="Back to Menu", 
                command=lambda: controller.show_frame("MainMenuFrame")).pack(pady=10)


class Option3Frame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        center_frame = tk.Frame(self)
        center_frame.pack(expand=True, pady=50)
        
        tk.Label(center_frame, text="Option 3 Screen", font=("Helvetica", 18)).pack(pady=20)
        tk.Button(center_frame, text="Back to Menu", 
                command=lambda: controller.show_frame("MainMenuFrame")).pack(pady=10)


class Option4Frame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        center_frame = tk.Frame(self)
        center_frame.pack(expand=True, pady=50)
        
        tk.Label(center_frame, text="Option 4 Screen", font=("Helvetica", 18)).pack(pady=20)
        tk.Button(center_frame, text="Back to Menu", 
                command=lambda: controller.show_frame("MainMenuFrame")).pack(pady=10)


class AppController(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Yu-Gi-Oh! Limited Tool (Name STILL Pending)")
        self.geometry("700x500")
        self.minsize(700, 500)

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (MainMenuFrame, CollectionManager, Option2Frame, Option3Frame, Option4Frame):
            frame = F(container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MainMenuFrame")

    def show_frame(self, frame_name):
        frame = self.frames[frame_name]
        frame.tkraise()


if __name__ == "__main__":
    app = AppController()
    app.mainloop()