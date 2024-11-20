import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import re

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
    # Load the CSV safely
    # Replace append with concat
    new_booking_df = pd.DataFrame([new_booking])  # Convert the new booking to DataFrame
    bookings_df = pd.concat([bookings_df, new_booking_df], ignore_index=True)  # Concatenate
    save_bookings(bookings_df)  # Save the updated DataFrame


    # Normalize 'Date', 'Start', 'End' columns
    try:
        bookings_df["Date"] = pd.to_datetime(bookings_df["Date"], errors="coerce").dt.date  # Convert to `datetime.date`
        bookings_df["Start"] = pd.to_datetime(bookings_df["Start"], errors="coerce")
        bookings_df["End"] = pd.to_datetime(bookings_df["End"], errors="coerce")

        # Drop rows with invalid dates/times
        bookings_df = bookings_df.dropna(subset=["Date", "Start", "End"])
    except Exception as e:
        st.error(f"Error processing the bookings file: {e}")
        bookings_df = pd.DataFrame(columns=["User", "Email", "Date", "Room", "Priority", "Description", "Start", "End"])
else:
    # Create an empty DataFrame if the file doesn't exist
    bookings_df = pd.DataFrame(columns=["User", "Email", "Date", "Room", "Priority", "Description", "Start", "End"])

# Save bookings to the CSV file
def save_bookings(df):
    df.to_csv(BOOKINGS_FILE, index=False)

# Email-sending function
def send_email(user_email, user_name, room, date, start_time, end_time):
    sender_email = "19bd1a1021@gmail.com"
    sender_password = "agvrujrctxxwcggk"  # Use environment variables for sensitive information
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
        msg["To"] = f"{user_email}, kteja@phoenixteam.com"  # Send to both user and admin
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
    # Check for conflicting bookings for the same room on the selected date
    conflicts = bookings_df[(bookings_df["Date"] == pd.Timestamp(selected_date)) & (bookings_df["Room"] == room)]
    for _, booking in conflicts.iterrows():
        # If there's an overlap with an existing booking, return False
        if (start_datetime < booking["End"]) and (end_datetime > booking["Start"]):
            return False
    return True

# Booking Form Section
#page = "Book a Conference Room"  # Assuming you have a mechanism to define the current page

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
        
        # Time Range Slider with custom color
        start_time = st.slider("Start Time", value=time(11, 0), min_value=time(11, 0), max_value=time(20, 0), step=timedelta(minutes=30), format="HH:mm", help="Select start time")
        end_time = st.slider("End Time", value=time(12, 0), min_value=time(11, 30), max_value=time(20, 0), step=timedelta(minutes=30), format="HH:mm", help="Select end time")
        
        start_datetime = datetime.combine(selected_date, start_time)
        end_datetime = datetime.combine(selected_date, end_time)
        
        # Validation checks
        valid_name = True
        valid_email = True
        valid_times = True
        conflict = False

        # Check if name is empty
        if not user_name:
            st.error("⚠️ Name cannot be empty.")
            valid_name = False

        # Check if email is valid
        if not user_email:
            st.error("⚠️ Email cannot be empty.")
            valid_email = False
        elif not is_valid_email(user_email):
            st.error("⚠️ Please enter a valid email address.")
            valid_email = False
                    # Check if the timeslot is available
        if not is_time_slot_available(bookings_df, selected_room, selected_date, start_datetime, end_datetime):
            st.error("⚠️ The selected time slot is already booked for this room.")
            conflict = True
            valid_times = False

        submit_button = st.form_submit_button("Book Room")

        # If form is valid and submitted, process the booking
        if submit_button and valid_name and valid_email and valid_times and not conflict:
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

            # Append the new booking to the DataFrame and save it
            bookings_df = bookings_df.append(new_booking, ignore_index=True)
            save_bookings(bookings_df)

            # Send a confirmation email to the user and admin
            send_email(user_email, user_name, selected_room, selected_date, start_datetime, end_datetime)

            # Success message
            st.success(f"Booking successfully confirmed for {user_name}!")
            st.info("You will receive a confirmation email shortly.")

# View Bookings Section
elif page == "View Bookings":
    st.write('<h1 class="title">View Bookings</h1>', unsafe_allow_html=True)
    
    # Display all bookings
    if bookings_df.empty:
        st.warning("No bookings yet.")
    else:
        st.dataframe(bookings_df)

# Admin Section
elif page == "Admin":
    st.write('<h1 class="title">Admin Login</h1>', unsafe_allow_html=True)
    
    # Admin login form
    with st.form("admin_login"):
        username = st.text_input("Admin Username", placeholder="Enter your admin username")
        password = st.text_input("Admin Password", type="password", placeholder="Enter your password")
        login_button = st.form_submit_button("Login")

    # Check if admin credentials are correct
    if login_button:
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.success("Login successful!")
            st.write('<h2 class="title">Manage Bookings</h2>', unsafe_allow_html=True)

            # Show the list of bookings for the admin
            st.dataframe(bookings_df)

            # Option to delete a booking
            booking_to_delete = st.selectbox("Select booking to delete", bookings_df.index)
            if st.button("Delete Booking"):
                bookings_df = bookings_df.drop(booking_to_delete).reset_index(drop=True)
                save_bookings(bookings_df)
                st.success("Booking deleted successfully.")
        else:
            st.error("Incorrect username or password.")

