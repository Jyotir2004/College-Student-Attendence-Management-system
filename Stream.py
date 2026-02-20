import json
import os
from typing import List, Dict, Tuple

import streamlit as st


DATA_FILE = "storage.json"


def get_data_file_path() -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), DATA_FILE)


def load_students() -> List[Dict[str, str]]:
    path = get_data_file_path()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except Exception:
            pass
    return []


def save_students(students: List[Dict[str, str]]) -> None:
    path = get_data_file_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(students, f, indent=2)


def validate_inputs(name: str, enrollment: str, courses: str, phone: str) -> Tuple[bool, str]:
    if not name.strip():
        return False, "Name is required."
    if not enrollment.strip():
        return False, "Enrollment number is required."
    if not courses.strip():
        return False, "Courses are required."
    digits = "".join(ch for ch in phone if ch.isdigit())
    if len(digits) < 7:
        return False, "Phone must have at least 7 digits."
    return True, ""


def init_state():
    if "students" not in st.session_state:
        st.session_state.students = load_students()
    if "edit_index" not in st.session_state:
        st.session_state.edit_index = None


def add_student(name: str, enrollment: str, courses: str, phone: str) -> bool:
    ok, msg = validate_inputs(name, enrollment, courses, phone)
    if not ok:
        st.warning(msg)
        return False
    st.session_state.students.append({
        "name": name.strip(),
        "enrollment": enrollment.strip(),
        "courses": courses.strip(),
        "phone": phone.strip(),
    })
    save_students(st.session_state.students)
    return True


def update_student(index: int, name: str, enrollment: str, courses: str, phone: str) -> bool:
    if not (0 <= index < len(st.session_state.students)):
        return False
    ok, msg = validate_inputs(name, enrollment, courses, phone)
    if not ok:
        st.warning(msg)
        return False
    st.session_state.students[index] = {
        "name": name.strip(),
        "enrollment": enrollment.strip(),
        "courses": courses.strip(),
        "phone": phone.strip(),
    }
    save_students(st.session_state.students)
    return True


def delete_student(index: int) -> None:
    if 0 <= index < len(st.session_state.students):
        st.session_state.students.pop(index)
        save_students(st.session_state.students)


def main():
    st.set_page_config(page_title="College Management Dashboard", page_icon="🎓", layout="wide")
    init_state()

    st.markdown(
        """
        <style>
        .app-card { background: #111827; padding: 16px; border-radius: 10px; border: 1px solid #1f2937; }
        .app-title { color: #e2e8f0; font-size: 26px; font-weight: 700; }
        .card-title { color: #e5e7eb; font-size: 16px; font-weight: 700; margin-bottom: 4px; }
        .table-note { color: #9ca3af; font-size: 13px; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='app-title'>College Management Dashboard</div>", unsafe_allow_html=True)
    st.write("")

    # Add form
    with st.container():
        st.markdown("<div class='app-card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>Add Student</div>", unsafe_allow_html=True)
        c1, c2, c3, c4, c5 = st.columns([1.5, 1.2, 1.5, 1.2, 0.6])
        with c1:
            name = st.text_input("Name", key="add_name")
        with c2:
            enrollment = st.text_input("Enrollment No.", key="add_enroll")
        with c3:
            courses = st.text_input("Courses", key="add_courses")
        with c4:
            phone = st.text_input("Phone", key="add_phone")
        with c5:
            st.write("")
            if st.button("Add", use_container_width=True):
                if add_student(name, enrollment, courses, phone):
                    st.success("Student added")
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.write("")

    # Table view (read-only)
    with st.container():
        st.markdown("<div class='app-card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>Students</div>", unsafe_allow_html=True)

        # Build a read-only table; include a textual Actions column
        table_rows = []
        for s in st.session_state.students:
            table_rows.append({
                "Student Name": s.get("name", ""),
                "Enrollment No.": s.get("enrollment", ""),
                "Courses": s.get("courses", ""),
                "Phone": s.get("phone", ""),
                "Actions": "[ Edit ]    [ Delete ]",  # visual cue; real buttons below
            })

        if len(table_rows) == 0:
            st.info("No students yet. Add the first one above.")
        else:
            st.dataframe(
                table_rows,
                use_container_width=True,
                hide_index=True,
            )
            st.markdown("<div class='table-note'>Tip: Use buttons below to Edit/Delete a specific row.</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    st.write("")

    # Per-row actions with real buttons
    if len(st.session_state.students) > 0:
        with st.expander("Row Actions", expanded=True):
            for idx, s in enumerate(st.session_state.students):
                cols = st.columns([3, 2, 2, 2, 1, 1])
                cols[0].write(f"{idx+1}. {s.get('name','')} | {s.get('enrollment','')} | {s.get('courses','')} | {s.get('phone','')}")
                edit_clicked = cols[4].button("Edit", key=f"edit_{idx}")
                delete_clicked = cols[5].button("Delete", key=f"delete_{idx}")
                if edit_clicked:
                    st.session_state.edit_index = idx
                    st.rerun()
                if delete_clicked:
                    delete_student(idx)
                    st.success("Deleted")
                    st.rerun()

    # Edit form (only shown if triggered)
    if st.session_state.edit_index is not None:
        i = st.session_state.edit_index
        if not (0 <= i < len(st.session_state.students)):
            st.session_state.edit_index = None
        else:
            record = st.session_state.students[i]
            st.write("")
            with st.container():
                st.markdown("<div class='app-card'>", unsafe_allow_html=True)
                st.markdown("<div class='card-title'>Edit Student</div>", unsafe_allow_html=True)
                c1, c2, c3, c4, c5 = st.columns([1.5, 1.2, 1.5, 1.2, 0.6])
                with c1:
                    e_name = st.text_input("Name", value=record.get("name", ""), key=f"edit_name_{i}")
                with c2:
                    e_enroll = st.text_input("Enrollment No.", value=record.get("enrollment", ""), key=f"edit_enroll_{i}")
                with c3:
                    e_courses = st.text_input("Courses", value=record.get("courses", ""), key=f"edit_courses_{i}")
                with c4:
                    e_phone = st.text_input("Phone", value=record.get("phone", ""), key=f"edit_phone_{i}")
                with c5:
                    st.write("")
                    if st.button("Save", use_container_width=True, key=f"save_{i}"):
                        if update_student(i, e_name, e_enroll, e_courses, e_phone):
                            st.success("Saved")
                            st.session_state.edit_index = None
                            st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()


