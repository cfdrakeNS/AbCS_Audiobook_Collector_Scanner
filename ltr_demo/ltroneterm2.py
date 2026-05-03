import tkinter as tk

class AS400Simulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Terminal Emulator - Commercial Loan Inquiry")
        self.root.configure(bg="#222222") # Dark grey border area
        
        # Padding to move the screen away from the top/left edges
        self.container = tk.Frame(root, bg="#222222", padx=40, pady=40)
        self.container.pack()

        # Standard Terminal Grid: 80x25
        self.text_area = tk.Text(self.container, font=("Courier New", 14), 
                                 width=80, height=25, 
                                 bg="black", insertbackground="white",
                                 relief="flat", bd=0)
        self.text_area.pack()

        # Tags for Colors and Protection
        self.text_area.tag_configure("label", foreground="turquoise") 
        self.text_area.tag_configure("field", foreground="white")     
        self.text_area.tag_configure("alert", foreground="red")       
        self.text_area.tag_configure("msg", foreground="yellow")      

        # New Tab Stops for Commercial Layout (Row, Col, Length)
        self.fields = [
            (2, 14, 10), (2, 40, 12), (2, 65, 8), # ID, Short Name, Portfolio
            (3, 14, 25), (3, 65, 10),             # Legal Name, Risk Rating
            (4, 14, 15), (4, 40, 15), (4, 65, 10), # Contact, Title, Phone
            (5, 14, 30)                           # Email/Web
        ]
        self.current_field_index = 0

        # Bindings
        self.root.bind("<Tab>", self.tab_next)
        self.root.bind("<Shift-Tab>", self.tab_prev)
        self.text_area.bind("<Key>", self.intercept_typing)

        self.setup_grid()
        self.build_screen()
        self.focus_field()

    def setup_grid(self):
        self.text_area.delete("1.0", tk.END)
        for _ in range(25):
            self.text_area.insert(tk.END, " " * 80 + "\n")

    def write(self, row, col, text, tag):
        start = f"{row}.{col}"
        end = f"{row}.{col + len(text)}"
        self.text_area.delete(start, end)
        self.text_area.insert(start, text, tag)

    def build_screen(self):
        # Header Row 1
        self.write(1, 0, "LN-INQ-04", "label")
        self.write(1, 28, "COMMERCIAL PORTFOLIO REVIEW", "label")
        self.write(1, 68, "2026-05-02", "label")

        # Customer Header Info
        self.write(2, 0, "ENTITY ID:   ", "label")
        self.write(2, 14, "88421-990", "field")
        self.write(2, 28, "SHORT NAME: ", "label")
        self.write(2, 40, "GLOBAL-TECH", "field")
        self.write(2, 54, "DEPT:     ", "label")
        self.write(2, 65, "CORP-01", "field")

        self.write(3, 0, "LEGAL NAME:  ", "label")
        self.write(3, 14, "GLOBAL TECHNOLOGY SOLUTIONS INC", "field")
        self.write(3, 54, "RISK RATING: ", "label")
        self.write(3, 67, "B3", "field")
        
        self.write(4, 0, "PRIMARY CTR: ", "label")
        self.write(4, 14, "SARAH JENKINS", "field")
        self.write(4, 32, "TITLE: ", "label")
        self.write(4, 40, "TREASURY MGR", "field")
        self.write(4, 54, "STATUS:   ", "label")
        self.write(4, 65, "PAST DUE", "alert") # Auto-read target

        self.write(5, 0, "CONTACT EM:  ", "label")
        self.write(5, 14, "S.JENKINS@GTS-CORP.COM", "field")
        self.write(5, 54, "REGION:   ", "label")
        self.write(5, 65, "EAST-CAN", "label")

        # Column Processing Section (Rows 8-12)[cite: 1, 2]
        self.write(7, 2, "LOAN INSTRUMENT", "label")
        self.write(7, 25, "CURR BALANCE", "label")
        self.write(7, 45, "INT RATE", "label")
        self.write(7, 60, "NEXT MATURITY", "label")

        # Column Data with *E* flags for demo
        data = [
            ("*E* REVOLVING CR", "450,000.00", "5.25%", "2027-01-15"),
            ("TERM LOAN-01", "1,200,344.12", "4.50%", "2030-06-01"),
            ("*E* EQUIP LEASE", "89,322.00", "6.10%", "2026-12-20"),
            ("CORP REAL EST", "3,455,000.00", "4.15%", "2035-11-01"),
            ("OP-OVERDRAFT", "12,000.00", "9.00%", "N/A")
        ]

        for i, (instr, bal, rate, mat) in enumerate(data):
            r = 9 + i
            self.write(r, 2, instr, "field")  # Column 1
            self.write(r, 25, bal, "field")    # Column 2[cite: 1]
            self.write(r, 45, rate, "field")   # Column 3[cite: 1]
            self.write(r, 60, mat, "field")    # Column 4[cite: 1]

        # Message Lines at bottom[cite: 1]
        self.write(21, 2, "MESSAGE: OUTSTANDING EXCEPTIONS ON REVOLVING CREDIT", "msg")
        self.write(22, 2, "         REVIEW RISK RATING FOR QUARTERLY AUDIT", "msg")
        self.write(24, 0, "F3=EXIT  F5=REFRESH  F7=BACKWARD  F8=FORWARD  F12=CANCEL", "label")

    def intercept_typing(self, event):
        """Forces overwrite mode within editable fields."""
        if len(event.char) == 1 and event.keysym not in ("BackSpace", "Delete", "Tab"):
            curr_pos = self.text_area.index(tk.INSERT)
            row, col = map(int, curr_pos.split('.'))
            for f_row, f_col, f_len in self.fields:
                if row == f_row and f_col <= col < (f_col + f_len):
                    self.write(row, col, event.char, "field")
                    self.text_area.mark_set("insert", f"{row}.{col+1}")
                    return "break"
        if event.keysym not in ("Up", "Down", "Left", "Right"):
            return "break"

    def tab_next(self, event):
        self.current_field_index = (self.current_field_index + 1) % len(self.fields)
        self.focus_field()
        return "break"

    def tab_prev(self, event):
        self.current_field_index = (self.current_field_index - 1) % len(self.fields)
        self.focus_field()
        return "break"

    def focus_field(self):
        row, col, _ = self.fields[self.current_field_index]
        self.text_area.mark_set("insert", f"{row}.{col}")
        self.text_area.focus_set()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1100x800") # Larger window to show whitespace
    app = AS400Simulator(root)
    root.mainloop()