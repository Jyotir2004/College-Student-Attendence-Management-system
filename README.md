## College Management Dashboard (Tkinter)

A Tkinter desktop app to manage college students with a dashboard-style UI. It shows a table with columns: Student Name, Enrollment No., Courses, Phone, and an Actions column with Edit/Delete.

### Features
- Add, view, edit, and delete students (CRUD)
- Rows are read-only; editing only via the per-row Edit action
- Styled `ttk.Treeview` and modern layout
- JSON persistence (`storage.json`) created automatically
- Basic validation for required fields and phone length

### Requirements
- Python 3.9+ (Tkinter included on Windows)

### Run
1. Open terminal in the folder `project cursor`.
2. Run:
```bash
python app.py
```

Or run the Streamlit version:
```bash
pip install streamlit
streamlit run stream.py
```

### Usage
- Fill Name, Enrollment No., Courses, Phone; click Add.
- Click Edit in the row to modify; click Delete to remove.

### Data File
- Stored in `storage.json` next to `app.py`. Auto-created.

### Customize
- Update colors/fonts in `_configure_styles()` and column widths in `_build_layout()` within `app.py`.

### Structure
```
project cursor/
├─ app.py
├─ stream.py
├─ storage.json (created at runtime)
└─ README.md
```

### Notes
- The Actions column uses clickable text regions inside the Treeview cell to simulate buttons.

### License
MIT


