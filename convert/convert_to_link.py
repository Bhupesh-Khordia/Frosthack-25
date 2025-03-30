import requests

def upload_to_hastebin(file_path, api_token):
    # Read the content of the file
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Define the headers, including the Authorization token
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'text/plain'
    }

    # Send the POST request to Hastebin's /documents endpoint
    response = requests.post('https://hastebin.com/documents', data=content, headers=headers)

    # Handle the response
    if response.status_code == 200:
        response_data = response.json()
        key = response_data.get('key')
        if key:
            print(f"File uploaded successfully! Access it at: https://hastebin.com/{key}")
        else:
            print("Upload failed: No key returned in response.")
    else:
        print(f"Upload failed. Status code: {response.status_code}, Response: {response.text}")

# Example usage (replace 'YOURTOKEN' with your actual token)
upload_to_hastebin('input.txt', '53ec751cce9916bd7cb1ab5f8f93f4c91fdfa1420df61a4a337ba3a4bb2a6d10730d3052aaff8b22c8f40abba878bf0d0d7e04fb1fb5d04dfb77fd15f60988d7')
