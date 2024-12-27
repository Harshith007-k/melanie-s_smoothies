import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import re
import matplotlib.pyplot as plt
import seaborn as sns

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
page = st.sidebar.radio("Choose a page:", ["View Bookings","Book a Conference Room","Admin"])

# Load the bookings from CSV
BOOKINGS1_FILE = "conference_bookings.csv"

if os.path.exists(BOOKINGS1_FILE):
    bookings_df = pd.read_csv(BOOKINGS1_FILE)
    try:
        bookings_df["From Date"] = pd.to_datetime(bookings_df["From Date"], errors="coerce").dt.date
        bookings_df["To Date"] = pd.to_datetime(bookings_df["To Date"], errors="coerce").dt.date
        bookings_df["Start"] = pd.to_datetime(bookings_df["Start"], errors="coerce")
        bookings_df["End"] = pd.to_datetime(bookings_df["End"], errors="coerce")
        bookings_df = bookings_df.dropna(subset=["From Date", "To Date", "Start", "End"])
    except Exception as e:
        st.error(f"Error processing the bookings file: {e}")
        bookings_df = pd.DataFrame(columns=["User", "Email", "From Date", "To Date", "Room", "Priority", "Description", "Start", "End"])
else:
    bookings_df = pd.DataFrame(columns=["User", "Email", "From Date", "To Date", "Room", "Priority", "Description", "Start", "End"])

# Save bookings to the CSV file
def save_bookings(df):
    df.to_csv(BOOKINGS1_FILE, index=False)

# Function to validate email format using regex
def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

# Function to check if the time slot overlaps with any existing bookings
def is_time_slot_available(bookings_df, room, from_date, to_date, start_datetime, end_datetime):
    conflicts = bookings_df[(bookings_df["Room"] == room) &
                            (bookings_df["To Date"] >= from_date) &
                            (bookings_df["From Date"] <= to_date)]
    for _, booking in conflicts.iterrows():
        if (start_datetime < booking["End"]) and (end_datetime > booking["Start"]):
            return False
    return True

# Booking Form Section
if page == "Book a Conference Room":
    st.image("https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.skyintravels.com%2F&psig=AOvVaw0m-7diGEaKaa4CKBrJNaA9&ust=1735377840523000&source=images&cd=vfe&opi=89978449&ved=0CBQQjRxqFwoTCLjqrbjQx4oDFQAAAAAdAAAAABAE", width=200)
    st.write('<h1 class="title">Book a Conference Room</h1>', unsafe_allow_html=True)
    
    with st.form("booking_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            user_name = st.text_input("Your Name", placeholder="Enter your full name")
            user_email = st.text_input("Your Email", placeholder="Enter your email")
        with col2:
            selected_room = st.selectbox("Choose Room", ["101", "102", "201","202","301","302","401","402"])
        with col3:
            priority = st.selectbox("Priority Level", ["Low", "Medium-Low", "Medium", "Medium-High", "High"])

        description = st.text_area("Booking Description (optional)", placeholder="Enter details of your booking")
        from_date = st.date_input("From Date", min_value=datetime.today().date())
        to_date = st.date_input("To Date", min_value=from_date)

        start_time = st.time_input("Start Time", value=time(11, 0))
        end_time = st.time_input("End Time", value=time(12, 0))

        # Prevent zero-duration bookings
        if start_time >= end_time:
            st.error("⚠️ End time must be later than start time.")
            valid_times = False
        else:
            start_datetime = datetime.combine(from_date, start_time)
            end_datetime = datetime.combine(to_date, end_time)

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
            if not is_time_slot_available(bookings_df, selected_room, from_date, to_date, start_datetime, end_datetime):
                st.error("⚠️ The selected time slot is already booked for this room.")
                conflict = True
                valid_times = False

            submit_button = st.form_submit_button("Book Room")

            if submit_button and valid_name and valid_email and valid_times and not conflict:
                # Proceed with booking if valid
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

                # Create a DataFrame for the new booking
                new_booking_df = pd.DataFrame([new_booking])

                # Concatenate the new booking with the existing bookings DataFrame
                bookings_df = pd.concat([bookings_df, new_booking_df], ignore_index=True)

                # Save the updated bookings DataFrame to the CSV
                save_bookings(bookings_df)

                # Show a success message to the user
                st.success(f"Your room has been successfully booked! A confirmation email has been sent to {user_email}.")

            # If form is not valid, show an error message
            elif submit_button and not (valid_name and valid_email and valid_times):
                st.error("⚠️ Please ensure all fields are valid and try again.")

if page == "View Bookings":
    st.title("View Bookings")
    
    if bookings_df.empty:
        st.warning("No bookings available yet.")
    else:
        # Date selection input
        selected_view_date = st.date_input("Filter by Date", value=datetime.today().date())
        
        # Filter the bookings based on the selected date
        filtered_df = bookings_df[bookings_df["Date"] == selected_view_date]
        
        # Display the filtered bookings
        if not filtered_df.empty:
            st.dataframe(filtered_df)
        else:
            st.warning(f"No bookings available for {selected_view_date}.")
    
    # Metrics and Analytics
   # st.header("📊 Analytics Dashboard")         
# Admin Page: Admin Login for booking management
# Update Booking Section
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
                    #st.balloons()
            
            # Logout option for admin
            if st.button("Logout"):
                st.session_state.authenticated = False
                st.success("Logged out successfully.")
        else:
            st.write("No bookings found in the system.")

