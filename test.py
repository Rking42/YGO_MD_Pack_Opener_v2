import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont

class SearchableDropdown(tk.Tk):
    def __init__(self, options):
        super().__init__()
        self.title("Fixed-width Dropdown Example")
        self.geometry("300x200")

        self.options = options
        self.filtered_options = options.copy()
        self.popup = None
        self.updating = False

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.on_type)

        self.search_entry = ttk.Entry(self, textvariable=self.search_var)
        self.search_entry.pack(pady=20)
        self.search_entry.bind("<FocusIn>", self.show_popup)
        self.search_entry.bind("<FocusOut>", self.hide_popup_delayed)
        self.search_entry.bind("<Escape>", self.close_popup)

        self.selection_label = ttk.Label(self, text="Selected: None")
        self.selection_label.pack(pady=10)

        self.bind_all("<Button-1>", self.on_click_outside)

        # Font object for measuring text width
        self.font = tkFont.Font(font=self.search_entry['font'])

        # Fixed character count width for popup
        self.char_count = 53
        self.fixed_width = self.char_count * self.font.measure("0") + 20  # padding

    def on_type(self, *args):
        if self.updating:
            return
        search_term = self.search_var.get().lower()
        self.filtered_options = [item for item in self.options if search_term in item.lower()]

        # If popup is closed, open it again when typing
        if not self.popup or not self.popup.winfo_exists():
            self.show_popup()

        self.update_popup()


    def show_popup(self, event=None):
        if self.popup:
            self.popup.destroy()

        self.popup = tk.Toplevel(self)
        self.popup.wm_overrideredirect(True)
        self.popup.wm_geometry(self.get_popup_position())
        self.popup.lift()
        self.popup.attributes('-topmost', True)

        # Just Listbox + Scrollbar directly in popup (simpler)
        self.listbox = tk.Listbox(self.popup, height=6, activestyle="dotbox")
        self.listbox.pack(side="left", fill="both", expand=True)

        self.scrollbar = ttk.Scrollbar(self.popup, orient="vertical", command=self.listbox.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=self.scrollbar.set)

        self.listbox.bind("<<ListboxSelect>>", self.on_select)
        self.search_entry.bind("<KeyPress-Up>", self.navigate_up)
        self.search_entry.bind("<KeyPress-Down>", self.navigate_down)
        self.search_entry.bind("<Return>", self.select_current)

        self.update_popup()

    def get_popup_position(self):
        x = self.search_entry.winfo_rootx()
        y = self.search_entry.winfo_rooty() + self.search_entry.winfo_height()
        return f"+{x}+{y}"

    def update_popup(self):
        if not self.popup:
            return

        self.listbox.delete(0, tk.END)

        for item in self.filtered_options:
            self.listbox.insert(tk.END, item)

        self.popup.update_idletasks()  # update geometry

        # Set fixed width & height to popup
        height = self.listbox.winfo_reqheight()
        self.popup.geometry(f"{self.fixed_width}x{height}+{self.search_entry.winfo_rootx()}+{self.search_entry.winfo_rooty() + self.search_entry.winfo_height()}")

        if self.filtered_options:
            self.popup.deiconify()
            self.listbox.select_set(0)
            self.listbox.activate(0)
        else:
            self.popup.withdraw()

    def on_select(self, event):
        self.after(50, self._finalize_selection)  # Delay to allow click

    def _finalize_selection(self):
        try:
            index = self.listbox.curselection()[0]
            value = self.filtered_options[index]
            self.updating = True
            self.search_var.set(value)
            self.updating = False
            self.selection_label.config(text=f"Selected: {value}")
            self.focus_set()  # Move focus away to close popup
        except IndexError:
            pass

        if self.popup and self.popup.winfo_exists():
            self.popup.destroy()
            self.popup = None

    def hide_popup_delayed(self, event=None):
        self.after(150, self.try_hide_popup)

    def try_hide_popup(self):
        if self.popup and not self.focus_get() in (self.search_entry, self.listbox):
            self.popup.destroy()
            self.popup = None

    def navigate_up(self, event):
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
        self.after(50, self._finalize_selection)

    def close_popup(self, event=None):
        if self.popup and self.popup.winfo_exists():
            self.popup.destroy()
            self.popup = None

    def on_click_outside(self, event):
        # Get the widget clicked on
        widget = event.widget
        if self.popup and self.popup.winfo_exists():
            # Check if clicked widget is NOT the popup or the entry or inside popup
            if widget not in (self.search_entry, self.listbox) and not self.is_child_of(widget, self.popup):
                self.popup.destroy()
                self.popup = None

    def is_child_of(self, widget, parent):
        # Walk up widget's parents to see if it matches 'parent'
        while widget:
            if widget == parent:
                return True
            widget = widget.master
        return False




if __name__ == "__main__":

    with open("cardlist.txt", "r", encoding="utf-8") as f:
        items = [line.strip() for line in f if line.strip()]

    app = SearchableDropdown(items)
    app.mainloop()
