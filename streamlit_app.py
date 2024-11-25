import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, time
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

# Set up page configuration
st.set_page_config(page_title="Conference Room Booking", layout="wide")

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Choose a page:", ["Home", "Admin"])

# Load bookings from CSV
BOOKINGS_FILE = "conference_bookings.csv"
if os.path.exists(BOOKINGS_FILE):
    bookings_df = pd.read_csv(BOOKINGS_FILE)
    bookings_df["Date"] = pd.to_datetime(bookings_df["Date"], errors="coerce").dt.date
else:
    bookings_df = pd.DataFrame(columns=["User", "Email", "Date", "Room", "Priority", "Description", "Start", "End"])

# Save bookings to the CSV file
def save_bookings(df):
    df.to_csv(BOOKINGS_FILE, index=False)

# Email-sending function
def send_email(user_email, user_name, room, date, start_time, end_time):
    sender_email = "fahmad@phoenixteam.com"
    sender_password = "qbtmrkwyspwxpbln"
    smtp_server = "smtp-mail.outlook.com"
    smtp_encryption = "STARTTLS"
    smtp_port = 587

# Function to send email
def send_booking_email(user_email, admin_email, booking_details):
    try:
        # Email content
        subject = "Conference Room Booking Confirmation"
        body = f"""
        Dear User,

        Your conference room has been successfully booked. Here are the details:

        User: {booking_details['User']}
        Email: {booking_details['Email']}
        Room: {booking_details['Room']}
        Date: {booking_details['Date']}
        Start Time: {booking_details['Start']}
        End Time: {booking_details['End']}
        Priority: {booking_details['Priority']}
        Description: {booking_details['Description']}

        Thank you for using the Conference Room Booking System.

        Regards,
        Admin
        """

        # Create the email
        message = MIMEMultipart()
        message["From"] = SENDER_EMAIL
        message["To"] = user_email
        message["Cc"] = admin_email
        message["Subject"] = subject

        message.attach(MIMEText(body, "plain"))

        # Connect to SMTP server and send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Upgrade connection to secure
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, [user_email, admin_email], message.as_string())
        print("Email sent successfully!")

    except Exception as e:
        print(f"Error sending email: {e}")

# Updated Booking Section
if page == "Home":
    st.title("Welcome to the Conference Room Booking System")
    tab1, tab2, tab3 = st.tabs(["🗂 View Bookings", "📅 Book a Room", "📊 Metrics"])  # Reordered tabs

    # Tab 2: Book a Room
    with tab2:
        st.header("Book a Conference Room")
        with st.form("booking_form"):
            col1, col2 = st.columns(2)
            with col1:
                user_name = st.text_input("Your Name", placeholder="Enter your full name")
                user_email = st.text_input("Your Email", placeholder="Enter your email")
            with col2:
                selected_room = st.selectbox("Choose Room", ["Big Conference Room", "Discussion Room 1", "Discussion Room 2"])
                priority = st.selectbox("Priority Level", ["Low", "Medium-Low", "Medium", "Medium-High", "High"])
            description = st.text_area("Booking Description (optional)", placeholder="Enter details of your booking")
            selected_date = st.date_input("Select Date", min_value=datetime.today().date())

            # Restrict time inputs
            start_time = st.time_input("Start Time", value=time(11, 0), step=300)
            end_time = st.time_input("End Time", value=time(20, 0), step=300)

            if start_time < time(11, 0) or end_time > time(20, 0):
                st.error("⚠️ Bookings are only allowed between 11:00 AM and 8:00 PM.")
            elif start_time >= end_time:
                st.error("⚠️ End time must be after start time.")
            else:
                if st.form_submit_button("Book Room"):
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
                    bookings_df = pd.concat([bookings_df, pd.DataFrame([new_booking])], ignore_index=True)
                    save_bookings(bookings_df)
                    st.success("Your room has been successfully booked!")

                    # Send confirmation email
                    send_booking_email(user_email, "kteja@phoenixteam.com", new_booking)

    # Tab 3: Metrics
    with tab3:
        st.header("Metrics")
        total_bookings = len(bookings_df)
        st.metric("Total Bookings", total_bookings)
        st.metric("Unique Rooms", bookings_df["Room"].nunique())

        if not bookings_df.empty:
            # Chart: Bookings by Date
            st.subheader("📅 Bookings Over Time")
            bookings_by_date = bookings_df["Date"].value_counts().reset_index()
            bookings_by_date.columns = ["Date", "Count"]
            bookings_by_date = bookings_by_date.sort_values(by="Date")
            fig_date = px.line(bookings_by_date, x="Date", y="Count", title="Bookings Over Time", markers=True)
            st.plotly_chart(fig_date, use_container_width=True)

            # Chart: Bookings by Room
            st.subheader("🏢 Bookings by Room")
            bookings_by_room = bookings_df["Room"].value_counts().reset_index()
            bookings_by_room.columns = ["Room", "Count"]
            fig_room = px.bar(bookings_by_room, x="Room", y="Count", title="Bookings by Room", text="Count")
            st.plotly_chart(fig_room, use_container_width=True)

            # Chart: Priority Levels
            st.subheader("📊 Priority Level Distribution")
            priority_counts = bookings_df["Priority"].value_counts().reset_index()
            priority_counts.columns = ["Priority", "Count"]
            fig_priority = px.pie(priority_counts, names="Priority", values="Count", title="Priority Level Distribution")
            st.plotly_chart(fig_priority, use_container_width=True)

            # Summary Table
            st.subheader("📋 Summary")
            st.dataframe(bookings_df)

# Admin Page
elif page == "Admin":
    st.title("Admin Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.success("Logged in successfully!")
            admin_tab1, admin_tab2 = st.tabs(["🛠 Manage Bookings", "📈 View Metrics"])
            
            # Manage Bookings Tab
            with admin_tab1:
                st.header("Manage Bookings")
                if not bookings_df.empty:
                    st.dataframe(bookings_df)
                    booking_to_delete = st.text_input("Enter Booking ID to delete")
                    if st.button("Delete Booking"):
                        if booking_to_delete.isnumeric() and int(booking_to_delete) in bookings_df.index:
                            bookings_df = bookings_df.drop(int(booking_to_delete))
                            save_bookings(bookings_df)
                            st.success("Booking deleted.")
                        else:
                            st.error("Invalid Booking ID.")

            # View Metrics Tab
            with admin_tab2:
                st.header("Admin Metrics")
                st.metric("Total Bookings", len(bookings_df))
                st.metric("Rooms Booked", bookings_df["Room"].nunique())

        else:
            st.error("Invalid credentials. Please try again.")
