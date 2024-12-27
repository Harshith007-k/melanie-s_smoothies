import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import re

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

# Set up page configuration
st.set_page_config(page_title="Conference Room Booking", layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
        .title {
            text-align: center;
            color: #003366;
        }
        .booking-table th {
            background-color: #4CAF50;
            color: white;
            padding: 8px;
        }
        .booking-table td {
            padding: 8px;
            text-align: left;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Choose a page:", ["View Bookings", "Book a Conference Room", "Admin"])

# Load bookings from CSV
BOOKINGS_FILE = "conference_bookings.csv"
if os.path.exists(BOOKINGS_FILE):
    bookings_df = pd.read_csv(BOOKINGS_FILE)
    bookings_df["From Date"] = pd.to_datetime(bookings_df["From Date"], errors="coerce").dt.date
    bookings_df["To Date"] = pd.to_datetime(bookings_df["To Date"], errors="coerce").dt.date
    bookings_df["Start"] = pd.to_datetime(bookings_df["Start"], errors="coerce")
    bookings_df["End"] = pd.to_datetime(bookings_df["End"], errors="coerce")
else:
    bookings_df = pd.DataFrame(columns=["User", "Email", "From Date", "To Date", "Room", "Priority", "Description", "Start", "End"])

# Save bookings to CSV
def save_bookings(df):
    df.to_csv(BOOKINGS_FILE, index=False)

# Validate email format
def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

# Check for time slot conflicts
def is_time_slot_available(df, room, from_date, to_date, start_datetime, end_datetime):
    conflicts = df[(df["Room"] == room) &
                   (df["To Date"] >= from_date) &
                   (df["From Date"] <= to_date)]
    for _, booking in conflicts.iterrows():
        if (start_datetime < booking["End"]) and (end_datetime > booking["Start"]):
            return False
    return True

# Page: Book a Conference Room
if page == "Book a Conference Room":
    st.write('<h1 class="title">Book a Conference Room</h1>', unsafe_allow_html=True)

    with st.form("booking_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            user_name = st.text_input("Your Name", placeholder="Enter your full name")
            user_email = st.text_input("Your Email", placeholder="Enter your email")
        with col2:
            selected_room = st.selectbox("Choose Room", ["101", "102", "201", "202", "301", "302", "401", "402"])
        with col3:
            priority = st.selectbox("Priority Level", ["Low", "Medium", "High"])
        description = st.text_area("Booking Description (optional)", placeholder="Enter details of your booking")
        from_date = st.date_input("From Date", min_value=datetime.today().date())
        to_date = st.date_input("To Date", min_value=from_date)
        start_time = st.time_input("Start Time", value=time(9, 0))
        end_time = st.time_input("End Time", value=time(10, 0))

        # Validate inputs
        if start_time >= end_time:
            st.error("End time must be later than start time.")
        else:
            start_datetime = datetime.combine(from_date, start_time)
            end_datetime = datetime.combine(to_date, end_time)

        valid = st.form_submit_button("Book Room")
        if valid:
            if not user_name:
                st.error("Name cannot be empty.")
            elif not is_valid_email(user_email):
                st.error("Invalid email format.")
            elif not is_time_slot_available(bookings_df, selected_room, from_date, to_date, start_datetime, end_datetime):
                st.error("The selected time slot is already booked.")
            else:
                new_booking = {
                    "User": user_name,
                    "Email": user_email,
                    "From Date": from_date,
                    "To Date": to_date,
                    "Room": selected_room,
                    "Priority": priority,
                    "Description": description,
                    "Start": start_datetime,
                    "End": end_datetime
                }
                bookings_df = pd.concat([bookings_df, pd.DataFrame([new_booking])], ignore_index=True)
                save_bookings(bookings_df)
                st.success(f"Room {selected_room} successfully booked for {user_name}.")

# Page: View Bookings
if page == "View Bookings":
    st.title("View Bookings")
    if bookings_df.empty:
        st.warning("No bookings available.")
    else:
        selected_date = st.date_input("Select Date to View", value=datetime.today().date())
        filtered_bookings = bookings_df[(bookings_df["From Date"] <= selected_date) & (bookings_df["To Date"] >= selected_date)]
        if not filtered_bookings.empty:
            st.dataframe(filtered_bookings)
        else:
            st.warning(f"No bookings available for {selected_date}.")

# Page: Admin
if page == "Admin":
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        st.subheader("Admin Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                st.session_state["authenticated"] = True
                st.success("Login successful.")
            else:
                st.error("Invalid credentials.")
    else:
        st.subheader("Admin Dashboard")
        if bookings_df.empty:
            st.warning("No bookings available.")
        else:
            st.dataframe(bookings_df)
            to_delete = st.selectbox("Select User to Delete Booking", bookings_df["User"].unique())
            if st.button("Delete Booking"):
                bookings_df = bookings_df[bookings_df["User"] != to_delete]
                save_bookings(bookings_df)
                st.success(f"Booking for {to_delete} deleted successfully.")

        if st.button("Logout"):
            st.session_state["authenticated"] = False
            st.success("Logged out successfully.")
