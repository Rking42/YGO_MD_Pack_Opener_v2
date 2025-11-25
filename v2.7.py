import datetime
import json
import random
import re
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import csv
from collections import defaultdict
from PIL import Image, ImageTk
from tkinter import simpledialog
import threading
import cv2
import numpy as np
from PIL import Image, ImageTk
import cv2
import pygame
import threading
import time
from PIL import Image, ImageTk
import os
import time
from PIL import Image, ImageTk
import ctypes
import sys
import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk


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
        tk.Button(button_frame, text="Pack Simulator", 
                 command=lambda: controller.show_frame("PackSimulator"),
                 width=20, height=2).pack(pady=10)
        tk.Button(button_frame, text="Pull History", 
                 command=lambda: controller.show_frame("PullHistory"),
                 width=20, height=2).pack(pady=10)
        tk.Button(button_frame, text="🎁Surprise for the Lonely🎁", 
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

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller .exe """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class CollectionManager(tk.Frame):
    PULLED_CARDS_HEADERS = [
        'cardname', 'cardq', 'cardrarity', 'card_edition', 
        'cardset', 'cardcode', 'cardid', 'print_id'
    ]
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.current_filters = {
            'cardtype': [],    # Monster/Spell/Trap
            'type': [],        # Normal/Effect/Ritual/etc.
            'monstertype': [], # Aqua/Beast/etc. (race)
            'attribute': [],   # DARK/LIGHT/etc.
            'level': None,     # Specific level/rank
            'pscales': None,   # Specific pendulum scale
            'link': None       # Specific link rating
        }
        
        self.card_data = defaultdict(lambda: defaultdict(int))
        self.card_catalog = {} 
        self.card_sets_map = defaultdict(set)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.card_data = defaultdict(lambda: defaultdict(int))
        self.card_catalog = {} 
        self.card_sets_map = defaultdict(set)

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

        tk.Label(self.center_frame, text="Collection Manager", font=("Helvetica", 18)).grid(row=0, column=0, columnspan=2, pady=10)

        # Search and Filter Controls Frame
        control_frame = tk.Frame(self.center_frame)
        control_frame.grid(row=1, column=0, sticky="ew", pady=5)
        control_frame.grid_columnconfigure(1, weight=1)  # Search bar expands

        # Filter button
        filter_button = tk.Button(control_frame, text="Filter", command=self.show_filter_dialog)
        filter_button.grid(row=0, column=0, padx=(0, 5), sticky="w")

        # Search entry (replaces your original search_entry)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.update_list)
        self.search_entry = tk.Entry(control_frame, textvariable=self.search_var, width=40)
        self.search_entry.grid(row=0, column=1, sticky="ew")
        self.search_entry.focus()

        # Clear search button
        clear_btn = tk.Button(control_frame, text="✕", command=self.clear_search,
                            width=2, relief="flat")
        clear_btn.grid(row=0, column=2, padx=5)

        # Search mode toggle
        self.search_mode = tk.StringVar(value="both")
        mode_frame = tk.Frame(control_frame)
        mode_frame.grid(row=0, column=3, sticky="e")
        
        tk.Radiobutton(mode_frame, text="Name Only", variable=self.search_mode, 
                      value="name", command=self.update_list).pack(side="left")
        tk.Radiobutton(mode_frame, text="Name+Desc", variable=self.search_mode, 
                      value="both", command=self.update_list).pack(side="left", padx=5)

        # Treeview frame
        tree_frame = tk.Frame(self.center_frame)
        tree_frame.grid(row=2, column=0, sticky="nsew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # First create the Treeview
        columns = ("cardname", "total", "sets", "cardtype", "type", "monstertype", 
                "attribute", "atk", "def", "level", "pscales", "lcount", "larrows", "description")

        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")

        # Then create the scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)

        # Configure treeview to use both scrollbars
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Grid layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

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
        self.tree.column("monstertype", anchor="w", width=120, stretch=False)
        self.tree.column("attribute", anchor="w", width=70, stretch=False)
        self.tree.column("atk", anchor="center", width=50, stretch=False)
        self.tree.column("def", anchor="center", width=50, stretch=False)
        self.tree.column("level", anchor="center", width=50, stretch=False)
        self.tree.column("pscales", anchor="center", width=60, stretch=False)
        self.tree.column("lcount", anchor="center", width=50, stretch=False)
        self.tree.column("larrows", anchor="w", width=100, stretch=False)
        self.tree.column("description", anchor="w", width=300, stretch=True)

        # Configure columns with minimum widths and stretch settings
        min_column_widths = {
            "cardname": 100, "total": 40, "sets": 80, "cardtype": 60, 
            "type": 80, "monstertype": 100, "attribute": 60, "atk": 40, 
            "def": 40, "level": 40, "pscales": 50, "lcount": 40, 
            "larrows": 80, "description": 150
        }

        for col, width in min_column_widths.items():
            self.tree.column(col, width=width, minwidth=width, stretch=False)

        # Create scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)

        # Configure treeview scrolling
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Grid layout with proper weights
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        # Make sure the treeview can expand
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)

        # Prevent columns from being resized too small
        def enforce_min_width(self, event):
            try:
                column = self.tree.identify_column(event.x)
                if column:
                    col_id = column[1:]  # Remove the '#' prefix
                    # Only enforce width for columns we know exist
                    if col_id in self.min_column_widths:
                        current_width = self.tree.column(col_id, 'width')
                        min_width = self.min_column_widths[col_id]
                        if current_width < min_width:
                            self.tree.column(col_id, width=min_width)
            except Exception as e:
                # Silently ignore errors to prevent console spam
                pass

        self.tree.bind('<ButtonRelease-1>', enforce_min_width)

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

        details_button = tk.Button(bottom_frame, text="Show Card Details", 
                                 command=self.show_card_details)
        details_button.pack(side="left", padx=10)

        # In the bottom_frame section where other buttons are defined
        mdm_button = tk.Button(bottom_frame, text="Open MDM Link", 
                            command=self.open_mdm_link)
        mdm_button.pack(side="left", padx=10)

        #test_button = tk.Button(bottom_frame, text="Test Monster Types", 
        #                    command=self.test_monster_types)
        #test_button.pack(side="left", padx=10)

        self.load_cards_catalog()
        self.load_cards()
        self.load_dropdown_names()
        self.update_list()

    def test_monster_types(self):
        """Test if monster types can be displayed in the treeview"""
        test_items = [
            ("Test Monster 1", "1", "Test Set", "Monster", "Effect", "Dragon", "FIRE", "1500", "1000", "4", "", "", "", "Test Desc"),
            ("Test Monster 2", "1", "Test Set", "Monster", "Link", "Cyberse", "LIGHT", "2000", "", "", "", "3", "Bottom", "Test Desc"),
            ("Test Spell", "1", "Test Set", "Spell", "Normal", "", "", "", "", "", "", "", "", "Test Desc")
        ]
        
        self.tree.delete(*self.tree.get_children())
        for item in test_items:
            self.tree.insert("", "end", values=item)
        
        messagebox.showinfo("Test", "Test data inserted. Check if monster types appear.")

    def load_cards(self):
        """Load all card data from pulled_cards.csv"""
        self.card_data = defaultdict(lambda: defaultdict(int))
        self.card_sets_map = defaultdict(set)
        
        try:
            with open("pulled_cards.csv", newline='', encoding='utf-8-sig') as csvfile:
                # Check if file has header
                sniffer = csv.Sniffer()
                has_header = sniffer.has_header(csvfile.read(1024))
                csvfile.seek(0)
                
                if has_header:
                    reader = csv.DictReader(csvfile)
                else:
                    reader = csv.DictReader(csvfile, fieldnames=CollectionManager.PULLED_CARDS_HEADERS)
                    
                for row in reader:
                    try:
                        cardname = row.get("cardname", "").strip()
                        if not cardname:
                            continue
                            
                        quantity = int(row.get("cardq", "1").strip() or "1")
                        cardset = row.get("cardset", "").strip() or "Unknown Set"
                        
                        self.card_data[cardname][cardset] += quantity
                        self.card_sets_map[cardname].add(cardset)
                        
                    except Exception as e:
                        print(f"Error processing row: {row}\nError: {e}")
                        continue
                        
        except FileNotFoundError:
            # File doesn't exist yet, that's fine
            pass
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load cards:\n{str(e)}")

    def clear_search(self):
        """Clear the search field"""
        self.search_var.set("")
        self.search_entry.focus()

    def update_list(self, *args):
        """Update the treeview with search and filter results"""
        self.tree.delete(*self.tree.get_children())
        search_term = self.search_var.get().lower()
        
        for cardname, sets_dict in self.card_data.items():
            if cardname not in self.card_catalog:
                continue
                
            card_info = self.card_catalog[cardname]
            
            # Apply search filter with operators
            if search_term:
                search_terms = [t.strip() for t in search_term.split() if t.strip()]
                if not self.matches_search(cardname, card_info, search_terms):
                    continue
                    
            # Apply other filters
            if not self.passes_filters(card_info):
                continue
                
            total_qty = sum(sets_dict.values())
            sets_info = ", ".join([f"{setname}: {qty}" for setname, qty in sets_dict.items()])
            
            self.tree.insert("", "end", values=(
                cardname,
                total_qty,
                sets_info,
                card_info.get("cardtype", ""),
                card_info.get("type", ""),
                card_info.get("monstertype", ""),
                card_info.get("attribute", ""),
                card_info.get("atk", ""),
                card_info.get("def", ""),
                card_info.get("level", ""),
                card_info.get("pscales", ""),
                card_info.get("lcount", ""),
                card_info.get("larrows", ""),
                card_info.get("description", ""),
            ))

    def load_dropdown_names(self):
        try:
            with open("cards.csv", newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                cardnames = sorted(set(row["cardname"].strip() for row in reader if "cardname" in row))
                self.dropdown.options = cardnames
                self.dropdown.update_list()
        except FileNotFoundError:
            messagebox.showerror("Error", "cards.csv not found.")

    def card_selected(self, selected_name):
        if not selected_name:
            return
        self.quantity_var.set("1")

        # Get possible sets for the card from the catalog
        card_info = self.card_catalog.get(selected_name, {})
        if not card_info:
            return
            
        # Get sets from the card info (split by semicolon)
        sets_from_card = []
        if 'cardset' in card_info:
            sets_from_card = [s.strip() for s in card_info['cardset'].split(';') if s.strip()]
        
        # Always include "Crafted Card" as an option
        all_sets = set(sets_from_card)  # Convert to set to remove duplicates
        all_sets.add("Crafted Card")    # Add the crafted card option
        
        # Also include any sets where we already have this card from pulled_cards.csv
        if selected_name in self.card_sets_map:
            all_sets.update(self.card_sets_map[selected_name])
        
        # Sort the sets alphabetically
        sorted_sets = sorted(all_sets)
        
        # Update the combobox
        self.set_name_combo['values'] = sorted_sets
        if sorted_sets:
            self.set_name_var.set(sorted_sets[0])
        else:
            self.set_name_var.set("")

    def load_cards_catalog(self):
        self.card_catalog = {}
        self.card_sets_map = defaultdict(set)  # This will store sets for each card
        
        try:
            with open("cards.csv", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cardname = row.get("cardname", "").strip()
                    if not cardname:
                        continue
                    
                    # Get the set information from the row and split by semicolon
                    cardset = row.get("cardset", "").strip()
                    set_list = [s.strip() for s in cardset.split(';') if s.strip()]
                    
                    # Store all card data
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
                        'cardset': cardset  # Keep original field
                    }
                    
                    # Add each set separately to the sets map
                    for s in set_list:
                        self.card_sets_map[cardname].add(s)
                    
                    # Also add "Crafted Card" as an option
                    self.card_sets_map[cardname].add("Crafted Card")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load card catalog:\n{str(e)}")

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

        row = {
            'cardname': selected_card,
            'cardq': card_quantity,
            'cardrarity': cardrarity,
            'card_edition': "Unlimited",
            'cardset': selected_set,
            'cardcode': cardcode,
            'cardid': cardid,
            'print_id': ""
        }

        # Check if file exists and has headers
        file_exists = os.path.exists("pulled_cards.csv")
        needs_header = not file_exists
        
        if file_exists:
            with open("pulled_cards.csv", 'r', newline='', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                first_row = next(reader, None)
                needs_header = first_row != self.PULLED_CARDS_HEADERS

        with open("pulled_cards.csv", "a", newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.PULLED_CARDS_HEADERS)
            if needs_header:
                writer.writeheader()
            writer.writerow(row)

        messagebox.showinfo("Success", f"Added {selected_card} x{card_quantity} to pulled_cards.csv")
        
        self.deduplicate_pulled_cards()
        self.load_cards()
        self.update_list()

    def load_pulled_cards(self):
        self.card_data = defaultdict(int)  # cardid -> quantity
        try:
            with open("pulled_cards.csv", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cardid = row["cardid"]
                    qty = int(row.get("cardq", 1))
                    self.card_data[cardid] += qty
        except FileNotFoundError:
            pass

    def deduplicate_pulled_cards(self):
        """Deduplicate entries in pulled_cards.csv and sort alphabetically"""
        if not os.path.exists("pulled_cards.csv"):
            return

        deduped = {}
        header = None

        with open("pulled_cards.csv", newline='', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            rows = list(reader)

            if rows and rows[0] == self.PULLED_CARDS_HEADERS:
                header = rows[0]
                rows = rows[1:]

            for row in rows:
                if not row or len(row) < 7:  # Need at least cardname, cardq, and cardid
                    continue

                # Create a key without quantity (cardname + all other fields except quantity)
                key = tuple([row[0]] + row[2:])
                qty = int(row[1]) if row[1].isdigit() else 1
                
                if key in deduped:
                    deduped[key] += qty
                else:
                    deduped[key] = qty

        # Sort alphabetically by card name (case-insensitive)
        sorted_keys = sorted(deduped.keys(), key=lambda x: x[0].lower())

        with open("pulled_cards.csv", "w", newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(self.PULLED_CARDS_HEADERS)
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
        removed = False  # Initialize the removed flag

        with open("pulled_cards.csv", newline='', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            rows = list(reader)

        # Check if first row is header
        if rows and rows[0] == self.PULLED_CARDS_HEADERS:
            header = rows[0]
            rows = rows[1:]

        for row in rows:
            if not row or len(row) < 5:  # Need at least 5 elements (through cardset)
                continue

            row_cardname = row[0].strip()
            row_qty = int(row[1]) if row[1].isdigit() else 0
            row_setname = row[4].strip()  # cardset is index 4

            if row_cardname == cardname and row_setname == setname and not removed:
                if row_qty > qty_to_remove:
                    # Reduce quantity
                    row[1] = str(row_qty - qty_to_remove)
                    updated_rows.append(row)
                # If quantity matches exactly, don't append (remove the row)
                removed = True
            else:
                updated_rows.append(row)

        # Write back to file
        with open("pulled_cards.csv", "w", newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            # Write header if it existed originally
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
        filter_win.geometry("800x600")
        
        # Main container frame
        main_frame = tk.Frame(filter_win)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Card Type Section (unchanged)
        type_frame = tk.LabelFrame(main_frame, text="Card Type", padx=5, pady=5)
        type_frame.pack(fill="x", pady=5)
        
        self.cardtype_vars = {
            'Monster': tk.BooleanVar(),
            'Spell': tk.BooleanVar(),
            'Trap': tk.BooleanVar()
        }
        
        for i, (ctype, var) in enumerate(self.cardtype_vars.items()):
            cb = tk.Checkbutton(type_frame, text=ctype, variable=var)
            cb.grid(row=0, column=i, sticky="w", padx=5)
            if ctype in self.current_filters['cardtype']:
                var.set(True)

        # ===== SUBTYPE SECTION (MOVED BEFORE MONSTER TYPE) =====
        subtype_frame = tk.LabelFrame(main_frame, text="Type", padx=5, pady=5)
        subtype_frame.pack(fill="x", pady=5)
        
        subtypes = [
            'Normal', 'Effect', 'Ritual', 'Fusion', 'Synchro', 'Xyz', 
            'Pendulum', 'Link', 'Flip', 'Toon', 'Union', 'Spirit',
            'Gemini', 'Tuner', 'Field', 'Equip', 'Continuous', 
            'Quick-Play', 'Counter'
        ]
        self.subtype_vars = {st: tk.BooleanVar() for st in subtypes}
        
        for i, subtype in enumerate(subtypes):
            cb = tk.Checkbutton(subtype_frame, text=subtype, variable=self.subtype_vars[subtype])
            cb.grid(row=i//4, column=i%4, sticky="w", padx=5)
            if subtype in self.current_filters['type']:
                self.subtype_vars[subtype].set(True)

        # ===== MONSTER TYPE SECTION (NOW AFTER SUBTYPE) =====
        monster_frame = tk.LabelFrame(main_frame, text="Monster Type", padx=5, pady=5)
        monster_frame.pack(fill="x", pady=5)
        
        monster_types = [
            'Aqua', 'Beast', 'Beast-Warrior', 'Cyberse', 'Dinosaur',
            'Divine-Beast', 'Dragon', 'Fairy', 'Fiend', 'Fish',
            'Insect', 'Machine', 'Plant', 'Psychic', 'Pyro',
            'Reptile', 'Rock', 'Sea Serpent', 'Spellcaster',
            'Thunder', 'Warrior', 'Winged Beast', 'Wyrm', 'Zombie'
        ]
        self.monster_type_vars = {mt: tk.BooleanVar() for mt in monster_types}
        
        for i, mtype in enumerate(monster_types):
            cb = tk.Checkbutton(monster_frame, text=mtype, variable=self.monster_type_vars[mtype])
            cb.grid(row=i//4, column=i%4, sticky="w", padx=5)
            if mtype in self.current_filters['monstertype']:
                self.monster_type_vars[mtype].set(True)
        
        # Attribute and Stats Section
        stats_frame = tk.LabelFrame(main_frame, text="Attributes & Stats", padx=5, pady=5)
        stats_frame.pack(fill="x", pady=5)
        
        # Attributes
        attr_frame = tk.Frame(stats_frame)
        attr_frame.pack(fill="x", pady=5)
        tk.Label(attr_frame, text="Attributes:").pack(side="left")
        
        attributes = ['DARK', 'DIVINE', 'EARTH', 'FIRE', 'LIGHT', 'WATER', 'WIND']
        self.attribute_vars = {a: tk.BooleanVar() for a in attributes}
        
        for attr in attributes:
            cb = tk.Checkbutton(attr_frame, text=attr, variable=self.attribute_vars[attr])
            cb.pack(side="left", padx=5)
            if attr in self.current_filters['attribute']:
                self.attribute_vars[attr].set(True)
        
        # Stats entries
        stats_grid = tk.Frame(stats_frame)
        stats_grid.pack(fill="x", pady=5)
        
        tk.Label(stats_grid, text="Level/Rank:").grid(row=0, column=0, sticky="e")
        self.level_var = tk.StringVar()
        tk.Entry(stats_grid, textvariable=self.level_var, width=5).grid(row=0, column=1, sticky="w")
        
        tk.Label(stats_grid, text="Pendulum Scale:").grid(row=0, column=2, sticky="e")
        self.pscale_var = tk.StringVar()
        tk.Entry(stats_grid, textvariable=self.pscale_var, width=5).grid(row=0, column=3, sticky="w")
        
        tk.Label(stats_grid, text="Link Rating:").grid(row=0, column=4, sticky="e")
        self.link_var = tk.StringVar()
        tk.Entry(stats_grid, textvariable=self.link_var, width=5).grid(row=0, column=5, sticky="w")
        
        # Set current values if they exist
        if self.current_filters['level'] is not None:
            self.level_var.set(str(self.current_filters['level']))
        if self.current_filters['pscales'] is not None:
            self.pscale_var.set(str(self.current_filters['pscales']))
        if self.current_filters['link'] is not None:
            self.link_var.set(str(self.current_filters['link']))
        
        # Button frame
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill="x", pady=10)
        
        def apply_filters():
            self.current_filters = {
                'cardtype': [ctype for ctype, var in self.cardtype_vars.items() if var.get()],
                'type': [st for st, var in self.subtype_vars.items() if var.get()],
                'monstertype': [mt for mt, var in self.monster_type_vars.items() if var.get()],
                'attribute': [attr for attr, var in self.attribute_vars.items() if var.get()],
                'level': int(self.level_var.get()) if self.level_var.get().isdigit() else None,
                'pscales': float(self.pscale_var.get()) if self.pscale_var.get().replace('.', '').isdigit() else None,
                'link': int(self.link_var.get()) if self.link_var.get().isdigit() else None
            }
            filter_win.destroy()
            self.update_list()
        
        def clear_filters():
            for var in self.cardtype_vars.values():
                var.set(False)
            for var in self.subtype_vars.values():
                var.set(False)
            for var in self.monster_type_vars.values():
                var.set(False)
            for var in self.attribute_vars.values():
                var.set(False)
            self.level_var.set("")
            self.pscale_var.set("")
            self.link_var.set("")
        
        tk.Button(button_frame, text="Apply", command=apply_filters).pack(side="left", padx=5)
        tk.Button(button_frame, text="Clear All", command=clear_filters).pack(side="left", padx=5)
        tk.Button(button_frame, text="Cancel", command=filter_win.destroy).pack(side="right", padx=5)

    def passes_filters(self, card_info):
        """Check if card passes all active filters"""
        card_type = card_info.get('cardtype', '')
        is_monster = card_type == 'Monster'
        card_subtypes = card_info.get('type', '').split('; ')
        
        # Card Type filter
        if self.current_filters['cardtype']:
            if card_type not in self.current_filters['cardtype']:
                return False
        
        # Subtype filter
        if self.current_filters['type']:
            if not any(t in card_subtypes for t in self.current_filters['type']):
                return False
        
        # For monster-specific filters, immediately exclude non-monsters
        if (self.current_filters['monstertype'] or 
            self.current_filters['attribute'] or 
            self.current_filters['level'] is not None or
            self.current_filters['pscales'] is not None or
            self.current_filters['link'] is not None):
            if not is_monster:
                return False
        
        # Monster Type filter
        if (self.current_filters['monstertype'] and 
            card_info.get('monstertype') not in self.current_filters['monstertype']):
            return False
        
        # Attribute filter
        if (self.current_filters['attribute'] and 
            card_info.get('attribute') not in self.current_filters['attribute']):
            return False
        
        # Level filter
        if self.current_filters['level'] is not None:
            try:
                if int(card_info.get('level', 0)) != self.current_filters['level']:
                    return False
            except ValueError:
                return False
        
        # Pendulum Scale filter (only for Pendulum monsters)
        if self.current_filters['pscales'] is not None:
            if 'Pendulum' not in card_subtypes:
                return False
            try:
                if float(card_info.get('pscales', 0)) != self.current_filters['pscales']:
                    return False
            except ValueError:
                return False
        
        # Link Rating filter (only for Link monsters)
        if self.current_filters['link'] is not None:
            if 'Link' not in card_subtypes:
                return False
            try:
                if int(card_info.get('lcount', 0)) != self.current_filters['link']:
                    return False
            except ValueError:
                return False
        
        return True
    
    def matches_search(self, cardname, card_info, search_terms):
        """Handle search with AND operator between terms"""
        search_in_name = self.search_mode.get() in ["name", "both"]
        search_in_desc = self.search_mode.get() == "both"
        
        for term in search_terms:
            name_match = term in cardname.lower() if search_in_name else False
            desc_match = term in card_info.get('description', '').lower() if search_in_desc else False
            
            # AND operator - all terms must match
            if not (name_match or desc_match):
                return False
        return True
    
    def show_card_details(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a card first.")
            return

        cardname = self.tree.item(selected_item, "values")[0]
        card_info = self.card_catalog.get(cardname)
        
        if not card_info:
            messagebox.showerror("Error", f"No details found for {cardname}")
            return

        # Create fixed-size details window
        detail_win = tk.Toplevel(self)
        detail_win.title(f"Card Details - {cardname}")
        detail_win.geometry("820x480")
        detail_win.resizable(False, False)
        
        # Main content frame
        main_frame = tk.Frame(detail_win, padx=10, pady=10)
        main_frame.pack(fill="both", expand=True)

        # Image frame (left 40%)
        img_frame = tk.Frame(main_frame, width=300)
        img_frame.pack(side="left", fill="y", padx=(0, 15))
        img_frame.pack_propagate(False)

        # Load card image
        try:
            cardid = card_info.get('cardid', '').strip()
            if cardid:
                img_path = f"card_images/{cardid}.jpg"
                if os.path.exists(img_path):
                    img = Image.open(img_path)
                    img.thumbnail((280, 400))
                    photo = ImageTk.PhotoImage(img)
                    img_label = tk.Label(img_frame, image=photo)
                    img_label.image = photo
                    img_label.pack()
                else:
                    img_label = tk.Label(img_frame, text="Image not found", 
                                    font=("Helvetica", 12), pady=20)
                    img_label.pack()
            else:
                img_label = tk.Label(img_frame, text="No card ID available", 
                                font=("Helvetica", 12), pady=20)
                img_label.pack()
        except Exception as e:
            img_label = tk.Label(img_frame, text="Image load error", 
                            font=("Helvetica", 12), pady=20)
            img_label.pack()
            print(f"Error loading image: {e}")

        # Details frame (right 60%)
        details_frame = tk.Frame(main_frame)
        details_frame.pack(side="right", fill="both", expand=True)

        # Create scrolling canvas
        details_canvas = tk.Canvas(details_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(details_frame, orient="vertical", command=details_canvas.yview)
        scrollable_frame = tk.Frame(details_canvas)

        scrollable_frame.bind("<Configure>", lambda e: details_canvas.configure(scrollregion=details_canvas.bbox("all")))
        details_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=450)
        details_canvas.configure(yscrollcommand=scrollbar.set)

        details_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Configure grid columns for perfect alignment
        scrollable_frame.grid_columnconfigure(0, minsize=120, weight=1)  # Label column
        scrollable_frame.grid_columnconfigure(1, minsize=300, weight=3)  # Value column

        # Field definitions - now with consistent alignment
        FIELD_DEFS = [
            ("Card Type:", 'cardtype'),
            ("Type:", 'type'),
            ("Attribute:", 'attribute'),
            ("Monster Type:", 'monstertype'), 
            ("ATK:", 'atk'),
            ("DEF:", 'def'), 
            ("Level/Rank:", 'level'),
            ("Pendulum Scale:", 'pscales'),
            ("Link Rating:", 'lcount'),
            ("Link Arrows:", 'larrows'),
            ("Rarity:", 'cardrarity'),
            ("Set:", 'cardset')
        ]

        row = 0
        for label_text, field_key in FIELD_DEFS:
            if field_key in card_info and card_info[field_key]:
                # Label
                tk.Label(scrollable_frame,
                    text=label_text,
                    font=("Helvetica", 11, "bold"),
                    anchor="e").grid(row=row, column=0, sticky="w", padx=(5, 5))
                
                # Value
                tk.Label(scrollable_frame,
                    text=card_info[field_key],
                    font=("Helvetica", 11),
                    anchor="w",
                    wraplength=300,
                    justify="left").grid(row=row, column=1, sticky="w")
                row += 1

        # Special handling for Monster Type with perfect alignment
        '''if 'monstertype' in card_info and card_info['monstertype']:
            tk.Label(scrollable_frame,
                text="Monster Type:",
                font=("Helvetica", 11, "bold"),
                anchor="w").grid(row=row, column=0, sticky="w", padx=(5, 5))
            
            tk.Label(scrollable_frame,
                text=card_info['monstertype'],
                font=("Helvetica", 11),
                anchor="w",
                wraplength=300,
                justify="left").grid(row=row, column=1, sticky="w")
            row += 1'''

        # Card description with scrollable text
        if 'description' in card_info and card_info['description']:
            tk.Label(scrollable_frame,
                text="Effect:",
                font=("Helvetica", 11, "bold"),
                anchor="w").grid(row=row, column=0, sticky="w", padx=(5, 5), pady=(5, 0))
            
            desc_text = tk.Text(scrollable_frame,
                            wrap="word",
                            height=5,
                            font=("Helvetica", 11),
                            padx=5,
                            pady=5)
            desc_text.insert("1.0", card_info['description'])
            desc_text.config(state="disabled")
            desc_text.grid(row=row, column=1, sticky="nsew", pady=(5, 0))
            row += 1

        # Close button
        tk.Button(detail_win, text="Close", command=detail_win.destroy).pack(pady=10)

    def open_mdm_link(self):
        """Open the selected card's Master Duel Meta page in default browser"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a card first.")
            return

        try:
            item_values = self.tree.item(selected_item, "values")
            if not item_values:
                messagebox.showwarning("No Data", "Selected item has no data.")
                return
                
            cardname = item_values[0]
            if not cardname:
                messagebox.showwarning("No Name", "Card name is empty.")
                return

            # ===== SPECIAL HANDLING FOR MALISS CARDS =====
            # Handle all variants of angle brackets for Maliss cards
            if "Maliss" in cardname:
                # Replace all angle bracket variants with simple space
                bracket_variants = ['＜', '＞', '<', '>', 'ï¼œ', 'ï¼ž', '｟', '｠']
                for bracket in bracket_variants:
                    cardname = cardname.replace(bracket, ' ')
                # Collapse multiple spaces
                cardname = ' '.join(cardname.split())

            # ===== NORMALIZATION =====
            # Handle Greek letters
            greek_map = {"Ω": "Omega", "β": "Beta"}
            for greek, word in greek_map.items():
                cardname = cardname.replace(greek, word)

            # One-off smart-quote cases
            if cardname == 'Spell Card "Monster Reborn"':
                cardname = 'Spell Card "Monster Reborn"'
            elif cardname == 'Gigantic "Champion" Sargas':
                cardname = 'Gigantic "Champion" Sargas'

            # Global replacements
            cardname = cardname.replace(" - ", " – ")

            # Alternative name mappings
            alt_names = {
                "Alba System Dogmatikalamity": "Dogmatikalamity Alba System",
                "Synchronized Realm": "Synch Realm",
                "Trickstar Band Drumatis": "Trickstar Band Drummatis",
                "Falchionβ": "Falchion Beta",
                "FalchionBeta": "Falchion Beta",
                "Gift of The Mystical Elf": "Gift of the Mystical Elf",
                "Lil-la Rap": "Lil-la-Rap",
                "Man-eating Black Shark": "Man-Eating Black Shark",
                "Performapal Barokuriboh": "Performapal BaroKuriboh",
                "Performapal Classikuriboh": "Performapal ClassiKuriboh",
                "Battlin' Boxer Promoter": "Battlin' Boxer Promoter",
                "Battlin' Boxing Cross Counter": "Battlin' Boxing Cross Counter",
                "Cú Chulainn the Awakened": "Cu Chulainn the Awakened",
                "Machine Lord Ür": "Machine Lord Ur",
                "Mariña, Princess of Sunflowers": "Marina, Princess of Sunflowers",
                "Spell Reactor ・RE": "Spell Reactor RE",
                "Trap Reactor ・Y FI": "Trap Reactor Y FI",
                "Summon Reactor ・SK": "Summon Reactor SK",
            }
            cardname = alt_names.get(cardname, cardname)

            # ===== URL GENERATION =====
            # Clean up extra spaces
            cleaned_name = ' '.join(cardname.split())
            
            # Handle forward slashes first (convert to %2F)
            cleaned_name = cleaned_name.replace('/', '%2F')
            
            # Special URL encoding for MDM
            from urllib.parse import quote
            if cleaned_name.startswith("Maliss "):
                # For Maliss cards, use simple space replacement
                url_name = cleaned_name.replace(' ', '%20')
            else:
                # For other cards, use standard URL encoding
                url_name = quote(cleaned_name)

            url = f"https://www.masterduelmeta.com/cards/{url_name}"

            # Open the URL with two attempts (original and fallback)
            import webbrowser
            if not webbrowser.open(url):
                # Fallback attempt with more aggressive cleaning
                import re
                fallback_name = re.sub(r'[^\w\s-]', '', cleaned_name)
                fallback_name = fallback_name.replace(' ', '%20').replace('/', '%2F')
                fallback_url = f"https://www.masterduelmeta.com/cards/{fallback_name}"
                if not webbrowser.open(fallback_url):
                    messagebox.showerror("Error", f"Could not open URL for: {cardname}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to open browser:\n{str(e)}")



class PackSimulator(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.card_catalog = {}
        self.available_packs = ["Master Pack", "Legacy Pack"]
        self.save_file = "pack_results.json"
        self.current_pack_results = []
        
        # Main container setup
        container = tk.Frame(self)
        container.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Header with back button
        header_frame = tk.Frame(container)
        header_frame.pack(fill="x", pady=(0,5))
        tk.Button(header_frame, text="← Back", 
                command=lambda: controller.show_frame("MainMenuFrame")).pack(side="left")
        tk.Label(header_frame, text="Pack Simulator", font=("Helvetica", 14)).pack(side="left", padx=10)

        # Pack selection row
        pack_frame = tk.Frame(container)
        pack_frame.pack(fill="x", pady=(0,5), padx=5)
        
        tk.Label(pack_frame, text="Select Pack:").grid(row=0, column=0, padx=(0,5), sticky="w")
        self.pack_var = tk.StringVar(value=self.available_packs[0])
        self.pack_dropdown = ttk.Combobox(
            pack_frame, 
            textvariable=self.pack_var, 
            values=self.available_packs,
            state="readonly", 
            width=22
        )
        self.pack_dropdown.grid(row=0, column=1, padx=(0,5), sticky="ew")
        
        # Action buttons
        simulate_btn = tk.Button(pack_frame, text="Open Pack", command=self.simulate_pack, width=9)
        simulate_btn.grid(row=0, column=2, padx=(0,5))
        
        reset_btn = tk.Button(pack_frame, text="Reset", command=self.reset_packs, width=7)
        reset_btn.grid(row=0, column=3, padx=(0,5))

        # Show Card List button remains in the pack frame
        list_btn = tk.Button(pack_frame, text="Show Card List", 
                        command=self.show_card_list, width=12)
        list_btn.grid(row=0, column=4, padx=(5,0))
        
        # Configure column weights
        pack_frame.grid_columnconfigure(1, weight=1)

        # Results treeview
        results_frame = tk.LabelFrame(container, text="Pack Contents")
        results_frame.pack(fill="both", expand=True, pady=5)
        
        self.tree = ttk.Treeview(results_frame, columns=("cardname", "rarity", "pack"), show="headings", height=6)
        self.tree.heading("pack", text="From Pack")
        self.tree.heading("cardname", text="Card Name")
        self.tree.heading("rarity", text="Rarity")
        self.tree.column("cardname", width=200)
        self.tree.column("rarity", width=80)
        self.tree.column("pack", width=120)

        # Configure tags
        self.tree.tag_configure('separator', foreground='gray', font=('Helvetica', 10, 'bold'))
        self.tree.tag_configure('Common', foreground='black')
        self.tree.tag_configure('Rare', foreground='blue')
        self.tree.tag_configure('Super Rare', foreground='green')
        self.tree.tag_configure('Ultra Rare', foreground='gold')
        self.tree.tag_configure('header', font=('Helvetica', 10, 'bold'))
        
        # Scrollbars
        vsb = ttk.Scrollbar(results_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(results_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # Bottom button frame (new frame for the bottom buttons)
        bottom_frame = tk.Frame(container)
        bottom_frame.pack(fill="x", pady=(5,0))
        
        # MDM and Details buttons moved here
        self.mdm_btn = tk.Button(bottom_frame, text="MDM Link", 
                            command=self.open_mdm_for_main_selected, width=9)
        self.mdm_btn.pack(side="left", padx=(0,5))
        self.mdm_btn.config(state="disabled")
        
        self.details_btn = tk.Button(bottom_frame, text="Show Details", 
                                command=self.show_main_card_details, width=11)
        self.details_btn.pack(side="left")
        self.details_btn.config(state="disabled")

        self.show_pulls_btn = tk.Button(
            bottom_frame, 
            text="Show Current Pulls", 
            command=self.show_current_pulls,
            width=15
        )
        self.show_pulls_btn.pack(side="left", padx=5)

        # Add this to the bottom_frame section
        check_packs_btn = tk.Button(bottom_frame, text="Check ALL Available Packs", 
                                command=self.show_all_packs_window, width=20)
        check_packs_btn.pack(side="right", padx=(5,0))

        # Bind selection event
        self.tree.bind('<<TreeviewSelect>>', self.on_main_tree_select)

        # Load initial data
        self.load_card_catalog()
        self.load_pack_results()

    def setup_tree_sorting(self):
        for col in ("cardname", "rarity", "pack"):
            self.tree.heading(col, command=lambda _col=col: self.tree_sort_column(_col, False))
            
    def tree_sort_column(self, col, reverse):
        data = [(self.tree.set(child, col), child) for child in self.tree.get_children('')]
        data.sort(reverse=reverse)
        
        for index, (val, child) in enumerate(data):
            self.tree.move(child, '', index)
        
        self.tree.heading(col, command=lambda: self.tree_sort_column(col, not reverse))

    def load_card_catalog(self):
        """Load all card data for pack unlocking"""
        try:
            with open("cards.csv", newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if 'cardname' in row and 'cardset' in row:
                        self.card_catalog[row['cardname'].strip()] = {
                            'cardset': row['cardset'].strip(),
                            'rarity': row.get('cardrarity', 'Common').strip()
                        }
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load card data:\n{str(e)}")

    def reset_packs(self):
        """Reset all pack simulator state and save history to pull_history folder"""
        if self.current_pack_results:
            # Create pull_history directory if it doesn't exist
            history_dir = "pull_history"
            if not os.path.exists(history_dir):
                os.makedirs(history_dir)
            
            # Save current results to history file
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            history_file = os.path.join(history_dir, f"pull_history_{timestamp}.json")
            
            try:
                with open(history_file, 'w') as f:
                    json.dump({
                        'available_packs': self.available_packs,
                        'current_results': self.current_pack_results,
                        'pack_counter': getattr(self, 'pack_counter', 0),
                        'timestamp': timestamp
                    }, f)
                
                # Notify PullHistory frame to refresh
                if hasattr(self.controller, 'frames') and 'PullHistory' in self.controller.frames:
                    self.controller.frames['PullHistory'].refresh_history()
                    
            except Exception as e:
                print(f"Error saving pull history: {e}")
                messagebox.showerror("Error", f"Failed to save pull history:\n{str(e)}")
        
        # Reset simulator state
        self.available_packs = ["Master Pack", "Legacy Pack"]
        self.current_pack_results = []
        self.pack_counter = 0
        
        # Clear session tracking
        if hasattr(self, 'total_packs_to_open'):
            del self.total_packs_to_open
        if hasattr(self, 'packs_opened'):
            del self.packs_opened
        
        # Reset UI elements
        self.pack_var.set(self.available_packs[0])
        self.pack_dropdown['values'] = self.available_packs
        
        # Clear the treeview display
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Delete the session save file
        try:
            if os.path.exists(self.save_file):
                os.remove(self.save_file)
        except Exception as e:
            print(f"Error deleting save file: {e}")

    def simulate_pack(self):
        """Simulate pack opening with progress tracking and pack unlocking"""
        selected_pack = self.pack_var.get()
        if not selected_pack:
            return

        # First-time pack opening confirmation
        if not hasattr(self, 'pack_counter') or getattr(self, 'pack_counter', 0) == 0:
            if not hasattr(self, 'total_packs_to_open'):
                answer = simpledialog.askinteger(
                    "Pack Opening", 
                    "How many packs would you like to open?",
                    parent=self,
                    minvalue=1,
                    maxvalue=1000
                )
                if answer is None:  # User cancelled
                    return
                self.total_packs_to_open = answer
                self.packs_opened = 0

        # Initialize counters
        self.pack_counter = getattr(self, 'pack_counter', 0) + 1
        self.packs_opened = getattr(self, 'packs_opened', 0) + 1
        pack_header = f"Pack #{self.pack_counter}: {selected_pack}"

        # Show progress every 5 packs
        if (hasattr(self, 'total_packs_to_open') and 
            self.packs_opened % 5 == 0 and 
            self.packs_opened > 0):
            
            remaining = self.total_packs_to_open - self.packs_opened
            messagebox.showinfo(
                "Opening Progress",
                f"Opened: {self.packs_opened} packs\n"
                f"Remaining: {remaining} packs",
                parent=self
            )

        # Check completion
        if hasattr(self, 'total_packs_to_open') and self.packs_opened >= self.total_packs_to_open:
            messagebox.showinfo(
                "Opening Complete",
                f"Finished opening {self.total_packs_to_open} packs!",
                parent=self
            )
            del self.total_packs_to_open
            del self.packs_opened

        # Clear selection and add header
        self.tree.selection_remove(self.tree.selection())
        self.current_pack_results.insert(0, {'type': 'header', 'text': pack_header})

        # Load pack cards
        pack_cards = []
        try:
            with open("cards.csv", newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if selected_pack in row.get('cardset', ''):
                        card_info = {
                            'name': row['cardname'].strip(),
                            'rarity': row.get('cardrarity', 'Common').strip(),
                            'sets': [s.strip() for s in row['cardset'].split(';') if s.strip()]
                        }
                        pack_cards.append(card_info)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load pack data:\n{str(e)}")
            return

        if not pack_cards:
            return

        # Track unlocked packs
        unlocked_packs = set()
        pack_unlocked = False  # Flag for new pack unlock

        # Card selection logic
        commons = [c for c in pack_cards if c['rarity'] == 'Common']
        higher_rarity = [c for c in pack_cards if c['rarity'] != 'Common']

        selected = random.sample(commons, min(5, len(commons)))
        if len(selected) < 5:
            selected.extend(random.sample(pack_cards, 5 - len(selected)))

        rarities = ['Rare']*70 + ['Super Rare']*20 + ['Ultra Rare']*10
        for _ in range(3):
            chosen_rarity = random.choice(rarities)
            candidates = [c for c in higher_rarity if c['rarity'] == chosen_rarity] or higher_rarity
            if candidates:
                card = random.choice(candidates)
                selected.append(card)
                
                # Check for new packs to unlock
                if chosen_rarity in ['Super Rare', 'Ultra Rare']:
                    for pack in card.get('sets', []):
                        if pack and pack not in self.available_packs:
                            self.available_packs.append(pack)
                            unlocked_packs.add(pack)
                            pack_unlocked = True
        
        # Show new pack unlock popup if any were unlocked
        if pack_unlocked:
            self.pack_dropdown['values'] = self.available_packs
            messagebox.showinfo(
                "New Pack Unlocked!",
                f"Congratulations! You unlocked:\n\n" +
                "\n".join(f"• {pack}" for pack in unlocked_packs) +
                f"\n\nfrom {selected_pack}",
                parent=self
            )
        
        # Add cards to results
        for card in selected[:8]:
            card_data = {
                'type': 'card',
                'name': card['name'],
                'rarity': card['rarity'],
                'pack': selected_pack,
                'timestamp': datetime.datetime.now().isoformat()
            }
            self.current_pack_results.insert(1, card_data)
        
        # Update display and save
        self.log_pulled_cards(selected, selected_pack)
        self.save_pack_results()
        self.reload_pack_results()
        self.tree.yview_moveto(0)

    def show_card_list(self):
        """Show all cards in the selected pack with detail and MDM buttons"""
        selected_pack = self.pack_var.get()
        if not selected_pack:
            return

        # Create new window
        list_window = tk.Toplevel(self)
        list_window.title(f"Cards in {selected_pack}")
        list_window.geometry("900x650")

        # Main container
        container = tk.Frame(list_window)
        container.pack(fill="both", expand=True, padx=10, pady=10)
        container.grid_rowconfigure(1, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Header frame
        header_frame = tk.Frame(container)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0,10))
        
        tk.Label(header_frame, 
                text=f"Cards in {selected_pack} ({len(self.get_pack_cards(selected_pack))} cards)",
                font=("Helvetica", 12)).pack(side="left")

        # Treeview with scrollbars
        tree_frame = tk.Frame(container)
        tree_frame.grid(row=1, column=0, sticky="nsew")

        columns = ("cardname", "cardtype", "type", "monstertype", "attribute", 
                  "atk", "def", "level", "rarity")
        
        self.list_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=20)
        
        # Configure columns (same as Collection Manager)
        self.list_tree.heading("cardname", text="Card Name")
        self.list_tree.heading("cardtype", text="Card Type")
        self.list_tree.heading("type", text="Type")
        self.list_tree.heading("monstertype", text="Monster Type")
        self.list_tree.heading("attribute", text="Attribute")
        self.list_tree.heading("atk", text="ATK")
        self.list_tree.heading("def", text="DEF")
        self.list_tree.heading("level", text="Level")
        self.list_tree.heading("rarity", text="Rarity")

        self.list_tree.column("cardname", width=180)
        self.list_tree.column("cardtype", width=80)
        self.list_tree.column("type", width=100)
        self.list_tree.column("monstertype", width=120)
        self.list_tree.column("attribute", width=80)
        self.list_tree.column("atk", width=50, anchor="center")
        self.list_tree.column("def", width=50, anchor="center")
        self.list_tree.column("level", width=50, anchor="center")
        self.list_tree.column("rarity", width=80)

        # Add scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.list_tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.list_tree.xview)
        self.list_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.list_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Button frame
        button_frame = tk.Frame(container)
        button_frame.grid(row=2, column=0, sticky="ew", pady=(10,0))

        details_btn = tk.Button(button_frame, text="Show Card Details", 
                              command=self.show_card_details_from_list, width=15)
        details_btn.pack(side="left", padx=5)

        mdm_btn = tk.Button(button_frame, text="Open MDM Link", 
                           command=self.open_mdm_for_selected, width=15)
        mdm_btn.pack(side="left", padx=5)

        close_btn = tk.Button(button_frame, text="Close", 
                            command=list_window.destroy, width=10)
        close_btn.pack(side="right", padx=5)

        # Load cards
        for card in self.get_pack_cards(selected_pack):
            self.list_tree.insert("", "end", values=(
                card['name'],
                card.get('cardtype', ''),
                card.get('type', ''),
                card.get('monstertype', ''),
                card.get('attribute', ''),
                card.get('atk', ''),
                card.get('def', ''),
                card.get('level', ''),
                card.get('rarity', '')
            ))

    def get_pack_cards(self, pack_name):
        """Return list of all cards in specified pack"""
        pack_cards = []
        try:
            with open("cards.csv", newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if pack_name in row.get('cardset', ''):
                        pack_cards.append({
                            'name': row['cardname'].strip(),
                            'cardtype': row.get('cardtype', '').strip(),
                            'type': row.get('type', '').strip(),
                            'monstertype': row.get('monstertype', '').strip(),
                            'attribute': row.get('attribute', '').strip(),
                            'atk': row.get('atk', '').strip(),
                            'def': row.get('def', '').strip(),
                            'level': row.get('level', '').strip(),
                            'rarity': row.get('cardrarity', 'Common').strip(),
                            'description': row.get('description', '').strip(),
                            'cardid': row.get('cardid', '').strip()
                        })
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load pack cards:\n{str(e)}")
        return pack_cards

    def show_card_details_from_list(self):
        """Show details for selected card in list window"""
        selected = self.list_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a card first")
            return

        card_name = self.list_tree.item(selected[0], "values")[0]
        card_data = self.get_card_data(card_name)
        
        if not card_data:
            messagebox.showerror("Error", f"Could not find data for {card_name}")
            return

        self.show_card_details(card_data)

    def show_main_card_details(self):
        """Show details for card selected in main window"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a card first")
            return
        
        card_name = self.tree.item(selected[0], "values")[0]
        card_data = self.get_card_data(card_name)
        
        if not card_data:
            messagebox.showerror("Error", f"Could not find data for {card_name}")
            return

        self.show_card_details(card_data)

    def show_card_details(self, card_data):
        """Show details for a card (used by both main window and list window)"""
        # Create details window
        detail_win = tk.Toplevel(self)
        detail_win.title(f"Card Details - {card_data['name']}")
        detail_win.geometry("820x480")

        # Main content frame
        main_frame = tk.Frame(detail_win, padx=10, pady=10)
        main_frame.pack(fill="both", expand=True)

        # Image frame (left 40%)
        img_frame = tk.Frame(main_frame, width=300)
        img_frame.pack(side="left", fill="y", padx=(0, 15))
        img_frame.pack_propagate(False)

        # Load card image
        try:
            cardid = card_data.get('cardid', '').strip()
            if cardid:
                img_path = f"card_images/{cardid}.jpg"
                if os.path.exists(img_path):
                    img = Image.open(img_path)
                    img.thumbnail((280, 400))
                    photo = ImageTk.PhotoImage(img)
                    img_label = tk.Label(img_frame, image=photo)
                    img_label.image = photo
                    img_label.pack()
                else:
                    img_label = tk.Label(img_frame, text="Image not found", 
                                    font=("Helvetica", 12), pady=20)
                    img_label.pack()
            else:
                img_label = tk.Label(img_frame, text="No card ID available", 
                                font=("Helvetica", 12), pady=20)
                img_label.pack()
        except Exception as e:
            img_label = tk.Label(img_frame, text="Image load error", 
                            font=("Helvetica", 12), pady=20)
            img_label.pack()
            print(f"Error loading image: {e}")

        # Details frame (right 60%)
        details_frame = tk.Frame(main_frame)
        details_frame.pack(side="right", fill="both", expand=True)

        # Create scrolling canvas
        details_canvas = tk.Canvas(details_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(details_frame, orient="vertical", command=details_canvas.yview)
        scrollable_frame = tk.Frame(details_canvas)

        scrollable_frame.bind("<Configure>", lambda e: details_canvas.configure(scrollregion=details_canvas.bbox("all")))
        details_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=450)
        details_canvas.configure(yscrollcommand=scrollbar.set)

        details_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Configure grid columns
        scrollable_frame.grid_columnconfigure(0, minsize=120, weight=1)
        scrollable_frame.grid_columnconfigure(1, minsize=300, weight=3)

        # Field definitions
        FIELD_DEFS = [
            ("Card Type:", 'cardtype'),
            ("Type:", 'type'),
            ("Attribute:", 'attribute'),
            ("Monster Type:", 'monstertype'), 
            ("ATK:", 'atk'),
            ("DEF:", 'def'), 
            ("Level/Rank:", 'level'),
            ("Pendulum Scale:", 'pscales'),
            ("Link Rating:", 'lcount'),
            ("Link Arrows:", 'larrows'),
            ("Rarity:", 'rarity'),
            ("Set:", 'cardset')
        ]

        row = 0
        for label_text, field_key in FIELD_DEFS:
            if field_key in card_data and card_data[field_key]:
                tk.Label(scrollable_frame,
                    text=label_text,
                    font=("Helvetica", 11, "bold"),
                    anchor="w").grid(row=row, column=0, sticky="w", padx=(5, 5))
                
                tk.Label(scrollable_frame,
                    text=card_data[field_key],
                    font=("Helvetica", 11),
                    anchor="w",
                    wraplength=300,
                    justify="left").grid(row=row, column=1, sticky="w")
                row += 1

        # Monster Type special handling
        '''if 'monstertype' in card_data and card_data['monstertype']:
            tk.Label(scrollable_frame,
                text="Monster Type:",
                font=("Helvetica", 11, "bold"),
                anchor="w").grid(row=row, column=0, sticky="w", padx=(5, 5))
            
            tk.Label(scrollable_frame,
                text=card_data['monstertype'],
                font=("Helvetica", 11),
                anchor="w",
                wraplength=300,
                justify="left").grid(row=row, column=1, sticky="w")
            row += 1'''

        # Card description - Left-aligned version
        if 'description' in card_data and card_data['description']:
            # Effect label - left aligned like others
            effect_label = tk.Label(scrollable_frame,
                text="Effect:",
                font=("Helvetica", 11, "bold"),
                anchor="w")
            effect_label.grid(row=row, column=0, sticky="nw", padx=(5, 5), pady=(5, 0))
            
            # Text widget for description
            desc_text = tk.Text(scrollable_frame,
                            wrap="word",
                            height=5,
                            font=("Helvetica", 11),
                            padx=5,
                            pady=5)
            desc_text.insert("1.0", card_data['description'])
            desc_text.config(state="disabled")
            # Span both columns for the description text
            desc_text.grid(row=row, column=1, columnspan=1, sticky="nsew", pady=(5, 0))
            row += 1

        # Close button
        tk.Button(detail_win, text="Close", command=detail_win.destroy).pack(pady=10)

    def open_mdm_for_selected(self):
        """Open MDM page for selected card in list window"""
        selected = self.list_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a card first")
            return

        card_name = self.list_tree.item(selected[0], "values")[0]
        self.open_mdm_link(card_name)

    def get_card_data(self, card_name):
        """Get complete data for specific card"""
        try:
            with open("cards.csv", newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row['cardname'].strip() == card_name:
                        return {
                            'name': card_name,
                            'cardtype': row.get('cardtype', '').strip(),
                            'type': row.get('type', '').strip(),
                            'monstertype': row.get('monstertype', '').strip(),
                            'attribute': row.get('attribute', '').strip(),
                            'atk': row.get('atk', '').strip(),
                            'def': row.get('def', '').strip(),
                            'level': row.get('level', '').strip(),
                            'rarity': row.get('cardrarity', 'Common').strip(),
                            'description': row.get('description', '').strip(),
                            'cardid': row.get('cardid', '').strip(),
                            'cardset': row.get('cardset', '').strip()
                        }
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load card data:\n{str(e)}")
        return None

    def open_mdm_link(self, card_name):
        """Open Master Duel Meta page for card (works for both windows)"""
        if not card_name:
            messagebox.showwarning("No Name", "Card name is empty.")
            return

        try:
            # Handle special characters and formatting
            cardname = card_name
            
            # Special handling for Maliss cards
            if "Maliss" in cardname:
                bracket_variants = ['＜', '＞', '<', '>', 'ï¼œ', 'ï¼ž', '｟', '｠']
                for bracket in bracket_variants:
                    cardname = cardname.replace(bracket, ' ')
                cardname = ' '.join(cardname.split())

            # Handle Greek letters
            greek_map = {"Ω": "Omega", "β": "Beta"}
            for greek, word in greek_map.items():
                cardname = cardname.replace(greek, word)

            # One-off smart-quote cases
            if cardname == 'Spell Card "Monster Reborn"':
                cardname = 'Spell Card "Monster Reborn"'
            elif cardname == 'Gigantic "Champion" Sargas':
                cardname = 'Gigantic "Champion" Sargas'

            # Alternative name mappings
            name_fixes = {
                "Alba System Dogmatikalamity": "Dogmatikalamity Alba System",
                "Synchronized Realm": "Synch Realm",
                "Trickstar Band Drumatis": "Trickstar Band Drummatis",
                "Falchionβ": "Falchion Beta",
                "FalchionBeta": "Falchion Beta",
                "Gift of The Mystical Elf": "Gift of the Mystical Elf",
                "Lil-la Rap": "Lil-la-Rap",
                "Man-eating Black Shark": "Man-Eating Black Shark",
                "Performapal Barokuriboh": "Performapal BaroKuriboh",
                "Performapal Classikuriboh": "Performapal ClassiKuriboh",
                "Battlin' Boxer Promoter": "Battlin' Boxer Promoter",
                "Battlin' Boxing Cross Counter": "Battlin' Boxing Cross Counter",
                "Cú Chulainn the Awakened": "Cu Chulainn the Awakened",
                "Machine Lord Ür": "Machine Lord Ur",
                "Mariña, Princess of Sunflowers": "Marina, Princess of Sunflowers",
                "Spell Reactor ・RE": "Spell Reactor RE",
                "Trap Reactor ・Y FI": "Trap Reactor Y FI",
                "Summon Reactor ・SK": "Summon Reactor SK",
            }
            cardname = name_fixes.get(cardname, cardname)

            # Clean up name for URL - Keep regular hyphens as-is
            from urllib.parse import quote
            cleaned_name = ' '.join(cardname.split())
            
            # Handle special URL encoding cases
            if cleaned_name.startswith("Maliss "):
                url_name = cleaned_name.replace(' ', '%20')
            else:
                # First replace forward slashes
                cleaned_name = cleaned_name.replace('/', '%2F')
                # Then URL encode while preserving hyphens
                url_name = quote(cleaned_name).replace('%20%E2%80%93%20', ' - ')  # Fix en-dashes
                url_name = url_name.replace('%20-%20', ' - ')  # Fix regular hyphens

            # Construct MDM URL
            url = f"https://www.masterduelmeta.com/cards/{url_name}"

            # Open in browser
            import webbrowser
            if not webbrowser.open(url):
                # Fallback attempt if first fails
                import re
                fallback_name = re.sub(r'[^\w\s-]', '', cleaned_name)
                fallback_name = fallback_name.replace(' ', '%20').replace('/', '%2F')
                fallback_url = f"https://www.masterduelmeta.com/cards/{fallback_name}"
                if not webbrowser.open(fallback_url):
                    messagebox.showerror("Error", f"Could not open URL for: {card_name}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to open browser:\n{str(e)}")

    def on_main_tree_select(self, event):
        """Enable/disable buttons based on main tree selection"""
        selected = self.tree.selection()
        if selected and not self.tree.item(selected[0], "tags") == ('notification',):
            self.details_btn.config(state="normal")
            self.mdm_btn.config(state="normal")
        else:
            self.details_btn.config(state="disabled")
            self.mdm_btn.config(state="disabled")

    def open_mdm_for_main_selected(self):
        """Open MDM for card selected in main window"""
        selected = self.tree.selection()
        if not selected:
            return
        card_name = self.tree.item(selected[0], "values")[0]
        self.open_mdm_link(card_name)

    def save_pack_results(self):
        """Save all pack simulator state"""
        try:
            with open(self.save_file, 'w') as f:
                json.dump({
                    'available_packs': self.available_packs,
                    'current_results': self.current_pack_results,
                    'pack_counter': getattr(self, 'pack_counter', 0),
                    'total_packs_to_open': getattr(self, 'total_packs_to_open', None),
                    'packs_opened': getattr(self, 'packs_opened', 0)
                }, f)
        except Exception as e:
            print(f"Error saving pack results: {e}")

    def load_pack_results(self):
        """Load all pack simulator state"""
        try:
            if os.path.exists(self.save_file):
                with open(self.save_file, 'r') as f:
                    data = json.load(f)
                    self.available_packs = data.get('available_packs', ["Master Pack", "Legacy Pack"])
                    self.current_pack_results = data.get('current_results', [])
                    self.pack_counter = data.get('pack_counter', 0)
                    self.total_packs_to_open = data.get('total_packs_to_open', None)
                    self.packs_opened = data.get('packs_opened', 0)
                    
                    self.pack_var.set(self.available_packs[0])
                    self.pack_dropdown['values'] = self.available_packs
                    self.reload_pack_results()
        except Exception as e:
            print(f"Error loading pack results: {e}")

    def reload_pack_results(self):
        """Reload all packs with newest first and proper separators"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        need_separator = False
        
        for item in self.current_pack_results:
            if isinstance(item, dict):
                if item.get('type') == 'header':
                    if need_separator:
                        self.tree.insert("", "end", 
                                    values=("―"*40, "", ""),
                                    tags=("separator",))
                    need_separator = True
                    
                    self.tree.insert("", "end",
                                values=(item['text'], "", ""),
                                tags=("header",))  # This will now use the bold font
                
                elif item.get('type') == 'card':
                    self.tree.insert("", "end",
                                values=(item['name'], item['rarity'], item.get('pack', '')),
                                tags=(item['rarity'],))
        
        if self.current_pack_results:
            self.tree.yview_moveto(0)

    def show_all_packs_window(self):
        """Create window showing all packs from CSV with their cards"""
        packs_window = tk.Toplevel(self)
        packs_window.title("All Packs from Card Database")
        packs_window.geometry("800x600")
        
        # Main container
        container = tk.Frame(packs_window)
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Pack selection frame
        selection_frame = tk.Frame(container)
        selection_frame.pack(fill="x", pady=(0,10))
        
        tk.Label(selection_frame, text="Select Pack:").pack(side="left", padx=(0,5))
        
        self.all_packs_var = tk.StringVar()
        all_packs_list = self.get_all_packs_from_csv()  # Get ALL packs from CSV
        
        self.all_packs_dropdown = ttk.Combobox(
            selection_frame,
            textvariable=self.all_packs_var,
            values=all_packs_list,
            state="readonly",
            width=30
        )
        self.all_packs_dropdown.pack(side="left", padx=(0,10))
        self.all_packs_dropdown.bind("<<ComboboxSelected>>", self.update_all_packs_table)
        
        # Rest of the method remains the same...
        action_frame = tk.Frame(container)
        action_frame.pack(fill="x", pady=(0,10))
        
        self.all_packs_mdm_btn = tk.Button(
            action_frame, 
            text="MDM Link", 
            command=self.open_mdm_for_all_packs_selected,
            width=10,
            state="disabled"
        )
        self.all_packs_mdm_btn.pack(side="left", padx=(0,5))
        
        self.all_packs_details_btn = tk.Button(
            action_frame, 
            text="Show Details", 
            command=self.show_all_packs_card_details,
            width=12,
            state="disabled"
        )
        self.all_packs_details_btn.pack(side="left")
        
        # Treeview frame
        tree_frame = tk.Frame(container)
        tree_frame.pack(fill="both", expand=True)
        
        # Create treeview
        self.all_packs_tree = ttk.Treeview(
            tree_frame,
            columns=("cardname", "rarity"),
            show="headings",
            height=20
        )
        self.all_packs_tree.heading("cardname", text="Card Name")
        self.all_packs_tree.heading("rarity", text="Rarity")
        self.all_packs_tree.column("cardname", width=400)
        self.all_packs_tree.column("rarity", width=100)
        
        # Configure tags for rarity colors
        self.all_packs_tree.tag_configure('Common', foreground='black')
        self.all_packs_tree.tag_configure('Rare', foreground='blue')
        self.all_packs_tree.tag_configure('Super Rare', foreground='green')
        self.all_packs_tree.tag_configure('Ultra Rare', foreground='gold')
        
        # Add scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.all_packs_tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.all_packs_tree.xview)
        self.all_packs_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.all_packs_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Bind selection event
        self.all_packs_tree.bind('<<TreeviewSelect>>', self.on_all_packs_tree_select)
        
        # Set default to first pack if available
        if all_packs_list:
            self.all_packs_var.set(all_packs_list[0])
            self.update_all_packs_table()

    def update_all_packs_table(self, event=None):
        """Update the table with cards from selected pack, sorted by rarity"""
        selected_pack = self.all_packs_var.get()
        if not selected_pack:
            return
        
        # Clear current items
        for item in self.all_packs_tree.get_children():
            self.all_packs_tree.delete(item)
        
        # Get cards for selected pack
        pack_cards = self.get_pack_cards(selected_pack)
        
        # Sort by rarity (Ultra Rare > Super Rare > Rare > Common)
        rarity_order = {'Ultra Rare': 0, 'Super Rare': 1, 'Rare': 2, 'Common': 3}
        pack_cards.sort(key=lambda x: rarity_order.get(x.get('rarity', 'Common'), 3))
        
        # Add to treeview
        for card in pack_cards:
            rarity = card.get('rarity', 'Common')
            self.all_packs_tree.insert(
                "", "end", 
                values=(card['name'], rarity),
                tags=(rarity,)
            )

    def on_all_packs_tree_select(self, event):
        """Enable/disable buttons based on selection in all packs window"""
        selected = self.all_packs_tree.selection()
        if selected:
            self.all_packs_mdm_btn.config(state="normal")
            self.all_packs_details_btn.config(state="normal")
        else:
            self.all_packs_mdm_btn.config(state="disabled")
            self.all_packs_details_btn.config(state="disabled")

    def open_mdm_for_all_packs_selected(self):
        """Open MDM for selected card in all packs window"""
        selected = self.all_packs_tree.selection()
        if not selected:
            return
        card_name = self.all_packs_tree.item(selected[0], "values")[0]
        self.open_mdm_link(card_name)

    def show_all_packs_card_details(self):
        """Show details for selected card in all packs window"""
        selected = self.all_packs_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a card first")
            return
        
        card_name = self.all_packs_tree.item(selected[0], "values")[0]
        card_data = self.get_card_data(card_name)
        
        if not card_data:
            messagebox.showerror("Error", f"Could not find data for {card_name}")
            return
        
        self.show_card_details(card_data)

    def get_all_packs_from_csv(self):
        """Get all unique pack names from cards.csv"""
        all_packs = set()
        try:
            with open("cards.csv", newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if 'cardset' in row:
                        packs = [p.strip() for p in row['cardset'].split(';') if p.strip()]
                        all_packs.update(packs)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load pack data:\n{str(e)}")
        return sorted(all_packs)

    def log_pulled_cards(self, cards, pack_name):
        """Log pulled cards to pulled_cards.csv file"""
        try:
            file_exists = os.path.exists("pulled_cards.csv")
            needs_header = not file_exists
            
            if file_exists:
                with open("pulled_cards.csv", 'r', newline='', encoding='utf-8-sig') as f:
                    reader = csv.reader(f)
                    first_row = next(reader, None)
                    needs_header = first_row != CollectionManager.PULLED_CARDS_HEADERS

            with open("pulled_cards.csv", "a", newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=CollectionManager.PULLED_CARDS_HEADERS)
                if needs_header:
                    writer.writeheader()
                    
                for card in cards:
                    card_info = self.get_card_data(card['name'])
                    if not card_info:
                        continue
                        
                    row = {
                        'cardname': card['name'],
                        'cardq': '1',  # Each card is 1 copy
                        'cardrarity': card['rarity'],
                        'card_edition': "Unlimited",
                        'cardset': pack_name,
                        'cardcode': pack_name.replace(" ", "")[:4] + card_info.get('cardid', ''),
                        'cardid': card_info.get('cardid', ''),
                        'print_id': ""
                    }
                    writer.writerow(row)
                    
            # Notify Collection Manager to deduplicate and refresh
            self.notify_collection_manager()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to log pulled cards:\n{str(e)}")

    def notify_collection_manager(self):
        """Notify the Collection Manager to refresh and deduplicate its data"""
        if hasattr(self.controller, 'frames') and 'CollectionManager' in self.controller.frames:
            collection_manager = self.controller.frames['CollectionManager']
            collection_manager.deduplicate_pulled_cards()  # Deduplicate first
            collection_manager.load_cards()                # Then reload
            collection_manager.update_list()               # Finally update the view

    def show_current_pulls(self):
        """Show a treeview of all cards pulled in the current session."""
        if not self.current_pack_results:
            messagebox.showinfo("No Pulls Yet", "You haven't pulled any cards yet!")
            return

        # Create a new window
        pulls_window = tk.Toplevel(self)
        pulls_window.title("Current Session Pulls")
        pulls_window.geometry("700x600")

        # Create the treeview
        tree = ttk.Treeview(pulls_window)
        tree.pack(expand=True, fill="both", padx=10, pady=10)

        # Configure columns
        tree["columns"] = ("rarity", "pack")
        tree.heading("#0", text="Card Name", anchor="w")
        tree.heading("rarity", text="Rarity")
        tree.heading("pack", text="From Pack")

        # Set column widths
        tree.column("#0", width=300)
        tree.column("rarity", width=100)
        tree.column("pack", width=150)

        # Organize pulls by rarity (Ultra Rare > Super Rare > Rare > Common)
        rarity_order = {"Ultra Rare": 0, "Super Rare": 1, "Rare": 2, "Common": 3}
        pulls_by_rarity = {}

        for item in self.current_pack_results:
            if isinstance(item, dict) and item.get("type") == "card":
                rarity = item["rarity"]
                if rarity not in pulls_by_rarity:
                    pulls_by_rarity[rarity] = []
                pulls_by_rarity[rarity].append(item)

        # Sort rarities (highest first)
        sorted_rarities = sorted(pulls_by_rarity.keys(), key=lambda x: rarity_order.get(x, 4))

        # Populate the tree
        for rarity in sorted_rarities:
            rarity_node = tree.insert("", "end", text=f"{rarity} ({len(pulls_by_rarity[rarity])} cards)", open=True)
            
            # Group cards by name (to avoid duplicates)
            card_counts = {}
            for card in pulls_by_rarity[rarity]:
                name = card["name"]
                if name not in card_counts:
                    card_counts[name] = {"count": 0, "packs": set()}
                card_counts[name]["count"] += 1
                card_counts[name]["packs"].add(card["pack"])

            # Add each card to the tree
            for card_name, data in sorted(card_counts.items()):
                card_node = tree.insert(
                    rarity_node, 
                    "end", 
                    text=f"{card_name} (x{data['count']})",
                    values=(rarity, ", ".join(data["packs"])))



class PullHistory(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.history_files = []
        
        # Main container
        container = tk.Frame(self)
        container.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Header frame
        header_frame = tk.Frame(container)
        header_frame.pack(fill="x", pady=(0,5))
        
        tk.Button(header_frame, text="← Back", 
                command=lambda: controller.show_frame("MainMenuFrame")).pack(side="left")
        tk.Label(header_frame, text="Pull History", font=("Helvetica", 14)).pack(side="left", padx=10)
        
        # History selection frame
        selection_frame = tk.Frame(container)
        selection_frame.pack(fill="x", pady=(0,10))
        
        tk.Label(selection_frame, text="Select History:").pack(side="left", padx=(0,5))
        
        self.history_var = tk.StringVar()
        self.history_dropdown = ttk.Combobox(
            selection_frame, 
            textvariable=self.history_var,
            state="readonly",
            width=30
        )
        self.history_dropdown.pack(side="left", padx=(0,10))
        self.history_dropdown.bind("<<ComboboxSelected>>", self.load_history)
        
        # Button frame
        button_frame = tk.Frame(container)
        button_frame.pack(fill="x", pady=(0,10))
        
        self.details_btn = tk.Button(
            button_frame, 
            text="Show Details", 
            command=self.show_card_details,
            width=12,
            state="disabled"
        )
        self.details_btn.pack(side="left", padx=(0,5))
        
        self.mdm_btn = tk.Button(
            button_frame, 
            text="MDM Link", 
            command=self.open_mdm_link,
            width=10,
            state="disabled"
        )
        self.mdm_btn.pack(side="left")

        self.pack_details_btn = tk.Button(
            button_frame, 
            text="Card Pack Details", 
            command=self.show_card_pack_details,
            width=15
        )
        self.pack_details_btn.pack(side="left", padx=5)
        
        # Treeview frame
        tree_frame = tk.Frame(container)
        tree_frame.pack(fill="both", expand=True)
        
        # Create treeview
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("cardname", "rarity", "pack"),
            show="headings",
            height=20
        )
        self.tree.heading("cardname", text="Card Name")
        self.tree.heading("rarity", text="Rarity")
        self.tree.heading("pack", text="From Pack")
        
        self.tree.column("cardname", width=250)
        self.tree.column("rarity", width=100)
        self.tree.column("pack", width=150)
        
        # Configure tags for rarity colors
        self.tree.tag_configure('Common', foreground='black')
        self.tree.tag_configure('Rare', foreground='blue')
        self.tree.tag_configure('Super Rare', foreground='green')
        self.tree.tag_configure('Ultra Rare', foreground='gold')
        self.tree.tag_configure('header', font=('Helvetica', 10, 'bold'))
        
        # Add scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Bind selection event
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        
        # Load history files
        self.load_history_files()
    
    def load_history_files(self):
        """Find all pull history files in pull_history directory and populate dropdown"""
        self.history_files = []
        history_dir = "pull_history"
        
        try:
            # Check if directory exists
            if os.path.exists(history_dir) and os.path.isdir(history_dir):
                # Look for files matching pull_history_*.json pattern in the directory
                for file in os.listdir(history_dir):
                    if file.startswith('pull_history_') and file.endswith('.json'):
                        full_path = os.path.join(history_dir, file)
                        self.history_files.append(full_path)
                
                # Sort by creation time (newest first)
                self.history_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
                
                # Update dropdown with just the date portion
                display_names = [
                    os.path.basename(f).replace('pull_history_', '').replace('.json', '') 
                    for f in self.history_files
                ]
                self.history_dropdown['values'] = display_names
                
                if display_names:
                    self.history_var.set(display_names[0])
                    self.load_history()
            else:
                # Directory doesn't exist yet, no history files available
                self.history_dropdown['values'] = []
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load history files:\n{str(e)}")
    
    def load_history(self, event=None):
        """Load the selected history file into the treeview"""
        selected_index = self.history_dropdown.current()
        if selected_index == -1 and self.history_files:
            selected_index = 0
        
        if selected_index == -1:
            return
        
        selected_file = self.history_files[selected_index]
        
        # Clear current items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            with open(selected_file, 'r') as f:
                history_data = json.load(f)
                
                # Add headers and cards to treeview
                for item in history_data.get('current_results', []):
                    if item.get('type') == 'header':
                        self.tree.insert("", "end", 
                                    values=(item['text'], "", ""),
                                    tags=('header',))
                    elif item.get('type') == 'card':
                        self.tree.insert("", "end",
                                    values=(item['name'], item['rarity'], item.get('pack', '')),
                                    tags=(item['rarity'],))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load history file:\n{str(e)}")
    
    def on_tree_select(self, event):
        """Enable/disable buttons based on selection"""
        selected = self.tree.selection()
        if selected and not self.tree.item(selected[0], "tags") == ('header',):
            self.details_btn.config(state="normal")
            self.mdm_btn.config(state="normal")
        else:
            self.details_btn.config(state="disabled")
            self.mdm_btn.config(state="disabled")
    
    def show_card_details(self):
        """Show details for selected card"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a card first")
            return
        
        card_name = self.tree.item(selected[0], "values")[0]
        card_data = self.get_card_data(card_name)
        
        if not card_data:
            messagebox.showerror("Error", f"Could not find data for {card_name}")
            return
        
        # Reuse the PackSimulator's show_card_details method
        pack_simulator = self.controller.frames['PackSimulator']
        pack_simulator.show_card_details(card_data)
    
    def open_mdm_link(self):
        """Open MDM page for selected card"""
        selected = self.tree.selection()
        if not selected:
            return
        
        card_name = self.tree.item(selected[0], "values")[0]
        
        # Reuse the PackSimulator's open_mdm_link method
        pack_simulator = self.controller.frames['PackSimulator']
        pack_simulator.open_mdm_link(card_name)
    
    def get_card_data(self, card_name):
        """Get complete data for specific card"""
        # Reuse the PackSimulator's method
        pack_simulator = self.controller.frames['PackSimulator']
        return pack_simulator.get_card_data(card_name)

    def refresh_history(self):
        """Refresh the history file list and reload the selected history"""
        current_selection = self.history_var.get()
        self.load_history_files()
        
        # Try to maintain the same selection if it still exists
        if current_selection in self.history_dropdown['values']:
            self.history_var.set(current_selection)
        elif self.history_dropdown['values']:
            self.history_var.set(self.history_dropdown['values'][0])
        
        self.load_history()
    
    def tkraise(self, *args, **kwargs):
        """Override tkraise to refresh history when this frame is shown"""
        self.refresh_history()
        super().tkraise(*args, **kwargs)

    def show_card_pack_details(self):
        """Show window with all packs containing the selected card"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a card first")
            return
        
        card_name = self.tree.item(selected[0], "values")[0]
        card_data = self.get_card_data(card_name)
        
        if not card_data:
            messagebox.showerror("Error", f"Could not find data for {card_name}")
            return
        
        # Create details window
        details_win = tk.Toplevel(self)
        details_win.title(f"Pack Availability - {card_name}")
        details_win.geometry("800x600")
        
        # Get all packs containing this card
        packs = self.get_packs_for_card(card_name)
        if not packs:
            tk.Label(details_win, text=f"{card_name} not found in any packs").pack(pady=20)
            return
        
        # Pack selection dropdown
        pack_frame = tk.Frame(details_win)
        pack_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(pack_frame, text="Select Pack:").pack(side="left")
        pack_var = tk.StringVar(value=packs[0])
        pack_dropdown = ttk.Combobox(
            pack_frame,
            textvariable=pack_var,
            values=packs,
            state="readonly",
            width=40
        )
        pack_dropdown.pack(side="left", padx=10)
        
        # Treeview to show cards in selected pack
        tree_frame = tk.Frame(details_win)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        columns = ("cardname", "rarity")
        self.pack_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            height=20
        )
        
        self.pack_tree.heading("cardname", text="Card Name")
        self.pack_tree.heading("rarity", text="Rarity")
        self.pack_tree.column("cardname", width=400)
        self.pack_tree.column("rarity", width=100)
        
        # Add scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.pack_tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.pack_tree.xview)
        self.pack_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.pack_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Action buttons
        btn_frame = tk.Frame(details_win)
        btn_frame.pack(fill="x", pady=10)
        
        details_btn = tk.Button(
            btn_frame,
            text="Show Card Details",
            command=lambda: self.show_card_from_pack_tree(self.pack_tree, details_win),
            width=15
        )
        details_btn.pack(side="left", padx=5)
        
        mdm_btn = tk.Button(
            btn_frame,
            text="MDM Link",
            command=lambda: self.open_mdm_from_pack_tree(self.pack_tree),
            width=10
        )
        mdm_btn.pack(side="left", padx=5)
        
        # Load initial pack data
        self.load_pack_cards(pack_var.get())
        
        # Update when pack selection changes
        pack_var.trace_add("write", lambda *_: self.load_pack_cards(pack_var.get()))
        
    def get_packs_for_card(self, card_name):
        """Get all packs containing this card"""
        packs = set()
        try:
            with open("cards.csv", newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row['cardname'].strip() == card_name:
                        packs.update([p.strip() for p in row['cardset'].split(';') if p.strip()])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load pack data: {str(e)}")
        return sorted(packs)
        
    def load_pack_cards(self, pack_name):
        """Load cards from specified pack into the treeview"""
        for item in self.pack_tree.get_children():
            self.pack_tree.delete(item)
        
        try:
            with open("cards.csv", newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if pack_name in row.get('cardset', ''):
                        self.pack_tree.insert("", "end", values=(
                            row['cardname'].strip(),
                            row.get('cardrarity', 'Common').strip()
                        ), tags=(row.get('cardrarity', 'Common').strip(),))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load pack cards: {str(e)}")

    def show_card_from_pack_tree(self, tree, parent_window):
        """Show details for card selected in pack tree"""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a card first", parent=parent_window)
            return
        
        card_name = tree.item(selected[0], "values")[0]
        card_data = self.get_card_data(card_name)
        
        if card_data:
            # Reuse the existing show_card_details method
            pack_simulator = self.controller.frames['PackSimulator']
            pack_simulator.show_card_details(card_data)
        else:
            messagebox.showerror("Error", f"Could not find data for {card_name}", parent=parent_window)

    def open_mdm_from_pack_tree(self, tree):
        """Open MDM for card selected in pack tree"""
        selected = tree.selection()
        if not selected:
            return
        
        card_name = tree.item(selected[0], "values")[0]
        pack_simulator = self.controller.frames['PackSimulator']
        pack_simulator.open_mdm_link(card_name)
        

class Option4Frame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Load local VLC
        script_dir = os.path.dirname(os.path.abspath(__file__))
        vlc_dir = resource_path("vlc")
        dll_path = os.path.join(vlc_dir, 'libvlc.dll')

        if not os.path.exists(dll_path):
            raise FileNotFoundError(f"libvlc.dll not found at: {dll_path}")

        # Windows 10+ specific
        if sys.platform.startswith("win"):
            os.add_dll_directory(vlc_dir)

        ctypes.CDLL(dll_path)

        if os.path.exists(vlc_dir):
            try:
                os.environ["VLC_PLUGIN_PATH"] = os.path.join(vlc_dir, 'plugins')
                dll_path = os.path.join(vlc_dir, 'libvlc.dll')
                print(f"Trying to load: {dll_path}")

                if sys.platform.startswith("win"):
                    os.add_dll_directory(vlc_dir)
                    ctypes.CDLL(dll_path)  # Load DLL manually before importing vlc

                import vlc
                self.vlc = vlc
                self.vlc_loaded = True

            except Exception as e:
                print(f"Failed to load local VLC: {e}")
                messagebox.showwarning("VLC Error", "Could not load local VLC. Trying system VLC...")

        if not self.vlc_loaded:
            try:
                import vlc
                self.vlc = vlc
                self.vlc_loaded = True
            except ImportError:
                messagebox.showerror("VLC Error", "VLC not found. Please install VLC media player.")

        # VLC player references
        self.vlc_instance = None
        self.vlc_player = None
        self.video_window = None

        # Arrow animation setup
        self.arrow_size = 10
        self.arrow_growing = True

        # UI Setup
        container = tk.Frame(self)
        container.pack(expand=True, fill="both", padx=20, pady=20)

        tk.Button(container, text="← Back", command=lambda: controller.show_frame("MainMenuFrame"),
                  font=("Helvetica", 12)).pack(anchor="nw")

        content_frame = tk.Frame(container)
        content_frame.pack(expand=True, fill="both")

        # Left: Image
        try:
            original_img = Image.open(resource_path("Hen2.jpg"))
            width = 300
            ratio = width / original_img.width
            height = int(original_img.height * ratio)
            self.joke_img = original_img.resize((width, height), Image.LANCZOS)
            self.joke_photo = ImageTk.PhotoImage(self.joke_img)
            img_label = tk.Label(content_frame, image=self.joke_photo)
            img_label.grid(row=0, column=0, padx=20, sticky="ns")
        except Exception as e:
            print(f"Error loading image: {e}")
            tk.Label(content_frame, text="[Joke Image]", font=("Helvetica", 24)).grid(row=0, column=0)

        # Right: Arrows and text
        right_side = tk.Frame(content_frame)
        right_side.grid(row=0, column=1, sticky="ns")

        arrow_frame = tk.Frame(right_side)
        arrow_frame.pack(expand=True)

        self.down_arrow = tk.Button(arrow_frame, text="↓", command=self.down_arrow_action,
                                    font=("Helvetica", 14, "bold"), bg="lightblue", fg="black",
                                    padx=15, pady=5)
        self.down_arrow.pack(pady=(0, 5))

        self.joke_text = tk.Label(arrow_frame,
                                  text="Heneaqua is a mother in need",
                                  font=("Helvetica", 14, "bold"),
                                  fg="red", bg="yellow", padx=20, pady=10,
                                  cursor="hand2")
        self.joke_text.pack()
        self.joke_text.bind("<Button-1>", lambda e: self.play_joke_video())

        self.up_arrow = tk.Button(arrow_frame, text="↑", command=self.up_arrow_action,
                                  font=("Helvetica", 14, "bold"), bg="lightblue", fg="black",
                                  padx=15, pady=5)
        self.up_arrow.pack(pady=(5, 0))

        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)

        self.after(100, self.animate_arrows)

    def animate_arrows(self):
        if self.arrow_growing:
            self.arrow_size += 0.5
            if self.arrow_size >= 15:
                self.arrow_growing = False
        else:
            self.arrow_size -= 0.5
            if self.arrow_size <= 10:
                self.arrow_growing = True

        new_padx = int(self.arrow_size)
        self.down_arrow.config(padx=new_padx)
        self.up_arrow.config(padx=new_padx)
        self.after(50, self.animate_arrows)

    def up_arrow_action(self):
        messagebox.showinfo("Up", "You pressed the up arrow!")

    def down_arrow_action(self):
        messagebox.showinfo("Down", "You pressed the down arrow!")

    def play_joke_video(self):
        if not self.vlc_loaded:
            messagebox.showerror("Error", "VLC not available. Cannot play video.")
            return

        if self.video_window and self.video_window.winfo_exists():
            self.video_window.lift()
            return

        self.video_window = tk.Toplevel(self)
        self.video_window.title("Do you see the other side?")
        self.video_window.geometry("800x600")

        video_frame = tk.Frame(self.video_window)
        video_frame.pack(fill=tk.BOTH, expand=True)

        control_frame = tk.Frame(self.video_window)
        control_frame.pack(fill=tk.X, pady=5)

        try:
            self.vlc_instance = self.vlc.Instance([
                '--no-xlib',
                f'--plugin-path={os.environ.get("VLC_PLUGIN_PATH", "")}'
            ])
            self.vlc_player = self.vlc_instance.media_player_new()

            self.video_window.update()
            if sys.platform.startswith('win'):
                self.vlc_player.set_hwnd(video_frame.winfo_id())
            elif sys.platform.startswith('linux'):
                self.vlc_player.set_xwindow(video_frame.winfo_id())
            elif sys.platform.startswith('darwin'):
                self.vlc_player.set_nsobject(video_frame.winfo_id())

            script_dir = os.path.dirname(os.path.abspath(__file__))
            video_path = resource_path("video1.mp4")

            if not os.path.exists(video_path):
                messagebox.showerror("Error", f"Video file not found at: {video_path}")
                self.cleanup_vlc()
                self.video_window.destroy()
                self.video_window = None
                return

            media = self.vlc_instance.media_new_path(video_path)
            self.vlc_player.set_media(media)

            # Create control buttons
            tk.Button(control_frame, text="⏸ Pause", command=self.toggle_pause).pack(side="left", padx=5)
            tk.Button(control_frame, text="⏹ Stop", command=self.stop_video).pack(side="left", padx=5)
            tk.Button(control_frame, text="🔊 Vol+", command=self.volume_up).pack(side="right", padx=5)
            tk.Button(control_frame, text="🔈 Vol-", command=self.volume_down).pack(side="right", padx=5)
            
            # Add the new "Rickroll" button
            tk.Button(control_frame, text="🎵 Surprise! 🎵", 
                     command=self.open_rickroll, 
                     bg="red", fg="white",
                     font=("Helvetica", 10, "bold")).pack(side="left", padx=5)

            if self.vlc_player.play() == -1:
                messagebox.showerror("Error", "Could not play the video")
                self.cleanup_vlc()
                self.video_window.destroy()
                self.video_window = None
                return

            self.video_window.protocol("WM_DELETE_WINDOW", self.stop_video)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize VLC player:\n{str(e)}")
            self.cleanup_vlc()
            if self.video_window:
                self.video_window.destroy()
                self.video_window = None

    def open_rickroll(self):
        """Open the Never Gonna Give You Up YouTube link in default browser"""
        try:
            import webbrowser
            webbrowser.open("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open browser:\n{str(e)}")

    def toggle_pause(self):
        if self.vlc_player:
            self.vlc_player.pause()

    def stop_video(self):
        self.cleanup_vlc()
        if self.video_window:
            self.video_window.destroy()
            self.video_window = None

    def volume_up(self):
        if self.vlc_player:
            current = self.vlc_player.audio_get_volume()
            self.vlc_player.audio_set_volume(min(100, current + 10))

    def volume_down(self):
        if self.vlc_player:
            current = self.vlc_player.audio_get_volume()
            self.vlc_player.audio_set_volume(max(0, current - 10))

    def cleanup_vlc(self):
        if self.vlc_player:
            self.vlc_player.stop()
            self.vlc_player.release()
            self.vlc_player = None
        if self.vlc_instance:
            self.vlc_instance.release()
            self.vlc_instance = None


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

        # Removed Option3Frame from this list
        for F in (MainMenuFrame, CollectionManager, PackSimulator, PullHistory, Option4Frame):
            frame = F(container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MainMenuFrame")

    def show_frame(self, frame_name):
        """Show a frame for the given frame name"""
        frame = self.frames[frame_name]
        frame.tkraise()



if __name__ == "__main__":
    app = AppController()
    app.mainloop()