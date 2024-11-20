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
page = st.sidebar.radio("Choose a page:", ["Book a Conference Room","View Bookings", "Admin"])

# Load the bookings from CSV
BOOKINGS_FILE = "conference_bookings.csv"

if os.path.exists(BOOKINGS_FILE):
    # Load the CSV safely
    bookings_df = pd.read_csv(BOOKINGS_FILE)

    # Normalize 'Date', 'Start', 'End' columns
    try:
        bookings_df["Date"] = bookings_df["Date"].apply(
            lambda x: pd.to_datetime(x, errors="coerce").date()  # Convert to `datetime.date`
        )
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
        msg["To"] = f"{user_email}, rgurumurthy@phoenixteam.com"  # Send to both user and admin
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
        if not is_valid_email(user_email):
            st.error("⚠️ Please enter a valid email address.")
            valid_email = False

        # Check if start time is before end time
        if start_datetime >= end_datetime:
            st.error("⚠️ Start time must be earlier than end time.")
            valid_times = False

        # Check if the selected time slot conflicts with existing bookings
        if not is_time_slot_available(bookings_df, selected_room, selected_date, start_datetime, end_datetime):
            st.error("⚠️ This time slot is already booked! Please choose a different time.")
            conflict = True
        
        # If all fields are valid, proceed with the booking
        if st.form_submit_button("Confirm Booking") and valid_name and valid_email and valid_times and not conflict:
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

if page == "View Bookings":
    st.write("### View Bookings by Date")
    
    # Ensure the Date column is in datetime format
    if not pd.api.types.is_datetime64_any_dtype(bookings_df["Date"]):
        bookings_df["Date"] = pd.to_datetime(bookings_df["Date"], errors="coerce")
    
    # Add a calendar widget for selecting the date
    selected_view_date = st.date_input(
        "Select a date to view bookings",
        value=datetime.today().date(),  # Default to today's date
        min_value=None,                # Allow past dates
        max_value=None                 # No restriction on future dates
    )
    
    # Filter the bookings DataFrame for the selected date
    filtered_bookings = bookings_df[
        bookings_df["Date"].dt.date == selected_view_date
    ]
    
    if not filtered_bookings.empty:
        # Convert datetime objects to readable strings for display
        filtered_bookings["Date"] = filtered_bookings["Date"].apply(lambda x: x.strftime('%A, %B %d, %Y'))
        filtered_bookings["Start"] = filtered_bookings["Start"].dt.strftime('%H:%M')
        filtered_bookings["End"] = filtered_bookings["End"].dt.strftime('%H:%M')

        # Priority color mapping
        def get_priority_color(priority):
            priority_colors = {
                "Low": "background-color: #98FB98",  # Light green
                "Medium-Low": "background-color: #FFFF99",  # Light yellow
                "Medium": "background-color: #FFCC66",  # Light orange
                "Medium-High": "background-color: #FF9966",  # Darker orange
                "High": "background-color: #FF6666",  # Light red
            }
            return priority_colors.get(priority, "")

        def style_priority(val):
            return get_priority_color(val)

        # Apply color coding to the priority column
        styled_df = filtered_bookings.style.applymap(style_priority, subset=["Priority"])
        
        # Display the styled DataFrame
        st.dataframe(styled_df)
    else:
        st.write(f"No bookings found for {selected_view_date.strftime('%A, %B %d, %Y')}.")
# Admin Section
if page == "Admin":
    # Admin Authentication
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
        st.write("#### Manage Bookings")
        
        if not bookings_df.empty:
            # Display all bookings in a table
            st.write("### All Current Bookings")
            st.dataframe(bookings_df[["User", "Email", "Room", "Date", "Start", "End", "Priority", "Description"]])
            
            # Delete Booking
            booking_to_delete = st.selectbox("Select Booking to Delete", bookings_df["User"].unique())
            if st.button("Delete Booking"):
                bookings_df = bookings_df[bookings_df["User"] != booking_to_delete]
                save_bookings(bookings_df)
                st.success(f"Booking by {booking_to_delete} has been deleted.")
            
            # Update Booking
            booking_to_update = st.selectbox("Select Booking to Update", bookings_df["User"].unique())
            selected_booking = bookings_df[bookings_df["User"] == booking_to_update].iloc[0]
            
            with st.form("update_booking_form"):
                updated_user_name = st.text_input("Update User Name", value=selected_booking["User"])
                updated_user_email = st.text_input("Update Email", value=selected_booking["Email"])
                updated_room = st.selectbox("Update Room", ["Big Conference room", "Discussion_room_1", "Discussion room_2"], index=["Big Conference room", "Discussion_room_1", "Discussion room_2"].index(selected_booking["Room"]))
                updated_priority = st.selectbox("Update Priority Level", ["Low", "Medium-Low", "Medium", "Medium-High", "High"], index=["Low", "Medium-Low", "Medium", "Medium-High", "High"].index(selected_booking["Priority"]))
                updated_description = st.text_area("Update Description", value=selected_booking["Description"])
                updated_date = st.date_input("Update Date", value=pd.to_datetime(selected_booking["Date"]).date())
                updated_start_time = st.time_input("Update Start Time", value=pd.to_datetime(selected_booking["Start"]).time())
                updated_end_time = st.time_input("Update End Time", value=pd.to_datetime(selected_booking["End"]).time())
                
                updated_start_datetime = datetime.combine(updated_date, updated_start_time)
                updated_end_datetime = datetime.combine(updated_date, updated_end_time)

                # Check for time conflicts
                conflict = False
                for _, booking in bookings_df[(bookings_df["Date"] == pd.Timestamp(updated_date)) & (bookings_df["Room"] == updated_room)].iterrows():
                    if (updated_start_datetime < booking["End"]) and (updated_end_datetime > booking["Start"]) and booking["User"] != booking_to_update:
                        conflict = True
                        st.error("⚠️ This time slot is already booked! Please choose a different time.")
                        break
                
                if st.form_submit_button("Update Booking") and not conflict:
                    # Update the booking in the DataFrame
                    bookings_df.loc[bookings_df["User"] == booking_to_update, ["User", "Email", "Room", "Priority", "Description", "Date", "Start", "End"]] = [
                        updated_user_name, updated_user_email, updated_room, updated_priority, updated_description, updated_date, updated_start_datetime, updated_end_datetime
                    ]
                    save_bookings(bookings_df)

                    # Send updated email confirmation
                    send_email(updated_user_email, updated_user_name, updated_room, updated_date, updated_start_datetime, updated_end_datetime)

                    st.success(f"🎉 Booking updated successfully for {updated_room} from {updated_start_time.strftime('%H:%M')} to {updated_end_time.strftime('%H:%M')}.")
                    st.balloons()
            
            # Logout option for admin
            if st.button("Logout"):
                st.session_state.authenticated = False
                st.success("Logged out successfully.")
        else:
            st.write("No bookings found in the system.")
