import streamlit as st
import pandas as pd
from datetime import datetime, time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import re
import plotly.express as px
import matplotlib.pyplot as plt

# Priority Breakdown with Matplotlib
st.write("### Priority Breakdown")
priority_counts = bookings_df["Priority"].value_counts()

fig, ax = plt.subplots()
ax.pie(priority_counts, labels=priority_counts.index, autopct="%1.1f%%", startangle=90)
ax.axis("equal")  # Equal aspect ratio ensures the pie is circular.
st.pyplot(fig)

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

# Constants
BOOKINGS_FILE = "conference_bookings.csv"
SMTP_SERVER = "smtp-mail.outlook.com"
SMTP_PORT = 587
SENDER_EMAIL = "fahmad@phoenixteam.com"
SENDER_PASSWORD = "qbtmrkwyspwxpbln"

# Set page configuration
st.set_page_config(
    page_title="Conference Room Booking System",
    page_icon="📅",
    layout="wide",
)

# Initialize session state for user login
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Load and prepare booking data
@st.cache_data
def load_bookings():
    if os.path.exists(BOOKINGS_FILE):
        bookings = pd.read_csv(BOOKINGS_FILE)
        bookings["Date"] = pd.to_datetime(bookings["Date"]).dt.date
        bookings["Start"] = pd.to_datetime(bookings["Start"])
        bookings["End"] = pd.to_datetime(bookings["End"])
    else:
        bookings = pd.DataFrame(
            columns=["User", "Email", "Date", "Room", "Priority", "Description", "Start", "End"]
        )
    return bookings


def save_bookings(df):
    df.to_csv(BOOKINGS_FILE, index=False)


bookings_df = load_bookings()

# Email-sending function
def send_email(user_email, user_name, room, date, start_time, end_time):
    subject = "Conference Room Booking Confirmation"
    body = f"""
    <html>
        <body>
            <p>Dear {user_name},</p>
            <p>Your booking has been confirmed! Here are the details:</p>
            <ul>
                <li><strong>Room:</strong> {room}</li>
                <li><strong>Date:</strong> {date.strftime('%A, %B %d, %Y')}</li>
                <li><strong>Time:</strong> {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}</li>
            </ul>
            <p>Best regards,<br>Conference Booking Team</p>
        </body>
    </html>
    """
    try:
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = user_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html"))
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        st.toast("Email confirmation sent successfully!")
    except Exception as e:
        st.error(f"Failed to send email: {e}")


# Helper functions
def is_valid_email(email):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email)


def is_time_slot_available(bookings_df, room, selected_date, start_datetime, end_datetime):
    conflicts = bookings_df[
        (bookings_df["Date"] == selected_date) & (bookings_df["Room"] == room)
    ]
    for _, booking in conflicts.iterrows():
        if (start_datetime < booking["End"]) and (end_datetime > booking["Start"]):
            return False
    return True


# Authentication and navigation
with st.sidebar:
    st.title("Conference Room Booking")
    st.image("https://phoenixteam.com/wp-content/uploads/2024/02/Phoenix-Logo.png", width=200)

    if not st.session_state.authenticated:
        with st.form("login_form"):
            st.subheader("Admin Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                    st.session_state.authenticated = True
                    st.success("Login successful!")
                else:
                    st.error("Invalid credentials.")
    else:
        st.write("Welcome, Admin!")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.experimental_rerun()

# Main content
if st.session_state.authenticated:
    tabs = st.tabs(["📅 View Bookings", "📋 Book a Room", "📊 Analytics", "🛠 Admin"])

    # Tab: View Bookings
    with tabs[0]:
        st.subheader("View All Bookings")
        selected_date = st.date_input("Filter by date", value=datetime.today().date())
        filtered_df = bookings_df[bookings_df["Date"] == selected_date]

        if not filtered_df.empty:
            st.dataframe(filtered_df)
        else:
            st.info("No bookings found for the selected date.")

    # Tab: Book a Room
    with tabs[1]:
        st.subheader("Book a Conference Room")
        with st.form("booking_form"):
            user_name = st.text_input("Your Name")
            user_email = st.text_input("Your Email")
            room = st.selectbox("Select Room", ["Collaborate", "Innovate", "Echo", "Vibe"])
            priority = st.select_slider(
                "Priority Level",
                options=["Low", "Medium-Low", "Medium", "Medium-High", "High"],
                value="Medium",
            )
            description = st.text_area("Booking Description (Optional)")
            date = st.date_input("Select Date", min_value=datetime.today().date())
            start_time = st.time_input("Start Time", value=time(9, 0))
            end_time = st.time_input("End Time", value=time(10, 0))

            if st.form_submit_button("Submit Booking"):
                if not user_name or not is_valid_email(user_email):
                    st.error("Please provide a valid name and email.")
                elif start_time >= end_time:
                    st.error("Start time must be earlier than end time.")
                elif not is_time_slot_available(
                    bookings_df, room, date, datetime.combine(date, start_time), datetime.combine(date, end_time)
                ):
                    st.error("Time slot already booked!")
                else:
                    new_booking = {
                        "User": user_name,
                        "Email": user_email,
                        "Date": date,
                        "Room": room,
                        "Priority": priority,
                        "Description": description,
                        "Start": datetime.combine(date, start_time),
                        "End": datetime.combine(date, end_time),
                    }
                    bookings_df = bookings_df.append(new_booking, ignore_index=True)
                    save_bookings(bookings_df)
                    send_email(user_email, user_name, room, date, start_time, end_time)
                    st.success("Room booked successfully!")

    # Tab: Analytics
    # Tab: Analytics
    with tabs[2]:
        st.subheader("Booking Analytics")
        room_counts = bookings_df["Room"].value_counts()
        st.bar_chart(room_counts)
        st.write("### Priority Breakdown")
        priority_counts = bookings_df["Priority"].value_counts()
        st.pie_chart(priority_counts)
    
    st.write("### Priority Breakdown")
    priority_counts = bookings_df["Priority"].value_counts()
    fig = px.pie(priority_counts, 
                 values=priority_counts.values, 
                 names=priority_counts.index, 
                 title="Priority Distribution")
    st.plotly_chart(fig)


    # Tab: Admin
    with tabs[3]:
        st.subheader("Manage Bookings")
        editable_df = st.data_editor(
            bookings_df,
            num_rows="dynamic",
            use_container_width=True,
        )
        save_bookings(editable_df)
        st.success("Changes saved!")
else:
    st.warning("Please log in to access the system.")
