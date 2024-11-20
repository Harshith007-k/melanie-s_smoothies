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

# Load the bookings from CSV
BOOKINGS_FILE = "conference_bookings.csv"

if os.path.exists(BOOKINGS_FILE):
    bookings_df = pd.read_csv(BOOKINGS_FILE)
    try:
        bookings_df["Date"] = pd.to_datetime(bookings_df["Date"], errors="coerce").dt.date
        bookings_df["Start"] = pd.to_datetime(bookings_df["Start"], errors="coerce")
        bookings_df["End"] = pd.to_datetime(bookings_df["End"], errors="coerce")
        bookings_df = bookings_df.dropna(subset=["Date", "Start", "End"])
    except Exception as e:
        st.error(f"Error processing the bookings file: {e}")
        bookings_df = pd.DataFrame(columns=["User", "Email", "Date", "Room", "Priority", "Description", "Start", "End"])
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
        # Prepare the email
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = f"{user_email}, kteja@phoenixteam.com"
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html"))

        # Connect to SMTP server and send the email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        st.success(f"Email confirmation sent to {user_email} and admin.")
    except Exception as e:
        st.error(f"Error sending email: {e}")

# Function to validate email format using regex
def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

# Function to check if the time slot overlaps with any existing bookings
def is_time_slot_available(bookings_df, room, selected_date, start_datetime, end_datetime):
    conflicts = bookings_df[(bookings_df["Date"] == pd.Timestamp(selected_date)) & (bookings_df["Room"] == room)]
    for _, booking in conflicts.iterrows():
        if (start_datetime < booking["End"]) and (end_datetime > booking["Start"]):
            return False
    return True

# Booking Form Section
# Booking Form Section
# Booking Form Section
# Function to check if the time slot overlaps with any existing bookings
# Function to check if the time slot overlaps with any existing bookings
def is_time_slot_available(bookings_df, room, selected_date, start_datetime, end_datetime):
    # Filter bookings that match the room and date
    conflicts = bookings_df[(bookings_df["Date"] == selected_date) & (bookings_df["Room"] == room)]
    
    # Check if the new booking overlaps with any existing booking
    for _, booking in conflicts.iterrows():
        # Check if the new booking overlaps with an existing booking
        if (start_datetime < booking["End"]) and (end_datetime > booking["Start"]):
            return False
    return True

# Function to save the bookings to the CSV file
def save_bookings(df):
    df.to_csv("conference_bookings.csv", index=False)

# Booking Form Section
if page == "Book a Conference Room":
    st.image("https://phoenixteam.com/wp-content/uploads/2024/02/Phoenix-Logo.png", width=200)
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

        # Prevent zero-duration bookings
        if start_time >= end_time:
            st.error("⚠️ End time must be later than start time.")
            valid_times = False
        else:
            start_datetime = datetime.combine(selected_date, start_time)
            end_datetime = datetime.combine(selected_date, end_time)

            # Validation checks
            valid_name = True
            valid_email = True
            valid_times = True
            conflict = False

            if not user_name:
                st.error("⚠️ Name cannot be empty.")
                valid_name = False

            if not user_email:
                st.error("⚠️ Email cannot be empty.")
                valid_email = False
            elif not is_valid_email(user_email):
                st.error("⚠️ Please enter a valid email address.")
                valid_email = False

            # Check if the time slot is available
            if not is_time_slot_available(bookings_df, selected_room, selected_date, start_datetime, end_datetime):
                st.error("⚠️ The selected time slot is already booked for this room.")
                conflict = True
                valid_times = False

            submit_button = st.form_submit_button("Book Room")

            if submit_button and valid_name and valid_email and valid_times and not conflict:
                # Proceed with booking if valid
                new_booking = {
                    "User": user_name,
                    "Email": user_email,
                    "Date": selected_date,
                    "Room": selected_room,
                    "Priority": priority,
                    "Description": description,
                    "Start": start_datetime,
                    "End": end_datetime
                }

                # Create a DataFrame for the new booking
                new_booking_df = pd.DataFrame([new_booking])

                # Concatenate the new booking with the existing bookings DataFrame
                bookings_df = pd.concat([bookings_df, new_booking_df], ignore_index=True)

                # Save the updated bookings DataFrame to the CSV
                save_bookings(bookings_df)

                # Show a success message to the user
                st.success(f"Your room has been successfully booked! A confirmation email has been sent to {user_email}.")
                
                # Send email confirmation to user and admin
                send_email(user_email, user_name, selected_room, selected_date, start_datetime, end_datetime)

            # If form is not valid, show an error message
            elif submit_button and not (valid_name and valid_email and valid_times):
                st.error("⚠️ Please ensure all fields are valid and try again.")

# Admin Page: View all bookings with a Calendar
# Admin Page: View all bookings with a Calendar
# Assuming you have the DataFrame `bookings_df` loaded already

# Save bookings to the CSV file
def save_bookings(df):
    df.to_csv(BOOKINGS_FILE, index=False)

# Function to map priority to background color
def priority_to_color(priority):
    color_map = {
        "Low": "#4CAF50",
        "Medium-Low": "#80deea",
        "Medium": "#ffcc80",
        "Medium-High": "#ff7043",
        "High": "#e57373",
    }
    return color_map.get(priority, "#FFFFFF")

# Function to apply background colors based on Priority
def apply_priority_colors(row):
    color = priority_to_color(row["Priority"])
    return [f"background-color: {color}" for _ in row]

# View Bookings Page
if page == "View Bookings":
    st.write('<h1 class="title">All Bookings</h1>', unsafe_allow_html=True)

    # Select a date
    selected_date = st.date_input("Select a Date to View Bookings", min_value=datetime.today().date())

    # Debug: Show selected date
    st.write(f"Selected Date: {selected_date}")

    # Ensure 'Date' column is in datetime format (if not already)
    bookings_df['Date'] = pd.to_datetime(bookings_df['Date']).dt.date

    # Filter bookings by selected date
    bookings_filtered = bookings_df[bookings_df['Date'] == selected_date]

    # Debug: Show filtered bookings
    st.write(f"Filtered Bookings for {selected_date}:")
    st.write(bookings_filtered)

    if not bookings_filtered.empty:
        # Display bookings in AgGrid (without styling)
        AgGrid(bookings_filtered)
    else:
        st.warning(f"No bookings available for {selected_date}.")
# Admin Page: Admin Login for booking management
if page == "Admin":
    st.write('<h1 class="title">Admin Login</h1>', unsafe_allow_html=True)

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.success("Logged in successfully!")

            # Optionally, allow the admin to view, delete, or edit bookings here.
            st.write("Admin functionalities can be added here.")
        else:
            st.error("Invalid credentials. Please try again.")

