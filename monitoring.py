import tkinter as tk
from tkinter import ttk
import subprocess
import threading
import time
from datetime import datetime
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

# Global variable to control polling
is_polling = False
MAX_THREADS = 100

# Function to ping an IP
def ping_ip(ip):
    try:
        # Suppress the console window that opens during ping
        output = subprocess.check_output(
            ['ping', '-n', '1', ip],
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            creationflags=subprocess.CREATE_NO_WINDOW  # Suppress window creation
        )
        if "unreachable" in output or "timed out" in output:
            return ip, "Offline"
        else:
            return ip, "Online"
    except subprocess.CalledProcessError:
        return ip, "Offline"

# Function to update IP status in the UI
def update_status(ip_list, status_labels, last_checked_label, polling_status_label):
    global is_polling
    while is_polling:
        # Use ThreadPoolExecutor to ping all IPs concurrently with a maximum of 100 threads
        with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            futures = {executor.submit(ping_ip, ip): ip for ip in ip_list}
            for future in as_completed(futures):
                ip, status = future.result()
                # Find index of the IP in the list to update the correct label
                index = ip_list.index(ip)
                if status == "Online":
                    status_labels[index].config(text=status, fg="green")
                elif status == "Offline":
                    status_labels[index].config(text=status, fg="red")
                else:
                    status_labels[index].config(text=status)
        
        # Update the last checked date and time
        last_checked = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        last_checked_label.config(text=f"Last Checked: {last_checked}")
        
        time.sleep(30)  # 30 seconds interval
    
    # Update polling status when stopped
    polling_status_label.config(text="Polling Stopped", fg="red")

# Function to start pinging
def start_pinging(ip_list, status_labels, last_checked_label, polling_status_label):
    global is_polling
    if not is_polling:  # Prevent starting multiple polling threads
        is_polling = True
        polling_status_label.config(text="Polling in Progress", fg="green")
        ping_thread = threading.Thread(target=update_status, args=(ip_list, status_labels, last_checked_label, polling_status_label))
        ping_thread.daemon = True  # Daemon thread will stop when main thread stops
        ping_thread.start()

# Function to stop pinging
def stop_pinging(polling_status_label):
    global is_polling
    is_polling = False
    polling_status_label.config(text="Stopping Polling...", fg="orange")

# Function to read IPs from file
def read_ips_from_file(filename="ips.txt"):
    if not os.path.exists(filename):
        print(f"Error: {filename} not found.")
        return []
    
    with open(filename, "r") as file:
        # Read all lines and strip any newline or extra spaces
        ip_list = [line.strip() for line in file.readlines() if line.strip()]
    
    return ip_list

# UI setup
def create_ui(ip_list):
    root = tk.Tk()
    root.title("Epsum IPMon")

    # Create a frame for the canvas and scrollbar
    frame = tk.Frame(root)
    frame.grid(row=0, column=0, padx=10, pady=5, columnspan=2)

    # Create a canvas for the scrollable area
    canvas = tk.Canvas(frame, height=500)
    canvas.grid(row=0, column=0, sticky="nsew")

    # Add a scrollbar to the canvas
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    scrollbar.grid(row=0, column=1, sticky="ns")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Create another frame inside the canvas
    scrollable_frame = tk.Frame(canvas)

    # Bind the frame to the canvas
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    # Create window for the scrollable frame inside the canvas
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    # Create table headers
    tk.Label(scrollable_frame, text="IP Address").grid(row=0, column=0, padx=10, pady=5)
    tk.Label(scrollable_frame, text="Status").grid(row=0, column=1, padx=10, pady=5)

    # Create labels for each IP and its status inside the scrollable frame
    status_labels = []
    for i, ip in enumerate(ip_list):
        tk.Label(scrollable_frame, text=ip).grid(row=i+1, column=0, padx=10, pady=5)
        status_label = tk.Label(scrollable_frame, text="Unknown")
        status_label.grid(row=i+1, column=1, padx=10, pady=5)
        status_labels.append(status_label)

    # Label to show last checked date and time
    last_checked_label = tk.Label(root, text="Last Checked: Not yet checked")
    last_checked_label.grid(row=1, column=0, columnspan=2, pady=5)

    # Polling status label
    polling_status_label = tk.Label(root, text="Polling Stopped", fg="red")
    polling_status_label.grid(row=2, column=0, columnspan=2, pady=5)

    # Start and Stop buttons
    start_button = tk.Button(root, text="Start", command=lambda: start_pinging(ip_list, status_labels, last_checked_label, polling_status_label))
    start_button.grid(row=3, column=0, pady=10)

    stop_button = tk.Button(root, text="Stop", command=lambda: stop_pinging(polling_status_label))
    stop_button.grid(row=3, column=1, pady=10)

    # Signature label
    signature_label = tk.Label(root, text="Designed and Developed by Epsum Labs Private Limited", fg="blue", font=("Arial", 8))
    signature_label.grid(row=4, column=0, columnspan=2, pady=10)

    # Bind mousewheel event for scrolling
    root.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    root.mainloop()

# Main logic
if __name__ == "__main__":
    # Read the list of IPs from the ips.txt file
    ip_list = read_ips_from_file()

    # Check if there are IPs to monitor
    if ip_list:
        create_ui(ip_list)
    else:
        print("No IPs to monitor. Please check the ips.txt file.")
