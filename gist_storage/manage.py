import base64
import json
import logging
from pathlib import Path
from typing import Dict, Union

from cryptography.fernet import Fernet
from github import Github, InputFileContent
from requests.exceptions import ReadTimeout


class GistManager(object):
    """
    Initializes the GistManager with a specific GitHub gist and filename.

    This manager handles operations on a single file within a specified
    GitHub gist, such as fetching and updating its content. It requires a
    GitHub token for authentication, the hash of the gist, and the name (or
    path) of the file within the gist.
    """

    def __init__(
        self,
        github_token: str,
        gist_hash: str,
        filename: Union[str, Path],
        encryption_key: str = '',
    ):
        """
        Initializes the GistManager with a specific GitHub gist and filename.

        This manager handles operations on a single file within a specified
        GitHub gist, such as fetching and updating its content. It requires a
        GitHub token for authentication, the hash of the gist, and the name (or
        path) of the file within the gist.

        :param str github_token: The GitHub token used for authentication.
        :param str gist_hash: The hash identifier of the GitHub gist.
        :param Union[str, Path] filename: The name or path of the file within
            the gist to manage.
        """
        self.gist_handle = Github(github_token).get_gist(gist_hash)
        self.filename = str(filename)
        self.encryption_key = encryption_key
        if encryption_key:
            self.fernet = Fernet(base64.urlsafe_b64encode(
                encryption_key.encode(),
            ))

    def encrypt(self, data: str) -> str:
        """
        Encrypts the given data using the Fernet symmetric encryption.

        :param str data: Data to be encrypted.
        :return: Encrypted data.
        :rtype: str
        """
        return self.fernet.encrypt(data.encode()).decode()

    def decrypt(self, data: str) -> str:
        """
        Decrypts the given data using the Fernet symmetric encryption.

        :param str data: Data to be decrypted.
        :return: Decrypted data.
        :rtype: str
        """
        return self.fernet.decrypt(data.encode()).decode()

    def fetch_json(self) -> Dict[str, str]:
        """
        Retrieves the content of the json file returns it as a dictionary.

        :return: A dictionary containing the data from the file.
        :rtype: Dict[str, str]
        :raises KeyError: If the specified file is not found in the gist.
        :raises json.JSONDecodeError: If the file content is not valid JSON.
        """
        logging.info('Retrieving data from gist')
        try:
            file_content = self.gist_handle.files[self.filename].content
            if self.encryption_key:
                file_content = self.decrypt(file_content)
            return json.loads(file_content)
        except KeyError as e:
            logging.warning(f'File not found in gist: {e}')
            raise
        except json.JSONDecodeError as e:
            logging.warning(f'Error decoding JSON from file: {e}')
            raise

    def push_json(self, data: Dict[str, str]) -> bool:
        """
        Updates the specified file within the GitHub gist with new data.

        :param Dict data: A dictionary containing the data to be written to the
            file.
        :return: True if the update is successful, False otherwise.
        :rtype: bool
        :raises ReadTimeout: If a timeout occurs while trying to update the
            gist.
        """
        logging.info('Updating last seen alive')
        try:
            if self.encryption_key:
                data_public = self.encrypt(json.dumps(data))
            else:
                data_public = json.dumps(data, indent=4)
            self.gist_handle.edit(files={self.filename: InputFileContent(
                content=data_public,
            )})
            return True
        except ReadTimeout as e:
            logging.warning(f"Couldn't update status: {e}")
            return False

    def update_json(self, update_data: Dict[str, str]) -> bool:
        """
        Updates the JSON data in the specified file of the GitHub gist with
        provided entries.

        :param Dict update_data: A dictionary containing the data to be updated
            in the file.
        :return: True if the update is successful, False otherwise.
        :rtype: bool
        :raises Exception: If fetching or pushing data fails.
        """
        logging.info('Updating JSON data in gist')
        try:
            existing_data = self.fetch_json()

            # Check if the update is necessary
            if existing_data == update_data:
                logging.info('No update needed as the data is identical')
                return True

            existing_data.update(update_data)
            return self.push_json(existing_data)
        except Exception as e:
            logging.warning(f'Error updating JSON data: {e}')
            return False

