import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# 🔐 FIREBASE INIT (CLOUD SAFE)
if not firebase_admin._apps:
    firebase_dict = dict(st.secrets["firebase"])
    firebase_dict["private_key"] = firebase_dict["private_key"].replace("\\n", "\n")
    cred = credentials.Certificate(firebase_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# UI
st.title("🔥 MentorLoop Classroom")

st.write("If you see this, Firebase is working 😏")
