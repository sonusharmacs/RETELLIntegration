import streamlit as st
import requests
import pandas as pd
st.title("Sample ReTell connectivity Application")
# 1. Define the API endpoint (Using a free public mock API)
API_URL = "http://127.0.0.1:/items/"
st.link_button("Sample ReTell API call","https://agent.retellai.com/orb/agent_d490eebff4aa1fbafab6eff84c?token=b9c9d9a89ddd86a28b642b17d2655d7b")

# 1. Create the form container
with st.form("api_submission_form"):
  name = st.text_input("Name")
  description = st.text_input("Description")
  #role = st.selectbox("Role", ["Developer", "Designer", "Manager"])

  # Every form requires a submit button
  submitted = st.form_submit_button("Submit to API")

# 2. Handle submission and make the API request
if submitted:
  payload = {"name": name, "description": description}

  try:
    # Replace with your target API endpoint
    response = requests.post("http://127.0.0.1:8000/items", json=payload)

    if response.status_code == 200:
      st.success("Form data successfully sent to the API!")
      st.json(response.json())
    else:
      st.error(
        f"API returned status code {response.status_code}: {response.text}"
      )
  except requests.exceptions.RequestException as e:
    st.error(f"Failed to connect to the API: {e}")

# 2. Fetch data from the API
#@st.cache_data  # Caches the data so it doesn't reload on every user interaction
def fetch_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {e}")
        return None

# Get the JSON data
json_data = fetch_data(API_URL)

if json_data:
    # 3. Convert JSON data to a Pandas DataFrame
    # Flatten nested JSON structures if necessary (e.g., 'address' or 'company' fields)
    df = pd.json_normalize(json_data)
    
    # 4. Clean up columns for better display (Optional)
    # Select and rename specific columns to keep the table clean
    columns_to_show = {
        'id': 'ID',
        'name': 'Name',
        'description': 'Description'
    }
    df_filtered = df[list(columns_to_show.keys())].rename(columns=columns_to_show)

    # 5. Display the data in a table format
    st.subheader("Item Directory")
    
    # Option A: Interactive Table (Recommended)
    # Allows users to sort columns, search, resize, and download as CSV
    st.dataframe(df_filtered, use_container_width=True, hide_index=True)
    
    # Option B: Static Table (Alternative)
    # Uncomment the line below if you want a classic, fixed-width static table
    # st.table(df_filtered)
