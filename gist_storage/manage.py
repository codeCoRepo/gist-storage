import base64
import json
import logging
import os
from typing import Dict, Optional, Type

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
        gist_hash: str,
        filename: str,
        github_gist_token: Optional[str] = None,
        encryption_key: Optional[str] = None,
        disable_encryption: Optional[bool] = False,
    ) -> None:
        """
        Initializes GistManager with a specific GitHub gist and filename.

        This manager handles operations on a single file within a specified
        GitHub gist, such as fetching and updating its content. It requires
        a GitHub token for authentication, the hash of the gist, and the
        name (or path) of the file within the gist.

        :param str github_gist_token: The GitHub token used for
            authentication. If not provided, it will attempt to retrieve
            the token from the
            environment variable GITHUB_GIST_TOKEN.
        :param str gist_hash: The hash identifier of the GitHub gist.
        :param filename: The name file within the gist to manage.
        :param str encryption_key: The encryption key used for encrypting
            and decrypting the content. If not provided, encryption will be
            disabled.
        """
        if github_gist_token is None:
            github_gist_token = os.getenv('GITHUB_GIST_TOKEN')
        if github_gist_token is None:
            raise ValueError((
                'GitHub token is required, provide it as an argument ' +
                'or in .env file'
            ))
        self.disable_encryption = disable_encryption
        self.gist_handle = Github(github_gist_token).get_gist(gist_hash)
        self.filename = str(filename)
        self.encryption_key = encryption_key
        self.fernet: Optional[Fernet] = None
        if self.load_encryption_key():
            logging.info('Encryption enabled')

    def load_encryption_key(self) -> bool:
        """
        Load the encryption key if corresponding environment variables exists

        It initialize the Fernet object, used for symmetric encryption.

        Returns:
            bool: True if the encryption key is successfully loaded and
            initialized.

        Raises:
            ValueError: If the encryption key is not found in the environment
            variables.
            ValueError: If the encryption key is not in the correct
            format.
            ValueError: If the encryption key length is not 32 bytes
            after base64 decoding.
        """
        key = os.getenv('GIST_ENCRYPT_SECRET_KEY')
        if key and not self.disable_encryption:
            try:
                # Decode the key and check its length
                decoded_key = base64.urlsafe_b64decode(key)
            except (ValueError) as e:
                raise ValueError('Invalid encryption key format') from e
            fernet_key_length = 32
            if len(decoded_key) == fernet_key_length:
                self.fernet = Fernet(key)
                return True
            raise ValueError(
                'Encryption key must be 32 bytes long after base64 decoding.',
            )
        return False

    def encrypt(self, data: str) -> str:
        """
        Encrypts the given data using the Fernet symmetric encryption.

        :param str data: Data to be encrypted.
        :return: Encrypted data.
        :rtype: str
        """
        if self.fernet is None:
            raise ValueError('Encryption key is not provided')
        return self.fernet.encrypt(data.encode()).decode()

    def decrypt(self, data: str) -> str:
        """
        Decrypts the given data using the Fernet symmetric encryption.

        :param str data: Data to be decrypted.
        :return: Decrypted data.
        :rtype: str
        """
        if self.fernet is None:
            raise ValueError('Encryption key is not provided')
        return self.fernet.decrypt(data.encode()).decode()

    def fetch_content(self) -> str:
        """
        Retrieves the content of the file from the gist.

        :return: The content of the file.
        :rtype: str
        :raises KeyError: If the specified file is not found in the gist.
        """
        logging.info(f'Retrieving content from gist: {self.gist_handle.id}')
        try:
            file_content = self.gist_handle.files[self.filename].content
            if self.fernet:
                file_content = self.decrypt(file_content)
            return file_content
        except KeyError as e:
            logging.warning(f'File not found in gist: {e}')
            raise

    def push_content(self, content: str) -> bool:
        """
        Updates the specified file within the GitHub gist with new content.

        :param str content: The content to be written to the file.
        :return: True if the update is successful, False otherwise.
        :rtype: bool
        :raises ReadTimeout: If a timeout occurs while trying to update the
            gist.
        """
        logging.info(f'Pushing content to gist: {self.gist_handle.id}')
        try:
            if self.fernet:
                content = self.encrypt(content)
            self.gist_handle.edit(files={self.filename: InputFileContent(
                content=content,
            )})
            return True
        except ReadTimeout as e:
            logging.warning(f"Couldn't update status: {e}")
            return False

    def fetch_json(
        self,
        decoder: Optional[Type[json.JSONDecoder]] = None,
    ) -> Dict[str, str]:
        """
        Retrieves the content of the json file returns it as a dictionary.

        :return: A dictionary containing the data from the file.
        :rtype: Dict[str, str]
        :raises json.JSONDecodeError: If the file content is not valid JSON.
        """
        try:
            file_content = self.fetch_content()
            return json.loads(file_content, cls=decoder)
        except json.JSONDecodeError as e:
            logging.warning(f'Error decoding JSON from file: {e}')
            raise

    def push_json(
        self,
        data: Dict[str, str],
        encoder: Optional[Type[json.JSONEncoder]] = None,
    ) -> bool:
        """
        Updates the specified file within the GitHub gist with new data.

        :param Dict data: A dictionary containing the data to be written to the
            file.
        :return: True if the update is successful, False otherwise.
        :rtype: bool
        :raises ReadTimeout: If a timeout occurs while trying to update the
            gist.
        """
        try:
            file_content = json.dumps(data, indent=4, cls=encoder)
            self.push_content(file_content)
            return True
        except ReadTimeout as e:
            logging.warning(f"Couldn't update status: {e}")
            return False

    def update_json(self, update_data: Dict[str, str]) -> bool:
        """
        Updates the JSON data in the specified file of the GitHub gist with
        provided entries. If not present in the exisiting dict new keys are
        created.

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

