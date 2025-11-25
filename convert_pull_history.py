import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

def convert_file(input_path, output_folder):
    # Extract timestamp from filename (e.g., "pull_history_2025-06-23_22-24-53.json")
    filename = os.path.basename(input_path)
    timestamp_str = filename.replace("pull_history_", "").replace(".json", "")
    
    # Parse the input timestamp (YYYY-MM-DD_HH-MM-SS)
    dt = datetime.strptime(timestamp_str, "%Y-%m-%d_%H-%M-%S")
    
    # Convert to the desired output format (YYYYMMDD_HHMMSS)
    output_timestamp = dt.strftime("%Y%m%d_%H%M%S")
    iso_timestamp = dt.isoformat()

    # Load the original JSON data
    with open(input_path, 'r') as f:
        input_data = json.load(f)

    # Initialize the output structure
    output = {
        "available_packs": list(set(card["cardset"] for card in input_data)),
        "current_results": [],
        "pack_counter": len(input_data) // 8,  # Total packs (8 cards per pack)
        "timestamp": output_timestamp
    }

    # Split cards into packs of 8
    for pack_num in range(output["pack_counter"]):
        start_idx = pack_num * 8
        end_idx = start_idx + 8
        pack_cards = input_data[start_idx:end_idx]

        # All cards in a pack should have the same cardset (verify if needed)
        pack_name = pack_cards[0]["cardset"] if pack_cards else "Unknown Pack"

        # Add pack header
        output["current_results"].append({
            "type": "header",
            "text": f"Pack #{pack_num + 1}: {pack_name}"
        })

        # Add cards in this pack
        for card in pack_cards:
            output["current_results"].append({
                "type": "card",
                "name": card["cardname"],
                "rarity": card["cardrarity"],
                "pack": pack_name,
                "timestamp": iso_timestamp
            })

    # Save the converted file
    output_filename = f"pull_history_{output_timestamp}.json"
    output_path = os.path.join(output_folder, output_filename)
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Converted: {filename} → {output_filename}")

def main():
    input_folder = "pull_logs"  # Folder with original JSONs
    output_folder = "converted_files"    # Where to save results

    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Process each file in input_folder
    for filename in os.listdir(input_folder):
        if filename.startswith("pull_history_") and filename.endswith(".json"):
            input_path = os.path.join(input_folder, filename)
            convert_file(input_path, output_folder)

    # Show a popup when done
    root = tk.Tk()
    root.withdraw()  # Hide the main Tk window
    messagebox.showinfo("Done", "All files have been converted and saved.")

if __name__ == "__main__":
    main()