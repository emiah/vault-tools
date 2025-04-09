import hvac
import json
import os
import getpass
from hvac.api.secrets_engines import KvV1, KvV2

# Function to import secrets from the file system into Vault (KV v1)
def import_secrets_from_files_kv_v1(kv_v1, source_folder, mount_point, base_path=""):
    try:
        for item in os.listdir(source_folder):
            item_path = os.path.join(source_folder, item)
            vault_path = f"{base_path}/{item}" if base_path else item

            if os.path.isdir(item_path):  # If it's a folder
                import_secrets_from_files_kv_v1(kv_v1, item_path, mount_point, base_path=vault_path)
            else:  # If it's a file
                with open(item_path, "r", encoding="utf-8") as secret_file:
                    secret_data = json.load(secret_file)
                try:
                    kv_v1.create_or_update_secret(
                        mount_point=mount_point,
                        path=vault_path,
                        secret=secret_data
                    )
                    print(f"Imported KV v1 secret to {mount_point}/{vault_path}")
                except Exception as e:
                    print(f"Error importing KV v1 secret to {mount_point}/{vault_path}: {e}")
    except Exception as e:
        print(f"Error processing folder {source_folder}: {e}")

# Function to import secrets from the file system into Vault (KV v2)
def import_secrets_from_files_kv_v2(kv_v2, source_folder, mount_point, base_path=""):
    try:
        for item in os.listdir(source_folder):
            item_path = os.path.join(source_folder, item)
            vault_path = f"{base_path}/{item}" if base_path else item

            if os.path.isdir(item_path):  # If it's a folder
                import_secrets_from_files_kv_v2(kv_v2, item_path, mount_point, base_path=vault_path)
            else:  # If it's a file
                with open(item_path, "r", encoding="utf-8") as secret_file:
                    secret_data = json.load(secret_file)
                try:
                    kv_v2.create_or_update_secret(
                        mount_point=mount_point,
                        path=vault_path,
                        secret=secret_data
                    )
                    print(f"Imported KV v2 secret to {mount_point}/{vault_path}")
                except Exception as e:
                    print(f"Error importing KV v2 secret to {mount_point}/{vault_path}: {e}")
    except Exception as e:
        print(f"Error processing folder {source_folder}: {e}")

# Choose KV version and perform import
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

    source_folder = input("Enter the source folder path: ").strip()
    mount_point = input("Enter the mount point in the new Vault: ").strip()

    if not os.path.exists(source_folder):
        print(f"Source folder {source_folder} does not exist. Exiting.")
        return

    if choice == "1":
        print(f"Using KV v1. Importing from {source_folder} to mount point '{mount_point}'")
        kv_v1 = KvV1(adapter=client.adapter)
        import_secrets_from_files_kv_v1(kv_v1, source_folder, mount_point)
    elif choice == "2":
        print(f"Using KV v2. Importing from {source_folder} to mount point '{mount_point}'")
        kv_v2 = KvV2(adapter=client.adapter)
        import_secrets_from_files_kv_v2(kv_v2, source_folder, mount_point)
    else:
        print("Invalid choice. Exiting.")

# Run the script
if __name__ == "__main__":
    main()
