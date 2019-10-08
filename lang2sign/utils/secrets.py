"""
Utility to access secrets stored in files
or to input them on prompt
"""
# pylint: disable=unexpected-keyword-arg
import os
from getpass import getpass

class Secret(object):
    """
    Secret class to store and retrieve secret
    """

    def __init__(self, name, filepath):
        self.name = name
        self.filepath = filepath
        self.full_path = self.filepath

    def set_base_directory(self, directory):
        self.filepath = os.path.join(
            directory,
            self.filepath
        )

    def get(self):
        with open(self.full_path, "r") as file_obj:
            return file_obj.read()

    def set(self, value):
        os.makedirs(
            os.path.dirname(self.full_path),
            exist_ok=True
        )
        with open(self.full_path, "w") as file_obj:
            file_obj.write(value)

    def get_or_prompt(self):

        try:
            value = self.get()
        except IOError:
            value = getpass(
                ("{name} not found at {filepath}. Please type in.\n" + \
                "**Note this will write your input to {filepath}:\n").format(
                    name=self.name,
                    filepath=self.full_path
                )
            )

            self.set(value)

        return value

class SecretManager(object):
    """
    Stores and retrieves secrets from files
    """

    def __init__(self, secrets):
        self.secrets = {
            secret.name: secret for secret in secrets
        }

    def set_base_directory(self, directory):
        for secret in self.secrets.values():
            secret.set_base_directory(directory)

    def get(self, name):
        try:
            return self.secrets[name]
        except KeyError:
            raise KeyError(
                "No secret registered with name {}".format(name)
            )

manager = SecretManager([
    Secret("aws_access_key_id", "secrets/aws_access_key_id"),
    Secret("aws_secret_access_key", "secrets/aws_secret_access_key")
])
