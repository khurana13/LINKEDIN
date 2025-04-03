import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import json
import os
import sys

# Import the bot at module level to avoid circular imports
try:
    from linkedin_bot import LinkedInBot
except ImportError:
    # Will be handled when login is attempted
    pass

class LinkedInAutomationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("LinkedIn Automation Tool")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Variables
        self.email_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.search_query_var = tk.StringVar()
        self.num_requests_var = tk.StringVar(value="10")
        self.include_note_var = tk.BooleanVar(value=False)
        self.custom_note_var = tk.StringVar(value="Hi, I'd like to connect with you!")
        self.save_creds_var = tk.BooleanVar(value=False)
        
        # Status message and automation instance
        self.status_message = ""
        self.bot = None
        self.automation_running = False
        
        # Create tabbed interface
        self.create_notebook()
        
        # Try to load saved settings
        self.load_settings()
    
    def create_notebook(self):
        """Create the tabbed interface"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.login_frame = ttk.Frame(self.notebook)
        self.connect_frame = ttk.Frame(self.notebook)
        self.settings_frame = ttk.Frame(self.notebook)
        self.logs_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(self.login_frame, text="Login")
        self.notebook.add(self.connect_frame, text="Connect")
        self.notebook.add(self.settings_frame, text="Settings")
        self.notebook.add(self.logs_frame, text="Logs")
        
        # Create content for each tab
        self.create_login_tab()
        self.create_connect_tab()
        self.create_settings_tab()
        self.create_logs_tab()
    
    def create_login_tab(self):
        """Create the login tab content"""
        frame = ttk.LabelFrame(self.login_frame, text="LinkedIn Credentials")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Email
        ttk.Label(frame, text="Email:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        ttk.Entry(frame, textvariable=self.email_var, width=40).grid(row=0, column=1, padx=10, pady=10)
        
        # Password
        ttk.Label(frame, text="Password:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        password_entry = ttk.Entry(frame, textvariable=self.password_var, width=40, show="*")
        password_entry.grid(row=1, column=1, padx=10, pady=10)
        
        # Save credentials checkbox
        ttk.Checkbutton(frame, text="Save credentials", variable=self.save_creds_var).grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="w")
        
        # Status display
        ttk.Label(frame, text="Status:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.login_status_label = ttk.Label(frame, text="Not logged in")
        self.login_status_label.grid(row=3, column=1, padx=10, pady=10, sticky="w")
        
        # Login button
        login_button = ttk.Button(frame, text="Login to LinkedIn", command=self.handle_login)
        login_button.grid(row=4, column=0, columnspan=2, padx=10, pady=20)
    
    def create_connect_tab(self):
        """Create the connect tab content"""
        frame = ttk.LabelFrame(self.connect_frame, text="Connection Settings")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Search query
        ttk.Label(frame, text="Search Query:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        ttk.Entry(frame, textvariable=self.search_query_var, width=40).grid(row=0, column=1, padx=10, pady=10)
        
        # Number of requests
        ttk.Label(frame, text="Number of Requests:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        ttk.Entry(frame, textvariable=self.num_requests_var, width=10).grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # Include note option
        note_check = ttk.Checkbutton(frame, text="Include note with requests", variable=self.include_note_var, 
                                    command=self.toggle_note_field)
        note_check.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="w")
        
        # Custom note field
        ttk.Label(frame, text="Custom Note:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.note_entry = ttk.Entry(frame, textvariable=self.custom_note_var, width=40, state="disabled")
        self.note_entry.grid(row=3, column=1, padx=10, pady=10)
        
        # Status label
        self.connect_status_label = ttk.Label(frame, text="")
        self.connect_status_label.grid(row=4, column=0, columnspan=2, padx=10, pady=10)
        
        # Control buttons frame
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=5, column=0, columnspan=2, padx=10, pady=10)
        
        # Start button
        self.start_button = ttk.Button(button_frame, text="Start Automation", command=self.start_automation)
        self.start_button.pack(side="left", padx=5)
        
        # Stop button
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_automation, state="disabled")
        self.stop_button.pack(side="left", padx=5)
    
    def create_settings_tab(self):
        """Create the settings tab content"""
        frame = ttk.LabelFrame(self.settings_frame, text="Application Settings")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Clear saved data button
        clear_button = ttk.Button(frame, text="Clear Saved Credentials", command=self.clear_saved_credentials)
        clear_button.pack(pady=20)
        
        # About section
        about_frame = ttk.LabelFrame(frame, text="About")
        about_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        about_text = "LinkedIn Automation Tool\n\n" \
                    "This application helps automate LinkedIn connection requests.\n" \
                    "Use responsibly and be aware of LinkedIn's terms of service."
        
        ttk.Label(about_frame, text=about_text, justify="center").pack(padx=10, pady=10)
    
    def create_logs_tab(self):
        """Create the logs tab content"""
        frame = ttk.LabelFrame(self.logs_frame, text="Activity Logs")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=70, height=20)
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.log_text.config(state="disabled")
        
        # Clear logs button
        clear_logs_button = ttk.Button(frame, text="Clear Logs", command=self.clear_logs)
        clear_logs_button.pack(pady=10)
    
    def handle_login(self):
        """Handle the login process"""
        if not self.email_var.get() or not self.password_var.get():
            messagebox.showerror("Error", "Please enter both email and password")
            return
            
        self.update_status("Initializing login process...")
        
        def login_thread():
            try:
                # Import here for thread safety
                from linkedin_bot import LinkedInBot
                
                self.bot = LinkedInBot(update_status_callback=self.update_status)
                
                if not self.bot.initialize_driver():
                    self.update_status("Failed to initialize browser")
                    return
                    
                success = self.bot.login(self.email_var.get(), self.password_var.get())
                
                if success:
                    # Save credentials if requested
                    if self.save_creds_var.get():
                        self.save_settings()
                    
                    # Update UI
                    self.root.after(0, lambda: self.login_status_label.config(text="Logged in successfully"))
                    self.root.after(0, lambda: self.notebook.select(1))  # Switch to Connect tab
                else:
                    self.root.after(0, lambda: self.login_status_label.config(text="Login failed"))
            
            except Exception as e:
                self.update_status(f"Error in login thread: {e}")
                self.root.after(0, lambda: self.login_status_label.config(text="Error occurred"))
        
        # Run login in a separate thread
        threading.Thread(target=login_thread, daemon=True).start()
    
    def start_automation(self):
        """Start the automation process"""
        if not self.bot:
            messagebox.showerror("Error", "Please log in first")
            self.notebook.select(0)  # Switch to Login tab
            return
            
        if not self.search_query_var.get():
            messagebox.showerror("Error", "Please enter a search query")
            return
            
        try:
            num_requests = int(self.num_requests_var.get())
            if num_requests <= 0:
                messagebox.showerror("Error", "Number of requests must be positive")
                return
        except ValueError:
            messagebox.showerror("Error", "Number of requests must be a number")
            return
            
        # Update UI
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.automation_running = True
            
        # Get parameters
        search_query = self.search_query_var.get()
        include_note = self.include_note_var.get()
        custom_note = self.custom_note_var.get() if include_note else ""
            
        def automation_thread():
            try:
                self.update_status(f"Starting automation for '{search_query}'...")
                self.bot.search_and_connect(search_query, num_requests, include_note, custom_note)
            except Exception as e:
                self.update_status(f"Error in automation: {e}")
            finally:
                # Re-enable UI elements
                self.root.after(0, lambda: self.start_button.config(state="normal"))
                self.root.after(0, lambda: self.stop_button.config(state="disabled"))
                self.automation_running = False
                
        # Run automation in a separate thread
        threading.Thread(target=automation_thread, daemon=True).start()
    
    def stop_automation(self):
        """Stop the automation process"""
        if self.bot and self.automation_running:
            self.bot.stop()
            self.update_status("Stopping automation...")
            self.automation_running = False
            
            # Update buttons
            self.stop_button.config(state="disabled")
            # Don't enable start button until automation is fully stopped
    
    def toggle_note_field(self):
        """Enable or disable the note field based on checkbox"""
        if self.include_note_var.get():
            self.note_entry.config(state="normal")
        else:
            self.note_entry.config(state="disabled")
    
    def update_status(self, message):
        """Update status message and log"""
        self.status_message = message
        
        # Update connection status label
        self.root.after(0, lambda: self.connect_status_label.config(text=message))
        
        # Add to logs
        self.root.after(0, self.add_log)
    
    def add_log(self):
        """Add message to log"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {self.status_message}\n"
        
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")
    
    def clear_logs(self):
        """Clear the logs"""
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state="disabled")
    
    def save_settings(self):
        """Save settings to file"""
        settings = {
            "email": self.email_var.get() if self.save_creds_var.get() else "",
            "search_query": self.search_query_var.get(),
            "include_note": self.include_note_var.get(),
            "custom_note": self.custom_note_var.get(),
        }
        
        try:
            with open("linkedin_settings.json", "w") as f:
                json.dump(settings, f)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def load_settings(self):
        """Load settings from file"""
        try:
            if os.path.exists("linkedin_settings.json"):
                with open("linkedin_settings.json", "r") as f:
                    settings = json.load(f)
                    
                    if "email" in settings and settings["email"]:
                        self.email_var.set(settings["email"])
                        self.save_creds_var.set(True)
                    
                    if "search_query" in settings:
                        self.search_query_var.set(settings["search_query"])
                    
                    if "include_note" in settings:
                        self.include_note_var.set(settings["include_note"])
                        self.toggle_note_field()
                    
                    if "custom_note" in settings:
                        self.custom_note_var.set(settings["custom_note"])
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def clear_saved_credentials(self):
        """Clear saved credentials"""
        try:
            if os.path.exists("linkedin_settings.json"):
                with open("linkedin_settings.json", "r") as f:
                    settings = json.load(f)
                
                settings["email"] = ""
                
                with open("linkedin_settings.json", "w") as f:
                    json.dump(settings, f)
                    
                messagebox.showinfo("Success", "Saved credentials cleared")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear credentials: {e}")
    
    def on_closing(self):
        """Handle application closing"""
        if self.bot:
            if self.automation_running:
                self.bot.stop()
            self.bot.close()
        
        self.root.destroy()