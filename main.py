import sys
import traceback

def main():
    """Initialize and run the LinkedIn Automation Tool with error handling"""
    try:
        import tkinter as tk
        from gui import LinkedInAutomationGUI
        
        # Initialize the root window
        root = tk.Tk()
        app = LinkedInAutomationGUI(root)
        
        # Handle window closing
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        
        # Start the application
        print("Starting LinkedIn Automation Tool...")
        root.mainloop()
        
    except ImportError as e:
        print(f"Import Error: {e}")
        print("Make sure all required packages are installed. Try running: pip install -r requirements.txt")
        input("Press Enter to exit...")
        
    except Exception as e:
        print(f"Error starting application: {e}")
        print("Detailed error information:")
        traceback.print_exc()
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()