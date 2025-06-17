import streamlit as st
import tensorflow as tf
from PIL import Image
import numpy as np
from streamlit_option_menu import option_menu
import base64
from fpdf import FPDF
import mysql.connector
import os
import pandas as pd

# Database Connection
def connect_to_db():
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="Alzheimers",
            password="",
            database="Alzheimers"
        )
        return mydb
    except mysql.connector.Error as err:
        st.error(f"Database connection error: {err}")
        return None

mydb = connect_to_db()
mycursor = mydb.cursor(buffered=True) if mydb else None

# Load the saved model
model_path = os.path.join('C:/Users/haris/Downloads/Alzheimers-disease-detection/models', 'model.h5')
if os.path.exists(model_path):
    model = tf.keras.models.load_model(model_path)
    print("Model Loaded Successfully.")
else:
    st.error("Model file not found. Please check the path or train the model.")

# Define class labels
class_labels = ['Mild Demented', 'Moderate Demented', 'Non Demented', 'Very Mild Demented']

# Set background image
def set_background(image_file):
    with open(image_file, 'rb') as f:
        data = f.read()
    encoded_data = base64.b64encode(data).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url('data:image/png;base64,{encoded_data}');
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_background('./images/bg3.png')

# Preprocess image
def preprocess_image(image):
    image = image.convert('RGB')
    image = image.resize((176, 176))
    image = np.array(image) / 255.0
    return np.expand_dims(image, axis=0)

# Insert data into database
def insert_data(name, age, gender, contact, prediction):
    try:
        if not mydb or not mycursor or not mydb.is_connected():
            st.error("Database connection is not available.")
            return
        sql = "INSERT INTO predictions (Patient_Name, Age, Gender, Contact, Prediction) VALUES (%s, %s, %s, %s, %s)"
        val = (name, age, gender, contact, prediction)
        mycursor.execute(sql, val)
        mydb.commit()
        st.success("Data inserted successfully.")
    except mysql.connector.Error as err:
        st.error(f"Failed to insert data: {err}")

# PDF class
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, "Hospital Alzheimer's Report", align='C', ln=1)
        self.set_font('Arial', 'I', 12)
        self.cell(0, 10, 'Detailed Diagnosis and Patient Information', align='C', ln=1)
        self.ln(10)

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, title, ln=1, align='L')
        self.ln(5)

    def chapter_body(self, body):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, body)
        self.ln()

    def add_page_border(self):
        self.set_draw_color(0, 0, 0)
        self.rect(5.0, 5.0, 200.0, 287.0)

    def add_image(self, image_path):
        img_width = 70
        img_x = (210 - img_width) / 2
        img_y = self.get_y()

        self.image(image_path, x=img_x, y=img_y, w=img_width)

        img_height = img_width * 1.0  # Keep square aspect ratio (adjust if needed)
        border_padding = 2
        self.set_draw_color(50, 50, 50)
        self.rect(img_x - border_padding, img_y - border_padding,
                  img_width + 2 * border_padding, img_height + 2 * border_padding)

        self.ln(img_height + 15)

# Generate PDF with Patient Details
def generate_pdf(image_path, name, age, gender, contact, prediction):
    pdf = PDF()
    pdf.add_page()
    pdf.add_page_border()

    pdf.chapter_title("Patient Details")
    patient_info = (
        f"Name: {name}\n"
        f"Age: {age}\n"
        f"Gender: {gender}\n"
        f"Contact: {contact}\n"
        f"Prediction: {prediction}\n"
    )
    pdf.chapter_body(patient_info)

    pdf.chapter_title("Uploaded MRI Scan")
    pdf.add_image(image_path)

    pdf.chapter_title("Alzheimer's Precaution Points")
    precautions = (
        "1. Maintain a healthy diet with balanced nutrition.\n"
        "2. Engage in regular physical exercise.\n"
        "3. Stay mentally active with puzzles and reading.\n"
        "4. Manage chronic conditions like diabetes and hypertension.\n"
        "5. Stay socially connected and build a strong support network.\n"
        "6. Get enough sleep and manage stress effectively."
    )
    pdf.chapter_body(precautions)

    pdf_path = f"report_{name}.pdf"
    pdf.output(pdf_path)
    return pdf_path

# Sidebar Navigation
with st.sidebar:
    selected = option_menu(
        menu_title="Navigation",
        options=["Home", "Alzheimer Detection", "Patient Records", "About Us"],
        icons=["house", "book", "table", "info-circle"],
        menu_icon="cast",
        default_index=0,
    )

# Home Page
if selected == "Home":
    st.markdown("""
        <style>
            .title-container {
                text-align: center;
                margin-top: -60px;
            }
            .hero-img {
                border-radius: 15px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                max-width: 100%;
                height: auto;
            }
            .feature-card {
                border: 1px solid #eee;
                border-radius: 12px;
                padding: 1rem;
                background: transparent;
                backdrop-filter: blur(10px);
                box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
                margin-bottom: 1rem;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="title-container"><h1>🧠 Welcome to Alzheimer\'s Disease Detection</h1></div>', unsafe_allow_html=True)
    st.image("hero.png", use_column_width=True, caption="AI-powered Alzheimer Detection System")

    st.markdown("### 🩺 About This App")
    st.write("""
        This AI-powered web application helps in the early detection of Alzheimer's Disease by analyzing MRI scans. 
        Users can upload a brain scan, receive an instant prediction, and download a detailed PDF report with precautionary recommendations.
    """)

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="feature-card"><h4>⚡ Fast & Accurate</h4><p>Deep learning ensures reliable predictions within seconds.</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="feature-card"><h4>📁 Patient Records</h4><p>All predictions are saved for future reference and diagnosis tracking.</p></div>', unsafe_allow_html=True)
    with col1:
        st.markdown('<div class="feature-card"><h4>🧾 PDF Reports</h4><p>Generate downloadable reports for sharing with doctors or caregivers.</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="feature-card"><h4>💡 AI-driven Insights</h4><p>Backed by convolutional neural networks and medical datasets.</p></div>', unsafe_allow_html=True)

# Alzheimer Detection Page
elif selected == "Alzheimer Detection":
    st.title("🔎 Alzheimer Detection Web App")
    with st.form(key='patient_form', clear_on_submit=True):
        name = st.text_input('Name')
        age = st.number_input('Age', min_value=1, max_value=150, value=40)
        gender = st.radio('Gender', ('Male', 'Female', 'Other'))
        contact = st.text_input('Contact Number')
        file = st.file_uploader('Upload an MRI Scan', type=['jpg', 'jpeg', 'png'])
        submit = st.form_submit_button("Submit")

    if submit and file:
        image = Image.open(file)
        image_array = preprocess_image(image)
        prediction = np.argmax(model.predict(image_array), axis=1)
        result = class_labels[prediction[0]]
        st.success(f'The predicted class is: **{result}**')

        insert_data(name, age, gender, contact, result)

        # Save image temporarily
        image_path = f"temp_{name}.png"
        image.save(image_path)

        # Generate and Download PDF with patient details
        pdf_path = generate_pdf(image_path, name, age, gender, contact, result)
        with open(pdf_path, 'rb') as f:
            st.download_button(label="Download Report PDF", data=f, file_name=f"report_{name}.pdf", mime='application/pdf')

        # Clean up
        os.remove(image_path)

# Patient Records Page
elif selected == "Patient Records":
    st.title("📋 Patient Records")
    if not mydb or not mycursor or not mydb.is_connected():
        st.error("Database connection is not available.")
    else:
        try:
            mycursor.execute("SELECT id, Patient_Name, Age, Gender, Contact, Prediction FROM predictions")
            result = mycursor.fetchall()
            if result:
                df = pd.DataFrame(result, columns=["ID", "Name", "Age", "Gender", "Contact", "Prediction Result"])
                st.write(df.style.set_properties(**{'text-align': 'center'}).set_table_styles(
                    [{'selector': 'th', 'props': [('background-color', '#f2f2f2')]}]))
            else:
                st.warning("No records found in the database.")
        except mysql.connector.Error as err:
            st.error(f"Error fetching data: {err}")

# About Us Page
elif selected == "About Us":
    st.title("ℹ️ About Us")
    st.write("We are dedicated to leveraging AI technology for Alzheimer's detection and providing efficient medical support.")
