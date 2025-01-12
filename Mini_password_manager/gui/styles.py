from tkinter import ttk

def apply_styles():
    style = ttk.Style()
    
    # Configure Treeview
    style.configure("Treeview",
                   background="#ffffff",
                   foreground="black",
                   rowheight=25,
                   fieldbackground="#ffffff")
    
    style.configure("Treeview.Heading",
                   background="#f0f0f0",
                   font=('Helvetica', 10, 'bold'))
    
    # Configure Buttons
    style.configure("TButton",
                   padding=6,
                   relief="flat",
                   background="#2196F3")
    
    # Configure Entry fields
    style.configure("TEntry",
                   padding=5)
    
    # Configure Frames
    style.configure("TFrame",
                   background="#ffffff")
    
    # Configure Labels
    style.configure("TLabel",
                   padding=5) 