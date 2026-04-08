import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# =====================
# 🔐 FIREBASE INIT (FINAL FIX)
# =====================
if not firebase_admin._apps:
    try:
        # ✅ Get secrets from Streamlit Cloud
        firebase_dict = dict(st.secrets["firebase"])

        # 🔥 FIX PRIVATE KEY FORMAT
        firebase_dict["private_key"] = firebase_dict["private_key"].replace("\\n", "\n")

        cred = credentials.Certificate(firebase_dict)

    except Exception:
        # ✅ Fallback for local testing
        cred = credentials.Certificate("serviceAccountKey.json")

    firebase_admin.initialize_app(cred)

db = firestore.client()

# =====================
# SESSION STATE
# =====================
if "user" not in st.session_state:
    st.session_state.user = None

if "role" not in st.session_state:
    st.session_state.role = None

# =====================
# LOGIN UI
# =====================
st.title("📚 MentorLoop Classroom")

role = st.selectbox("Select Role", ["Student", "Teacher"])
username = st.text_input("Enter Username")

if st.button("Login"):
    if username.strip():
        st.session_state.user = username.strip()
        st.session_state.role = role
        st.success(f"Logged in as {username}")
    else:
        st.warning("Please enter a username")

# =====================
# MAIN SYSTEM
# =====================
if st.session_state.user:

    st.sidebar.success(f"👤 {st.session_state.user}")
    st.sidebar.info(f"Role: {st.session_state.role}")

    # =====================
    # 🧑‍🏫 TEACHER PANEL
    # =====================
    if st.session_state.role == "Teacher":
        st.header("🧑‍🏫 Teacher Dashboard")

        st.subheader("➕ Create Assignment")

        title = st.text_input("Title")
        desc = st.text_area("Description")
        due_date = st.date_input("Due Date")

        if st.button("Create Assignment"):
            if title and desc:
                db.collection("assignments").add({
                    "title": title,
                    "description": desc,
                    "due_date": str(due_date),
                    "created_by": st.session_state.user,
                    "timestamp": datetime.now().isoformat()
                })
                st.success("Assignment Created!")
            else:
                st.warning("Fill all fields")

        st.subheader("📥 Student Submissions")

        submissions = list(db.collection("submissions").stream())

        if not submissions:
            st.info("No submissions yet.")
        else:
            for sub in submissions:
                data = sub.to_dict()
                doc_id = sub.id

                st.markdown("---")
                st.write(f"👤 Student: {data.get('student')}")
                st.write(f"📄 Assignment: {data.get('assignment')}")
                st.write(f"✍️ Answer: {data.get('answer')}")
                st.write(f"🏆 Marks: {data.get('marks', 'Not graded')}")

                marks = st.number_input(
                    "Give Marks",
                    min_value=0,
                    max_value=100,
                    key=f"marks_{doc_id}"
                )

                if st.button(f"Submit Marks", key=f"btn_{doc_id}"):
                    db.collection("submissions").document(doc_id).update({
                        "marks": marks
                    })
                    st.success("Marks updated!")

    # =====================
    # 🎓 STUDENT PANEL
    # =====================
    else:
        st.header("🎓 Student Dashboard")

        st.subheader("📚 Assignments")

        assignments = list(db.collection("assignments").stream())

        if not assignments:
            st.info("No assignments yet.")
        else:
            for doc in assignments:
                data = doc.to_dict()

                st.markdown("---")
                st.write(f"### {data.get('title')}")
                st.write(data.get("description"))
                st.write(f"📅 Due: {data.get('due_date')}")

                answer = st.text_area(
                    "Your Answer",
                    key=f"ans_{doc.id}"
                )

                if st.button(f"Submit {data.get('title')}", key=f"submit_{doc.id}"):
                    if answer.strip():
                        db.collection("submissions").add({
                            "student": st.session_state.user,
                            "assignment": data.get("title"),
                            "answer": answer,
                            "marks": None,
                            "submitted_at": datetime.now().isoformat()
                        })
                        st.success("Submitted!")
                    else:
                        st.warning("Write an answer first")

        # =====================
        # 📊 RESULTS
        # =====================
        st.subheader("📊 Your Results")

        subs = list(db.collection("submissions").stream())

        user_subs = [
            s.to_dict()
            for s in subs
            if s.to_dict().get("student") == st.session_state.user
        ]

        if not user_subs:
            st.info("No submissions yet.")
        else:
            for d in user_subs:
                st.write(f"{d.get('assignment')} → {d.get('marks', 'Pending')}")
