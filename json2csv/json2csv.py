import pandas as pd
import json

def json_to_csv(json_file_path, csv_file_path):
    # Read JSON file
    with open(json_file_path, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    
    # Extract student data
    students_data = data["Students"]
    
    # Convert student data to DataFrame
    df = pd.DataFrame.from_dict(students_data, orient='index')
    
    # Write DataFrame to a CSV file
    df.to_csv(csv_file_path, index=False)

    print(f"JSON data has been successfully converted to {csv_file_path}")

# Example usage
json_file_path = 'faceattendancerealtime-7a66f-default-rtdb-export.json'  # Replace with your JSON file path
csv_file_path = 'data0.csv'  # Replace with your desired CSV file path
json_to_csv(json_file_path, csv_file_path)
