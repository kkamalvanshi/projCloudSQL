import streamlit as st
import requests
from datetime import datetime
import matplotlib.pyplot as plt
# Base URL of your Flask app
BASE_URL = "http://127.0.0.1:5000"

st.title('Model Deployment Service')

def get_data(endpoint, params=None):
    """
    Fetch data from a specified endpoint. Optionally include query parameters.

    Args:
    - endpoint (str): The endpoint to fetch data from.
    - params (dict, optional): A dictionary of query parameters.

    Returns:
    - JSON response data if the request is successful, otherwise an empty list.
    """
    if params is None:
        response = requests.get(f"{BASE_URL}/{endpoint}")
    else:
        response = requests.get(f"{BASE_URL}/{endpoint}", params=params)
    
    return response.json() if response.status_code == 200 else []

def update_data(endpoint, data):
    """Function to update data on the backend."""
    response = requests.put(f"{BASE_URL}/{endpoint}", json=data)
    return response.status_code


def post_data(endpoint, data):
    """Function to post data to the backend."""
    response = requests.post(f"{BASE_URL}/{endpoint}", json=data)
    return response.status_code == 201

def delete_data(endpoint, item_id):
    """Function to delete data from the backend."""
    response = requests.delete(f"{BASE_URL}/{endpoint}/{item_id}")
    return response.status_code == 200
# Sidebar for navigation
st.sidebar.title("Navigation")
options = ["Models","Datasets", "Versions", "Servers", "Deployments", "Deployment Reports", "Top Servers Report", "Model Types Count", "Top Datasets", "Top Models Report", "Dataset By Models", "Server Deployments"]
choice = st.sidebar.radio("Choose an option", options)

if choice == "Models":
    st.subheader('Add a Model')

    # Add Model
    with st.form("add_model"):
        
        name = st.text_input("Model Name")
        description = st.text_area("Model Description")
        model_type = st.selectbox("Model Type", ["LLM", "Regression", "Neural Network", "Other"])  # Added dropdown for model type
        submit_button = st.form_submit_button("Add Model")
        if submit_button:
            model_data = {
                'name': name,
                'description': description,
                'type': model_type  # Include the model type in the data sent to the backend
            }
            if post_data('models', model_data):
                st.success("Model added successfully")
            else:
                st.error("Failed to add model")
    st.subheader('Update Existing Model')
    models = get_data('models')
    model_id = st.selectbox("Select Model", [model['id'] for model in models], format_func=lambda x: f"ID {x}: {next(item['name'] for item in models if item['id'] == x)}")
    if model_id:
        selected_model = next((item for item in models if item['id'] == model_id), None)
        if selected_model:
            with st.form("update_model"):
                new_name = st.text_input("Model Name", value=selected_model['name'])
                new_description = st.text_area("Model Description", value=selected_model['description'])
                new_type = st.selectbox("Model Type", ["LLM", "Regression", "Neural Network", "Other"], index=["LLM", "Regression", "Neural Network", "Other"].index(selected_model['type']))
                submit_button = st.form_submit_button("Update Model")
                if submit_button:
                    model_update_data = {'name': new_name, 'description': new_description, 'type': new_type}
                    if update_data('models/' + str(model_id), model_update_data) == 200:
                        st.success("Model updated successfully")
                    else:
                        st.error("Failed to update model")

    # List Models
    models = get_data('models')
    model_type = st.selectbox("Model Type", ["All", "LLM", "Regression", "Neural Network"])
    if model_type != "All":
        models = [model for model in models if model['type'] == model_type]
    for model in models:
        st.text(f"ID: {model['id']} - Name: {model['name']} - Type: {model['type']} - Description: {model['description']}")
        if st.button("Delete", key=f"delete_model_{model['id']}"):
            if delete_data('models', model['id']):
                st.success(f"Model {model['id']} deleted")
            else:
                st.error(f"Failed to delete model {model['id']}")

elif choice == "Datasets":
    st.subheader('Add Dataset')

    # Add Dataset Form
    with st.form("add_dataset"):
        name = st.text_input("Dataset Name")
        description = st.text_area("Dataset Description")
        data_type = st.selectbox("Data Type", ["text", "image", "video", "audio"])
        submit_button = st.form_submit_button("Add Dataset")
        if submit_button:
            if post_data('datasets', {'name': name, 'description': description, 'data_type': data_type}):
                st.success("Dataset added successfully")
            else:
                st.error("Failed to add dataset")

    st.subheader('Update Existing Dataset')
    datasets = get_data('datasets')
    dataset_id = st.selectbox("Select Dataset", [dataset['id'] for dataset in datasets], format_func=lambda x: f"ID {x}: {next(item['name'] for item in datasets if item['id'] == x)}")
    if dataset_id:
        selected_dataset = next((item for item in datasets if item['id'] == dataset_id), None)
        if selected_dataset:
            with st.form("update_dataset"):
                new_name = st.text_input("Dataset Name", value=selected_dataset['name'])
                new_description = st.text_area("Dataset Description", value=selected_dataset['description'])
                new_data_type = st.selectbox("Data Type", ["text", "image", "video", "audio"], index=["text", "image", "video", "audio"].index(selected_dataset['data_type']))
                submit_button = st.form_submit_button("Update Dataset")
                if submit_button:
                    dataset_update_data = {'name': new_name, 'description': new_description, 'data_type': new_data_type}
                    if update_data('datasets/' + str(dataset_id), dataset_update_data) == 200:
                        st.success("Dataset updated successfully")
                    else:
                        st.error("Failed to update dataset")

    # List Datasets
    datasets = get_data('datasets')
    for dataset in datasets:
        st.text(f"ID: {dataset['id']} - Name: {dataset['name']} - Description: {dataset['description']} - Type: {dataset['data_type']}")
        if st.button("Delete", key=f"delete_dataset_{dataset['id']}"):
            if delete_data('datasets', dataset['id']):
                st.success(f"Dataset {dataset['id']} deleted")
            else:
                st.error(f"Failed to delete dataset {dataset['id']}")

    # Update and other operations go here

elif choice == "Versions":
    st.subheader('Add Version')

    # Add Version Form
    with st.form("add_version"):
        model_id = st.number_input("Model ID", step=1)
        dataset_id = st.number_input("Dataset ID", step=1)
        version_number = st.text_input("Version Number")
        performance_metrics = st.text_area("Performance Metrics")
        submit_button = st.form_submit_button("Add Version")
        if submit_button:
            if post_data('versions', {'model_id': model_id, 'dataset_id': dataset_id, 'version_number': version_number, 'performance_metrics': performance_metrics}):
                st.success("Version added successfully")
            else:
                st.error("Failed to add version")
    st.subheader('Update Existing Version')
    versions = get_data('versions')
    version_id = st.selectbox("Select Version", [version['id'] for version in versions], format_func=lambda x: f"ID {x}: Model ID {next(item['model_id'] for item in versions if item['id'] == x)}")
    if version_id:
        selected_version = next((item for item in versions if item['id'] == version_id), None)
        if selected_version:
            with st.form("update_version"):
                new_model_id = st.number_input("Model ID", value=selected_version['model_id'], step=1)
                new_dataset_id = st.number_input("Dataset ID", value=selected_version['dataset_id'], step=1)
                new_version_number = st.text_input("Version Number", value=selected_version['version_number'])
                new_performance_metrics = st.text_area("Performance Metrics", value=selected_version['performance_metrics'])
                submit_button = st.form_submit_button("Update Version")
                if submit_button:
                    version_update_data = {
                        'model_id': new_model_id,
                        'dataset_id': new_dataset_id,
                        'version_number': new_version_number,
                        'performance_metrics': new_performance_metrics
                    }
                    if update_data('versions/' + str(version_id), version_update_data) == 200:
                        st.success("Version updated successfully")
                    else:
                        st.error("Failed to update version")
    # List Versions
    versions = get_data('versions')
    for version in versions:
        st.text(f"ID: {version['id']} - Model ID: {version['model_id']} - Dataset ID: {version['dataset_id']} - Version Number: {version['version_number']} - Metrics: {version['performance_metrics']}")
        if st.button("Delete", key=f"delete_version_{version['id']}"):
            if delete_data('versions', version['id']):
                st.success(f"Version {version['id']} deleted")
            else:
                st.error(f"Failed to delete version {version['id']}")

    # Update and other operations go here


elif choice == "Servers":
    st.subheader('Add Servers')

    # Add Server Form
    with st.form("add_server"):
        name = st.text_input("Server Name")
        ip_address = st.text_input("IP Address")
        submit_button = st.form_submit_button("Add Server")
        if submit_button:
            if post_data('servers', {'name': name, 'ip_address': ip_address}):
                st.success("Server added successfully")
            else:
                st.error("Failed to add server")

    st.subheader('Update Existing Server')
    servers = get_data('servers')
    server_id = st.selectbox("Select Server", [server['id'] for server in servers], format_func=lambda x: f"ID {x}: {next(item['name'] for item in servers if item['id'] == x)}")
    if server_id:
        selected_server = next((item for item in servers if item['id'] == server_id), None)
        if selected_server:
            with st.form("update_server"):
                new_name = st.text_input("Server Name", value=selected_server['name'])
                new_ip_address = st.text_input("IP Address", value=selected_server['ip_address'])
                submit_button = st.form_submit_button("Update Server")
                if submit_button:
                    new_server_data = {'name': new_name, 'ip_address': new_ip_address}
                    if update_data('servers/' + str(server_id), new_server_data) == 200:
                        st.success("Server updated successfully")
                    else:
                        st.error("Failed to update server")
    # List Servers
    servers = get_data('servers')
    for server in servers:
        st.text(f"ID: {server['id']} - Name: {server['name']} - IP Address: {server['ip_address']}")
        if st.button("Delete", key=f"delete_server_{server['id']}"):
            if delete_data('servers', server['id']):
                st.success(f"Server {server['id']} deleted")
            else:
                st.error(f"Failed to delete server {server['id']}")

    # Update and other operations go here


elif choice == "Deployments":
    st.subheader('Deployment Management')

    # Add Deployment Form
    with st.form("add_deployment"):
        server_id = st.number_input("Server ID", step=1)
        version_id = st.number_input("Version ID", step=1)
        deployment_date = st.number_input("Deployment Date (MMDD)", min_value=101, max_value=1231, step=1)

        submit_button = st.form_submit_button("Add Deployment")
        if submit_button:
            deployment_data = {'server_id': server_id, 'version_id': version_id, 'deployment_time': deployment_date}
            if post_data('modeldeployments', deployment_data):
                st.success("Deployment added successfully.")
                st.experimental_rerun()
            else:
                st.error("Failed to add deployment.")

    # List Deployments
    st.subheader("Current Deployments")
    deployments = get_data('modeldeployments')
    if deployments:
        for deployment in deployments:
            # Formatting MMDD integer for display
            deployment_date_str = f"{str(deployment['deployment_time'])[:-2]}/{str(deployment['deployment_time'])[-2:]}"
            st.write(f"ID: {deployment['id']} - Server ID: {deployment['server_id']} - Version ID: {deployment['version_id']} - Deployment Date: {deployment_date_str}")
            if st.button("Delete", key=f"delete_{deployment['id']}"):
                if delete_data('modeldeployments', deployment['id']):
                    st.success(f"Successfully deleted deployment {deployment['id']}")
                    st.experimental_rerun()
                else:
                    st.error("Failed to delete deployment.")
    else:
        st.write("No deployments found.")
elif choice == "Deployment Reports":
    st.subheader('Deployment Reports by Name and Server')

    start_date = st.number_input("Start Date (MMDD)", min_value=101, max_value=1231, step=1, format='%d')
    end_date = st.number_input("End Date (MMDD)", min_value=101, max_value=1231, step=1, format='%d')
    
    # Assuming this part fetches model types successfully from another function
    model_type_options = ["All"] + [model['type'] for model in get_data('models')]
    selected_model_type = st.selectbox("Model Type", model_type_options)

    if st.button("Generate Report"):
        params = {"start_date": start_date, "end_date": end_date}
        if selected_model_type != "All":
            params["model_type"] = selected_model_type
            
        report_data = get_data('reports/deployments', params=params)

        if report_data:
            st.write("Deployments Matching Criteria:")
            #for deployment in report_data["deployments"]:
            for deployment in report_data:
                st.write(deployment)
    
        else:
            st.error("No data found for selected filters.")
elif choice == "Top Servers Report":
    st.subheader("Top Servers Deploying the Most Models")
    top_x = st.number_input("Enter number of top servers to fetch", min_value=1, value=5)
    if st.button("Show Top Servers"):
        top_servers = get_data("reports/top-servers", params={"top": top_x})
        if top_servers:
            for server in top_servers:
                st.text(f"Server Name: {server['server_name']} - Server Id: {server['server_id']} - Deployments Count: {server['deployment_count']}")
        else:
            st.error("Failed to fetch top servers report.")
elif choice == "Top Models Report":
        st.subheader("Top Models Deploying the Most")
        top_x = st.number_input("Enter number of top models to fetch", min_value=1, value=5)
        if st.button("Show Top Models"):
            top_models = get_data("reports/top-models", params={"top": top_x})
            if top_models:
                for model in top_models:
                    st.text(f"Model Name: {model['model_name']} - Model Id: {model['model_id']} - Deployments Count: {model['deployment_count']}")
            else:
                st.error("Failed to fetch top models report.")

elif choice == "Update Model":
    st.subheader("Update an Existing Model")

    # Fetch all models to populate the selection box
    models = get_data('models')
    model_names = {model['name']: model['id'] for model in models}
    selected_model_name = st.selectbox("Select a model to update", options=list(model_names.keys()))

    if selected_model_name:
        selected_model_id = model_names[selected_model_name]
        # Fetch details of the selected model
        selected_model_details = next((model for model in models if model['id'] == selected_model_id), None)

        if selected_model_details:
            # Display model details for editing
            name = st.text_input("Model Name", value=selected_model_details['name'])
            description = st.text_area("Description", value=selected_model_details['description'])
            model_type = st.selectbox("Type", options=["LLM", "Regression", "Neural Network", "Other"], index=["LLM", "Regression", "Neural Network", "Other"].index(selected_model_details['type']))

            if st.button(f"Update Model #{selected_model_id}"):
                updated_data = {
                    'name': name,
                    'description': description,
                    'type': model_type
                }
                response = update_data(f'models/{selected_model_id}', updated_data)
                print("Update response:", response)  # Temporary debug print
                if response == 200:
                    st.success("Model updated successfully.")
                else:
                    st.error(f"Failed to update model. Response code: {response}")

elif choice == "Model Types Count":
    st.subheader("Model Types Deployment Count")

    # Fetching model types count data from the Flask backend
    model_types_count = get_data("reports/model-types-count")

    if model_types_count:

        for item in model_types_count:
            st.write(f"Model Type: {item['model_type']} - Deployments: {item['deployment_count']}")
        types = [item['model_type'] for item in model_types_count]
        counts = [item['deployment_count'] for item in model_types_count]

        # Create a pie chart
        fig, ax = plt.subplots()
        ax.pie(counts, labels=types, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        st.pyplot(fig)  # Display the figure in the Streamlit app
        # Displaying each model type with its deployment count
        
    else:
        st.write("No data found.")
elif choice == "Top Datasets":
    st.subheader("Top Datasets by Number of Versions")
    top_x = st.number_input("Enter number of top datasets to fetch", min_value=1, value=5)
    if st.button("Show Top Datasets"):
        top_datasets = get_data("reports/top-datasets", params={"top": top_x})
        if top_datasets:
            for dataset in top_datasets:
                st.text(f"Dataset Name: {dataset['dataset_name']} - Dataset Id: {dataset['dataset_id']} - Versions Count: {dataset['version_count']}")
        else:
            st.error("Failed to fetch top datasets report.")
elif choice == "Dataset By Models":
    
    # Fetch datasets for dropdown
    datasets = get_data('datasets/list')
    dataset_names = {dataset['dataset_name']: dataset['dataset_id'] for dataset in datasets} if datasets else {}

    st.subheader("Select a Dataset to View Models")
    dataset_choice = st.selectbox("Choose Dataset", options=list(dataset_names.keys()))

    if dataset_choice:
        dataset_id = dataset_names[dataset_choice]
        models = get_data('models/by-dataset', params={'dataset_id': dataset_id})
        
        if models:
            for model in models:
                st.write(f"**Model Name:** {model['model_name']} (ID: {model['model_id']})")
                st.write(f"**Description:** {model['model_description']}")
                st.write(f"**Deployments Count:** {model['deployment_count']}")
                st.write("------")
        else:
            st.error("No models found for the selected dataset.")

if choice == "Server Deployments":
        st.subheader('Deployment Reports by Server')

        start_date = st.number_input("Start Date (MMDD)", min_value=101, max_value=1231, step=1, format='%d')
        end_date = st.number_input("End Date (MMDD)", min_value=101, max_value=1231, step=1, format='%d')
        
        #model_type_options = ["All"] + [model['type'] for model in get_data('models/list-types')]
        #selected_model_type = st.selectbox("Model Type", model_type_options)

        if st.button("Generate Report"):
            params = {"start_date": start_date, "end_date": end_date}

            report_data = get_data('reports/server-deployments', params=params)

            if report_data:
                st.write("Deployments Matching Criteria:")
                for deployment in report_data:
                    st.write(f"Server Name: {deployment['server_name']} - Server ID: {deployment['server_id']} - Deployments Count: {deployment['deployment_count']}")
            else:
                st.error("Failed to fetch report.")