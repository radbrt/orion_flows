# first run "pip install azure-storage-blob"

from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

def write_to_azure_blob(sas_token, container_name, blob_name, file_path):
  """ upload file to azure blob storage """
  blob_service_client = BlobServiceClient.from_connection_string(sas_token)
  container_client = blob_service_client.get_container_client(container_name)
  blob_client = container_client.get_blob_client(blob_name)
  with open(file_path, "rb") as data:
    blob_client.upload_blob(data)


def main():

  file_to_upload = "<data/kron_data_2022_01_01.csv>"
  destination_file_name = "<kron_data_2022_01_01.csv>"
  sas_token = "<secret token sent in different channel>"
  
  
  connection_string = f"BlobEndpoint=https://cocerxsftp.blob.core.windows.net/;SharedAccessSignature={sas_token}"

  container_name = "krondata"
  
  write_to_azure_blob(sas_token, container_name, destination_file_name, file_to_upload)

if __name__ == '__main__':
  main()