import tkinter as tk

class AS400Simulator:
    def __init__(self, root):
        self.root = root
        self.root.title("AS/400 Banking Inquiry - ltrOne Demo")
        
        # Fixed 80x25 grid style
        self.text_area = tk.Text(root, font=("Courier New", 14), 
                                 width=80, height=25, 
                                 bg="black", insertbackground="white")
        self.text_area.pack()

        # Terminal Color Scheme (AS/400 Style)
        self.text_area.tag_configure("label", foreground="turquoise") # Protected
        self.text_area.tag_configure("field", foreground="white")     # User Entry
        self.text_area.tag_configure("alert", foreground="red")       # Errors/Flags
        self.text_area.tag_configure("status", foreground="green")    # Messages

        self.fields = []
        self.current_field_index = 0
        self.root.bind("<Tab>", self.tab_next)
        self.root.bind("<Shift-Tab>", self.tab_prev)

        self.build_screen()

    def add_element(self, row, col, text, tag):
        # Coordinates must be exact for JAWS Row/Col retrieval
        pos = f"{row}.{col}"
        self.text_area.delete(pos, f"{row}.{col + len(text)}")
        self.text_area.insert(pos, text, tag)
        if tag == "field":
            self.fields.append(pos)

    def build_screen(self):
        # 1. Initialize Blank 80x25 Buffer
        self.text_area.delete("1.0", tk.END)
        for _ in range(25):
            self.text_area.insert(tk.END, " " * 80 + "\n")

        # --- ROW 1: Header (Auto-read targets) ---
        self.add_element(1, 1, "INQ-99", "label")
        self.add_element(1, 30, "BANKING CUSTOMER OVERVIEW", "label")
        self.add_element(1, 68, "2026-05-02", "label")

        # --- ROW 3: Customer Info ---
        self.add_element(3, 1, "CUSTOMER NAME:", "label")
        self.add_element(3, 16, "CLIFFORD DRAKE", "field")
        self.add_element(3, 50, "STATUS:", "label")
        self.add_element(3, 58, "PAST DUE", "alert") # Flag for your script

        # --- ROW 6: Column Headers ---
        self.add_element(6, 5, "ACCOUNT DESCRIPTION", "label")
        self.add_element(6, 40, "BALANCE", "label")
        self.add_element(6, 60, "LAST TRANS", "label")

        # --- ROWS 8-12: Column Data with *E* flags ---
        # Demoing Column Navigation (Alt+Control+Arrows)
        accounts = ["*E* MORTGAGE LOAN", "CHKG-PRIMARY", "SAVINGS-HLDR", "*E* HELOC-REPAIR", "VISA-GOLD"]
        balances = ["250,431.12", "4,312.45", "12,980.00", "5,200.00", "1,155.00"]
        
        for i, (acc, bal) in enumerate(zip(accounts, balances)):
            row = 8 + i
            self.add_element(row, 5, acc, "field")     # Column 1
            self.add_element(row, 40, bal, "field")    # Column 2

        # --- ROW 20: Message Line (Auto-read) ---
        self.add_element(20, 2, "MESSAGE: PLEASE CORRECT ITEMS MARKED WITH *E*", "status")
        
        # --- ROW 22: F-Keys ---
        self.add_element(22, 1, "F3=EXIT   F5=REFRESH   F7=UP   F8=DOWN", "label")

    def tab_next(self, event):
        self.current_field_index = (self.current_field_index + 1) % len(self.fields)
        self.focus_field()
        return "break"

    def tab_prev(self, event):
        self.current_field_index = (self.current_field_index - 1) % len(self.fields)
        self.focus_field()
        return "break"

    def focus_field(self):
        pos = self.fields[self.current_field_index]
        self.text_area.mark_set("insert", pos)
        self.text_area.focus_set()

if __name__ == "__main__":
    root = tk.Tk()
    app = AS400Simulator(root)
    root.mainloop()