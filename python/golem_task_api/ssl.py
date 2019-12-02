import ssl
from pathlib import Path
from typing import Optional


SERVER_KEY_FILE_NAME: str = 'task_api_server_key.pem'
SERVER_CERT_FILE_NAME: str = 'task_api_server_cert.pem'
CLIENT_KEY_FILE_NAME: str = 'task_api_client_key.pem'
CLIENT_CERT_FILE_NAME: str = 'task_api_client_cert.pem'


def create_client_ssl_context(
        directory: Path,
        server_cert_directory: Path,
        client_key_file_name: str = CLIENT_KEY_FILE_NAME,
        client_cert_file_name: str = CLIENT_CERT_FILE_NAME,
        server_cert_file_name: str = SERVER_CERT_FILE_NAME,
) -> Optional[ssl.SSLContext]:
    """ Helper function for creating a client SSL context.
        All client files must reside in the same directory """
    return create_ssl_context(
        directory / client_key_file_name,
        directory / client_cert_file_name,
        server_cert_directory / server_cert_file_name,
        ssl.Purpose.SERVER_AUTH
    )


def create_server_ssl_context(
        directory: Path,
        server_key_file_name: str = SERVER_KEY_FILE_NAME,
        server_cert_file_name: str = SERVER_CERT_FILE_NAME,
        client_cert_file_name: str = CLIENT_CERT_FILE_NAME,
) -> Optional[ssl.SSLContext]:
    """ Helper function for creating a server SSL context.
        All files must reside in the same directory """
    return create_ssl_context(
        directory / server_key_file_name,
        directory / server_cert_file_name,
        directory / client_cert_file_name,
        ssl.Purpose.CLIENT_AUTH
    )


def create_ssl_context(
        key_path: Path,
        cert_path: Path,
        verify_cert_path: Path,
        purpose: ssl.Purpose,
) -> Optional[ssl.SSLContext]:
    """ Create an SSL context with """

    locations_exist = (
        key_path.exists() and
        cert_path.exists() and
        verify_cert_path.exists()
    )

    if not locations_exist:
        return None

    try:
        context = ssl.create_default_context(purpose)
        context.load_cert_chain(str(cert_path), str(key_path))
        context.load_verify_locations(str(verify_cert_path))
        context.check_hostname = False
        return context
    except Exception as exc:
        print(f"Error creating SSL context: {exc}")
    return None
