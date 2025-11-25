import csv
import re
import time
import tkinter as tk
from tkinter import filedialog, messagebox
from collections import defaultdict
import os
from tkinter import ttk
import threading
import tkinter.font as tkFont
import unicodedata

class MainMenuFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Center frame for content
        center_frame = tk.Frame(self)
        center_frame.pack(expand=True, pady=50)
        
        tk.Label(center_frame, text="Yu-Gi-Oh! Collection Manager", font=("Helvetica", 18)).pack(pady=20)

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

class SearchableDropdown:
    def __init__(self, parent, entry_widget, options):
        self.parent = parent
        self.entry = entry_widget
        self.options = options
        self.filtered_options = options.copy()
        self.popup = None
        self.updating = False
        self.allow_popup = False

        # Use parent's StringVar if it exists, otherwise create new
        if not hasattr(self.parent, 'cardname_var'):
            self.parent.cardname_var = tk.StringVar()
        
        self.var = self.parent.cardname_var
        self.entry.config(textvariable=self.var)

        # Bind selection callback to update sets
        self.on_select_callback = None

        # Bind events
        self.entry.bind("<FocusIn>", self.show_popup)
        self.entry.bind("<FocusOut>", self.hide_popup_delayed)
        self.entry.bind("<Escape>", self.close_popup)
        self.entry.bind("<KeyPress-Up>", self.navigate_up)
        self.entry.bind("<KeyPress-Down>", self.navigate_down)
        self.entry.bind("<Return>", self.select_current)
        self.entry.bind("<Button-1>", self.show_popup)
        self.entry.bind("<Tab>", self.close_popup)

        # Track the variable for changes
        self.var.trace_add("write", self.on_type)

        # Delay allowing popups until after initialization
        self.parent.after(100, self.enable_popups)

    def on_type(self, *args):
        if self.updating:
            return
            
        search_term = self.var.get().lower()
        self.filtered_options = [item for item in self.options if search_term in item.lower()]

        # If popup is closed, open it again when typing
        if not self.popup or not self.popup.winfo_exists():
            self.show_popup()

        self.update_popup()

    def show_popup(self, event=None):
        """Show the dropdown popup"""
        if not self.allow_popup:  # Check the flag
            return

        if self.popup and self.popup.winfo_exists():
            return
            
        self.popup = tk.Toplevel(self.parent)
        self.popup.wm_overrideredirect(True)
        
        # Position below the entry widget
        x = self.entry.winfo_rootx()
        y = self.entry.winfo_rooty() + self.entry.winfo_height()
        self.popup.wm_geometry(f"+{x}+{y}")
        
        self.listbox = tk.Listbox(self.popup, height=8, activestyle="dotbox")
        self.listbox.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(self.popup, orient="vertical", command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)

        # Bind selection event
        self.listbox.bind("<<ListboxSelect>>", self.on_select)
        
        # Update with current filtered options
        self.update_popup()

    def get_popup_position(self):
        x = self.entry.winfo_rootx()
        y = self.entry.winfo_rooty() + self.entry.winfo_height()
        return f"+{x}+{y}"

    def update_popup(self):
        if not self.popup or not self.popup.winfo_exists():
            return

        self.listbox.delete(0, tk.END)

        for item in self.filtered_options:
            self.listbox.insert(tk.END, item)

        self.popup.update_idletasks()
        height = self.listbox.winfo_reqheight()
        self.popup.geometry(f"{self.entry.winfo_width()}x{height}+{self.entry.winfo_rootx()}+{self.entry.winfo_rooty() + self.entry.winfo_height()}")

        if self.filtered_options:
            self.popup.deiconify()
        else:
            self.popup.withdraw()

    def on_select(self, event):
        """Handle selection from the dropdown list"""
        widget = event.widget
        try:
            index = widget.curselection()[0]
            value = widget.get(index)
            self.updating = True
            self.var.set(value)
            self.updating = False
            
            # Close the popup immediately
            if self.popup and self.popup.winfo_exists():
                self.popup.destroy()
                self.popup = None
            
            # Return focus to entry
            self.entry.focus_set()
            
            # Call the callback if it exists (with small delay)
            if self.on_select_callback:
                self.parent.after(100, lambda: self.on_select_callback(value))
                
        except IndexError:
            pass

    def _finalize_selection(self):
        """Finalize the selection after a short delay"""
        try:
            if hasattr(self, 'listbox') and self.listbox.winfo_exists():
                index = self.listbox.curselection()[0]
                value = self.listbox.get(index)
                self.updating = True
                self.var.set(value)
                self.updating = False
                self.entry.focus_set()
                
                if self.on_select_callback:
                    self.on_select_callback(value)
        except IndexError:
            pass

        if self.popup and self.popup.winfo_exists():
            self.popup.destroy()
            self.popup = None

    def hide_popup_delayed(self, event=None):
        # Check if focus moved to another widget in our app
        focus = self.parent.focus_get()
        if (focus not in [self.entry, self.popup, self.listbox] if self.popup else focus != self.entry):
            self.parent.after(150, self.try_hide_popup)

    def try_hide_popup(self):
        # Double check focus before closing
        focus = self.parent.focus_get()
        if (focus not in [self.entry, self.popup, self.listbox] if self.popup else focus != self.entry):
            if self.popup and self.popup.winfo_exists():
                self.popup.destroy()
                self.popup = None

    def navigate_up(self, event):
        if not self.popup or not self.popup.winfo_exists():
            self.show_popup()
            return
            
        cur = self.listbox.curselection()
        if cur:
            index = max(cur[0] - 1, 0)
        else:
            index = 0
        self.listbox.select_clear(0, tk.END)
        self.listbox.select_set(index)
        self.listbox.activate(index)
        self.listbox.see(index)

    def navigate_down(self, event):
        if not self.popup or not self.popup.winfo_exists():
            self.show_popup()
            return
            
        cur = self.listbox.curselection()
        if cur:
            index = min(cur[0] + 1, self.listbox.size() - 1)
        else:
            index = 0
        self.listbox.select_clear(0, tk.END)
        self.listbox.select_set(index)
        self.listbox.activate(index)
        self.listbox.see(index)

    def select_current(self, event):
        if self.popup and self.popup.winfo_exists():
            self.popup.destroy()
            self.popup = None
        self.parent.after(50, self._finalize_selection)

    def close_popup(self, event=None):
        if self.popup and self.popup.winfo_exists():
            self.popup.destroy()
            self.popup = None

    def destroy(self):
        if self.popup and self.popup.winfo_exists():
            self.popup.destroy()
        if hasattr(self, 'var'):
            self.var.trace_remove("write", self.on_type)

    def enable_popups(self):
        """Enable popups after initialization is complete"""
        self.allow_popup = True


class SetDropdown:
    def __init__(self, parent, entry_widget, sets):
        self.parent = parent
        self.entry = entry_widget
        self.sets = sets
        self.popup = None
        
        self.var = tk.StringVar()
        self.entry.config(textvariable=self.var)
        
        # Bind events
        self.entry.bind("<FocusIn>", self.show_popup)
        self.entry.bind("<Button-1>", self.toggle_popup)
        self.parent.bind("<Button-1>", self.check_click_outside)
        self.entry.bind("<Tab>", self.hide_popup)
        self.entry.bind("<Return>", self.hide_popup)

    def toggle_popup(self, event=None):
        """Toggle the popup visibility"""
        if self.popup and self.popup.winfo_exists():
            self.hide_popup()
        else:
            self.show_popup()

    def check_click_outside(self, event):
        """Check if click occurred outside dropdown"""
        if not self.popup or not self.popup.winfo_exists():
            return
            
        # Get the widget that was clicked
        clicked_widget = event.widget
        
        # Check if click was outside our dropdown widgets
        if clicked_widget not in [self.entry, self.popup] and (
            not hasattr(self, 'listbox') or clicked_widget != self.listbox
        ):
            self.hide_popup()

    def show_popup(self, event=None):
        """Show the set dropdown popup"""
        if self.popup and self.popup.winfo_exists():
            return
            
        if not self.sets:
            return
            
        self.popup = tk.Toplevel(self.parent)
        self.popup.wm_overrideredirect(True)
        
        # Calculate required width based on longest set name
        font = tkFont.Font(font=self.entry.cget("font"))
        max_width = max(font.measure(set_name) for set_name in self.sets) + 20  # Add padding
        popup_width = min(max_width, 400)  # Set maximum width if needed
        
        # Position below the entry widget
        x = self.entry.winfo_rootx()
        y = self.entry.winfo_rooty() + self.entry.winfo_height()
        self.popup.wm_geometry(f"{popup_width}x200+{x}+{y}")  # Set fixed height or calculate dynamically
        
        self.listbox = tk.Listbox(self.popup, height=6, exportselection=False, width=0)  # width=0 allows dynamic sizing
        self.listbox.pack(fill="both", expand=True)
        
        for set_name in self.sets:
            self.listbox.insert(tk.END, set_name)
            
        # Bind selection events
        self.listbox.bind("<<ListboxSelect>>", self.on_select)
        self.listbox.bind("<ButtonRelease-1>", self.on_item_click)
        
        # Make sure popup closes when losing focus
        self.popup.bind("<FocusOut>", lambda e: self.hide_popup())

    def on_item_click(self, event):
        """Handle mouse click on listbox items"""
        # Get the clicked item immediately
        widget = event.widget
        try:
            index = widget.nearest(event.y)
            value = widget.get(index)
            self.var.set(value)
        except IndexError:
            pass
        self.hide_popup()

    def on_select(self, event):
        """Handle selection from the set dropdown"""
        widget = event.widget
        try:
            index = widget.curselection()[0]
            value = widget.get(index)
            self.var.set(value)
            self.hide_popup()  # Close immediately after selection
        except IndexError:
            pass

    def finalize_selection(self):
        """Finalize the selection and close the popup"""
        if hasattr(self, 'listbox') and self.listbox.winfo_exists():
            try:
                index = self.listbox.curselection()[0]
                value = self.listbox.get(index)
                self.var.set(value)
            except IndexError:
                pass
                
        self.hide_popup()
        self.entry.focus_set()
            
    def hide_popup(self, event=None):
        """Hide the popup immediately"""
        if self.popup and self.popup.winfo_exists():
            self.popup.destroy()
            self.popup = None
        self.entry.focus_set()

    def destroy(self):
        """Clean up resources"""
        self.hide_popup()
        self.entry.unbind("<FocusIn>")
        self.entry.unbind("<Button-1>")
        self.parent.unbind("<Button-1>")
        self.entry.unbind("<Tab>")

class CollectionManager(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.data_lock = threading.Lock() 

        # Create loading frame
        self.loading_frame = tk.Frame(self)
        self.loading_label = tk.Label(self.loading_frame, text="Loading card database...")
        self.loading_label.pack(pady=5)
        self.progress = ttk.Progressbar(self.loading_frame, mode='indeterminate')
        self.progress.pack(pady=5)
        self.loading_frame.place(relx=0.5, rely=0.5, anchor='center')
        self.progress.start()
        
        # Start loading in background
        self.loading_complete = False
        threading.Thread(target=self._initialize_with_retry, daemon=True).start()

        # Main container
        main_container = tk.Frame(self)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(main_container)
        header_frame.pack(fill="x", pady=(0, 10))
        tk.Button(header_frame, text="← Back to Menu", 
                command=lambda: controller.show_frame("MainMenuFrame")).pack(side="left")
        tk.Label(header_frame, text="Collection Manager", 
                font=("Helvetica", 14)).pack(side="left", padx=10)
        
        # Search frame
        search_frame = tk.Frame(main_container)
        search_frame.pack(fill="x", pady=(0, 10))
        tk.Label(search_frame, text="Search:").pack(side="left", padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=40)
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_var.trace_add("write", lambda *args: self.update_list())

        # Listbox
        list_container = tk.Frame(main_container)
        list_container.pack(fill="both", expand=True)
        self.listbox = tk.Listbox(list_container)
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar = tk.Scrollbar(list_container, command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set, selectmode=tk.SINGLE)

        # Add card frame
        add_frame = tk.LabelFrame(main_container, text="Add New Card", padx=10, pady=10)
        add_frame.pack(fill="x", pady=(10, 0))
        
        # Card name
        name_frame = tk.Frame(add_frame)
        name_frame.pack(fill="x", pady=5)
        tk.Label(name_frame, text="Card Name:").pack(side="left")
        self.add_name_entry = tk.Entry(name_frame)
        self.add_name_entry.pack(side="left", fill="x", expand=True, padx=5)

        # Quantity and set
        qty_set_frame = tk.Frame(add_frame)
        qty_set_frame.pack(fill="x", pady=5)
        tk.Label(qty_set_frame, text="Quantity:").pack(side="left")
        self.add_qty_entry = tk.Entry(qty_set_frame, width=5)
        self.add_qty_entry.pack(side="left", padx=5)
        tk.Label(qty_set_frame, text="Set Name:").pack(side="left", padx=(10, 0))
        self.add_set_entry = tk.Entry(qty_set_frame)
        self.add_set_entry.pack(side="left", fill="x", expand=True, padx=5)

        # Crafted checkbox and buttons
        button_frame = tk.Frame(add_frame)
        button_frame.pack(fill="x", pady=(5, 0))
        self.crafted_var = tk.BooleanVar(value=False)
        crafted_check = tk.Checkbutton(button_frame, text="Crafted Card", 
                                     variable=self.crafted_var,
                                     command=self.toggle_set_entry)
        crafted_check.pack(side="left")
        add_button = tk.Button(button_frame, text="Add Card", command=self.add_card)
        add_button.pack(side="right", padx=(5, 0))
        self.remove_card_button = tk.Button(button_frame, text="Remove Selected", 
                                          command=self.remove_selected_card)
        self.remove_card_button.pack(side="right")

        # Temporary debug button
        tk.Button(button_frame, text="Debug Matching",
                  command=self.test_card_matching).pack(side="left", padx=5)
        tk.Button(button_frame, text="Inspect CSV", 
         command=self.inspect_csv_file).pack(side="left", padx=5)

        # File operations
        file_frame = tk.Frame(main_container)
        file_frame.pack(fill="x", pady=(10, 0))
        tk.Button(file_frame, text="Load CSV", command=self.load_csv).pack(side="left", padx=5)
        tk.Button(file_frame, text="Save CSV", command=self.save_csv).pack(side="left", padx=5)
        tk.Button(file_frame, text="Export Whitelist", 
                command=self.generate_whitelist_from_file).pack(side="right")

        self.toggle_set_entry()
        self.collection = {}
        self.default_csv_path = "pulled_cards.csv"
        self.card_database = []
        
        if os.path.exists(self.default_csv_path):
            self.load_csv_from_path(self.default_csv_path)

    def _initialize(self):
        """Thread-safe initialization"""
        try:
            with self.data_lock:
                self.load_card_database()
                self.verify_data_integrity()
            self.after(0, self._finish_loading)
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"Failed to initialize: {e}"))
            self.after(0, self._finish_loading)
            
    def toggle_set_entry(self):
        """Toggle the set entry field based on crafted checkbox"""
        if self.crafted_var.get():
            self.add_set_entry.config(state="disabled")
            self.add_set_entry.delete(0, tk.END)
            self.add_set_entry.insert(0, "Crafted Card")
        else:
            self.add_set_entry.config(state="normal")
            self.add_set_entry.delete(0, tk.END)

    def _initialize_dropdowns(self):
        """Initialize the dropdown components after data is fully loaded"""
        if not hasattr(self, 'card_sets_map') or not self.card_sets_map:
            print("Card sets map not ready, delaying dropdown initialization")
            self.after(500, self._initialize_dropdowns)
            return
            
        card_names = sorted(self.card_sets_map.keys())
        print(f"Initializing dropdown with {len(card_names)} cards")
        
        # Destroy previous dropdown if it exists
        if hasattr(self, 'card_dropdown'):
            self.card_dropdown.destroy()
        
        # Create new dropdown with all card names
        self.card_dropdown = SearchableDropdown(self, self.add_name_entry, card_names)
        self.card_dropdown.on_select_callback = self.update_set_dropdown
        
        # Verify some sample cards are present
        test_cards = ["Abyss Actor - Wild Hope", "3-Hump Lacooda"]
        for card in test_cards:
            if card not in self.card_sets_map:
                print(f"Warning: Test card '{card}' not found in card sets map")
        
        self.add_name_entry.focus_set()

    def update_set_dropdown(self, cardname):
        """Update the set dropdown when a card is selected"""
        if not hasattr(self, 'card_sets_map') or cardname not in self.card_sets_map:
            return
            
        # Clean up previous dropdown if it exists
        if hasattr(self, 'set_dropdown'):
            self.set_dropdown.destroy()
        
        sets = self.card_sets_map[cardname]
        self.add_set_entry.config(state="normal")
        self.add_set_entry.delete(0, tk.END)
        
        if sets:
            self.set_dropdown = SetDropdown(self, self.add_set_entry, sets)
            self.add_set_entry.focus_set()

    def verify_card_loading(self):
        """Debug method to verify specific cards loaded"""
        test_cards = ["Abyss Actor - Wild Hope", "3-Hump Lacooda"]
        print("\n=== Verifying Card Loading ===")
        
        for cardname in test_cards:
            found = any(cardname.lower() == c['cardname'].lower() 
                       for c in self.card_database)
            print(f"Card '{cardname}' found: {found}")
            
            if not found:
                similar = [c['cardname'] for c in self.card_database 
                          if cardname.lower() in c['cardname'].lower()]
                print(f"Similar cards: {similar[:3]}")

    def _finish_loading(self):
        """Complete the loading process"""
        self.progress.stop()
        self.loading_frame.place_forget()
        self.loading_complete = True
        
        # Verify loading
        print("\n=== Loading Verification ===")
        print(f"Total cards loaded: {len(self.card_database)}")
        print(f"Unique card names: {len(self.card_sets_map)}")
        
        # Test specific cards
        test_cards = ["Abyss Actor - Wild Hope", "3-Hump Lacooda"]
        for card in test_cards:
            found = card in self.card_sets_map
            print(f"Card '{card}' found: {found}")
            if not found:
                similar = [c for c in self.card_sets_map.keys() if card.lower() in c.lower()]
                print(f"Similar cards: {similar[:3]}")
        
        # Initialize dropdowns after small delay to ensure everything is ready
        self.after(200, self._initialize_dropdowns)
        
        # Load existing collection if available
        if os.path.exists(self.default_csv_path):
            self.load_csv_from_path(self.default_csv_path)

    def add_card(self):
        """Add a new card to the collection"""
        if not self.loading_complete:
            messagebox.showwarning("Loading", "Card database is still loading, please wait")
            return
            
        cardname = self.cardname_var.get().strip()
        qty_str = self.add_qty_entry.get().strip()
        setname = "Crafted Card" if self.crafted_var.get() else self.add_set_entry.get().strip()

        # Validate inputs
        if not cardname:
            messagebox.showerror("Error", "Please select a card from the dropdown")
            return
            
        if not qty_str:
            messagebox.showerror("Error", "Please enter a quantity")
            return
            
        try:
            qty = int(qty_str)
            if qty < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a positive integer")
            return
            
        if not setname:
            messagebox.showerror("Error", "Please select a set")
            return

        # Get card data - modified to handle crafted cards differently
        card_data = None
        if setname != "Crafted Card":
            card_data = self.find_card_data(cardname)
            if not card_data:
                self.inspect_card(cardname)  # Add this line for debugging
                # Get suggestions
                suggestions = [c['cardname'] for c in self.card_database 
                            if cardname.lower() in c['cardname'].lower()]
                
                msg = f"Card '{cardname}' not found in database."
                if suggestions:
                    msg += f"\n\nDid you mean:\n- " + "\n- ".join(suggestions[:5])
                    if len(suggestions) > 5:
                        msg += f"\n(and {len(suggestions)-5} more)"
                
                # Show debug info in console
                print("\n=== Failed to find card ===")
                self.debug_card_matching(cardname)
                
                messagebox.showerror("Card Not Found", msg)
                return

        # Add to collection
        key = (cardname, setname)
        if key not in self.collection:
            self.collection[key] = {
                'quantity': 0,
                'rarity': card_data.get('cardrarity', 'Unknown') if card_data else 'Unknown',
                'edition': card_data.get('card_edition', 'Unlimited') if card_data else 'Unlimited',
                'cardid': card_data.get('cardid', '') if card_data else '',
                'cardcode': card_data.get('cardcode', '') if card_data else '',
                'print_id': card_data.get('print_id', '') if card_data else ''
            }
        self.collection[key]['quantity'] += qty
        
        # Update and save
        self.update_list()
        self.autosave_csv()
        
        # Clear form
        self.add_name_entry.delete(0, tk.END)
        self.add_qty_entry.delete(0, tk.END)
        if not self.crafted_var.get():
            self.add_set_entry.delete(0, tk.END)
        
        messagebox.showinfo("Success", f"Added {qty}x {cardname}")

    def update_list(self, *args):
        """Update the listbox with current collection"""
        search_text = self.search_var.get().lower()
        self.listbox.delete(0, tk.END)

        agg = defaultdict(lambda: {"total": 0, "sets": defaultdict(int)})
        for (name, setname), data in self.collection.items():
            agg[name]["total"] += data["quantity"]
            agg[name]["sets"][setname] += data["quantity"]

        for cardname, data in sorted(agg.items()):
            if search_text and search_text not in cardname.lower():
                continue
            sets_str = ", ".join(f"{setname}: {qty}" for setname, qty in data["sets"].items())
            line = f"{cardname} - Total: {data['total']} ({sets_str})"
            self.listbox.insert(tk.END, line)

    def load_card_database(self):
        """Reliably load all card data from CSV"""
        csv_path = "cards.csv"
        self.card_database = []
        self.card_sets_map = {}
        self.card_printings_map = {}

        try:
            # First read entire file to memory (for reliability)
            with open(csv_path, 'rb') as f:
                raw_data = f.read()
            
            # Decode with proper encoding handling
            try:
                content = raw_data.decode('utf-8-sig')
            except UnicodeDecodeError:
                content = raw_data.decode('latin-1')

            # Use csv reader on the decoded content
            reader = csv.DictReader(content.splitlines())
            
            for row in reader:
                try:
                    cardname = row['cardname'].strip()
                    if not cardname:
                        continue

                    # Clean and normalize the card name
                    cardname = self.normalize_cardname(cardname, keep_case=True)
                    
                    card_data = {
                        'cardname': cardname,
                        'cardq': row.get('cardq', '').strip(),
                        'cardrarity': row.get('cardrarity', '').strip(),
                        'card_edition': row.get('card_edition', 'Unlimited').strip(),
                        'cardset': row.get('cardset', '').strip(),
                        'cardcode': row.get('cardcode', '').strip(),
                        'cardid': row.get('cardid', '').strip(),
                        'print_id': row.get('print_id', '').strip()
                    }
                    
                    self.card_database.append(card_data)
                    
                    # Process sets - split by semicolon and clean each set name
                    sets = [s.strip() for s in card_data['cardset'].split(';') if s.strip()]
                    sets = [s for s in sets if s]  # Remove empty strings
                    
                    # Initialize card entry if not exists
                    if cardname not in self.card_sets_map:
                        self.card_sets_map[cardname] = []
                    
                    # Add sets that aren't already present
                    for s in sets:
                        if s not in self.card_sets_map[cardname]:
                            self.card_sets_map[cardname].append(s)
                    
                    # Track all printings
                    self.card_printings_map.setdefault(cardname, []).append(card_data)

                except Exception as e:
                    print(f"Error processing row: {e}")
                    continue

            print(f"Loaded {len(self.card_database)} cards with {len(self.card_sets_map)} unique names")
            
        except Exception as e:
            print(f"Fatal error loading database: {e}")
            raise

    def find_card_data(self, cardname):
        """Find card data with flexible matching"""
        if not cardname or not self.card_database:
            return None
            
        # Normalize the search name
        def normalize(name):
            name = name.lower().strip()
            # Remove all non-alphanumeric characters except spaces and hyphens
            name = re.sub(r'[^\w\s-]', '', name)
            # Replace multiple spaces with single space
            name = re.sub(r'\s+', ' ', name)
            return name.strip()
        
        search_name = normalize(cardname)
        
        # First try exact match
        for card in self.card_database:
            db_name = normalize(card['cardname'])
            if db_name == search_name:
                return card
                
        # Then try contains match with relaxed rules
        for card in self.card_database:
            db_name = normalize(card['cardname'])
            # Remove all spaces and hyphens for more flexible matching
            clean_search = search_name.replace(' ', '').replace('-', '')
            clean_db = db_name.replace(' ', '').replace('-', '')
            
            if clean_search in clean_db or clean_db in clean_search:
                return card
                
        # Try fuzzy matching if installed
        try:
            from fuzzywuzzy import fuzz
            best_match = None
            best_score = 0
            
            for card in self.card_database:
                db_name = normalize(card['cardname'])
                score = fuzz.ratio(search_name, db_name)
                if score > best_score and score > 75:  # Only consider good matches
                    best_score = score
                    best_match = card
                    
            return best_match
        except ImportError:
            pass
            
        # Final attempt - look for partial matches
        for card in self.card_database:
            db_name = normalize(card['cardname'])
            if any(word in db_name for word in search_name.split()):
                return card
                
        return None

    def load_csv(self):
        """Load collection from CSV file"""
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if path:
            self.load_csv_from_path(path)

    def load_csv_from_path(self, path):
        """Load collection from specific CSV path"""
        try:
            with open(path, newline='', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                self.collection.clear()
                
                for row in reader:
                    try:
                        name = row.get("cardname", "").strip()
                        qty = int(row.get("cardq", "0"))
                        setname = row.get("cardset", "Unknown Set").strip()
                        rarity = row.get("cardrarity", "Unknown")
                        edition = row.get("card_edition", "Unlimited")
                        cardid = row.get("cardid", "")
                        cardcode = row.get("cardcode", "")
                        print_id = row.get("print_id", "")

                        if name:
                            key = (name, setname)
                            if key not in self.collection:
                                self.collection[key] = {
                                    "quantity": 0,
                                    "rarity": rarity,
                                    "edition": edition,
                                    "cardid": cardid,
                                    "cardcode": cardcode,
                                    "print_id": print_id
                                }
                            self.collection[key]["quantity"] += qty
                            
                    except ValueError:
                        continue
                        
            self.update_list()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV: {e}")

    def save_csv(self):
        """Save collection to CSV file"""
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        if path:
            self._save_csv_to_path(path)

    def autosave_csv(self):
        """Auto-save collection to default path"""
        self._save_csv_to_path(self.default_csv_path)

    def _save_csv_to_path(self, path):
        """Internal method to save collection to specified path"""
        try:
            with open(path, mode="w", newline="", encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    "cardname", "cardq", "cardrarity", "card_edition",
                    "cardset", "cardcode", "cardid", "print_id"
                ])
                writer.writeheader()
                
                for (cardname, setname), data in sorted(self.collection.items()):
                    writer.writerow({
                        "cardname": cardname,
                        "cardq": data["quantity"],
                        "cardrarity": data["rarity"],
                        "card_edition": data["edition"],
                        "cardset": setname,
                        "cardcode": data["cardcode"],
                        "cardid": data["cardid"],
                        "print_id": data["print_id"]
                    })
                    
            if path != self.default_csv_path:
                messagebox.showinfo("Success", f"Collection saved to {path}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save CSV: {e}")

    def generate_whitelist_from_file(self):
        """Generate whitelist file from collection"""
        output_path = "whitelist.conf"
        try:
            card_counts = defaultdict(int)
            for (_, _), data in self.collection.items():
                cardid = data.get("cardid", "").strip()
                qty = data.get("quantity", 0)
                if cardid.isdigit():
                    card_counts[cardid] += qty

            with open(output_path, "w", encoding="utf-8") as outfile:
                outfile.write("!Limited Collection Whitelist\n$whitelist\n")
                for cardid, qty in sorted(card_counts.items()):
                    outfile.write(f"{cardid} {min(qty, 3)}\n")

            messagebox.showinfo("Success", f"Whitelist saved to {output_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate whitelist: {e}")

    def remove_selected_card(self):
        """Remove selected card from collection"""
        selected = self.listbox.curselection()
        if not selected:
            messagebox.showerror("Error", "Please select a card to remove")
            return
        
        selected_text = self.listbox.get(selected[0])
        try:
            cardname = selected_text.split(" - Total:")[0].strip()
            matching_entries = [(name, setname) for (name, setname) in self.collection.keys() if name == cardname]
            
            if not matching_entries:
                messagebox.showerror("Error", "Selected card not found in collection")
                return
            
            if len(matching_entries) == 1:
                setname = matching_entries[0][1]
                self._remove_card_from_set(cardname, setname)
            else:
                self._show_set_selection_popup(cardname, matching_entries)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to parse selection: {str(e)}")

    def _remove_card_from_set(self, cardname, setname, quantity=1):
        """Remove card from specific set"""
        key = (cardname, setname)
        if key in self.collection:
            current_qty = self.collection[key]["quantity"]
            if quantity >= current_qty:
                del self.collection[key]
            else:
                self.collection[key]["quantity"] -= quantity
            
            self.update_list()
            self.autosave_csv()
        else:
            messagebox.showerror("Error", "Card not found in specified set")

    def _show_set_selection_popup(self, cardname, matching_entries):
        """Show popup to select which set to remove from"""
        popup = tk.Toplevel(self.controller)
        popup.title("Select Set to Remove From")
        popup.transient(self.controller)
        popup.grab_set()
        
        x = self.controller.winfo_x() + (self.controller.winfo_width() - 300) // 2
        y = self.controller.winfo_y() + (self.controller.winfo_height() - 200) // 2
        popup.geometry(f"300x200+{x}+{y}")
        
        content_frame = tk.Frame(popup, padx=20, pady=20)
        content_frame.pack(fill="both", expand=True)
        
        tk.Label(content_frame, text=f"Select set for: {cardname}").pack(pady=5)
        
        set_var = tk.StringVar()
        set_dropdown = tk.OptionMenu(content_frame, set_var, *[setname for (_, setname) in matching_entries])
        set_dropdown.pack(fill="x", pady=5)
        set_var.set(matching_entries[0][1])
        
        tk.Label(content_frame, text="Quantity to remove:").pack()
        qty_var = tk.IntVar(value=1)
        qty_spin = tk.Spinbox(content_frame, from_=1, to=100, textvariable=qty_var)
        qty_spin.pack(pady=5)
        
        button_frame = tk.Frame(content_frame)
        button_frame.pack(pady=(10, 0))
        
        def confirm_remove():
            setname = set_var.get()
            qty = qty_var.get()
            self._remove_card_from_set(cardname, setname, qty)
            popup.destroy()
        
        tk.Button(button_frame, text="Remove", command=confirm_remove).pack(side="left", padx=5)
        tk.Button(button_frame, text="Cancel", command=popup.destroy).pack(side="right", padx=5)
        popup.focus_set()

    def debug_card_matching(self, search_name):
        """Debug why a card isn't being found"""
        print(f"\n=== DEBUG: Searching for '{search_name}' ===")
        
        # Show exact matches
        exact_matches = [c for c in self.card_database if c['cardname'].lower() == search_name.lower()]
        print(f"Found {len(exact_matches)} exact matches")
        for card in exact_matches[:3]:  # Show first 3 matches
            print(f"  '{card['cardname']}' (ID: {card['cardid']})")

        # Show partial matches
        partial_matches = [c for c in self.card_database if search_name.lower() in c['cardname'].lower()]
        print(f"\nFound {len(partial_matches)} partial matches")
        for card in partial_matches[:5]:  # Show first 5 partial matches
            print(f"  '{card['cardname']}' (ID: {card['cardid']})")

        # Show character-by-character comparison
        if exact_matches:
            db_name = exact_matches[0]['cardname']
            print("\nCharacter comparison:")
            for i, (a, b) in enumerate(zip(search_name, db_name)):
                mark = " " if a == b else "✗"
                print(f"  {i:2d}: {a} {mark} {b}")
            if len(search_name) != len(db_name):
                print(f"Different lengths: input={len(search_name)}, db={len(db_name)}")
        
        return bool(exact_matches)

    def inspect_card(self, cardname):
        """Debug method to inspect a card's data"""
        search_name = cardname.lower()
        print(f"\nSearching for: '{cardname}' (normalized: '{search_name}')")
        
        matches = [c for c in self.card_database if search_name in c['cardname'].lower()]
        print(f"Found {len(matches)} potential matches")
        
        for i, card in enumerate(matches[:5], 1):
            print(f"\nMatch {i}:")
            print(f"Raw name: '{card['cardname']}'")
            print(f"Normalized: '{card['cardname'].strip().lower()}'")
            print("Character codes:")
            for char in card['cardname']:
                print(f"  {char} (U+{ord(char):04X})")

    def test_card_matching(self):
        """Test card matching functionality"""
        print("\n=== Testing card matching ===")
        
        test_cards = [
            "Abyss Actor - Wild Hope",  # Known working
            "3-Hump Lacooda",
            '"A" Cell Incubator',
            "Dark Magician"  # Common card that should exist
        ]
        
        for card in test_cards:
            print(f"\nTesting: {card}")
            found = self.find_card_data(card)
            if found:
                print(f"Found: {found['cardname']} (ID: {found['cardid']})")
            else:
                print("Not found!")
                self.debug_specific_card(card)

    def inspect_csv_file(self):
        """Debug the raw CSV file contents"""
        csv_path = "cards.csv"
        print(f"\n=== Inspecting CSV File: {csv_path} ===")
        
        with open(csv_path, 'rb') as f:
            content = f.read()
            print("First 200 bytes:")
            print(content[:200])
            
            # Search for Abyss Actor entries
            abyss_actor_positions = []
            search_term = b"Abyss Actor"
            pos = content.find(search_term)
            while pos != -1:
                abyss_actor_positions.append(pos)
                pos = content.find(search_term, pos + 1)
            
            print(f"\nFound {len(abyss_actor_positions)} occurrences of 'Abyss Actor'")
            for pos in abyss_actor_positions[:3]:  # Show first 3 occurrences
                excerpt = content[pos-20:pos+40]
                print(f"\nAt position {pos}:")
                print(excerpt.decode('utf-8', errors='replace'))
                print("Hex:", excerpt.hex(' '))

    def _initialize_with_error_handling(self):
        """Wrapper to catch and display thread exceptions"""
        try:
            self._initialize()
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Loading Error", f"Failed to load database: {str(e)}"))
            self.after(0, self._finish_loading)

    def verify_data_integrity(self):
        """Verify all expected cards are loaded"""
        test_cards = [
            "Abyss Actor - Wild Hope",
            "3-Hump Lacooda",
            '"A" Cell Incubator'
        ]
        
        print("\n=== Data Integrity Check ===")
        for card in test_cards:
            found = any(card.lower() == c['cardname'].lower() for c in self.card_database)
            print(f"Card '{card}' found: {found}")
            
            if not found:
                similar = [c['cardname'] for c in self.card_database 
                        if card.lower() in c['cardname'].lower()]
                print(f"Similar cards: {similar[:3]}")

    def debug_specific_card(self, cardname):
        """Debug why a specific card isn't being found"""
        print(f"\n=== Debugging card: {cardname} ===")
        
        # Show raw CSV lines containing the card
        with open("cards.csv", 'r', encoding='utf-8-sig') as f:
            for i, line in enumerate(f, 1):
                if cardname.lower() in line.lower():
                    print(f"Found in CSV line {i}: {line.strip()}")
        
        # Show how it appears in memory
        in_memory = [c for c in self.card_database if cardname.lower() in c['cardname'].lower()]
        print(f"\nIn memory matches ({len(in_memory)}):")
        for card in in_memory[:3]:  # Show first 3 matches
            print(f"  {card['cardname']} (ID: {card['cardid']})")
        
        # Show normalization comparison
        print("\nNormalization comparison:")
        search_norm = self.normalize_cardname(cardname)
        print(f"Search term: '{cardname}' → normalized: '{search_norm}'")
        
        if in_memory:
            db_norm = self.normalize_cardname(in_memory[0]['cardname'])
            print(f"Database: '{in_memory[0]['cardname']}' → normalized: '{db_norm}'")
        
        # Show character codes
        print("\nCharacter codes (search term):")
        for char in cardname:
            print(f"  '{char}' (U+{ord(char):04X})")

    def normalize_cardname(self, name, keep_case=False):
        """Normalize card names for consistent comparison and display"""
        if not name:
            return ""
        
        # First normalize Unicode (convert fancy quotes, dashes, etc.)
        name = unicodedata.normalize('NFKC', name)
        
        if not keep_case:
            name = name.lower()
        
        # Remove all non-alphanumeric characters except spaces, hyphens, and apostrophes
        name = re.sub(r'[^\w\s\'-]', '', name)
        
        # Replace multiple spaces with single space
        name = re.sub(r'\s+', ' ', name)
        
        return name.strip()
    
    def _initialize_with_retry(self, attempts=3):
        """Try loading multiple times before failing"""
        for attempt in range(attempts):
            try:
                self._initialize()
                return
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt == attempts - 1:
                    self.after(0, lambda: messagebox.showerror("Error", 
                        f"Failed to load after {attempts} attempts: {e}"))
                    self.after(0, self._finish_loading)
                time.sleep(1)

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
        self.title("Yu-Gi-Oh! Collection Manager")
        self.geometry("800x600")
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
    # Check for required files
    if not os.path.exists("cards.csv"):
        response = messagebox.askyesno(
            "File Missing", 
            "cards.csv not found. Create an empty template file?",
            detail="You'll need to populate it with your card data."
        )
        if response:
            with open("cards.csv", "w", encoding='utf-8') as f:
                f.write("cardname,cardq,cardrarity,card_edition,cardset,cardcode,cardid,print_id\n")
    
    app = AppController()
    app.mainloop()