import streamlit as st
from PIL import Image
import numpy as np
import csv
import os  
import qrcode
import io
import cv2

# Function to create a CSV file to store user credentials
def create_credentials_file():
    if not os.path.exists("user_credentials.csv"):
        with open("user_credentials.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["username", "password"])

# Function to register a new user
def register_user(username, password):
    with open("user_credentials.csv", "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([username, password])
    st.success("Registration successful. Please log in.")

# Function to check if a user exists in the CSV file and if the password matches
def login_user(username, password):
    with open("user_credentials.csv", "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["username"] == username and row["password"] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Welcome, {username}! You are now logged in.")
                return True
    st.error("Invalid username or password. Please try again.")
    return False

# Function to perform BB84 key exchange with Basis Matching & Key Sifting
def bb84_key_exchange(length):
    alice_bits = np.random.randint(2, size=length)
    alice_bases = np.random.randint(2, size=length)
    bob_bases = np.random.randint(2, size=length)
    matching_indices = np.where(alice_bases == bob_bases)[0]
    sifted_key = alice_bits[matching_indices]
    return sifted_key

# Function to encrypt and decrypt messages
def encrypt_message(message, key):
    return ''.join(chr(ord(message[i]) ^ key[i % len(key)]) for i in range(len(message)))

def decrypt_message(encrypted_message, key):
    return ''.join(chr(ord(encrypted_message[i]) ^ key[i % len(key)]) for i in range(len(encrypted_message)))

# Function to generate a QR code for the shared key
def generate_qr_code(shared_key):
    qr = qrcode.QRCode(
        version=3,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=5,
        border=2,
    )
    qr.add_data(shared_key)
    qr.make(fit=True)
    return qr.make_image(fill_color="green", back_color="white")

# Main function to run the application
def main():
    create_credentials_file()

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.title("🔒 Lock Chat")
        st.subheader("A secure messaging platform using Quantum Key Distribution (QKD)")
        st.sidebar.title("Authentication")
        option = st.sidebar.radio("Choose an option", ("Login", "Register"))
        
        if option == "Register":
            new_username = st.sidebar.text_input("Username")
            new_password = st.sidebar.text_input("Password", type="password")
            if st.sidebar.button("Register"):
                register_user(new_username, new_password)
        elif option == "Login":
            username = st.sidebar.text_input("Username")
            password = st.sidebar.text_input("Password", type="password")
            if st.sidebar.button("Login"):
                login_user(username, password)
    elif st.sidebar.button("Logout"):
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        st.sidebar.title("Navigation")
        navigation_option = st.sidebar.radio("Go to:", ("Secure Chat Interface",))

        if navigation_option == "Secure Chat Interface":
            st.subheader("Secure Chat Interface")
            st.write(f"Welcome, {st.session_state.username}!")
            
            message_to_send = st.text_area("Type your message:")
            if st.button("Send Message"):
                st.success("Message sent successfully!")
                shared_key = bb84_key_exchange(len(message_to_send))
                encrypted_message = encrypt_message(message_to_send, shared_key)
                qr_code_img = generate_qr_code(''.join(map(str, shared_key)))
                img_byte_arr = io.BytesIO()
                qr_code_img.save(img_byte_arr, format='PNG')
                st.image(img_byte_arr, caption="QR Code for Shared Key")
                st.session_state.encrypted_message = encrypted_message
                st.session_state.shared_key = shared_key

            encrypted_message_received = st.text_input("Enter encrypted message:")
            shared_key_received = st.text_input("Enter shared key:")
            if st.button("Decrypt Message"):
                if encrypted_message_received and shared_key_received:
                    decrypted_message = decrypt_message(encrypted_message_received, list(map(int, shared_key_received)))
                    st.write("Decrypted message:", decrypted_message)
                    st.success("Message decrypted successfully!")
                else:
                    st.error("Please enter a valid encrypted message and key.")

if __name__ == "__main__":
    main()
