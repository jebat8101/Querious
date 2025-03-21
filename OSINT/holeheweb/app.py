import streamlit as st
import subprocess
import json
import re
import os

# Create output directories if they don't exist
RAW_OUTPUT_DIR = "raw_outputs"
FILTERED_OUTPUT_DIR = "filtered_outputs"
os.makedirs(RAW_OUTPUT_DIR, exist_ok=True)
os.makedirs(FILTERED_OUTPUT_DIR, exist_ok=True)

# Function to validate email
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# Function to check if a tool is installed
def is_tool_installed(tool_name):
    return subprocess.call(["which", tool_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0

# Function to filter unwanted lines from the output file
def filter_output(input_file, output_file):
    try:
        with open(input_file, 'r') as file:
            lines = file.readlines()

        # Filtering out the unwanted lines
        filtered_lines = [
            line for line in lines 
            if not line.startswith("Twitter :") and 
               not line.startswith("Github :") and 
               not line.startswith("For BTC Donations :")
        ]

        # Writing the filtered output back to a file
        with open(output_file, 'w') as file:
            file.writelines(filtered_lines)

        return output_file

    except FileNotFoundError:
        st.error(f"File {input_file} not found. Please ensure the file exists.")
        return None

# Define the main function
def main():
    st.title("Email Checker")
    st.write("Check which sites are linked to a specific email address.")

    # Validate that Holehe is installed
    if not is_tool_installed("holehe"):
        st.error("Holehe is not installed or not available in the system PATH. Please install it and try again.")
        return

    # Get the email address from user input
    email = st.text_input("Enter the email address to check:", placeholder="example@example.com").strip()

    if st.button("Check Email"):
        if email and is_valid_email(email):
            st.write(f"Checking accounts for email: {email}")
            
            with st.spinner("Processing..."):
                try:
                    # Run the holehe command and capture output
                    result = subprocess.run(
                        ['holehe', email],
                        capture_output=True,
                        text=True,
                        check=True  # Ensure that subprocess raises an error on failure
                    )

                    # Save raw output to the raw_outputs folder
                    raw_output_file = os.path.join(RAW_OUTPUT_DIR, f"{email}_holehe_result.txt")
                    with open(raw_output_file, 'w') as raw_file:
                        raw_file.write(result.stdout)

                    # Save filtered output to the filtered_outputs folder
                    filtered_output_file = os.path.join(FILTERED_OUTPUT_DIR, f"{email}_filtered_result.txt")
                    filtered_file = filter_output(raw_output_file, filtered_output_file)

                    if filtered_file:
                        st.success("Filtered output saved.")
                        with open(filtered_file, 'r') as file:
                            filtered_content = file.read()
                            st.subheader("Filtered Output:")
                            st.text(filtered_content)

                        # Add download button for filtered output
                        st.download_button(
                            label="Download Filtered Output",
                            data=filtered_content,
                            file_name=f"{email}_filtered_result.txt",
                            mime="text/plain",
                        )

                except subprocess.CalledProcessError as e:
                    st.error("Error executing Holehe command.")
                    st.text(e.output)

                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")
        else:
            st.error("Please enter a valid email address.")

    # Footer with Copyright
    st.markdown("""
    ---
    © 2025, All rights reserved.  
    Developed by ECLOGIC.
    """)

# Run the app
if __name__ == "__main__":
    main()
