import os
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

        self.entry = tk.Entry(self, width=60)
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
        
        self.card_data = defaultdict(lambda: defaultdict(int))
        self.card_catalog = {}  # Initialize empty catalog first
        self.card_sets_map = defaultdict(set)  # Initialize empty sets map

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Top frame for Back button
        header_frame = tk.Frame(self)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        header_frame.grid_columnconfigure(1, weight=1)

        back_button = tk.Button(header_frame, text="Back to Menu",
                                command=lambda: controller.show_frame("MainMenuFrame"))
        back_button.grid(row=0, column=0, sticky="w")

        # Center frame for main content
        self.center_frame = tk.Frame(self)
        self.center_frame.grid(row=1, column=0, sticky="nsew")
        self.center_frame.grid_rowconfigure(2, weight=1)
        self.center_frame.grid_columnconfigure(0, weight=1)

        tk.Label(self.center_frame, text="Collection Manager", font=("Helvetica", 18)).grid(row=0, column=0, pady=10)

                # Add this near the search entry (around row 1 in center_frame)
        filter_button = tk.Button(self.center_frame, text="Filter", command=self.show_filter_dialog)
        filter_button.grid(row=1, column=1, pady=5, sticky="e")
        
        # Add these instance variables to track filters
        self.current_filters = {
            'cardtype': [],    # Monster/Spell/Trap
            'type': [],        # Normal/Effect/Ritual/etc.
            'monstertype': [], # Aqua/Beast/etc. (race)
            'attribute': [],   # DARK/LIGHT/etc.
            'level': None,     # Specific level/rank
            'pscales': None,   # Specific pendulum scale
            'link': None       # Specific link rating
        }

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.update_list)
        search_entry = tk.Entry(self.center_frame, textvariable=self.search_var, width=40)
        search_entry.grid(row=1, column=0, pady=5, sticky="ew")
        search_entry.focus()

        tree_frame = tk.Frame(self.center_frame)
        tree_frame.grid(row=2, column=0, sticky="nsew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        columns = ("cardname", "total", "sets", "cardtype", "type", "monstertype", 
                "attribute", "atk", "def", "level", "pscales", "lcount", "larrows", "description")

        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        self.tree.heading("cardname", text="Card Name")
        self.tree.heading("total", text="Total")
        self.tree.heading("sets", text="Sets")
        self.tree.heading("cardtype", text="Card Type")
        self.tree.heading("type", text="Type")
        self.tree.heading("monstertype", text="Monster Type")
        self.tree.heading("attribute", text="Attribute")
        self.tree.heading("atk", text="ATK")
        self.tree.heading("def", text="DEF")
        self.tree.heading("level", text="Level")
        self.tree.heading("pscales", text="P.Scale")
        self.tree.heading("lcount", text="Link")
        self.tree.heading("larrows", text="Link Arrows")
        self.tree.heading("description", text="Description")

        # Adjust column widths as needed
        self.tree.column("cardname", anchor="w", width=200, stretch=True)
        self.tree.column("total", anchor="center", width=50, stretch=False)
        self.tree.column("sets", anchor="w", width=150, stretch=True)
        self.tree.column("cardtype", anchor="w", width=80, stretch=False)
        self.tree.column("type", anchor="w", width=100, stretch=False)
        self.tree.column("monstertype", anchor="w", width=100, stretch=False)
        self.tree.column("attribute", anchor="w", width=70, stretch=False)
        self.tree.column("atk", anchor="center", width=50, stretch=False)
        self.tree.column("def", anchor="center", width=50, stretch=False)
        self.tree.column("level", anchor="center", width=50, stretch=False)
        self.tree.column("pscales", anchor="center", width=60, stretch=False)
        self.tree.column("lcount", anchor="center", width=50, stretch=False)
        self.tree.column("larrows", anchor="w", width=100, stretch=False)
        self.tree.column("description", anchor="w", width=300, stretch=True)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

        dropdown_frame = tk.Frame(self.center_frame)
        dropdown_frame.grid(row=3, column=0, pady=(10, 5), sticky="ew")
        dropdown_frame.grid_columnconfigure(1, weight=1)

        tk.Label(dropdown_frame, text="Card Name:").grid(row=0, column=0, padx=(0, 5), sticky="w")
        self.dropdown = SearchableDropdown(dropdown_frame, [], callback=self.card_selected)
        self.dropdown.grid(row=0, column=1, sticky="w")

        tk.Label(dropdown_frame, text="Quantity:").grid(row=1, column=0, padx=(0, 5), sticky="w", pady=(5, 0))
        self.quantity_var = tk.StringVar(value="1")
        self.quantity_combo = ttk.Combobox(dropdown_frame, textvariable=self.quantity_var, values=["1", "2", "3"], state="readonly", width=5)
        self.quantity_combo.grid(row=1, column=1, sticky="w", pady=(5, 0))

        tk.Label(dropdown_frame, text="Set Name:").grid(row=2, column=0, sticky="w", pady=(5, 0))
        self.set_name_var = tk.StringVar()
        self.set_name_combo = ttk.Combobox(dropdown_frame, textvariable=self.set_name_var, values=[], state="readonly", width=20)
        self.set_name_combo.grid(row=2, column=1, sticky="w", pady=(5, 0))

        # Bottom frame for Add and Remove buttons side by side
        bottom_frame = tk.Frame(self)
        bottom_frame.grid(row=2, column=0, sticky="ew", pady=10)
        bottom_frame.grid_columnconfigure(0, weight=1)
        bottom_frame.grid_columnconfigure(1, weight=1)

        export_button = tk.Button(bottom_frame, text="Export Whitelist", command=self.export_whitelist)
        export_button.pack(side="left", padx=10)

        remove_button = ttk.Button(bottom_frame, text="Remove Selected Card", command=self.remove_selected_card)
        remove_button.pack(side="left", padx=10)

        add_button = tk.Button(bottom_frame, text="Add Card to Collection", command=self.add_card)
        add_button.pack(side="left", padx=10)

        # Load data from files
        self.load_cards_catalog()
        self.load_cards()
        self.load_dropdown_names()
        self.update_list()


    def load_cards(self):
        """Load all card data from pulled_cards.csv"""
        self.card_data.clear()
        try:
            with open("pulled_cards.csv", newline='', encoding='utf-8-sig') as csvfile:
                # Read first line to check if it's a header
                first_line = csvfile.readline()
                has_header = 'cardname' in first_line.lower()  # Check if header exists
                
                # Rewind and read properly
                csvfile.seek(0)
                
                if has_header:
                    reader = csv.DictReader(csvfile)
                else:
                    # If no header, use the expected fieldnames
                    fieldnames = [
                        'cardname', 'cardq', 'cardrarity', 'card_edition', 'cardset',
                        'cardcode', 'cardid', 'print_id', 'description', 'cardtype',
                        'type', 'monstertype', 'attribute', 'atk', 'def', 'level',
                        'pscales', 'lcount', 'larrows'
                    ]
                    reader = csv.DictReader(csvfile, fieldnames=fieldnames)
                
                for row in reader:
                    try:
                        cardname = row.get("cardname", "").strip()
                        if not cardname:
                            continue
                            
                        # Safely get quantity with fallback
                        quantity_str = row.get("cardq", "1").strip() or "1"
                        try:
                            quantity = int(quantity_str)
                        except ValueError:
                            quantity = 1
                            
                        cardset = row.get("cardset", "").strip() or "Unknown Set"
                        
                        # Store quantity by set
                        self.card_data[cardname][cardset] += quantity
                        
                        # Create catalog entry if missing
                        if cardname not in self.card_catalog:
                            self.card_catalog[cardname] = {
                                'cardname': cardname,
                                'cardtype': row.get("cardtype", "").strip(),
                                'type': row.get("type", "").strip(),
                                'monstertype': row.get("monstertype", "").strip(),
                                'attribute': row.get("attribute", "").strip(),
                                'atk': row.get("atk", "").strip(),
                                'def': row.get("def", "").strip(),
                                'level': row.get("level", "").strip(),
                                'pscales': row.get("pscales", "").strip(),
                                'lcount': row.get("lcount", "").strip(),
                                'larrows': row.get("larrows", "").strip(),
                                'description': row.get("description", "").strip(),
                                'cardid': row.get("cardid", "").strip(),
                                'cardrarity': row.get("cardrarity", "").strip(),
                                'cardset': cardset
                            }
                        
                        # Add to sets map
                        self.card_sets_map[cardname].add(cardset)
                        self.card_sets_map[cardname].add("Crafted Card")
                        
                    except Exception as e:
                        print(f"Error processing row: {row}\nError: {e}")
                        continue
                        
            # Convert sets to sorted lists
            for card in self.card_sets_map:
                self.card_sets_map[card] = sorted(self.card_sets_map[card])
                
        except FileNotFoundError:
            messagebox.showerror("Error", "pulled_cards.csv not found.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load cards:\n{str(e)}")

    def update_list(self, *args):
        query = self.search_var.get().lower()
        self.tree.delete(*self.tree.get_children())

        for cardname, sets in sorted(self.card_data.items()):
            # Skip if search query doesn't match
            if query and query not in cardname.lower():
                continue
                
            # Get card info from catalog
            card_info = self.card_catalog.get(cardname, {})
            if not card_info:  # Skip if no catalog data
                continue
                
            # Get all relevant card properties
            card_type = card_info.get('cardtype', '')
            types = card_info.get('type', '').split(';') if card_info.get('type') else []
            monster_race = card_info.get('monstertype', '')
            attribute = card_info.get('attribute', '')
            atk = card_info.get('atk', '')
            defense = card_info.get('def', '')
            level = card_info.get('level', '')
            pscale = card_info.get('pscales', '')
            link = card_info.get('lcount', '')
            larrows = card_info.get('larrows', '')
            description = card_info.get('description', '')

            # If card passed all active filters, add it to the tree
            if (self.passes_filters(card_type, types, monster_race, attribute, level, pscale, link)):
                total = sum(sets.values())
                set_breakdown = ", ".join(f"{s}:{q}" for s, q in sets.items())
                
                self.tree.insert("", "end", values=(
                    cardname, 
                    total, 
                    set_breakdown,
                    card_type,
                    "; ".join(types),  # Properly format multiple types
                    monster_race,
                    attribute,
                    atk,
                    defense,
                    level,
                    pscale,
                    link,
                    larrows,
                    description
                ))

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
        """Load all card data from cards.csv for filtering and display"""
        self.card_catalog = {}  # cardname -> full card data dictionary
        self.card_sets_map = defaultdict(set)  # cardname -> set of sets
        
        try:
            with open("cards.csv", newline='', encoding='utf-8-sig') as csvfile:
                # Try to detect delimiter
                first_line = csvfile.readline()
                sep = '\t' if '\t' in first_line else ','
                csvfile.seek(0)  # Rewind to start of file
                
                reader = csv.DictReader(csvfile, delimiter=sep)
                if 'cardname' not in reader.fieldnames:
                    messagebox.showerror("Error", "CSV file missing 'cardname' header")
                    return
                    
                for row in reader:
                    try:
                        cardname = row["cardname"].strip()
                        if not cardname:  # Skip empty rows
                            continue
                            
                        # Store all card attributes
                        self.card_catalog[cardname] = {
                            'cardname': cardname,
                            'cardtype': row.get("cardtype", "").strip(),
                            'type': row.get("type", "").strip(),
                            'monstertype': row.get("monstertype", "").strip(),
                            'attribute': row.get("attribute", "").strip(),
                            'atk': row.get("atk", "").strip(),
                            'def': row.get("def", "").strip(),
                            'level': row.get("level", "").strip(),
                            'pscales': row.get("pscales", "").strip(),
                            'lcount': row.get("lcount", "").strip(),
                            'larrows': row.get("larrows", "").strip(),
                            'description': row.get("description", "").strip(),
                            'cardid': row.get("cardid", "").strip(),
                            'cardrarity': row.get("cardrarity", "").strip(),
                            'cardset': row.get("cardset", "").strip()
                        }
                        
                        # Store sets information
                        if 'cardset' in row and row["cardset"].strip():
                            self.card_sets_map[cardname].add(row["cardset"].strip())
                        
                        # Always include Crafted Card as an option
                        self.card_sets_map[cardname].add("Crafted Card")
                        
                    except Exception as e:
                        print(f"Error processing row: {row}\nError: {e}")
                        continue
                        
                # Convert sets to sorted lists for consistency
                for card in self.card_sets_map:
                    self.card_sets_map[card] = sorted(self.card_sets_map[card])
                    
        except FileNotFoundError:
            messagebox.showerror("Error", "cards.csv not found.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load card catalog:\n{e}")


    def add_card(self):
        selected_card = self.dropdown.entry.get().strip()
        card_quantity = self.quantity_var.get().strip()
        selected_set = self.set_name_var.get().strip()

        if not selected_card:
            messagebox.showerror("Error", "Please select a card.")
            return

        if not selected_set:
            messagebox.showerror("Error", "Please select a set.")
            return

        if not card_quantity.isdigit():
            messagebox.showerror("Error", "Quantity must be a number.")
            return

        card_info = self.card_catalog.get(selected_card)
        if not card_info:
            messagebox.showerror("Error", f"No catalog data found for card: {selected_card}")
            return

        cardid = card_info.get("cardid", "").strip()
        cardrarity = card_info.get("cardrarity", "").strip()
        if not cardid:
            messagebox.showerror("Error", f"No cardid found for {selected_card}")
            return

        cardcode = selected_set.replace(" ", "")[:4] + cardid

        row = [
            selected_card,
            card_quantity,
            cardrarity,
            "Unlimited",
            selected_set,
            cardcode,
            cardid,
            ""
        ]

        with open("pulled_cards.csv", "a", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(row)

        messagebox.showinfo("Success", f"Added {selected_card} x{card_quantity} to pulled_cards.csv")
        
        self.deduplicate_pulled_cards()
        self.load_cards()
        self.update_list()

    def deduplicate_pulled_cards(self):
        if not os.path.exists("pulled_cards.csv"):
            return

        deduped = {}
        header = None

        with open("pulled_cards.csv", newline='', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            rows = list(reader)

            if rows:
                # Assume first row is header if it contains text, not a number in second column
                if not rows[0][1].isdigit():
                    header = rows[0]
                    rows = rows[1:]

            for row in rows:
                if not row:  # skip blank lines
                    continue

                key = tuple(row[:1] + row[2:])  # everything except quantity
                qty = int(row[1]) if row[1].isdigit() else 1
                if key in deduped:
                    deduped[key] += qty
                else:
                    deduped[key] = qty

        # Sort alphabetically by card name (case-insensitive)
        sorted_keys = sorted(deduped.keys(), key=lambda x: x[0].lower())

        with open("pulled_cards.csv", "w", newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            if header:
                writer.writerow(header)
            for key in sorted_keys:
                writer.writerow([key[0], deduped[key], *key[1:]])

    def remove_selected_card(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a card first.")
            return

        cardname = self.tree.item(selected_item, "values")[0]
        sets = self.card_data.get(cardname, {})
        if not sets:
            messagebox.showerror("Error", f"No sets found for '{cardname}' in your collection.")
            return

        self.show_remove_window(cardname, sets)

    def show_remove_window(self, cardname, sets_dict):
        remove_win = tk.Toplevel(self)
        remove_win.title(f"Remove {cardname}")
        remove_win.geometry("460x225")
        remove_win.resizable(False, False)

        tk.Label(remove_win, text=f"Remove copies of:\n '{cardname}'", font=("Helvetica", 12)).pack(pady=(10, 5))

        tk.Label(remove_win, text="Select Set:").pack(pady=(5, 0))
        set_var = tk.StringVar()

        # Create dropdown values with quantities in brackets
        options = [f"{set_name} ({qty})" for set_name, qty in sets_dict.items()]
        set_dropdown = ttk.Combobox(remove_win, textvariable=set_var, values=options, state="readonly")
        set_dropdown.current(0)
        set_dropdown.pack(pady=5, fill='x', padx=10)

        tk.Label(remove_win, text="Quantity to Remove:").pack(pady=(10, 0))
        qty_var = tk.StringVar()
        qty_entry = tk.Entry(remove_win, textvariable=qty_var)
        qty_entry.pack(pady=5, fill='x', padx=10)
        qty_entry.focus()

        def confirm_removal():
            selected = set_var.get()
            if not selected:
                messagebox.showerror("Error", "Please select a set.")
                return

            # Parse set name (remove quantity in brackets)
            set_name = selected.rsplit(" (", 1)[0]

            qty_str = qty_var.get().strip()
            if not qty_str.isdigit() or int(qty_str) <= 0:
                messagebox.showerror("Error", "Please enter a valid positive number for quantity.")
                return

            qty = int(qty_str)
            owned_qty = sets_dict.get(set_name, 0)
            if qty > owned_qty:
                messagebox.showerror("Error", f"You only have {owned_qty} copies in set '{set_name}'.")
                return

            self.remove_card_from_file(cardname, set_name, qty)
            remove_win.destroy()

        def cancel_removal():
            remove_win.destroy()

        button_frame = tk.Frame(remove_win)
        button_frame.pack(pady=15)

        confirm_btn = tk.Button(button_frame, text="Confirm", command=confirm_removal, width=10)
        confirm_btn.pack(side="left", padx=10)

        cancel_btn = tk.Button(button_frame, text="Cancel", command=cancel_removal, width=10)
        cancel_btn.pack(side="left", padx=10)

        def cancel_removal():
            remove_win.destroy()

        button_frame = tk.Frame(remove_win)
        button_frame.pack(pady=15)

        confirm_btn = tk.Button(button_frame, text="Confirm", command=confirm_removal, width=10)
        confirm_btn.pack(side="left", padx=10)

        cancel_btn = tk.Button(button_frame, text="Cancel", command=cancel_removal, width=10)
        cancel_btn.pack(side="left", padx=10)


    def remove_card_from_file(self, cardname, setname, qty_to_remove):
        if not os.path.exists("pulled_cards.csv"):
            messagebox.showerror("Error", "pulled_cards.csv not found.")
            return

        updated_rows = []
        header = None
        removed = False

        with open("pulled_cards.csv", newline='', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            rows = list(reader)

        if rows and not rows[0][1].isdigit():
            header = rows[0]
            rows = rows[1:]

        for row in rows:
            if not row or len(row) < 3:
                continue

            row_cardname = row[0].strip()
            row_setname = row[4].strip()
            row_qty = int(row[1]) if row[1].isdigit() else 0

            if row_cardname == cardname and row_setname == setname and not removed:
                if row_qty > qty_to_remove:
                    row[1] = str(row_qty - qty_to_remove)
                    updated_rows.append(row)
                else:
                    # Don't append — removes the row
                    pass
                removed = True
            else:
                updated_rows.append(row)

        with open("pulled_cards.csv", "w", newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            if header:
                writer.writerow(header)
            writer.writerows(updated_rows)

        self.load_cards()
        self.update_list()
        messagebox.showinfo("Removed", f"Removed {qty_to_remove}x {cardname} from set {setname}.")

    def remove_selected_card(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("No selection", "Please select a card to remove.")
            return

        cardname = self.tree.item(selected_item[0], "values")[0]
        sets = self.card_data.get(cardname, {})
        if not sets:
            messagebox.showerror("Error", f"No sets found for '{cardname}' in your collection.")
            return

        self.show_remove_window(cardname, sets)

    def export_whitelist(self):
        if not os.path.exists("pulled_cards.csv"):
            messagebox.showerror("Error", "pulled_cards.csv not found.")
            return

        card_id_counts = defaultdict(int)

        with open("pulled_cards.csv", newline='', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            next(reader, None)  # Skip header if it exists

            for row in reader:
                if len(row) < 7:
                    continue
                qty_str = row[1].strip()
                card_id = row[6].strip()

                if not qty_str.isdigit() or not card_id.isdigit():
                    continue

                qty = int(qty_str)
                card_id_counts[card_id] += qty

        # Cap each card ID count at 3
        whitelist_lines = [f"{card_id} {min(3, total)}" for card_id, total in card_id_counts.items()]

        try:
            with open("whitelist.conf", "w", encoding="utf-8") as f:
                f.write("!Limited Between Reece & Ant\n")
                f.write("$whitelist\n")
                for line in whitelist_lines:
                    f.write(line + "\n")

            messagebox.showinfo("Success", "Whitelist exported to whitelist.conf.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to write whitelist.conf:\n{e}")

    def show_filter_dialog(self):
        filter_win = tk.Toplevel(self)
        filter_win.title("Filter Cards")
        filter_win.geometry("600x600")
        
        # Notebook for different filter categories
        notebook = ttk.Notebook(filter_win)
        notebook.pack(fill="both", expand=True)
        
        # Card Type tab
        cardtype_frame = ttk.Frame(notebook)
        notebook.add(cardtype_frame, text="Card Type")
        
        self.cardtype_vars = {
            'Monster': tk.BooleanVar(),
            'Spell': tk.BooleanVar(),
            'Trap': tk.BooleanVar()
        }
        
        for i, (ctype, var) in enumerate(self.cardtype_vars.items()):
            cb = tk.Checkbutton(cardtype_frame, text=ctype, variable=var)
            cb.pack(anchor="w")
            if ctype in self.current_filters['cardtype']:
                var.set(True)
        
        # Type tab (for all card types - Normal, Effect, Ritual, etc. for monsters, also spell/trap types)
        type_frame = ttk.Frame(notebook)
        notebook.add(type_frame, text="Type")

        all_types = [
            'Effect', 'Pendulum', 'Flip', 'Tuner', 'Synchro', 'Xyz', 
            'Link', 'Gemini', 'Spirit', 'Toon', 'Union', 'Normal',
            'Field', 'Equip', 'Continuous', 'Quick-Play', 'Ritual',
            'Counter', 'Fusion', 'Ritual', 'Spirit'
        ]
        self.type_vars = {t: tk.BooleanVar() for t in all_types}
        
        for i, (mtype, var) in enumerate(self.type_vars.items()):
            cb = tk.Checkbutton(type_frame, text=mtype, variable=var)
            cb.grid(row=i//3, column=i%3, sticky="w")
            if mtype in self.current_filters['type']:
                var.set(True)
        
        # Monster Race tab (previously mislabeled as Attribute)
        monsterrace_frame = ttk.Frame(notebook)
        notebook.add(monsterrace_frame, text="Monster Race")
        
        races = [
            'Aqua', 'Beast', 'Beast-Warrior', 'Creator God', 'Cyberse', 
            'Dinosaur', 'Divine-Beast', 'Dragon', 'Fairy', 'Fiend', 
            'Fish', 'Illusion', 'Insect', 'Machine', 'Plant', 'Psychic', 
            'Pyro', 'Reptile', 'Rock', 'Sea Serpent', 'Spellcaster', 
            'Thunder', 'Warrior', 'Winged Beast', 'Wyrm', 'Zombie'
        ]
        self.monsterrace_vars = {r: tk.BooleanVar() for r in races}
        
        for i, (race, var) in enumerate(self.monsterrace_vars.items()):
            cb = tk.Checkbutton(monsterrace_frame, text=race, variable=var)
            cb.grid(row=i//3, column=i%3, sticky="w")
            if race in self.current_filters['monstertype']:
                var.set(True)
        
        # Attribute tab (for actual attributes)
        attribute_frame = ttk.Frame(notebook)
        notebook.add(attribute_frame, text="Attribute")
        
        attributes = ['DARK', 'DIVINE', 'EARTH', 'FIRE', 'LIGHT', 'WATER', 'WIND']
        self.attribute_vars = {a: tk.BooleanVar() for a in attributes}
        
        for i, (attr, var) in enumerate(self.attribute_vars.items()):
            cb = tk.Checkbutton(attribute_frame, text=attr, variable=var)
            cb.grid(row=i//3, column=i%3, sticky="w")
            if attr in self.current_filters['attribute']:
                var.set(True)
        
        # Other filters tab
        other_frame = ttk.Frame(notebook)
        notebook.add(other_frame, text="Other")
        
        # Level/Rank
        tk.Label(other_frame, text="Level/Rank:").grid(row=0, column=0, sticky="w")
        self.level_var = tk.StringVar()
        self.level_entry = tk.Entry(other_frame, textvariable=self.level_var, width=5)
        self.level_entry.grid(row=0, column=1, sticky="w")
        if self.current_filters['level'] is not None:
            self.level_var.set(str(self.current_filters['level']))
        
        # Pendulum Scale
        tk.Label(other_frame, text="Pendulum Scale:").grid(row=1, column=0, sticky="w")
        self.pscale_var = tk.StringVar()
        self.pscale_entry = tk.Entry(other_frame, textvariable=self.pscale_var, width=5)
        self.pscale_entry.grid(row=1, column=1, sticky="w")
        if self.current_filters['pscales'] is not None:
            self.pscale_var.set(str(self.current_filters['pscales']))
        
        # Link Rating
        tk.Label(other_frame, text="Link Rating:").grid(row=2, column=0, sticky="w")
        self.link_var = tk.StringVar()
        self.link_entry = tk.Entry(other_frame, textvariable=self.link_var, width=5)
        self.link_entry.grid(row=2, column=1, sticky="w")
        if self.current_filters['link'] is not None:
            self.link_var.set(str(self.current_filters['link']))
        
        # Button frame
        button_frame = tk.Frame(filter_win)
        button_frame.pack(fill="x", pady=5)
        
        def apply_filters():
            # Get card type filters
            self.current_filters['cardtype'] = [
                ctype for ctype, var in self.cardtype_vars.items() if var.get()
            ]
            
            # Get type filters (Normal, Effect, etc. for monsters; types for spells/traps)
            self.current_filters['type'] = [
                mtype for mtype, var in self.type_vars.items() if var.get()
            ]
            
            # Get monster race filters
            self.current_filters['monstertype'] = [
                race for race, var in self.monsterrace_vars.items() if var.get()
            ]
            
            # Get attribute filters
            self.current_filters['attribute'] = [
                attr for attr, var in self.attribute_vars.items() if var.get()
            ]
            
            # Get level/rank
            level_val = self.level_var.get()
            self.current_filters['level'] = int(level_val) if level_val.isdigit() else None
            
            # Get pendulum scale
            pscale_val = self.pscale_var.get()
            self.current_filters['pscales'] = float(pscale_val) if pscale_val.replace('.', '').isdigit() else None
            
            # Get link rating
            link_val = self.link_var.get()
            self.current_filters['link'] = int(link_val) if link_val.isdigit() else None
            
            filter_win.destroy()
            self.update_list()
        
        def clear_filters():
            for var in self.cardtype_vars.values():
                var.set(False)
            for var in self.type_vars.values():
                var.set(False)
            for var in self.monsterrace_vars.values():
                var.set(False)
            for var in self.attribute_vars.values():
                var.set(False)
            self.level_var.set("")
            self.pscale_var.set("")
            self.link_var.set("")
            self.current_filters = {
                'cardtype': [],
                'type': [],
                'monstertype': [],
                'attribute': [],
                'level': None,
                'pscales': None,
                'link': None
            }
            filter_win.destroy()
            self.update_list()
        
        tk.Button(button_frame, text="Apply", command=apply_filters).pack(side="left", padx=5)
        tk.Button(button_frame, text="Clear All", command=clear_filters).pack(side="left", padx=5)
        tk.Button(button_frame, text="Cancel", command=filter_win.destroy).pack(side="right", padx=5)

    def passes_filters(self, card_type, types, attribute, monster_race, level, pscale, link):
        """Check if a card passes all active filters"""
        # Check card type filter (Monster/Spell/Trap)
        if self.current_filters['cardtype']:
            if card_type not in self.current_filters['cardtype']:
                return False
        
        # Check type filter (Normal/Effect/Ritual/etc.)
        if self.current_filters['type']:
            type_match = any(t in types for t in self.current_filters['type'])
            if not type_match:
                return False
        
        # Check monster race filter
        if self.current_filters['monstertype'] and card_type == "Monster":
            if monster_race not in self.current_filters['monstertype']:
                return False
        
        # Check attribute filter
        if self.current_filters['attribute'] and card_type == "Monster":
            if attribute not in self.current_filters['attribute']:
                return False
        
        # Check level filter
        if self.current_filters['level'] is not None and card_type == "Monster":
            try:
                if int(level) != self.current_filters['level']:
                    return False
            except (ValueError, TypeError):
                return False
        
        # Check pendulum scale filter
        if self.current_filters['pscales'] is not None and "Pendulum" in types:
            try:
                if float(pscale) != self.current_filters['pscales']:
                    return False
            except (ValueError, TypeError):
                return False
        
        # Check link rating filter
        if self.current_filters['link'] is not None and "Link" in types:
            try:
                if int(link) != self.current_filters['link']:
                    return False
            except (ValueError, TypeError):
                return False
        
        # If all filters passed
        return True

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