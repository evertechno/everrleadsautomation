import streamlit as st
import pandas as pd
import google.generativeai as genai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from io import StringIO

# Configure the API key securely from Streamlit's secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Email credentials for sending emails
EMAIL_SENDER = st.secrets["EMAIL_SENDER"]
EMAIL_PASSWORD = st.secrets["EMAIL_PASSWORD"]
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587

# Function to load and display CSV
def load_csv(file):
    try:
        df = pd.read_csv(file)
        return df
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        return None

# Function to generate sales proposal using AI
def generate_proposal(lead_name):
    try:
        prompt = f"Generate a personalized sales proposal for {lead_name}, a potential client for our product."
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating proposal: {e}")
        return None

# Function to send email
def send_email(recipient_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, recipient_email, msg.as_string())

        return True
    except Exception as e:
        st.error(f"Error sending email to {recipient_email}: {e}")
        return False

# Streamlit UI for the web app
st.title("Bulk Email Campaign with AI Sales Proposals")
st.write("Upload your CSV file with lead details (name, email), and send personalized proposals.")

# File uploader for CSV
uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

if uploaded_file:
    df = load_csv(uploaded_file)
    if df is not None:
        st.write("Leads Data:")
        st.write(df)

        # Button to start campaign
        if st.button("Start Campaign"):
            email_sent = 0
            total_leads = len(df)
            failed_emails = []

            # Loop through leads and send emails
            for _, row in df.iterrows():
                lead_name = row['Name']
                lead_email = row['Email']
                
                proposal = generate_proposal(lead_name)
                if proposal:
                    subject = "Your Personalized Sales Proposal"
                    body = f"Dear {lead_name},\n\n{proposal}\n\nBest Regards,\nYour Company"
                    
                    if send_email(lead_email, subject, body):
                        email_sent += 1
                    else:
                        failed_emails.append(lead_email)
                
                # Display status after every email sent
                st.write(f"Sent email to {lead_name} ({lead_email})")

            # Display Campaign Stats
            st.write(f"Campaign completed!")
            st.write(f"Total leads: {total_leads}")
            st.write(f"Emails sent successfully: {email_sent}")
            st.write(f"Failed to send to: {failed_emails}")

# Display the prompt for AI generation
prompt = st.text_input("Customize AI prompt:", "Best alternatives to JavaScript?")

if st.button("Generate Response"):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        st.write("AI Generated Response:")
        st.write(response.text)
    except Exception as e:
        st.error(f"Error: {e}")
