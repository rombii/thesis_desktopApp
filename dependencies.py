from mega import Mega
import zipfile
import os

mega_url = 'https://mega.nz/file/JFIzAIKT#hg5xK3rk6RmoxFqZwV0qsdg0N7zQQr-6qSSas4fNusg'
zip_file_path = './use_model.zip'
extract_path = './ConditioningAugmentation'

mega = Mega()
m = mega.login()

# Check if the zip file already exists
if not os.path.exists(zip_file_path):
    print("Downloading...")
    try:
        file = m.download_url(mega_url)
    except PermissionError as e:
        pass

# Check if the folder where you want to extract the zip file exists
if not os.path.exists(os.path.join(extract_path, 'ConditioningAugmentation', 'saved_model.pb')):
    print("Extracting...")
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
else:
    print("Model file already exists")