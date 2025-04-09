import hvac
import json
import os
import getpass
from hvac.api.secrets_engines import KvV1, KvV2

# Function to list and create folders/files for KV v1
def create_folders_and_files_kv_v1(client, mount_point, base_path="", base_folder="."):
    try:
        response = client.list(f"{mount_point}/{base_path}")
        if response and "data" in response and "keys" in response["data"]:
            paths = response["data"]["keys"]
            for path in paths:
                full_path = f"{base_path}/{path}" if base_path else path
                local_folder = os.path.join(base_folder, base_path)
                if path.endswith("/"):  # If it's a directory
                    create_folders_and_files_kv_v1(client, mount_point, base_path=full_path.rstrip("/"), base_folder=base_folder)
                else:  # If it's a secret
                    try:
                        secret = client.read(f"{mount_point}/{full_path}")
                        secret_data = secret["data"]
                        os.makedirs(local_folder, exist_ok=True)
                        local_file_path = os.path.join(local_folder, path)
                        with open(local_file_path, "w", encoding="utf-8") as secret_file:
                            json.dump(secret_data, secret_file, ensure_ascii=False, indent=4)
                        print(f"Created file: {local_file_path}")
                    except Exception as e:
                        print(f"Error writing file for secret at {full_path}: {e}")
        else:
            print(f"No paths found under '{mount_point}/{base_path}'.")
    except Exception as e:
        print(f"Error: {e}")

# Function to list and create folders/files for KV v2
def create_folders_and_files_kv_v2(kv_v2, mount_point, base_path="", base_folder="."):
    try:
        response = kv_v2.list_secrets(mount_point=mount_point, path=base_path)
        if response and "data" in response and "keys" in response["data"]:
            paths = response["data"]["keys"]
            for path in paths:
                full_path = f"{base_path}/{path}" if base_path else path
                local_folder = os.path.join(base_folder, base_path)
                if path.endswith("/"):  # If it's a directory
                    create_folders_and_files_kv_v2(kv_v2, mount_point, base_path=full_path.rstrip("/"), base_folder=base_folder)
                else:  # If it's a secret
                    try:
                        secret = kv_v2.read_secret_version(mount_point=mount_point, path=full_path)
                        secret_data = secret["data"]["data"]
                        os.makedirs(local_folder, exist_ok=True)
                        local_file_path = os.path.join(local_folder, path)
                        with open(local_file_path, "w", encoding="utf-8") as secret_file:
                            json.dump(secret_data, secret_file, ensure_ascii=False, indent=4)
                        print(f"Created file: {local_file_path}")
                    except Exception as e:
                        print(f"Error writing file for secret at {full_path}: {e}")
        else:
            print(f"No paths found under '{mount_point}/{base_path}'.")
    except Exception as e:
        print(f"Error: {e}")

# Choose KV engine version and call the appropriate function
def main():
    print("Enter the Vault server URL:")
    url = input("URL: ").strip()

    print("Enter the Vault token (input will be hidden):")
    token = getpass.getpass("Token: ").strip()

    # Initialize the Vault client
    client = hvac.Client(url=url, token=token)

    print("Select Vault Key-Value engine version:")
    print("1: KV v1")
    print("2: KV v2")
    choice = input("Enter your choice (1 or 2): ").strip()

    # Prompt user for input variables
    secrets_namespace = input("Enter the mount point for secrets: ").strip()
    base_folder = input("Enter the output folder (path): ").strip()

    if not os.path.exists(base_folder):
        print(f"Base folder {base_folder} does not exist. Creating it...")
        os.makedirs(base_folder, exist_ok=True)

    if choice == "1":
        print(f"Using KV v1 at mount point '{secrets_namespace}'")
        create_folders_and_files_kv_v1(client, mount_point=secrets_namespace, base_path="", base_folder=base_folder)
    elif choice == "2":
        print(f"Using KV v2 at mount point '{secrets_namespace}'")
        kv_v2 = KvV2(adapter=client.adapter)
        create_folders_and_files_kv_v2(kv_v2, mount_point=secrets_namespace, base_path="", base_folder=base_folder)
    else:
        print("Invalid choice. Exiting.")

# Run the script
if __name__ == "__main__":
    main()
