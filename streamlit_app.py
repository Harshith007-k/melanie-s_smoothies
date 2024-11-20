import streamlit as st
import pandas as pd
from datetime import datetime, time
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
        .low-priority {
            background-color: #e0f7fa;
        }
        .medium-low-priority {
            background-color: #80deea;
        }
        .medium-priority {
            background-color: #ffcc80;
        }
        .medium-high-priority {
            background-color: #ff7043;
        }
        .high-priority {
            background-color: #e57373;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Choose a page:", ["Book a Conference Room", "View Bookings", "Admin"])

# File to save bookings
BOOKINGS_FILE = "conference_bookings.csv"

# Load existing bookings or initialize an empty DataFrame
if os.path.exists(BOOKINGS_FILE):
    bookings_df = pd.read_csv(BOOKINGS_FILE)
    bookings_df["Date"] = pd.to_datetime(bookings_df["Date"], errors="coerce").dt.date
    bookings_df["Start"] = pd.to_datetime(bookings_df["Start"], errors="coerce")
    bookings_df["End"] = pd.to_datetime(bookings_df["End"], errors="coerce")
    bookings_df = bookings_df.dropna(subset=["Date", "Start", "End"])
else:
    bookings_df = pd.DataFrame(columns=["User", "Email", "Date", "Room", "Priority", "Description", "Start", "End"])

# Save bookings
def save_bookings(df):
    df.to_csv(BOOKINGS_FILE, index=False)

# Send email
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
                <tr>
                    <th style="padding: 8px; background-color: #f2f2f2;">Field</th>
                    <th style="padding: 8px; background-color: #f2f2f2;">Details</th>
                </tr>
                <tr>
                    <td style="padding: 8px;">Room</td>
                    <td style="padding: 8px;">{room}</td>
                </tr>
                <tr>
                    <td style="padding: 8px;">Date</td>
                    <td style="padding: 8px;">{date.strftime('%A, %B %d, %Y')}</td>
                </tr>
                <tr>
                    <td style="padding: 8px;">Time</td>
                    <td style="padding: 8px;">{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}</td>
                </tr>
            </table>
            <p>If you have any questions, feel free to contact us.</p>
            <p>Best regards,<br>Conference Room Booking Team</p>
        </body>
    </html>
    """
    
    try:
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = f"{user_email}, kteja@phoenixteam.com"
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html"))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)

        st.success(f"Confirmation email sent to {user_email} and admin.")
    except Exception as e:
        st.error(f"Error sending email: {e}")

# Validate email
def is_valid_email(email):
    return re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email) is not None

# Check time slot availability
def is_time_slot_available(room, selected_date, start_datetime, end_datetime):
    conflicts = bookings_df[(bookings_df["Date"] == selected_date) & (bookings_df["Room"] == room)]
    for _, booking in conflicts.iterrows():
        if start_datetime < booking["End"] and end_datetime > booking["Start"]:
            return False
    return True

# Priority to color mapping
def priority_to_color(priority):
    return {
        "Low": "#e0f7fa",
        "Medium-Low": "#80deea",
        "Medium": "#ffcc80",
        "Medium-High": "#ff7043",
        "High": "#e57373",
    }.get(priority, "#FFFFFF")

# Style DataFrame rows
def style_dataframe(df):
    def apply_colors(row):
        color = priority_to_color(row["Priority"])
        return [f"background-color: {color}" for _ in row]
    return df.style.apply(apply_colors, axis=1)

# Booking Form
if page == "Book a Conference Room":
    st.title("Book a Conference Room")
    with st.form("booking_form"):
        user_name = st.text_input("Your Name")
        user_email = st.text_input("Your Email")
        selected_room = st.selectbox("Choose Room", ["Big Conference Room", "Discussion Room 1", "Discussion Room 2"])
        priority = st.selectbox("Priority Level", ["Low", "Medium-Low", "Medium", "Medium-High", "High"])
        description = st.text_area("Description (optional)")
        selected_date = st.date_input("Select Date", min_value=datetime.today().date())
        start_time = st.time_input("Start Time", value=time(11, 0))
        end_time = st.time_input("End Time", value=time(12, 0))

        if st.form_submit_button("Book Room"):
            start_datetime = datetime.combine(selected_date, start_time)
            end_datetime = datetime.combine(selected_date, end_time)

            if not user_name:
                st.error("Name cannot be empty.")
            elif not is_valid_email(user_email):
                st.error("Invalid email.")
            elif start_datetime >= end_datetime:
                st.error("End time must be after start time.")
            elif not is_time_slot_available(selected_room, selected_date, start_datetime, end_datetime):
                st.error("This time slot is already booked.")
            else:
                bookings_df = pd.concat([bookings_df, pd.DataFrame([{
                    "User": user_name, "Email": user_email, "Date": selected_date, 
                    "Room": selected_room, "Priority": priority, "Description": description, 
                    "Start": start_datetime, "End": end_datetime
                }])], ignore_index=True)
                save_bookings(bookings_df)
                st.success("Room booked successfully!")
                send_email(user_email, user_name, selected_room, selected_date, start_datetime, end_datetime)

# View Bookings
elif page == "View Bookings":
    st.title("All Bookings")
    if bookings_df.empty:
        st.warning("No bookings available.")
    else:
        st.write(style_dataframe(bookings_df.sort_values(["Date", "Start"])).to_html(), unsafe_allow_html=True)

# Admin Page
elif page == "Admin":
    st.title("Admin Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.success("Logged in as admin!")
            if st.button("Clear All Bookings"):
                bookings_df = bookings_df.iloc[0:0]
                save_bookings(bookings_df)
                st.success("All bookings cleared.")
        else:
            st.error("Invalid credentials.")
