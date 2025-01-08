"""
Utils for handling file operations
"""

import json


def delete_exam_reminder(data_file: str, cert_code: str) -> bool:
    """
    Deletes an exam reminder entry from email/data.json.
    If the <cert_code> is not found a ValueError exception
    is caught forcing the function to return

    Args:
        data_file (str): exam reminders data file
        cert_code (str): certification code

    Returns:
        bool: False if failed otherwise True
    """
    with open(data_file, "r+", encoding="utf-8") as file:
        config = json.loads(file.read())
        # delete the entry
        try:
            del config[cert_code]
        except KeyError:
            return False
        # clear existing content
        file.seek(0)
        file.truncate()
        # write the data back
        file.write(json.dumps(config))
    return True


def create_exam_reminder(data_file: str, cert_code: str, cert_obj: dict) -> None:
    """
    Reads the current data from email/data.json and
    stores it before wiping the file and writing the
    original data back along with the new reminder
    data

    Args:
        data_file (str): exam reminders data file
        cert_code (str): certification code
        cert_obj (dict): exam reminder details
    """
    with open(data_file, "r+", encoding="utf-8") as file:
        config = json.loads(file.read())
        # clear existing content
        file.seek(0)
        file.truncate()
        # update the data
        config[cert_code] = cert_obj
        # write the data back
        file.write(json.dumps(config))
