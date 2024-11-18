import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

# Set up page configuration
st.set_page_config(page_title="Conference Room Booking", layout="wide")

# Initialize session state for the current page
if "current_page" not in st.session_state:
    st.session_state.current_page = "View Bookings"

# Define page order
pages = ["View Bookings", "Book a Conference Room", "Admin"]

# Load the bookings from CSV
BOOKINGS_FILE = "conference_bookings.csv"

if os.path.exists(BOOKINGS_FILE):
    bookings_df = pd.read_csv(BOOKINGS_FILE)
    bookings_df["Date"] = pd.to_datetime(bookings_df["Date"], errors="coerce")
    bookings_df["Start"] = pd.to_datetime(bookings_df["Start"], errors="coerce")
    bookings_df["End"] = pd.to_datetime(bookings_df["End"], errors="coerce")
    bookings_df = bookings_df.dropna(subset=["Date", "Start", "End"])
else:
    bookings_df = pd.DataFrame(columns=["User", "Email", "Date", "Room", "Priority", "Description", "Start", "End"])

# Save bookings to the CSV file
def save_bookings(df):
    df.to_csv(BOOKINGS_FILE, index=False)

# Email-sending function
def send_email(user_email, user_name, room, date, start_time, end_time):
    sender_email = "19bd1a1021@gmail.com"
    sender_password = "agvrujrctxxwcggk"
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    subject = "Conference Room Booking Confirmation"
    body = f"""
    <html>
        <body>
            <p>Dear {user_name},</p>
            <p>Your booking has been confirmed! Here are the details:</p>
            <table border="1" style="border-collapse: collapse; width: 50%; text-align: left;">
                <tr><th>Field</th><th>Details</th></tr>
                <tr><td>Room</td><td>{room}</td></tr>
                <tr><td>Date</td><td>{date.strftime('%A, %B %d, %Y')}</td></tr>
                <tr><td>Time</td><td>{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}</td></tr>
            </table>
            <p>Best regards,<br>Conference Room Booking Team</p>
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
        st.success(f"Email confirmation sent to {user_email}.")
    except Exception as e:
        st.error(f"Error sending email: {e}")

# Display content for each page
current_page = st.session_state.current_page

if current_page == "View Bookings":
    st.write("### All Booked Slots")
    if not bookings_df.empty:
        bookings_df["Date"] = bookings_df["Date"].dt.strftime('%A, %B %d, %Y')
        bookings_df["Start"] = bookings_df["Start"].dt.strftime('%H:%M')
        bookings_df["End"] = bookings_df["End"].dt.strftime('%H:%M')
        st.dataframe(bookings_df[["User", "Email", "Room", "Date", "Start", "End", "Priority", "Description"]])
    else:
        st.write("No bookings available.")

elif current_page == "Book a Conference Room":
    st.image("https://phoenixteam.com/wp-content/uploads/2024/02/Phoenix-Logo.png", use_column_width="always")
    st.write('<h1 class="title">Book a Conference Room</h1>', unsafe_allow_html=True)
    with st.form("booking_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            user_name = st.text_input("Your Name", placeholder="Enter your full name")
            user_email = st.text_input("Your Email", placeholder="Enter your email")
        with col2:
            selected_room = st.selectbox("Choose Room", ["Big Conference room", "Discussion_room_1", "Discussion room_2"])
        with col3:
            priority = st.selectbox("Priority Level", ["Low", "Medium-Low", "Medium", "Medium-High", "High"])
        description = st.text_area("Booking Description (optional)", placeholder="Enter details of your booking")
        selected_date = st.date_input("Select Date", min_value=datetime.today().date())
        start_time = st.time_input("Start Time", value=time(11, 0))
        end_time = st.time_input("End Time", value=time(12, 0))
        start_datetime = datetime.combine(selected_date, start_time)
        end_datetime = datetime.combine(selected_date, end_time)
        conflict = False
        for _, booking in bookings_df[(bookings_df["Date"] == pd.Timestamp(selected_date)) & (bookings_df["Room"] == selected_room)].iterrows():
            if (start_datetime < booking["End"]) and (end_datetime > booking["Start"]):
                conflict = True
                st.error("⚠️ This time slot is already booked! Please choose a different time.")
                break
        if st.form_submit_button("Confirm Booking") and not conflict:
            new_booking = pd.DataFrame({
                "User": [user_name],
                "Email": [user_email],
                "Date": [selected_date],
                "Room": [selected_room],
                "Priority": [priority],
                "Description": [description],
                "Start": [start_datetime],
                "End": [end_datetime],
            })
            bookings_df = pd.concat([bookings_df, new_booking], ignore_index=True)
            save_bookings(bookings_df)
            send_email(user_email, user_name, selected_room, selected_date, start_datetime, end_datetime)
            st.success(f"🎉 {selected_room} successfully booked from {start_time.strftime('%H:%M')} to {end_time.strftime('%H:%M')}.")
            st.balloons()

elif current_page == "Admin":
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        st.write("### Admin Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                st.session_state.authenticated = True
                st.success("Login successful!")
            else:
                st.error("Invalid username or password.")
    else:
        st.write("### Admin Dashboard")
        if not bookings_df.empty:
            st.dataframe(bookings_df)
        else:
            st.write("No bookings found.")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.success("Logged out successfully.")

# Add "Back" and "Next" buttons
col1, col2, col3 = st.columns([1, 8, 1])  # Adjust the column proportions as needed

with col1:
    if st.button("Back"):
        current_index = pages.index(current_page)
        if current_index > 0:
            st.session_state.current_page = pages[current_index - 1]

with col3:  # Place "Next" in the rightmost column
    if st.button("Next"):
        current_index = pages.index(current_page)
        if current_index < len(pages) - 1:
            st.session_state.current_page = pages[current_index + 1]

