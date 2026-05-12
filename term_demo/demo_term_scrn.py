import tkinter as tk

class AS400Simulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Terminal Emulator - Commercial Loan Inquiry")
        self.root.configure(bg="#1A1A1A") 
        
        self.container = tk.Frame(root, bg="#1A1A1A", padx=50, pady=50)
        self.container.pack(expand=True)

        # 80x25 Grid
        self.text_area = tk.Text(self.container, font=("Courier New", 14), 
                                 width=80, height=25, 
                                 bg="black", insertbackground="white",
                                 relief="flat", bd=0)
        self.text_area.pack()

        # Terminal Colors
        self.text_area.tag_configure("label", foreground="turquoise") 
        self.text_area.tag_configure("field", foreground="white")     
        self.text_area.tag_configure("alert", foreground="red")       
        self.text_area.tag_configure("msg", foreground="yellow")      

        # Tab Stops (Row, Col, Length)
        self.fields = [
            (3, 15, 10), (3, 42, 12), (3, 67, 8), 
            (4, 15, 30), (4, 67, 10),             
            (5, 15, 15), (5, 42, 15), (5, 67, 10), 
            (6, 15, 30)                           
        ]
        self.current_field_index = 0

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

    def write_aligned(self, row, anchor_col, text, tag):
        """Right-aligns text ending at anchor_col."""
        start_col = anchor_col - len(text)
        self.write(row, start_col, text, tag)

    def write(self, row, col, text, tag):
        start = f"{row}.{col}"
        end = f"{row}.{col + len(text)}"
        self.text_area.delete(start, end)
        self.text_area.insert(start, text, tag)

    def build_screen(self):
        # Row 1: Header
        self.write(1, 0, "LN-INQ-04", "label")
        self.write(1, 28, "COMMERCIAL PORTFOLIO REVIEW", "label")
        self.write(1, 68, "2026-05-02", "label")

        # Row 2: BLANK LINE (per request)

        # Row 3-6: Aligned Labels (Anchor at column 13)[cite: 2]
        self.write_aligned(3, 13, "ENTITY ID:", "label")
        self.write(3, 15, "88421-990", "field")
        self.write_aligned(3, 40, "SHORT NAME:", "label")
        self.write(3, 42, "GLOBAL-TECH", "field")
        self.write_aligned(3, 65, "DEPT:", "label")
        self.write(3, 67, "CORP-01", "field")

        self.write_aligned(4, 13, "LEGAL NAME:", "label")
        self.write(4, 15, "GLOBAL TECHNOLOGY SOLUTIONS INC", "field")
        self.write_aligned(4, 65, "RISK:", "label")
        self.write(4, 67, "B3", "field")
        
        self.write_aligned(5, 13, "CONTACT:", "label")
        self.write(5, 15, "SARAH JENKINS", "field")
        self.write_aligned(5, 40, "TITLE:", "label")
        self.write(5, 42, "TREASURY MGR", "field")
        self.write_aligned(5, 65, "STATUS:", "label")
        self.write(5, 67, "PAST DUE", "alert") 

        self.write_aligned(6, 13, "EMAIL:", "label")
        self.write(6, 15, "S.JENKINS@GTS-CORP.COM", "field")

        # Column Processing Section
        self.write(9, 2, "LOAN INSTRUMENT", "label")
        self.write(9, 25, "CURR BALANCE", "label")
        self.write(9, 45, "INT RATE", "label")
        self.write(9, 60, "NEXT MATURITY", "label")

        data = [
            ("*E* REVOLVING CR", "450,000.00", "5.25%", "2027-01-15"),
            ("TERM LOAN-01", "1,200,344.12", "4.50%", "2030-06-01"),
            ("*E* EQUIP LEASE", "89,322.00", "6.10%", "2026-12-20"),
            ("CORP REAL EST", "3,455,000.00", "4.15%", "2035-11-01")
        ]

        for i, (instr, bal, rate, mat) in enumerate(data):
            r = 11 + i
            self.write(r, 2, instr, "field")
            self.write(r, 25, bal, "field")
            self.write(r, 45, rate, "field")
            self.write(r, 60, mat, "field")

        # Bottom Messages
        self.write(21, 2, "MESSAGE: OUTSTANDING EXCEPTIONS ON REVOLVING CREDIT", "msg")
        self.write(22, 2, "         REVIEW RISK RATING FOR QUARTERLY AUDIT", "msg")
        self.write(24, 0, "F3=EXIT  F5=REFRESH  F7=BACKWARD  F8=FORWARD  F12=CANCEL", "label")

    def intercept_typing(self, event):
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
    root.geometry("1100x850")
    app = AS400Simulator(root)
    root.mainloop()