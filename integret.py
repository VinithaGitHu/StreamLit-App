import time
from PIL import Image, ImageDraw, ImageFont
import streamlit as st
import requests

# Google Drive API access token
headers = {
    "Authorization": "Bearer ya29.a0AXeO80QpizoOmLvqSEjj6P0nCAA6Yr5vZjUF4fzqUuUYTyIl1mmOjI3ue3atgHAru-pj_QJ9zCnNHDBzsKO3YjhQV335FdSZoUj6o0NN9l0IwNyP8pETc5vnygAHcDaDOHzKSXAoErOBySWTBw65nFvwhIbAVIa7rG6RfngeaCgYKAcwSARESFQHGX2MizH8NkQMh-jvj3p_1riW2nw0175"
}

# Folder IDs
migration_a_folder_id = "1TziRD9usEqbxyWMMFk_ydPmnHyp-prk5"  # Replace with Migration A folder ID
migration_b_folder_id = "1FhBr8CaeixqLzBqag1mAAMQMoB9D1nyg"  # Replace with Migration B folder ID

# Draw progress tracker
def draw_progress(stage, failure=False, messages=None):
    stages = ["Stage 1", "Stage 2", "Stage 3", "Stage 4"]
    total_stages = len(stages)
    width, height = 500, 700  # Adjusted for vertical layout
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    radius = 5  # Adjusted circle radius for better visibility
    circle_color = "lightgreen"
    failure_color = "#FF9999"
    line_color = "lightgreen"
    failure_line_color = "#FF9999"
    text_color = "black"
    message_color_success = "green"
    message_color_failure = "red"
    x_position = width // 2
    y_positions = [80 + i * 100 for i in range(total_stages)]

    # Gap between the circle and the line
    gap = 10  # Set gap between the circle and the line

    # Font settings (using default font)
    font = ImageFont.load_default()

    for i in range(total_stages):
        if failure and i == stage - 1:
            fill = failure_color
        else:
            fill = circle_color if i < stage else "gray"

        # Draw lines between circles
        if i < total_stages - 1:
            line_start = (x_position, y_positions[i] + radius + gap)  # Adjusted with gap
            line_end = (x_position, y_positions[i + 1] - radius - gap)  # Adjusted with gap
            if failure and i == stage - 1:  # Make the line after the failure circle red
                draw.line([line_start, line_end], fill=failure_line_color, width=2)
            else:
                draw.line([line_start, line_end], fill=line_color if i < stage else "gray", width=2)

        # Draw circles
        draw.ellipse(
            [
                x_position - radius,
                y_positions[i] - radius,
                x_position + radius,
                y_positions[i] + radius
            ],
            fill=fill,
            outline="black"
        )

        # Draw stage name next to each circle
        text_bbox = draw.textbbox((0, 0), stages[i], font=font)
        draw.text(
            (x_position + 20, y_positions[i] - text_bbox[3] // 2),
            stages[i],
            fill=text_color,
            font=font
        )

        # Draw messages below each stage if provided
        if messages and i < len(messages) and messages[i]:
            msg = messages[i]
            lines = msg.split("\n")
            for j, line in enumerate(lines):
                draw.text(
                    (x_position + 20, y_positions[i] + 20 + j * 15),
                    line,
                    fill=message_color_failure if failure and i == stage - 1 else message_color_success,
                    font=font
                )

    return img

# List files in a folder
def list_files_in_folder(folder_id):
    query = f"'{folder_id}' in parents and trashed = false"
    url = f"https://www.googleapis.com/drive/v3/files?q={query}&fields=files(id,name,modifiedTime)"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json().get("files", [])
    else:
        st.error(f"Failed to list files: {response.status_code}, {response.text}")
        return []

# Move file to another folder
def move_file_to_folder(file_id, destination_folder_id, source_folder_id, file_name):
    url = f"https://www.googleapis.com/drive/v3/files/{file_id}?addParents={destination_folder_id}&removeParents={source_folder_id}"
    response = requests.patch(url, headers=headers)
    
    if response.status_code != 200:
        st.error(f"Failed to move file {file_id}: {response.status_code}, {response.text}")

# Read file content
def read_file_content(file_id):
    url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.text.strip()
    else:
        st.error(f"Failed to read file content: {response.status_code}, {response.text}")
        return None

# Main process logic
def process_files():
    stage = 1

    # Display the initial progress image
    placeholder = st.empty()
    messages = ["" for _ in range(4)]  # Initialize messages for each stage
    img = draw_progress(stage, messages=messages)
    placeholder.image(img, use_container_width=True)

    while True:
        files = list_files_in_folder(migration_a_folder_id)
        txt_files = [file for file in files if file["name"].endswith(".txt")]

        if not txt_files:
            time.sleep(10)  # Wait before checking again
            continue

        # If files are found, break the monitoring loop and proceed
        break

    file_count = 0  # Counter to track the number of processed files

    while stage <= 4:
        # Step 1: Monitoring
        files = list_files_in_folder(migration_a_folder_id)
        txt_files = [file for file in files if file["name"].endswith(".txt")]

        if txt_files:
            sorted_files = sorted(txt_files, key=lambda x: x["modifiedTime"])

            for file in sorted_files:
                file_id = file["id"]
                file_name = file["name"]

                # Read file content
                file_content = read_file_content(file_id)

                if file_content == "success":
                    messages[stage - 1] = f"Success."

                    # Update progress image
                    img = draw_progress(stage, messages=messages)
                    placeholder.image(img, use_container_width=True)

                    # Wait for new file to arrive
                    while True:
                        time.sleep(10)
                        updated_files = list_files_in_folder(migration_a_folder_id)
                        updated_txt_files = [
                            f for f in updated_files if f["name"].endswith(".txt")
                        ]

                        if len(updated_txt_files) > len(txt_files):
                            break

                    # Move the processed file to Migration B
                    move_file_to_folder(file_id, migration_b_folder_id, migration_a_folder_id, file_name)

                    file_count += 1

                    if file_count == 4:
                        st.info("All files processed.")
                        st.stop()

                elif file_content == "failure":
                    messages[stage - 1] = f"Failure encountered."

                    # Update progress image with failure status
                    img = draw_progress(stage, failure=True, messages=messages)
                    placeholder.image(img, use_container_width=True)
                    st.error("Process stopped due to failure.")
                    st.stop()

                # Mark the file as processed
                stage += 1
                if stage > 4:
                    st.info("All files processed.")
                    st.stop()
                    break

# Main function for Streamlit app
def main():
    st.set_page_config(page_title="Client Information", page_icon="📋")
    
    # Session state to store input details
    if 'client_name' not in st.session_state:
        st.session_state.client_name = ""
    if 'client_id' not in st.session_state:
        st.session_state.client_id = ""
    if 'database' not in st.session_state:
        st.session_state.database = ""
    if 'page' not in st.session_state:
        st.session_state.page = "form"
    
    if st.session_state.page == "form":
        show_form()
    elif st.session_state.page == "details":
        show_details()

def show_form():
    st.title("Enter Client Information")
    
    st.session_state.client_name = st.text_input("Client Name", st.session_state.client_name)
    st.session_state.client_id = st.text_input("Client ID", st.session_state.client_id)
    st.session_state.database = st.text_input("Database", st.session_state.database)
    
    if st.button("Submit"):
        if st.session_state.client_name and st.session_state.client_id and st.session_state.database:
            st.session_state.page = "details"
            st.rerun()
        else:
            st.warning("Please fill in all fields before submitting.")

def show_details():
    st.title("Client Details")
    
    st.write(f"**Client Name:** {st.session_state.client_name}")
    st.write(f"**Client ID:** {st.session_state.client_id}")
    st.write(f"**Database:** {st.session_state.database}")
    
    # Start the process files logic from the second script after showing details
    process_files()

    if st.button("Go Back"):
        st.session_state.page = "form"
        st.rerun()

if __name__ == "__main__":
    main()
