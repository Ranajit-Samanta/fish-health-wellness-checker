import streamlit as st
import math
import os
import pandas as pd
import smtplib
from email.mime.text import MIMEText
import uuid
import base64
st.set_page_config(layout="wide")

# Apply Background Color
st.markdown(
    """
    <style>
    .stApp {
        background-color: lightgreen;
        background-image: linear-gradient(90deg,rgb(135, 206, 235),
rgb(0, 84, 119));
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state variables if not set
if "name" not in st.session_state:
    st.session_state.name = None
if "N" not in st.session_state:
    st.session_state.N = None
if "W" not in st.session_state:
    st.session_state.W = None
if "L" not in st.session_state:
    st.session_state.L = None  
if "average_weight" not in st.session_state:
    st.session_state.average_weight = None
if "average_length" not in st.session_state:
    st.session_state.average_length = None
if "CI" not in st.session_state:
    st.session_state.CI = None
if "ci_results" not in st.session_state:
    st.session_state.ci_results = {}
if "feed_consumed_initial_day" not in st.session_state:
    st.session_state.feed_consumed_initial_day = None  
if "feed_consumed_final_day" not in st.session_state:
    st.session_state.feed_consumed_final_day = None
if "n1" not in st.session_state:
    st.session_state.n1 = None   
if "biomass_initial_day" not in st.session_state:
    st.session_state.biomass_initial_day = None
if "biomass_final_day" not in st.session_state:
    st.session_state.biomass_final_day = None
if "n2" not in st.session_state:
    st.session_state.n2 = None
if "fcr" not in st.session_state:
    st.session_state.fcr = None
if "fcr_results" not in st.session_state:
    st.session_state.fcr_results = {}


# Define calculations
def calculate_average_weight(N,W):
    return (W/N)
def calculate_average_length(N,L):
    return (L/N)
def calculate_ci(average_weight, average_length):
    return ((average_weight) / (average_length*average_length*average_length))*100

def calculate_change_in_feed_consumption(feed_consumed_initial_day,feed_consumed_final_day):
    return (feed_consumed_final_day - feed_consumed_initial_day)
def calculate_change_in_biomass(biomass_in_initial_day,biomass_in_final_day):
    return (biomass_in_final_day - biomass_in_initial_day)

def calculate_fcr(change_in_feed_consumption,change_in_biomass):
    return (change_in_feed_consumption /change_in_biomass)


def get_user_session_id():
    """Ensure the session ID persists across interactions."""
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())  # Create a new session ID for the user
    return st.session_state.session_id

#====== saving this values in excel ======#

def save_to_excel():
    # Define file path
    user_ip = get_user_session_id()
    excel_file = f"fish_health_wellness_checker_{user_ip}.xlsx"

    # Ensure all necessary calculations have been performed
    if None in [st.session_state.get("CI"), st.session_state.get("fcr")]:
        st.error("Please perform all calculations before saving to Excel.")
        return

    # Retrieve values from session state
    data = {
        "Name": [st.session_state.get("name", "N/A")],
        "No of fishes": [st.session_state.get("N", "N/A")],
        "Weight of all fishes (gm)": [st.session_state.get("W", "N/A")],
        "Average weight of fish (gm)": [st.session_state.get("average_weight", "N/A")],
        "Length of all fishes (cm)": [st.session_state.get("L", "N/A")],
        "Average length of fish (cm)": [st.session_state.get("average_length", "N/A")],
        "CI": [st.session_state.get("CI", "N/A")],
        "Feed consumed initial day (gm)": [st.session_state.get("feed_consumed_initial_day", "N/A")],
        "feed consumed final day (gm)": [st.session_state.get("feed_consumed_final_day", "N/A")],
        "NUmber of days": [st.session_state.get("n1", "N/A")],
        "Biomass in initial day (gm)": [st.session_state.get("biomass_initial_day", "N/A")],
        "Biomass in final day (gm)": [st.session_state.get("biomass_final_day", "N/A")],
        "Number of days": [st.session_state.get("n2", "N/A")],
        "FCR": [st.session_state.get("fcr", "N/A")],
        
    }

    # Convert to DataFrame
    new_data = pd.DataFrame(data)

    # Check if the file exists
    if os.path.exists(excel_file):
        # Load existing data
        existing_data = pd.read_excel(excel_file, engine="openpyxl")
        # Append new data
        updated_data = pd.concat([existing_data, new_data], ignore_index=True)
    else:
        # If file doesn't exist, create a new one
        updated_data = new_data

    # Save data to Excel
    updated_data.to_excel(excel_file, index=False, engine="openpyxl")

    st.success(f"Session data saved to {excel_file} successfully!")

def display():
    user_ip=get_user_session_id()
    excel_file=f"fish_health_wellness_checker_{user_ip}.xlsx"
    #   Display existing data
    if os.path.exists(excel_file):
        st.subheader("Stored Data:")
        df = pd.read_excel(excel_file, engine="openpyxl")
        st.dataframe(df)
    
def delete_item_from_excel(delete_name):
    user_ip=get_user_session_id()
    excel_file=f"fish_health_wellness_checker_{user_ip}.xlsx"
    
    if os.path.exists(excel_file):
        # Read the existing Excel file into a DataFrame
        data = pd.read_excel(excel_file, engine="openpyxl")

        # Check if the name exists in the data and delete that row
        data = data[data["Name"] != delete_name]

        # Save the updated DataFrame back to Excel
        data.to_excel(excel_file, index=False, engine="openpyxl")

        st.success(f"Item with name '{delete_name}' has been deleted from the Excel file!")
    else:
        st.error("The Excel file does not exist.")

# Layout

# st.write("<h1 style='color:white; text-align:center; padding: 20px; background-color: black; font-family: Times New Roman, Times, serif; font-style: italic;'>🌳Unlocking the Tree Carbon Locker🌍</h1>", unsafe_allow_html=True)
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

image_base64 = get_base64_image("WhatsApp Image 2025-02-27 at 10.43.12 PM.jpeg")

st.write(f"""
    <div class="unlocking_div" style='color: white; text-align:center; padding: 10px; background-color: #353839; 
    font-family: Times New Roman, Times, serif; font-style: italic; display: flex; 
    align-items: center; justify-content: center; gap: 18px;'>
        <img src="data:image/png;base64,{image_base64}" alt="Logo" 
        style="width:100px; height:auto;border-radius:50px">
        <h1 style='margin: 0; font-size: 42px;color: white;'>Fish Health & Wellness Tracker</h1>
    </div>
""", unsafe_allow_html=True)




col1, col2 = st.columns([2, 1])

# ======= FISH CONDITION CALCULATOR =======
with col1:
    st.write("<h1 style='color: purple;'>FISH CONDITION CALCULATOR</h1>", unsafe_allow_html=True)

    name = st.text_input("Name of the fish species")
    N = st.number_input("No. of fishes", min_value=1, value=st.session_state.N if st.session_state.N is not None else 1, key="num_trees_stem")
    W = st.number_input("Weight of all fishes (in gm)",value=None)
    L = st.number_input("Length of all fishes (in cm)", min_value=0.0, step=0.1,value=None,format="%.5f")

    if st.button("Calculate CI"):
        try:

            average_weight= calculate_average_weight(N,W)
            average_length= calculate_average_length(N,L)
            CI = calculate_ci(average_weight,average_length)

          

            # Store results in session state
            st.session_state.name=name
            st.session_state.N = N
            st.session_state.W = W
            st.session_state.L=L
            st.session_state.average_weight= average_weight
            st.session_state.average_length= average_length
            st.session_state.CI = CI
            st.session_state.ci_results = {
            "Average weight of fish": f"{average_weight} gm",
            "Average length of fish": f"{average_length} cm",
            "Total CI": CI
            }
        except:
            st.warning("Please enter proper values!!!")

    # Display Stem Biomass Results
    if st.session_state.ci_results:
        st.subheader("Calculated CI:")
        for key, value in st.session_state.ci_results.items():
            st.write(f"{key}: {value}")

    #if st.session_state.stem_results:
        


with col2:
    st.write("<h1 style='color: purple;'>Field Activities</h1>", unsafe_allow_html=True)
    st.write("<h3 style='color: black;'>Condition Index</h3>", unsafe_allow_html=True)
    st.write(
        "<h6 style='color: black;'>The Condition Index of Fish is a vital parameter used to assess the overall health, well-being, and nutritional status of fish populations. It is commonly determined using the ratio of body weight to length, providing insights into growth patterns, energy reserves, and environmental stressors. A high condition index indicates a well-fed and healthy fish, while a low value may suggest poor nutrition, disease, or adverse environmental conditions. This index is widely applied in fisheries management, aquaculture, and ecological studies to monitor stock health, optimize feeding strategies, and ensure sustainable fishery practices.</h6>",
        unsafe_allow_html=True,
    )
    st.image("WhatsApp Image 2025-02-27 at 10.46.06 PM.jpeg",width=270)


# ======= BRANCH BIOMASS CALCULATOR =======
col1, col2 = st.columns([2, 1])
with col1:
    st.write("<h1 style='color: purple;'>FEED CONVERSION RATIO CALCULATOR</h1>", unsafe_allow_html=True)

    feed_consumed_initial_day = st.number_input("Feed consumed in the initial day (in gm)", min_value=0.0, step=0.00001, format="%.5f",value=None)
    feed_consumed_final_day = st.number_input("Feed consumed in the final day (in gm)", min_value=0.0, step=0.00001, format="%.5f",value=None)
    n1 = st.number_input("Number of days", min_value=1,key="num_feed")
    biomass_initial_day = st.number_input("Biomass in the initial day (in gm)", min_value=0.0, step=0.00001, format="%.5f",value=None)
    biomass_final_day = st.number_input("Biomass in the final day (in gm)", min_value=0.0, step=0.00001, format="%.5f",value=None)
    n2 = st.number_input("Number of days", min_value=1,key="num_biomass")

    if st.button("Calculate FCR"):
        try:
            change_in_feed_consumption = calculate_change_in_feed_consumption(feed_consumed_initial_day, feed_consumed_final_day)
            change_in_biomass = calculate_change_in_biomass(biomass_initial_day,biomass_final_day)
            fcr=calculate_fcr(change_in_feed_consumption,change_in_biomass)

            # Store results in session state
            st.session_state.feed_consumed_initial_day = feed_consumed_initial_day
            st.session_state.feed_consumed_final_day= feed_consumed_final_day
            st.session_state.n1= n1 
            st.session_state.biomass_initial_day = biomass_initial_day
            st.session_state.biomass_final_day= biomass_final_day
            st.session_state.n2= n2
            st.session_state.fcr= fcr
            st.session_state.fcr_results = {
            "Change in feed consumption": f"{change_in_feed_consumption} gm",
            "Change in biomass": f"{change_in_biomass} gm",
            "Total FCR": fcr
            }
        except:
            st.warning("Please enter proper values!!!")
    # Display Branch Biomass Results
    if st.session_state.fcr_results:
        st.subheader("Calculated Branch Biomass:")
        for key, value in st.session_state.fcr_results.items():
            st.write(f"{key}: {value}")

with col2:
    st.write("<h3 style='color: black;'>Feed Conversion Ratio (FCR)</h3>", unsafe_allow_html=True)
    st.write(
        "<h6 style='color: dark green;'>The Feed Conversion Ratio (FCR) is a key measure in aquaculture that indicates the efficiency of feed utilization by fish. It is calculated as the amount of feed consumed divided by the weight gain of the fish. A lower FCR signifies better feed efficiency, reducing costs and minimizing environmental impact, while a higher FCR suggests inefficiencies in diet or culture conditions. Optimizing FCR is crucial for sustainable and profitable aquaculture practices.</h6>",
        unsafe_allow_html=True,
    )
    st.image("WhatsApp Image 2025-02-27 at 10.48.46 PM.jpeg",width=270)



if st.button("Save Results to Excel"):
    save_to_excel()
    display()
    st.warning("Please download your Excel file before refresh the page!!!")

# Example usage: Delete a row with a specific name
delete_name = st.text_input("Enter the Name to delete:")
if st.button("Delete Item"):
    delete_item_from_excel(delete_name)



#===== end note  =========#
col1,col2=st.columns([2,1])
with col1:
    st.write(
        "<h2 style='color: purple;'>End Note</h2>",
        unsafe_allow_html=True,
    )
    st.write(
        "<h5 style='color: green;'>Fish behaviour in different aquatic zones can be metaphorically compared to human nature:</h5>",
        unsafe_allow_html=True,
    )
    st.write(
        "<h5 style='color: blue;'>1. Deep-water fish They live in the dark, high-pressure environment, are often elusive, strategic, and cautious, much like cunning and clever individuals who navigate complexities with wisdom and patience.</h5>",
        unsafe_allow_html=True,
    )
    st.write(
        "<h5 style='color: blue;'>2. Mid-water fish - They constantly swim yet not too deep, resemble adaptable and social individuals who balance ambition with caution, adjusting to situations as needed.</h5>",
        unsafe_allow_html=True,
    )
    st.write(
        "<h5 style='color: blue;'>3. Surface-water fish - These fishes are exposed to light and frequent activity, often energetic, opportunistic, and sometimes impulsive—similar to extroverted, spontaneous people who thrive on visibility and quick actions but are more vulnerable to challenges.</h5>",
        unsafe_allow_html=True,
    )
    

with col2:
   st.write("<h3 style='color: black;'>Rooted Reflections: The Human-Fish Connection</h3>", unsafe_allow_html=True)
   st.image("WhatsApp Image 2025-02-27 at 10.54.57 PM.jpeg",width=250) 




#========== email configuration=========#



col1,col2=st.columns([2,1])

with col1:

# # Email Configuration

# Load email credentials from Streamlit Secrets
    EMAIL_ADDRESS = st.secrets["email"]["EMAIL_ADDRESS"]
    EMAIL_PASSWORD = st.secrets["email"]["EMAIL_PASSWORD"]

    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587

    def send_email(name, user_email, message):
        subject = f"New Contact Form Submission from {name}"
        body = f"Name: {name}\nEmail: {user_email}\n\nMessage:\n{message}"

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL_ADDRESS  # Use your email as sender
        msg["To"] = EMAIL_ADDRESS  # Send to yourself

        try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()  # Secure the connection
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, msg.as_string())
            server.quit()
            return "✅ Your message has been sent successfully!"
        except Exception as e:
            return f"❌ Error: {str(e)}"

# Streamlit UI
    st.title("📩 Contact Us")

    name = st.text_input("Your Name")
    email = st.text_input("Your Email")
    message = st.text_area("Your Message")

    if st.button("Send Email"):
        if name and email and message:
            response = send_email(name, email, message)
            st.success(response)
        else:
            st.error("⚠️ Please fill in all fields.")




with col2:
    st.title("Knowledge Hunter")
    st.image("WhatsApp Image 2025-02-27 at 11.03.36 PM.jpeg",width=180)
    st.write("<h3 style='color: black;'>Dr. Abhijit Mitra</h3>", unsafe_allow_html=True)
    st.write("<h5 style='color: green;'>Email: abhijitresearchmitra@gmail.com</h5>", unsafe_allow_html=True)
    st.write('<h5 style="color: black;">"Dive deep into the sea of knowledge to get pearl of peace."</h5>', unsafe_allow_html=True)



st.markdown(
    """
    <style>
        .footer {
            
            bottom: 0;
            width: 100%;
            text-align: center;
            font-size: 14px;
            color: gray;
            padding: 10px;
            background-color: #f8f9fa;
        }
    </style>
    <div class="footer">
        © 2025 Fish Health & Wellness Checker. All rights reserved.
    </div>
    """,
    unsafe_allow_html=True
)






