import streamlit as st
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import google.generativeai as genai

# Configure Google API key from Streamlit's secrets (for Generative AI)
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Streamlit app title
st.title("AI-Powered Bulk Email Campaign")

# File upload for CSV
uploaded_file = st.file_uploader("Upload CSV with Leads", type=["csv"])

# Function to send email via Brevo (SMTP)
def send_email(subject, body, to_email):
    sender_email = st.secrets["EMAIL_SENDER"]
    sender_password = st.secrets["EMAIL_PASSWORD"]

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to Brevo's SMTP server (smtp-relay.brevo.com)
        with smtplib.SMTP('smtp-relay.brevo.com', 587) as server:
            server.starttls()  # Start TLS encryption
            server.login(sender_email, sender_password)  # Login with email and SMTP API key (password)
            server.sendmail(sender_email, to_email, msg.as_string())  # Send email
            st.success(f"Email sent to {to_email}")
    except Exception as e:
        st.error(f"Failed to send email to {to_email}: {e}")

# Process the CSV file
if uploaded_file is not None:
    # Read the uploaded CSV
    df = pd.read_csv(uploaded_file)
    
    # Show the first few rows of the CSV for verification
    st.write("CSV Data Preview:")
    st.write(df.head())
    
    # Clean up column names (strip extra spaces)
    df.columns = df.columns.str.strip()

    # Check if required columns exist
    required_columns = ['FirstName', 'LastName', 'Email', 'Company', 'Product']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        st.error(f"Missing columns in the CSV: {', '.join(missing_columns)}")
    else:
        # Generate email content and send emails
        for index, row in df.iterrows():
            first_name = row['FirstName']
            last_name = row['LastName']
            email = row['Email']
            company = row['Company']
            product = row['Product']

            # AI-generated email proposal content
            prompt = f"Generate a sales proposal email for {first_name} {last_name}, working at {company}, interested in {product}. Keep it professional and friendly."
            
            try:
                # Generate content using Google Generative AI
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)
                email_content = response.text
                
                # Prepare the subject
                subject = f"Sales Proposal for {product} at {company}"

                # Send the email
                send_email(subject, email_content, email)
            except Exception as e:
                st.error(f"Error generating content or sending email to {email}: {e}")
        
        st.success("All emails have been processed.")
else:
    st.info("Please upload a CSV file with leads.")
