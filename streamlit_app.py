import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time
import os
import re

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

# Set up page configuration
st.set_page_config(page_title="Conference Room Booking", layout="wide")

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Choose a page:", ["Home", "View Bookings", "Admin"])

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

# Tabs on the Home Page
if page == "Home":
    st.title("Welcome to the Conference Room Booking System")
    tab1, tab2, tab3 = st.tabs(["📅 Book a Room", "🗂 View Bookings", "📊 Metrics"])

    # Tab 1: Book a Room
    with tab1:
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
            start_time = st.time_input("Start Time", value=time(11, 0))
            end_time = st.time_input("End Time", value=time(12, 0))

            if st.form_submit_button("Book Room"):
                # Check for validation and time slot conflicts
                if start_time >= end_time:
                    st.error("End time must be after start time.")
                else:
                    new_booking = {
                        "User": user_name,
                        "Email": user_email,
                        "Date": selected_date,
                        "Room": selected_room,
                        "Priority": priority,
                        "Description": description,
                        "Start": start_time,
                        "End": end_time
                    }
                    bookings_df = pd.concat([bookings_df, pd.DataFrame([new_booking])], ignore_index=True)
                    save_bookings(bookings_df)
                    st.success("Your room has been successfully booked!")

    # Tab 2: View Bookings
    with tab2:
        st.header("View Bookings")
        if not bookings_df.empty:
            selected_view_date = st.date_input("Filter by Date", value=datetime.today().date())
            filtered_df = bookings_df[bookings_df["Date"] == selected_view_date]
            
            if not filtered_df.empty:
                st.dataframe(filtered_df)
            else:
                st.warning(f"No bookings available for {selected_view_date}.")
        else:
            st.warning("No bookings available yet.")

    # Tab 3: Metrics
    with tab3:
        st.header("Metrics")
        total_bookings = len(bookings_df)
        st.metric("Total Bookings", total_bookings)
        st.metric("Unique Rooms", bookings_df["Room"].nunique())
        if not bookings_df.empty:
            st.metric("High Priority Bookings", len(bookings_df[bookings_df["Priority"] == "High"]))

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
