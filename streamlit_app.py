import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# =====================
# 🔐 FIREBASE INIT
# =====================
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# =====================
# SESSION
# =====================
if "user" not in st.session_state:
    st.session_state.user = None

if "role" not in st.session_state:
    st.session_state.role = None

# =====================
# LOGIN
# =====================
st.title("📚 MentorLoop Classroom")

role = st.selectbox("Select Role", ["Student", "Teacher"])
username = st.text_input("Enter Username")

if st.button("Login"):
    if username:
        st.session_state.user = username
        st.session_state.role = role
        st.success(f"Logged in as {username}")

# =====================
# MAIN
# =====================
if st.session_state.user:

    st.sidebar.write(f"👤 {st.session_state.user}")
    st.sidebar.write(f"Role: {st.session_state.role}")

    # =====================
    # 🧑‍🏫 TEACHER
    # =====================
    if st.session_state.role == "Teacher":
        st.header("🧑‍🏫 Teacher Dashboard")

        # CREATE ASSIGNMENT
        st.subheader("➕ Create Assignment")

        title = st.text_input("Title")
        desc = st.text_area("Description")
        due_date = st.date_input("Due Date")

        if st.button("Create Assignment"):
            db.collection("assignments").add({
                "title": title,
                "description": desc,
                "due_date": str(due_date),
                "created_by": st.session_state.user
            })
            st.success("Assignment created!")

        # VIEW SUBMISSIONS
        st.subheader("📥 Submissions")

        submissions = db.collection("submissions").stream()

        for sub in submissions:
            data = sub.to_dict()
            doc_id = sub.id

            st.markdown("----")
            st.write(f"👤 Student: {data.get('student')}")
            st.write(f"📄 Assignment: {data.get('assignment')}")
            st.write(f"✍️ Answer: {data.get('answer')}")
            st.write(f"🏆 Marks: {data.get('marks', 'Not graded')}")

            marks = st.number_input("Give Marks", 0, 100, key=doc_id)

            if st.button(f"Submit Marks", key="m"+doc_id):
                db.collection("submissions").document(doc_id).update({
                    "marks": marks
                })
                st.success("Marks updated!")

    # =====================
    # 🎓 STUDENT
    # =====================
    else:
        st.header("🎓 Student Dashboard")

        assignments = db.collection("assignments").stream()

        for doc in assignments:
            data = doc.to_dict()

            st.markdown("----")
            st.write(f"### {data.get('title')}")
            st.write(data.get("description"))
            st.write(f"📅 Due: {data.get('due_date')}")

            answer = st.text_area("Your Answer", key=doc.id)

            if st.button(f"Submit {data.get('title')}", key="btn"+doc.id):
                db.collection("submissions").add({
                    "student": st.session_state.user,
                    "assignment": data.get("title"),
                    "answer": answer,
                    "marks": None
                })
                st.success("Submitted!")

        # VIEW RESULTS
        st.subheader("📊 Your Results")

        subs = db.collection("submissions").stream()

        for s in subs:
            d = s.to_dict()
            if d.get("student") == st.session_state.user:
                st.write(f"{d.get('assignment')} → {d.get('marks', 'Pending')}")
