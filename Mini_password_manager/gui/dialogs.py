import tkinter as tk
from tkinter import ttk, messagebox
from utils.password_generator import PasswordGenerator

class AddPasswordDialog:
    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add Password")
        self.dialog.geometry("400x500")
        self.result = None
        self.setup_dialog()
        
    def setup_dialog(self):
        # Account Frame
        account_frame = ttk.LabelFrame(self.dialog, text="Account Details")
        account_frame.pack(padx=10, pady=5, fill="x")
        
        ttk.Label(account_frame, text="Account Name:").pack(pady=5)
        self.account_entry = ttk.Entry(account_frame)
        self.account_entry.pack(pady=5, fill="x", padx=5)
        
        ttk.Label(account_frame, text="Username:").pack(pady=5)
        self.username_entry = ttk.Entry(account_frame)
        self.username_entry.pack(pady=5, fill="x", padx=5)
        
        ttk.Label(account_frame, text="Password:").pack(pady=5)
        self.password_entry = ttk.Entry(account_frame, show="*")
        self.password_entry.pack(pady=5, fill="x", padx=5)
        
        # Password Generator Frame
        generator_frame = ttk.LabelFrame(self.dialog, text="Password Generator")
        generator_frame.pack(padx=10, pady=5, fill="x")
        
        self.length_var = tk.IntVar(value=12)
        ttk.Label(generator_frame, text="Length:").pack(pady=5)
        length_spin = ttk.Spinbox(generator_frame, from_=8, to=32, 
                                 textvariable=self.length_var)
        length_spin.pack(pady=5)
        
        self.uppercase_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(generator_frame, text="Uppercase", 
                       variable=self.uppercase_var).pack()
        
        self.lowercase_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(generator_frame, text="Lowercase", 
                       variable=self.lowercase_var).pack()
        
        self.numbers_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(generator_frame, text="Numbers", 
                       variable=self.numbers_var).pack()
        
        self.symbols_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(generator_frame, text="Symbols", 
                       variable=self.symbols_var).pack()
        
        ttk.Button(generator_frame, text="Generate Password",
                  command=self.generate_password).pack(pady=10)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(pady=20, fill="x")
        
        ttk.Button(button_frame, text="Save",
                  command=self.save).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel",
                  command=self.cancel).pack(side="left", padx=5)
    
    def generate_password(self):
        password = PasswordGenerator.generate_password(
            length=self.length_var.get(),
            use_uppercase=self.uppercase_var.get(),
            use_lowercase=self.lowercase_var.get(),
            use_numbers=self.numbers_var.get(),
            use_symbols=self.symbols_var.get()
        )
        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, password)
    
    def save(self):
        if not all([self.account_entry.get(), self.username_entry.get(), 
                   self.password_entry.get()]):
            messagebox.showerror("Error", "All fields are required!")
            return
            
        self.result = {
            "account": self.account_entry.get(),
            "username": self.username_entry.get(),
            "password": self.password_entry.get()
        }
        self.dialog.destroy()
    
    def cancel(self):
        self.dialog.destroy() 