import json
from azure.storage.blob import BlobServiceClient

def fetch_blob_data(connection_string, container_name, selected_date=None):
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)
    
    blobs_list = container_client.list_blobs()

    if selected_date:
        filtered_blobs = [blob for blob in blobs_list if selected_date in blob.name]
    else:
        filtered_blobs = blobs_list

    all_data = []
    for blob in filtered_blobs:
        blob_client = container_client.get_blob_client(blob)
        data = blob_client.download_blob().readall()
        all_data.append(json.loads(data))

    return all_data















