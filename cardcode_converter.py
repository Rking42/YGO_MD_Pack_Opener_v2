import csv
import os
from tkinter import *
from tkinter import filedialog, messagebox

def transform_cardcode(row):
    # Get first 4 characters of cardset (original case) and the cardid
    prefix = row['cardset'][:4]
    cardid = row['cardid']
    return f"{prefix}{cardid}"  # No space between

def process_file(input_file):
    output_file = os.path.splitext(input_file)[0] + "_converted.csv"
    
    with open(input_file, 'r', newline='') as infile, \
         open(output_file, 'w', newline='') as outfile:
        
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in reader:
            # Transform the cardcode
            row['cardcode'] = transform_cardcode(row)
            writer.writerow(row)
    
    return output_file

def select_file():
    filepath = filedialog.askopenfilename(
        title="Select CSV file",
        filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
    )
    if filepath:
        input_entry.delete(0, END)
        input_entry.insert(0, filepath)

def start_processing():
    input_file = input_entry.get()
    if not input_file:
        messagebox.showerror("Error", "Please select a file first")
        return
    
    try:
        output_file = process_file(input_file)
        messagebox.showinfo(
            "Complete", 
            f"File processed successfully!\nOutput saved to:\n{output_file}"
        )
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred:\n{str(e)}")

# Create the main window
root = Tk()
root.title("Card Code Converter")
root.geometry("500x200")

# File selection frame
frame = Frame(root, padx=10, pady=10)
frame.pack(fill=BOTH, expand=True)

Label(frame, text="Input CSV File:").grid(row=0, column=0, sticky=W, pady=5)

input_entry = Entry(frame, width=40)
input_entry.grid(row=0, column=1, padx=5)

browse_btn = Button(frame, text="Browse...", command=select_file)
browse_btn.grid(row=0, column=2, padx=5)

# Start button
start_btn = Button(root, text="Start Conversion", command=start_processing)
start_btn.pack(pady=20)

root.mainloop()