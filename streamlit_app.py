import streamlit as st
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import google.generativeai as genai

# Configure Google API key from Streamlit's secrets (for Generative AI)
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Streamlit app title
st.title("EasySales:AI-Powered Bulk Email Campaign creator")

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
    required_columns = ['FirstName', 'LastName', 'Email', 'Company', 'Product', 
                        'YourName', 'YourTitle', 'YourCompanyName', 'YourPhoneNumber', 'YourEmailAddress', 'YourWebsite']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        st.error(f"Missing columns in the CSV: {', '.join(missing_columns)}")
    else:
        # Placeholder for generated email contents
        generated_emails = []

        # Generate email content for each lead
        for index, row in df.iterrows():
            first_name = row['FirstName']
            last_name = row['LastName']
            email = row['Email']
            company = row['Company']
            product = row['Product']

            # Personal details
            your_name = row['YourName']
            your_title = row['YourTitle']
            your_company_name = row['YourCompanyName']
            your_phone_number = row['YourPhoneNumber']
            your_email_address = row['YourEmailAddress']
            your_website = row['YourWebsite']

            # AI-generated email proposal content with placeholders replaced
            prompt = f"Generate a sales proposal email for {first_name} {last_name}, working at {company}, interested in {product}. Keep it professional and friendly. Use the following signature for the email:\n\nName: {your_name}\nTitle: {your_title}\nCompany: {your_company_name}\nPhone: {your_phone_number}\nEmail: {your_email_address}\nWebsite: {your_website}"

            try:
                # Generate content using Google Generative AI
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)
                email_content = response.text
                
                # Prepare the subject
                subject = f"Sales Proposal for {product} at {company}"

                # Store the generated email for review
                generated_emails.append({
                    'Name': f"{first_name} {last_name}",
                    'Email': email,
                    'Subject': subject,
                    'Content': email_content
                })
                
            except Exception as e:
                st.error(f"Error generating content for {first_name} {last_name}: {e}")

        if generated_emails:
            st.write("Generated Email Campaigns:")
            for email in generated_emails:
                st.subheader(f"Email to {email['Name']} ({email['Email']})")
                st.write(f"**Subject:** {email['Subject']}")
                st.write(f"**Content:** {email['Content']}")
                st.markdown("---")

            # Button to trigger sending emails
            send_button = st.button("Send Emails")

            if send_button:
                for email in generated_emails:
                    send_email(email['Subject'], email['Content'], email['Email'])
                st.success("All emails have been sent.")

else:
    st.info("Please upload a CSV file with leads.")
