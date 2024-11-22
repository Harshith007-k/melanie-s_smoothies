import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import re
import plotly.express as px
#import plotly.express as px
import plotly.graph_objects as go
from streamlit_extras.metric_cards import style_metric_cards

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
    st.title("Analytics Dashboard")

    # Calculate summary metrics
    total_bookings = len(bookings_df)
    unique_users = bookings_df["User"].nunique()
    rooms_booked = bookings_df["Room"].nunique()
    high_priority_bookings = bookings_df[bookings_df["Priority"] == "High"].shape[0]

    # Use styled metric cards for displaying key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        style_metric_cards(
            label="Total Bookings", value=str(total_bookings), delta=None, icon="📅"
        )
    with col2:
        style_metric_cards(
            label="Unique Users", value=str(unique_users), delta=None, icon="👥"
        )
    with col3:
        style_metric_cards(
            label="Rooms Booked", value=str(rooms_booked), delta=None, icon="🏢"
        )
    with col4:
        style_metric_cards(
            label="High Priority Bookings", value=str(high_priority_bookings), delta=None, icon="⚠️"
        )

    # Analytics Tabs
    tab1, tab2, tab3 = st.tabs(["Priority Distribution", "Room Utilization", "Booking Trends"])

    # Priority Distribution Pie Chart
    with tab1:
        st.subheader("Priority Distribution")
        if not bookings_df.empty:
            priority_counts = bookings_df["Priority"].value_counts()
            fig = px.pie(
                names=priority_counts.index,
                values=priority_counts.values,
                title="Distribution of Booking Priorities",
                color_discrete_sequence=px.colors.qualitative.Set3,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data available for priority distribution.")

    # Room Utilization Bar Chart
    with tab2:
        st.subheader("Room Utilization")
        if not bookings_df.empty:
            room_counts = bookings_df["Room"].value_counts()
            fig = px.bar(
                x=room_counts.index,
                y=room_counts.values,
                title="Number of Bookings per Room",
                labels={"x": "Room", "y": "Bookings"},
                color=room_counts.index,
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data available for room utilization.")

    # Booking Trends Over Time
    with tab3:
        st.subheader("Booking Trends Over Time")
        if not bookings_df.empty:
            bookings_df["Date"] = pd.to_datetime(bookings_df["Date"])
            bookings_by_date = bookings_df.groupby("Date").size().reset_index(name="Bookings")

            fig = px.line(
                bookings_by_date,
                x="Date",
                y="Bookings",
                title="Bookings Over Time",
                markers=True,
                labels={"Date": "Date", "Bookings": "Number of Bookings"},
            )
            fig.update_traces(line=dict(color="royalblue"))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data available for booking trends.")
            metrics = { "Total Bookings": len(bookings_df),
                       "Unique Users": bookings_df["User"].nunique(),
                       "Rooms Booked": bookings_df["Room"].nunique(),
                       "High Priority Bookings": bookings_df[bookings_df["Priority"] == "High"].shape[0],
                      }
            style_metric_cards(metrics)
