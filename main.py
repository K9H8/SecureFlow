import tkinter as tk
from tkinter import ttk
import threading
from DataCollection import monitor_system 
import time

class WelcomeWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("SecureFlow")
        
        # Set window size and position it in center
        window_width = 400
        window_height = 300  # Increased height for progress bar
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Welcome message
        welcome_label = ttk.Label(
            main_frame, 
            text="Welcome to SecureFlow",
            font=('Helvetica', 16, 'bold')
        )
        welcome_label.grid(row=0, column=0, pady=20)
        
        # Start button
        self.start_button = ttk.Button(
            main_frame, 
            text="Start Data Collection",
            command=self.start_collection
        )
        self.start_button.grid(row=1, column=0, pady=20)
        
        # Progress bar
        self.progress = ttk.Progressbar(
            main_frame, 
            length=300, 
            mode='determinate'
        )
        self.progress.grid(row=2, column=0, pady=10)
        
        # Time remaining label
        self.time_label = ttk.Label(
            main_frame,
            text=f"Time Remaining: {tk.IntVar}:00", # !timechange
            font=('Helvetica', 10)
        )
        self.time_label.grid(row=3, column=0, pady=5)
        
        # Time selection dropdown
        self.time_options = [5, 10, 15, 20]  # Options in minutes
        self.time_var = tk.IntVar(value=self.time_options[0])  # Default to first option
        self.time_dropdown = ttk.Combobox(
            main_frame, 
            textvariable=self.time_var, 
            values=self.time_options,
            state='readonly'
        )
        self.time_dropdown.grid(row=4, column=0, pady=10)
        
        # Center all elements
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Make window non-resizable
        self.root.resizable(False, False)
        
    def start_collection(self):
        """Start the monitoring and disable the button"""
        self.start_button.config(state='disabled', text="Data Collection Running")
        thread = threading.Thread(target=monitor_system, daemon=True)
        thread.start()
        
        self.start_countdown()
        
    def start_countdown(self):
        """Start the countdown based on user selection"""
        total_minutes = self.time_var.get()  # Get selected time in minutes
        total_seconds = total_minutes * 60  # Convert to seconds
        self.progress['maximum'] = total_seconds  #Sets the progress bar maximum to 3 minutes
        
        def update_countdown():
            for remaining in range(total_seconds, -1, -1):
                if remaining >= 0:
                    # Update progress bar
                    self.progress['value'] = total_seconds - remaining
                    
                    # Update time label
                    minutes = remaining // 60
                    seconds = remaining % 60
                    self.time_label['text'] = f"Time Remaining: {minutes:01d}:{seconds:02d}"
                    
                    # Update GUI
                    self.root.update()
                    time.sleep(1)
            
            # When countdown finishes
            self.time_label['text'] = "Data Collection Complete"
        
        countdown_thread = threading.Thread(target=update_countdown, daemon=True)
        countdown_thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = WelcomeWindow(root)
    root.mainloop()

