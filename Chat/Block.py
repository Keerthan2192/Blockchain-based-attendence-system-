import cv2
import pandas as pd
from datetime import datetime
import hashlib
import os

# Define valid staff IDs and names
valid_staff = {
    "123": "Your record",
    "456": "Your record"
}


class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        return hashlib.sha256(
            (str(self.index) + str(self.timestamp) + str(self.data) + str(self.previous_hash)).encode()).hexdigest()


class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(0, datetime.now(), "Genesis Block", "0")

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, new_block):
        new_block.previous_hash = self.get_latest_block().hash
        new_block.hash = new_block.calculate_hash()
        self.chain.append(new_block)


def capture_photo(staff_name):
    # Create folder for images if it doesn't exist
    if not os.path.exists('images'):
        os.makedirs('images')

    # Create folder for current date if it doesn't exist
    current_date_folder = datetime.now().strftime("%Y-%m-%d")
    if not os.path.exists(os.path.join('images', current_date_folder)):
        os.makedirs(os.path.join('images', current_date_folder))

    # Initialize webcam
    cap = cv2.VideoCapture(0)

    # Capture frame-by-frame
    ret, frame = cap.read()

    # Save captured image with staff name
    image_filename = f'{staff_name}_{datetime.now().strftime("%H%M%S")}.jpg'
    image_path = os.path.join('images', current_date_folder, image_filename)
    cv2.imwrite(image_path, frame)

    # Release the camera
    cap.release()

    return image_path


def validate_staff(staff_id, staff_name):
    # Verify staff ID and name against predefined valid values
    if staff_id in valid_staff and valid_staff[staff_id] == staff_name:
        return True
    else:
        return False


def save_to_excel(data):
    try:
        existing_data = pd.read_excel('staff_data.xlsx')
        df = pd.DataFrame(data, columns=['Staff ID', 'Staff Name', 'Date', 'Time', 'Image Path'])
        updated_data = pd.concat([existing_data, df], ignore_index=True)
        updated_data.to_excel('staff_data.xlsx', index=False)
    except FileNotFoundError:
        df = pd.DataFrame(data, columns=['Staff ID', 'Staff Name', 'Date', 'Time', 'Image Path'])
        df.to_excel('staff_data.xlsx', index=False)


def hash_data(data):
    return hashlib.sha256(str(data).encode()).hexdigest()


def store_in_blockchain(data, blockchain):
    blockchain.add_block(Block(len(blockchain.chain), datetime.now(), data, blockchain.get_latest_block().hash))


def main():
    blockchain = Blockchain()

    staff_id = input("Enter Staff ID: ")
    staff_name = input("Enter Staff Name: ")

    if validate_staff(staff_id, staff_name):
        image_path = capture_photo(staff_name)
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H:%M:%S")

        # Data to be saved
        data = {
            'Staff ID': staff_id,
            'Staff Name': staff_name,
            'Date': current_date,
            'Time': current_time,
            'Image Path': image_path
        }

        # Save data to Excel
        save_to_excel([data])

        # Store data in blockchain
        store_in_blockchain(data, blockchain)

        print("Data captured and saved successfully.")
    else:
        print("Invalid Staff ID or Staff Name.")


if __name__ == "__main__":
    main()
