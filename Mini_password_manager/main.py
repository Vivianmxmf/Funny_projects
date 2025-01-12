import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import csv
from datetime import datetime
from ttkthemes import ThemedTk
from gui.dialogs import AddPasswordDialog

class PasswordManager:
    def __init__(self):
        self.root = ThemedTk(theme="arc")  # Modern theme
        self.root.title("Secure Password Manager")
        self.root.geometry("800x600")
        
        # Initialize encryption key
        self.key = None
        self.fernet = None
        self.is_encrypted = True
        
        # Load or create data file
        self.data_file = "passwords.json"
        self.load_data()
        
        self.setup_gui()
    
    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    self.passwords = json.load(f)
            except:
                self.passwords = {}
        else:
            self.passwords = {}
    
    def save_data(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.passwords, f)
    
    def generate_key(self, master_password):
        salt = b'salt_'  # In production, use a random salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
        return key
    
    def setup_gui(self):
        # Create notebook for multiple pages
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(pady=10, expand=True)
        
        # Create frames for different pages
        self.login_frame = ttk.Frame(self.notebook)
        self.passwords_frame = ttk.Frame(self.notebook)
        self.settings_frame = ttk.Frame(self.notebook)
        
        # Add frames to notebook
        self.notebook.add(self.login_frame, text="Login")
        self.notebook.add(self.passwords_frame, text="Passwords")
        self.notebook.add(self.settings_frame, text="Settings")
        
        self.setup_login_page()
        self.setup_passwords_page()
        self.setup_settings_page()
    
    def setup_login_page(self):
        login_label = ttk.Label(self.login_frame, text="Master Password", font=("Helvetica", 14))
        login_label.pack(pady=20)
        
        self.master_password_entry = ttk.Entry(self.login_frame, show="*")
        self.master_password_entry.pack(pady=10)
        
        login_button = ttk.Button(self.login_frame, text="Login", command=self.login)
        login_button.pack(pady=10)
        
        create_button = ttk.Button(self.login_frame, text="Create New Master Password", 
                                 command=self.create_master_password)
        create_button.pack(pady=10)
    
    def setup_passwords_page(self):
        # Buttons frame
        buttons_frame = ttk.Frame(self.passwords_frame)
        buttons_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(buttons_frame, text="Add Password", 
                  command=self.add_password_dialog).pack(side="left", padx=5)
        ttk.Button(buttons_frame, text="Toggle Encryption", 
                  command=self.toggle_encryption).pack(side="left", padx=5)
        ttk.Button(buttons_frame, text="Export Passwords", 
                  command=self.export_passwords).pack(side="left", padx=5)
        
        # Treeview for passwords
        self.tree = ttk.Treeview(self.passwords_frame, columns=("Account", "Username", "Password"),
                                show="headings")
        self.tree.heading("Account", text="Account")
        self.tree.heading("Username", text="Username")
        self.tree.heading("Password", text="Password")
        self.tree.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Search frame
        search_frame = ttk.Frame(self.passwords_frame)
        search_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side="left", padx=5)
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.search_entry.bind('<KeyRelease>', self.search_passwords)
    
    def setup_settings_page(self):
        ttk.Label(self.settings_frame, text="Settings", 
                 font=("Helvetica", 14)).pack(pady=20)
        
        ttk.Button(self.settings_frame, text="Change Master Password",
                  command=self.change_master_password).pack(pady=10)
        
        ttk.Button(self.settings_frame, text="Backup Passwords",
                  command=self.backup_passwords).pack(pady=10)
        
        ttk.Button(self.settings_frame, text="Clear All Data",
                  command=self.clear_data).pack(pady=10)
    
    def login(self):
        master_password = self.master_password_entry.get()
        if not master_password:
            messagebox.showerror("Error", "Please enter master password")
            return
            
        self.key = self.generate_key(master_password)
        self.fernet = Fernet(self.key)
        self.refresh_password_list()
        self.notebook.select(1)  # Switch to passwords tab
    
    def create_master_password(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Create Master Password")
        dialog.geometry("300x200")
        
        ttk.Label(dialog, text="New Master Password:").pack(pady=5)
        password_entry = ttk.Entry(dialog, show="*")
        password_entry.pack(pady=5)
        
        ttk.Label(dialog, text="Confirm Password:").pack(pady=5)
        confirm_entry = ttk.Entry(dialog, show="*")
        confirm_entry.pack(pady=5)
        
        def save_master():
            if password_entry.get() != confirm_entry.get():
                messagebox.showerror("Error", "Passwords don't match!")
                return
            if len(password_entry.get()) < 8:
                messagebox.showerror("Error", "Password too short!")
                return
                
            self.key = self.generate_key(password_entry.get())
            self.fernet = Fernet(self.key)
            dialog.destroy()
            messagebox.showinfo("Success", "Master password created!")
            
        ttk.Button(dialog, text="Save", command=save_master).pack(pady=20)
    
    def add_password_dialog(self):
        dialog = AddPasswordDialog(self.root)
        self.root.wait_window(dialog.dialog)
        if dialog.result:
            self.add_password(dialog.result)
    
    def add_password(self, data):
        if self.fernet:
            encrypted_password = self.fernet.encrypt(
                data['password'].encode()).decode()
            self.passwords[data['account']] = {
                'username': data['username'],
                'password': encrypted_password
            }
            self.save_data()
            self.refresh_password_list()
        else:
            messagebox.showerror("Error", "Please login first")
    
    def refresh_password_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for account, data in self.passwords.items():
            password = data['password']
            if not self.is_encrypted and self.fernet:
                try:
                    password = self.fernet.decrypt(
                        password.encode()).decode()
                except:
                    password = "**Decryption Failed**"
            
            self.tree.insert('', 'end', values=(
                account,
                data['username'],
                password if not self.is_encrypted else "********"
            ))
    
    def toggle_encryption(self):
        self.is_encrypted = not self.is_encrypted
        self.refresh_password_list()
    
    def export_passwords(self):
        if not self.fernet:
            messagebox.showerror("Error", "Please login first")
            return
            
        filename = f"passwords_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Account', 'Username', 'Password'])
            
            for account, data in self.passwords.items():
                password = self.fernet.decrypt(
                    data['password'].encode()).decode()
                writer.writerow([account, data['username'], password])
                
        messagebox.showinfo("Success", f"Passwords exported to {filename}")
    
    def search_passwords(self, event=None):
        search_term = self.search_entry.get().lower()
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for account, data in self.passwords.items():
            if search_term in account.lower() or \
               search_term in data['username'].lower():
                password = data['password']
                if not self.is_encrypted and self.fernet:
                    try:
                        password = self.fernet.decrypt(
                            password.encode()).decode()
                    except:
                        password = "**Decryption Failed**"
                
                self.tree.insert('', 'end', values=(
                    account,
                    data['username'],
                    password if not self.is_encrypted else "********"
                ))
    
    def backup_passwords(self):
        if not self.fernet:
            messagebox.showerror("Error", "Please login first")
            return
            
        backup_file = f"passwords_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(backup_file, 'w') as f:
            json.dump(self.passwords, f)
        messagebox.showinfo("Success", f"Backup created: {backup_file}")
    
    def clear_data(self):
        if messagebox.askyesno("Confirm", "Are you sure? This will delete all passwords!"):
            self.passwords = {}
            self.save_data()
            self.refresh_password_list()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = PasswordManager()
    app.run()

