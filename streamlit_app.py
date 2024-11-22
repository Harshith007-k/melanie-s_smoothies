import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import re
import plotly.express as px

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

# Set up page configuration
st.set_page_config(page_title="Conference Room Booking", layout="wide")

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Navigate to:", ["Book a Room", "View Bookings", "Admin", "Analytics"])

# Load Bookings Data
BOOKINGS_FILE = "conference_bookings.csv"

if os.path.exists(BOOKINGS_FILE):
    bookings_df = pd.read_csv(BOOKINGS_FILE)
    bookings_df["Date"] = pd.to_datetime(bookings_df["Date"], errors="coerce").dt.date
    bookings_df["Start"] = pd.to_datetime(bookings_df["Start"], errors="coerce")
    bookings_df["End"] = pd.to_datetime(bookings_df["End"], errors="coerce")
else:
    bookings_df = pd.DataFrame(columns=["User", "Email", "Date", "Room", "Priority", "Description", "Start", "End"])

# Save bookings to file
def save_bookings(df):
    df.to_csv(BOOKINGS_FILE, index=False)

# Email Sending Function
def send_email(user_email, user_name, room, date, start_time, end_time):
    sender_email = "your_email@example.com"
    sender_password = "your_email_password"
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    subject = "Booking Confirmation"
    body = f"""
    <html>
        <body>
            <p>Dear {user_name},</p>
            <p>Your booking has been confirmed!</p>
            <ul>
                <li><strong>Room:</strong> {room}</li>
                <li><strong>Date:</strong> {date.strftime('%Y-%m-%d')}</li>
                <li><strong>Time:</strong> {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}</li>
            </ul>
            <p>Thank you for using our booking system!</p>
        </body>
    </html>
    """

    try:
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = user_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html"))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        st.success(f"Confirmation email sent to {user_email}")
    except Exception as e:
        st.error(f"Failed to send email: {e}")

# Utility Functions
def is_time_slot_available(room, selected_date, start_time, end_time):
    conflicts = bookings_df[(bookings_df["Room"] == room) & (bookings_df["Date"] == selected_date)]
    for _, row in conflicts.iterrows():
        if (start_time < row["End"]) and (end_time > row["Start"]):
            return False
    return True

def is_valid_email(email):
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(regex, email) is not None

# Pages
if page == "Book a Room":
    st.title("Book a Conference Room")

    with st.form("booking_form"):
        user_name = st.text_input("Your Name")
        user_email = st.text_input("Your Email")
        selected_room = st.selectbox("Select Room", ["Room A", "Room B", "Room C"])
        priority = st.selectbox("Priority Level", ["Low", "Medium", "High"])
        description = st.text_area("Description (optional)")
        selected_date = st.date_input("Select Date", min_value=datetime.today())
        start_time = st.time_input("Start Time")
        end_time = st.time_input("End Time")

        submit = st.form_submit_button("Book Room")
        if submit:
            if not user_name or not user_email or not is_valid_email(user_email):
                st.error("Please provide valid details.")
            elif start_time >= end_time:
                st.error("End time must be after start time.")
            elif not is_time_slot_available(selected_room, selected_date, start_time, end_time):
                st.error("This time slot is already booked.")
            else:
                new_booking = {
                    "User": user_name,
                    "Email": user_email,
                    "Date": selected_date,
                    "Room": selected_room,
                    "Priority": priority,
                    "Description": description,
                    "Start": start_time,
                    "End": end_time,
                }
                bookings_df = bookings_df.append(new_booking, ignore_index=True)
                save_bookings(bookings_df)
                st.success("Room booked successfully!")
                send_email(user_email, user_name, selected_room, selected_date, start_time, end_time)

elif page == "View Bookings":
    st.title("View Bookings")

    tab1, tab2 = st.tabs(["Table View", "Calendar View"])
    with tab1:
        if not bookings_df.empty:
            st.dataframe(bookings_df)
        else:
            st.warning("No bookings available.")
    with tab2:
        st.write("Calendar View is under construction.")

elif page == "Admin":
    st.title("Admin Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.success("Login successful!")
            st.write("Welcome to the admin dashboard.")
        else:
            st.error("Invalid credentials.")

elif page == "Analytics":
    st.title("Booking Analytics")

    if not bookings_df.empty:
        room_counts = bookings_df["Room"].value_counts()
        priority_counts = bookings_df["Priority"].value_counts()

        tab1, tab2 = st.tabs(["Room Usage", "Priority Distribution"])
        with tab1:
            fig = px.bar(room_counts, x=room_counts.index, y=room_counts.values, labels={'x': 'Room', 'y': 'Bookings'})
            st.plotly_chart(fig)
        with tab2:
            fig = px.pie(priority_counts, names=priority_counts.index, values=priority_counts.values, title="Priority Distribution")
            st.plotly_chart(fig)
    else:
        st.warning("No data available for analytics.")
