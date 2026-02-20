import json
import os
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import font as tkfont


DATA_FILE = "storage.json"


class CollegeManagementApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("College Management Dashboard")
        self.root.geometry("980x560")
        self.root.minsize(900, 520)

        self.students = []  # list[dict]

        self._configure_styles()
        self._build_layout()
        self._load_data()

    # ---------------------- UI / Styles ----------------------
    def _configure_styles(self) -> None:
        style = ttk.Style()
        # Use default theme; try clam if available for nicer Treeview
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("App.TFrame", background="#0f172a")
        style.configure("Header.TLabel", background="#0f172a", foreground="#e2e8f0", font=("Segoe UI", 16, "bold"))
        style.configure("Card.TFrame", background="#111827", relief="flat")
        style.configure("CardTitle.TLabel", background="#111827", foreground="#e5e7eb", font=("Segoe UI", 11, "bold"))
        style.configure("TLabel", background="#111827", foreground="#e5e7eb", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10, "bold"))

        # Treeview styling
        style.configure(
            "App.Treeview",
            background="#0b1220",
            foreground="#e5e7eb",
            fieldbackground="#0b1220",
            rowheight=30,
            borderwidth=0,
            font=("Segoe UI", 10),
        )
        style.map("App.Treeview", background=[("selected", "#1f2937")])
        style.configure("App.Treeview.Heading", background="#0f172a", foreground="#93c5fd", font=("Segoe UI", 10, "bold"))

        # Keep a matching font object for precise hit-testing in Actions column
        self._tree_font = tkfont.Font(family="Segoe UI", size=10)

    def _build_layout(self) -> None:
        container = ttk.Frame(self.root, style="App.TFrame")
        container.pack(fill="both", expand=True)

        # Header
        header = ttk.Frame(container, style="App.TFrame")
        header.pack(fill="x", padx=16, pady=(16, 8))
        ttk.Label(header, text="College Management Dashboard", style="Header.TLabel").pack(side="left")

        # Card with form
        form_card = ttk.Frame(container, style="Card.TFrame")
        form_card.pack(fill="x", padx=16, pady=8)

        ttk.Label(form_card, text="Add Student", style="CardTitle.TLabel").grid(row=0, column=0, columnspan=8, sticky="w", padx=16, pady=(12, 4))

        # Inputs
        ttk.Label(form_card, text="Name").grid(row=1, column=0, sticky="w", padx=(16, 6), pady=6)
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(form_card, textvariable=self.name_var, width=p28)
        self.name_entry.grid(row=1, column=1, sticky="w", padx=(0, 16), pady=6)

        ttk.Label(form_card, text="Enrollment No.").grid(row=1, column=2, sticky="w", padx=(6, 6), pady=6)
        self.enroll_var = tk.StringVar()
        self.enroll_entry = ttk.Entry(form_card, textvariable=self.enroll_var, width=24)
        self.enroll_entry.grid(row=1, column=3, sticky="w", padx=(0, 16), pady=6)

        ttk.Label(form_card, text="Courses").grid(row=2, column=0, sticky="w", padx=(16, 6), pady=6)
        self.courses_var = tk.StringVar()
        self.courses_entry = ttk.Entry(form_card, textvariable=self.courses_var, width=28)
        self.courses_entry.grid(row=2, column=1, sticky="w", padx=(0, 16), pady=6)

        ttk.Label(form_card, text="Phone").grid(row=2, column=2, sticky="w", padx=(6, 6), pady=6)
        self.phone_var = tk.StringVar()
        self.phone_entry = ttk.Entry(form_card, textvariable=self.phone_var, width=24)
        self.phone_entry.grid(row=2, column=3, sticky="w", padx=(0, 16), pady=6)

        add_btn = ttk.Button(form_card, text="Add", command=self._on_add_student)
        add_btn.grid(row=1, column=4, rowspan=2, sticky="nsw", padx=(0, 16))

        # Spacer
        form_card.grid_columnconfigure(5, weight=1)

        # Table card
        table_card = ttk.Frame(container, style="Card.TFrame")
        table_card.pack(fill="both", expand=True, padx=16, pady=(8, 16))

        ttk.Label(table_card, text="Students", style="CardTitle.TLabel").pack(anchor="w", padx=16, pady=(12, 4))

        # Treeview with columns
        columns = ("name", "enrollment", "courses", "phone", "actions")
        self.tree = ttk.Treeview(table_card, columns=columns, show="headings", style="App.Treeview")
        self.tree.heading("name", text="Student Name")
        self.tree.heading("enrollment", text="Enrollment No.")
        self.tree.heading("courses", text="Courses")
        self.tree.heading("phone", text="Phone")
        self.tree.heading("actions", text="Actions")

        self.tree.column("name", width=220, anchor="w")
        self.tree.column("enrollment", width=150, anchor="center")
        self.tree.column("courses", width=200, anchor="w")
        self.tree.column("phone", width=130, anchor="center")
        self.tree.column("actions", width=160, anchor="center")

        vsb = ttk.Scrollbar(table_card, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_card, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscroll=vsb.set, xscroll=hsb.set)

        self.tree.pack(fill="both", expand=True, padx=12, pady=(0, 6))
        vsb.place(in_=self.tree, relx=1.0, rely=0, relheight=1.0, anchor="ne")
        hsb.pack(fill="x", padx=12, pady=(0, 12))

        # Bind click for actions
        self.tree.bind("<Button-1>", self._on_tree_click)

        # Footer action hints
        hint = ttk.Label(table_card, text="Tip: Click Edit to modify a row or Delete to remove it.")
        hint.pack(anchor="w", padx=16, pady=(0, 12))

    # ---------------------- Data Persistence ----------------------
    def _data_file_path(self) -> str:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), DATA_FILE)

    def _load_data(self) -> None:
        path = self._data_file_path()
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.students = json.load(f)
            except Exception:
                self.students = []
        else:
            self.students = []
        self._refresh_table()

    def _save_data(self) -> None:
        path = self._data_file_path()
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.students, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data: {e}")

    # ---------------------- Helpers ----------------------
    @staticmethod
    def _format_actions_text() -> str:
        # Using padded text to create clickable regions
        return "[ Edit ]    [ Delete ]"

    def _refresh_table(self) -> None:
        self.tree.delete(*self.tree.get_children())
        for idx, s in enumerate(self.students):
            values = (
                s.get("name", ""),
                s.get("enrollment", ""),
                s.get("courses", ""),
                s.get("phone", ""),
                self._format_actions_text(),
            )
            self.tree.insert("", "end", iid=str(idx), values=values)

    @staticmethod
    def _validate_inputs(name: str, enrollment: str, courses: str, phone: str) -> tuple[bool, str]:
        if not name.strip():
            return False, "Name is required."
        if not enrollment.strip():
            return False, "Enrollment number is required."
        if not courses.strip():
            return False, "Courses are required."
        phone_digits = ''.join(ch for ch in phone if ch.isdigit())
        if len(phone_digits) < 7:
            return False, "Phone must have at least 7 digits."
        return True, ""

    # ---------------------- Events: Add ----------------------
    def _on_add_student(self) -> None:
        name = self.name_var.get().strip()
        enrollment = self.enroll_var.get().strip()
        courses = self.courses_var.get().strip()
        phone = self.phone_var.get().strip()

        ok, msg = self._validate_inputs(name, enrollment, courses, phone)
        if not ok:
            messagebox.showwarning("Invalid Input", msg)
            return

        self.students.append({
            "name": name,
            "enrollment": enrollment,
            "courses": courses,
            "phone": phone,
        })
        self._save_data()
        self._refresh_table()

        # Clear inputs, keep read-only nature in table (Treeview cells are non-editable)
        self.name_var.set("")
        self.enroll_var.set("")
        self.courses_var.set("")
        self.phone_var.set("")

    # ---------------------- Events: Tree Click (Actions) ----------------------
    def _on_tree_click(self, event: tk.Event) -> None:
        # Determine if click was on actions column of a specific row
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        row_id = self.tree.identify_row(event.y)
        col_id = self.tree.identify_column(event.x)  # #1, #2, ...
        if not row_id or col_id != f"#{len(self.tree["columns"])}":  # last column 'actions'
            return

        # Determine whether Edit or Delete area was clicked based on x within cell bbox
        bbox = self.tree.bbox(row_id, "actions")
        if not bbox:
            return
        x_cell, y_cell, w_cell, h_cell = bbox
        rel_x = event.x - x_cell

        # Measure using the exact font used by the Treeview rows
        f = getattr(self, "_tree_font", tkfont.nametofont("TkDefaultFont"))
        segments = ["[ Edit ]", "    ", "[ Delete ]"]
        w_edit = f.measure(segments[0])
        w_gap = f.measure(segments[1])
        w_delete = f.measure(segments[2])

        # Boundaries inside the cell
        edit_start = 0
        edit_end = w_edit
        delete_start = w_edit + w_gap
        delete_end = delete_start + w_delete

        # Add a small tolerance to make clicking easier
        tol = 4

        if edit_start - tol <= rel_x <= edit_end + tol:
            self._open_edit_dialog(int(row_id))
        elif delete_start - tol <= rel_x <= delete_end + tol:
            self._confirm_delete(int(row_id))

    # ---------------------- Edit ----------------------
    def _open_edit_dialog(self, index: int) -> None:
        if not (0 <= index < len(self.students)):
            return

        record = self.students[index]

        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Student")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.geometry("420x260")

        frm = ttk.Frame(dialog, padding=16)
        frm.pack(fill="both", expand=True)

        name_var = tk.StringVar(value=record.get("name", ""))
        enroll_var = tk.StringVar(value=record.get("enrollment", ""))
        courses_var = tk.StringVar(value=record.get("courses", ""))
        phone_var = tk.StringVar(value=record.get("phone", ""))

        ttk.Label(frm, text="Name").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=8)
        ttk.Entry(frm, textvariable=name_var, width=34).grid(row=0, column=1, sticky="w", pady=8)

        ttk.Label(frm, text="Enrollment No.").grid(row=1, column=0, sticky="w", padx=(0, 8), pady=8)
        ttk.Entry(frm, textvariable=enroll_var, width=28).grid(row=1, column=1, sticky="w", pady=8)

        ttk.Label(frm, text="Courses").grid(row=2, column=0, sticky="w", padx=(0, 8), pady=8)
        ttk.Entry(frm, textvariable=courses_var, width=34).grid(row=2, column=1, sticky="w", pady=8)

        ttk.Label(frm, text="Phone").grid(row=3, column=0, sticky="w", padx=(0, 8), pady=8)
        ttk.Entry(frm, textvariable=phone_var, width=28).grid(row=3, column=1, sticky="w", pady=8)

        btns = ttk.Frame(frm)
        btns.grid(row=4, column=0, columnspan=2, sticky="e", pady=(12, 0))

        def on_save() -> None:
            name = name_var.get().strip()
            enrollment = enroll_var.get().strip()
            courses = courses_var.get().strip()
            phone = phone_var.get().strip()
            ok, msg = self._validate_inputs(name, enrollment, courses, phone)
            if not ok:
                messagebox.showwarning("Invalid Input", msg, parent=dialog)
                return
            self.students[index] = {
                "name": name,
                "enrollment": enrollment,
                "courses": courses,
                "phone": phone,
            }
            self._save_data()
            self._refresh_table()
            dialog.destroy()

        ttk.Button(btns, text="Cancel", command=dialog.destroy).pack(side="right", padx=(8, 0))
        ttk.Button(btns, text="Save", command=on_save).pack(side="right")

        dialog.wait_visibility()
        dialog.focus_set()

    # ---------------------- Delete ----------------------
    def _confirm_delete(self, index: int) -> None:
        if not (0 <= index < len(self.students)):
            return
        rec = self.students[index]
        name = rec.get("name", "this record")
        if messagebox.askyesno("Delete", f"Delete {name}? This cannot be undone."):
            del self.students[index]
            self._save_data()
            self._refresh_table()


def main() -> None:
    root = tk.Tk()
    app = CollegeManagementApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()


