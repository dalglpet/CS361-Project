# Password Generator - A terminal application for generating secure, random passwords with custom settings.
# Includes:
# - Login microservice
# - Export microservice
# - Session token microservice
# - Data backup microservice
# - Searching microservice

import json
import os
import random
import string
import requests


# attempt_login: Sends username/password to the login microservice and returns the status string.
# Prerequisites: login microservice is running on LOGIN_xURL.
# Arguments: username (str), password (str).
# Returns: str, one of "ok", "locked", "invalid_format", "invalid_credentials", or "service_error".
def attempt_login(username, password):
    LOGIN_URL = "http://127.0.0.1:5000/login"

    # Build the JSON payload exactly how the microservice expects it.
    payload = {"username": username, "password": password}

    # Try to send the POST request to the microservice.
    # If the service is not running, this will throw an exception.
    try:
        resp = requests.post(LOGIN_URL, json=payload, timeout=3)
    except:
        return "service_error"

    # Try to parse JSON response.
    # If it is not JSON for some reason, treat it as a service error.
    try:
        data = resp.json()
    except:
        return "service_error"

    # Return the status field from the microservice response.
    return data.get("status", "service_error")


# attempt_create_account: Sends username/password to the login microservice's create-account endpoint.
# Prerequisites: login microservice is running on localhost:5001.
# Arguments: username (str), password (str).
# Returns: str, one of "created", "user_exists", "invalid_format", or "service_error".
def attempt_create_account(username, password):
    CREATE_URL = "http://127.0.0.1:5000/create-account"
    payload = {"username": username, "password": password}
    try:
        resp = requests.post(CREATE_URL, json=payload, timeout=3)
    except:
        return "service_error"
    try:
        data = resp.json()
    except:
        return "service_error"
    return data.get("status", "service_error")


# create_session_token: Asks the session token microservice to issue a new token after a successful login.
# Prerequisites: session token microservice is running on SESSION_URL.
# Arguments: None.
# Returns: str token on success, or None if the service cannot be reached.
def create_session_token():
    SESSION_URL = "http://127.0.0.1:5003/create"

    # Try to send the POST request to the session token microservice.
    # If the service is not running, this will throw an exception.
    try:
        resp = requests.post(SESSION_URL, timeout=3)
    except:
        return None

    # Try to parse JSON response.
    # If it is not JSON for some reason, treat it as a service error.
    try:
        data = resp.json()
    except:
        return None

    # If the microservice returned status "ok", pull the token string out of the response.
    # Otherwise return None so the caller knows it did not work.
    if data.get("status") == "ok":
        return data.get("token")
    return None


# validate_session_token: Sends a token to the session token microservice and returns whether it is still valid.
# Prerequisites: session token microservice is running on SESSION_URL.
# Arguments: token (str).
# Returns: str, one of "ok", "expired", "invalid", or "service_error".
def validate_session_token(token):
    SESSION_URL = "http://127.0.0.1:5003/validate"

    # Build the JSON payload exactly how the microservice expects it.
    payload = {"token": token}

    # Try to send the POST request to the session token microservice.
    # If the service is not running, this will throw an exception.
    try:
        resp = requests.post(SESSION_URL, json=payload, timeout=3)
    except:
        return "service_error"

    # Try to parse JSON response.
    # If it is not JSON for some reason, treat it as a service error.
    try:
        data = resp.json()
    except:
        return "service_error"

    # Return the status field from the microservice response.
    return data.get("status", "service_error")


# run_login_screen: Prompts the user to log in until success or they quit.
# Prerequisites: None.
# Arguments: None.
# Returns: bool, True if user logged in; False if user chose to quit.
def run_login_screen():
    while True:
        print()
        print("Login Required")
        print("1) Log in")
        print("2) Create account")
        print("3) Quit")
        choice = input("\nEnter choice: ").strip()

        if choice == "3":
            return False

        if choice == "2":
            print()
            print("Create Account")
            username = input("Username: ").strip()
            if username == "":
                continue
            password = input("Password: ").strip()
            status = attempt_create_account(username, password)
            if status == "created":
                print("\nAccount created. You can now log in.\n")
            elif status == "user_exists":
                print("\nUsername already taken.\n")
            elif status == "invalid_format":
                print("\nInvalid input format. Username must be 3-32 chars, password 1-72 chars.\n")
            else:
                print("\nLogin service error. Make sure the login microservice is running.\n")
            continue

        if choice != "1":
            continue

        print()
        username = input("Username: ").strip()
        if username == "":
            continue
        password = input("Password: ").strip()

        status = attempt_login(username, password)

        if status == "ok":
            print("\nLogin successful.\n")
            return True
        elif status == "locked":
            print("\nAccount locked. Wait a bit and try again.\n")
        elif status == "invalid_credentials":
            print("\nInvalid username or password.\n")
        elif status == "invalid_format":
            print("\nInvalid input format.\n")
        else:
            print("\nLogin service error. Make sure the login microservice is running.\n")


# save_generated_password: Saves a generated password and its settings in a list for exporting later.
# Prerequisites: saved_passwords is a list.
# Arguments: saved_passwords (list of dict), password (str), length (int),
#            use_lower/use_upper/use_digit/use_symbol (bool).
# Returns: None.
def save_generated_password(saved_passwords, password, length, use_lower, use_upper, use_digit, use_symbol):
    # Store one record as a dictionary with password first for readability.
    record = {}
    record["password"] = password
    record["length"] = length
    record["lowercase"] = use_lower
    record["uppercase"] = use_upper
    record["numbers"] = use_digit
    record["symbols"] = use_symbol
    saved_passwords.append(record)


# export_saved_passwords: Sends saved records to the export microservice and returns its response.
# Prerequisites: export microservice is running on EXPORT_URL.
# Arguments: saved_passwords (list of dict), filename (str).
# Returns: dict response JSON on success, or None if the service cannot be reached.
def export_saved_passwords(saved_passwords, filename):
    EXPORT_URL = "http://127.0.0.1:5002/export"

    # Build the JSON payload exactly how the export microservice expects it.
    payload = {"filename": filename, "data": saved_passwords}

    # Try to send the POST request to the export microservice.
    # If the service is not running, this will throw an exception.
    try:
        resp = requests.post(EXPORT_URL, json=payload, timeout=5)
    except:
        return None

    # Try to parse JSON response.
    # If it is not JSON for some reason, treat it as a service error.
    try:
        return resp.json()
    except:
        return None


# create_password_backup: Sends saved passwords to the data backup microservice to create a backup.
# Prerequisites: data backup microservice is running on BACKUP_URL.
# Arguments: saved_passwords (list of dict), user_id (str), list_name (str).
# Returns: dict response JSON on success, or None if the service cannot be reached.
def create_password_backup(saved_passwords, user_id, list_name):
    BACKUP_URL = "http://127.0.0.1:8080/backup/create"

    # Build the JSON payload exactly how the backup microservice expects it.
    # Wrap the passwords with the list name so the backup file shows which list this is.
    headers = {"Content-Type": "application/json", "X-API-Key": "dev-secret-key"}
    backup_data = {
        "list_name": list_name,
        "passwords": saved_passwords
    }
    payload = {
        "user_id": user_id,
        "source_app": "PasswordGenerator",
        "data": backup_data
    }

    # Try to send the POST request to the backup microservice.
    # If the service is not running, this will throw an exception.
    try:
        resp = requests.post(BACKUP_URL, headers=headers, json=payload, timeout=5)
    except:
        return None

    # Try to parse JSON response.
    # If it is not JSON for some reason, treat it as a service error.
    try:
        return resp.json()
    except:
        return None


# restore_password_backup: Restores a specific backup by ID from the data backup microservice.
# Prerequisites: data backup microservice is running on BACKUP_URL.
# Arguments: user_id (str), backup_id (str).
# Returns: dict response JSON on success, or None if the service cannot be reached.
def restore_password_backup(user_id, backup_id):
    BACKUP_URL = "http://127.0.0.1:8080/backup/restore"

    # Build the JSON payload exactly how the backup microservice expects it.
    headers = {"Content-Type": "application/json", "X-API-Key": "dev-secret-key"}
    payload = {
        "user_id": user_id,
        "backup_id": backup_id
    }

    # Try to send the POST request to the backup microservice.
    # If the service is not running, this will throw an exception.
    try:
        resp = requests.post(BACKUP_URL, headers=headers, json=payload, timeout=5)
    except:
        return None

    # Try to parse JSON response.
    # If it is not JSON for some reason, treat it as a service error.
    try:
        return resp.json()
    except:
        return None


# INDEX_FILE_PATH is the full path to the local JSON file that maps list names to backup IDs.
# It is stored next to this script so it persists across sessions.
INDEX_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "password_lists_index.json")


# save_backup_index: Saves a list name and its backup ID to the local index file.
# Prerequisites: None.
# Arguments: list_name (str), backup_id (str).
# Returns: None.
def save_backup_index(list_name, backup_id):
    # Try to load the existing index from the JSON file.
    # If the file does not exist or is not valid JSON, start with an empty dict.
    index = {}
    try:
        file = open(INDEX_FILE_PATH, "r")
        index = json.load(file)
        file.close()
    except:
        index = {}

    # Add or update the entry for this list name.
    index[list_name] = backup_id

    # Write the updated index back to the file.
    file = open(INDEX_FILE_PATH, "w")
    file.write(json.dumps(index, indent=2))
    file.close()


# search_for_list: Uses the searching microservice to look up a list name in the local index file.
# Prerequisites: searching microservice is running on SEARCH_URL.
# Arguments: list_name (str).
# Returns: dict response JSON on success (e.g. {"MyList": "backup-id-here"}), or None if the service
#          cannot be reached or the index file does not exist.
def search_for_list(list_name):
    SEARCH_URL = "http://127.0.0.1:8001/search"

    # Build the JSON payload for a file lookup search.
    # The searching microservice will open the index file and look up the list name as a JSON key.
    payload = {
        "data_source": INDEX_FILE_PATH,
        "query": list_name,
        "file_lookup": True,
        "strict": False
    }

    # Try to send the POST request to the searching microservice.
    # If the service is not running, this will throw an exception.
    try:
        resp = requests.post(SEARCH_URL, json=payload, timeout=5)
    except:
        return None

    # Try to parse JSON response.
    # If it is not JSON for some reason, treat it as a service error.
    try:
        return resp.json()
    except:
        return None


# run_export_screen: Prompts the user for a filename and exports saved passwords using the microservice.
# Prerequisites: saved_passwords is a list.
# Arguments: saved_passwords (list of dict).
# Returns: None.
def run_export_screen(saved_passwords):
    print()
    print("Export Saved Passwords")

    # If there is nothing saved, do not call the microservice.
    if len(saved_passwords) == 0:
        print("There are no saved passwords to export yet.")
        input("\nPress Enter to return to menu: ")
        return

    # Ask the user what to name the CSV file.
    # Pressing Enter uses a default name.
    filename = input("Enter filename (example: passwords.csv) or press Enter for default: ").strip()
    if filename == "":
        filename = "passwords.csv"

    # Call the export microservice.
    result = export_saved_passwords(saved_passwords, filename)

    # If the service could not be reached, show an error.
    if result is None:
        print("\nExport service error. Make sure the export microservice is running.\n")
        input("Press Enter to return to menu: ")
        return

    # If status is ok, show where the file was saved.
    if result.get("status") == "ok":
        print("\nExport complete.")
        print("Saved file path:", result.get("path"))
    else:
        # Otherwise show the error message from the microservice.
        print("\nExport failed:", result.get("error_message", "Unknown error."))

    input("\nPress Enter to return to menu: ")


# run_name_list_screen: Prompts the user to name a new password list and returns the name.
# Prerequisites: all_lists is a dict of existing lists (used to check for duplicate names).
# Arguments: all_lists (dict).
# Returns: str, the list name the user chose.
def run_name_list_screen(all_lists):
    # Loop until the user provides a valid, non-empty, non-duplicate name.
    while True:
        print()
        print("Name Your Password List")
        print("Each list has a unique name so you can manage and back up lists separately.")
        print("Example names: WorkPasswords, PersonalAccounts, SchoolLogins")
        name = input("\nEnter a name for your new list: ").strip()

        # Empty names are not allowed.
        if name == "":
            print("\nList name cannot be empty. Please try again.")
            continue

        # Check if this name is already in use in the current session.
        if name in all_lists:
            print("\nA list named '" + name + "' already exists in this session. Please choose a different name.")
            continue

        return name


# run_password_lists_screen: Shows the Password Lists submenu and lets the user view, create/switch, backup/export, or restore lists.
# Prerequisites: all_lists is a dict mapping list names to lists of password dicts; current_list_name is the active list; user_id is a string.
# Arguments: all_lists (dict), current_list_name (str), user_id (str), length (int or None),
#            types_set (bool), use_lower, use_upper, use_digit, use_symbol (bool).
# Returns: tuple (current_list_name, length, types_set, use_lower, use_upper, use_digit, use_symbol).
def run_password_lists_screen(all_lists, current_list_name, user_id, length, types_set, use_lower, use_upper, use_digit, use_symbol):
    # Loop until "Return to menu" (5) is chosen.
    # Options 1-4 perform an action and the menu is shown again.
    while True:
        print()
        print("Password Lists")
        if current_list_name == "" or current_list_name not in all_lists:
            print("Current list: [none]")
        else:
            current_passwords = all_lists[current_list_name]
            print("Current list: [" + current_list_name + "] (" + str(len(current_passwords)) + " passwords)")
        print("\n1) View passwords in current list")
        print("2) Create or switch list")
        print("3) Backup or export current list")
        print("4) Find & restore a list")
        print("5) Return to menu")
        choice = input("\nEnter choice: ").strip()

        # Choice 1: display every password saved in the current list.
        if choice == "1":
            print()
            if current_list_name == "" or current_list_name not in all_lists:
                print("You have no active list. Use 'Generate passwords' from the main menu to create one first.")
                input("\nPress Enter to continue: ")
                continue
            current_passwords = all_lists[current_list_name]
            if len(current_passwords) == 0:
                print("Your list '" + current_list_name + "' has no passwords yet.")
                print("Use 'Generate passwords' from the main menu to add some.")
                input("\nPress Enter to continue: ")
                continue
            print("All passwords in '" + current_list_name + "' (" + str(len(current_passwords)) + " total):\n")
            for i in range(len(current_passwords)):
                record = current_passwords[i]
                print("  " + str(i + 1) + ") " + record["password"])
            input("\nPress Enter to continue: ")

        # Choice 2: create a new list or switch to an existing one.
        elif choice == "2":
            print()
            print("Create or Switch List")

            # Get all list names as a simple list so we can show them numbered.
            list_names = []
            for name in all_lists:
                list_names.append(name)

            # Show existing lists if there are any.
            if len(list_names) > 0:
                print("Your lists:\n")
                for i in range(len(list_names)):
                    name = list_names[i]
                    count = len(all_lists[name])
                    marker = ""
                    if name == current_list_name:
                        marker = " (current)"
                    print("  " + str(i + 1) + ") " + name + " (" + str(count) + " passwords)" + marker)
                print()

            print("Enter a number to switch, or type 'new' to create a new list.")
            raw = input("Choice (or press Enter to cancel): ").strip()

            if raw == "":
                continue

            if raw.lower() == "new":
                new_name = run_name_list_screen(all_lists)
                all_lists[new_name] = []
                current_list_name = new_name
                length = None
                types_set = False
                use_lower = True
                use_upper = True
                use_digit = True
                use_symbol = True
                print("\nCreated new list '" + new_name + "' and switched to it.")
                print("You'll set password settings when you generate passwords for this list.")
                input("\nPress Enter to continue: ")
                continue

            # Validate the input is a number within range.
            is_number = True
            for c in raw:
                if c not in "0123456789":
                    is_number = False
                    break
            if not is_number:
                continue

            pick = int(raw)
            if pick < 1 or pick > len(list_names):
                continue

            current_list_name = list_names[pick - 1]
            switched_passwords = all_lists[current_list_name]
            if len(switched_passwords) > 0:
                first = switched_passwords[0]
                length = first.get("length", length)
                use_lower = first.get("lowercase", use_lower)
                use_upper = first.get("uppercase", use_upper)
                use_digit = first.get("numbers", use_digit)
                use_symbol = first.get("symbols", use_symbol)
                types_set = True
            else:
                length = None
                types_set = False
                use_lower = True
                use_upper = True
                use_digit = True
                use_symbol = True
            print("\nSwitched to list '" + current_list_name + "'.")
            input("\nPress Enter to continue: ")

        # Choice 3: backup to the cloud or export to CSV.
        elif choice == "3":
            print()
            if current_list_name == "" or current_list_name not in all_lists:
                print("You have no active list. Use 'Generate passwords' from the main menu to create one first.")
                input("\nPress Enter to continue: ")
                continue
            current_passwords = all_lists[current_list_name]
            if len(current_passwords) == 0:
                print("Your list '" + current_list_name + "' has no passwords yet.")
                print("Generate some passwords first, then come back here.")
                input("\nPress Enter to continue: ")
                continue

            print("Save list '" + current_list_name + "' (" + str(len(current_passwords)) + " passwords)")
            print("\n1) Backup to cloud (can be restored later by name)")
            print("2) Export to CSV file")
            print("3) Cancel")
            save_choice = input("\nEnter choice: ").strip()

            if save_choice == "1":
                print("\nBacking up list '" + current_list_name + "'...")
                result = create_password_backup(current_passwords, user_id, current_list_name)

                if result is None:
                    print("\nBackup service error. Make sure the data backup microservice is running.")
                    input("\nPress Enter to continue: ")
                    continue

                if result.get("status") == "success":
                    backup_info = result.get("backup", {})
                    backup_id = backup_info.get("backup_id", "")
                    save_backup_index(current_list_name, backup_id)
                    print("\nBackup created successfully!")
                    print("List name: " + current_list_name)
                    print("Backup ID: " + backup_id)
                    print("\nYou can restore this list later by searching for '" + current_list_name + "'.")
                else:
                    print("\nBackup failed: " + result.get("error", "Unknown error."))

                input("\nPress Enter to continue: ")

            elif save_choice == "2":
                run_export_screen(current_passwords)

        # Choice 4: find a previously backed-up list by name using the search microservice, then restore it.
        elif choice == "4":
            print()
            print("Find & Restore a List")
            print("Type the exact name of a password list that was previously backed up.")
            list_name = input("\nEnter list name (or press Enter to cancel): ").strip()

            if list_name == "":
                continue

            # Check if the index file exists before trying to search.
            if not os.path.exists(INDEX_FILE_PATH):
                print("\nNo backup found with the name '" + list_name + "'.")
                input("\nPress Enter to continue: ")
                continue

            # Use the search microservice to look up the backup ID for this list name.
            print("\nSearching for '" + list_name + "'...")
            result = search_for_list(list_name)

            if result is None:
                print("\nSearch service error. Make sure the searching microservice is running.")
                input("\nPress Enter to continue: ")
                continue

            # The search microservice returns {list_name: backup_id} on success, or {list_name: null} if not found.
            backup_id = result.get(list_name)

            if backup_id is None:
                print("\nNo backup found with the name '" + list_name + "'.")
                input("\nPress Enter to continue: ")
                continue

            print("Found it! Restoring list '" + list_name + "'...")
            restore_result = restore_password_backup(user_id, backup_id)

            if restore_result is None:
                print("\nBackup service error. Make sure the data backup microservice is running.")
                input("\nPress Enter to continue: ")
                continue

            if restore_result.get("status") == "success":
                restored_data = restore_result.get("data", {})
                # The backup data is wrapped in a dict with "list_name" and "passwords" keys.
                # Pull the passwords list out of the wrapper.
                if "passwords" in restored_data:
                    password_list = restored_data["passwords"]
                else:
                    password_list = restored_data
                all_lists[list_name] = password_list
                current_list_name = list_name

                # Restore the settings from the first password record so the user
                # can keep generating with the same settings that were backed up.
                if len(password_list) > 0:
                    first = password_list[0]
                    length = first.get("length", length)
                    use_lower = first.get("lowercase", use_lower)
                    use_upper = first.get("uppercase", use_upper)
                    use_digit = first.get("numbers", use_digit)
                    use_symbol = first.get("symbols", use_symbol)
                    types_set = True

                print("\nRestore successful! Loaded " + str(len(password_list)) + " password(s) into list '" + list_name + "'.")
                print("Backup ID: " + backup_id)
                if length is not None:
                    print("Settings restored: length=" + str(length) + ", lowercase=" + str(use_lower) + ", uppercase=" + str(use_upper) + ", numbers=" + str(use_digit) + ", symbols=" + str(use_symbol))
                print("Switched to list '" + list_name + "'.")
            else:
                print("\nRestore failed: " + restore_result.get("error", "Unknown error."))

            input("\nPress Enter to continue: ")

        # Choice 5: return to the main menu.
        elif choice == "5":
            return current_list_name, length, types_set, use_lower, use_upper, use_digit, use_symbol


# show_welcome: Displays the welcome message and waits for the user to press Enter before continuing.
# Prerequisites: None.
# Arguments: None.
# Returns: None.
def show_welcome():
    print("\nPASSWORD GENERATOR\n")
    print("Welcome to the PASSWORD GENERATOR application by Peter Dalgleish!")
    print("This application is for generating secure, random passwords to protect any online account.")
    input("\nPress enter to continue: ")


# format_settings_line: Builds the status line shown at the top of most screens.
# Prerequisites: length is either None (not set) or an integer; types_set is a boolean;
#                current_list_name is a string; all_lists is a dict.
# Arguments: length (int or None), types_set (bool), current_list_name (str), all_lists (dict).
# Returns: str, the formatted line.
def format_settings_line(length, types_set, current_list_name="", all_lists=None):
    # Build the current list part of the status line.
    if current_list_name != "" and all_lists is not None:
        count = len(all_lists[current_list_name])
        list_str = "Current list: [" + current_list_name + "] (" + str(count) + " passwords)"
    else:
        list_str = ""
    # Build the length part of the status line.
    # Use "[not set]" when length is None, otherwise the number in brackets.
    if length is None:
        length_str = "[not set]"
    else:
        length_str = "[" + str(length) + "]"
    # Build the types part: "[set]" after the character types screen has been saved,
    # "[not set]" until then.
    if types_set:
        types_str = "[set]"
    else:
        types_str = "[not set]"
    line = ""
    if list_str != "":
        line = list_str + " | "
    line = line + "Length = " + length_str + " | Types = " + types_str
    line = line + "\n" + "MUST SET LENGTH AND CHARACTER TYPES FIRST!" + "\n"
    return line


# run_main_menu: Shows the main menu and returns the user's choice.
# Prerequisites: None.
# Arguments: None.
# Returns: str, one of "1", "2", "3", "4".
def run_main_menu():
    print()
    print("Menu")
    print("1) Generate passwords")
    print("2) Password lists")
    print("3) I need help!")
    print("4) Exit program")
    choice = input("\nEnter choice: ").strip()
    return choice


# run_settings: Runs the settings submenu until the user returns to menu or exits.
# Prerequisites: length and types_set are current; use_* are the four character-type flags.
# Arguments: length, types_set, use_lower, use_upper, use_digit, use_symbol (all as used in state).
# Returns: tuple (length, types_set, use_lower, use_upper, use_digit, use_symbol) with any updates.
def run_settings(length, types_set, use_lower, use_upper, use_digit, use_symbol):
    # Loop until "Return to menu" (3) or "Exit" (4) is chosen.
    while True:
        print()
        print(format_settings_line(length, types_set))
        print("1) Set length")
        print("2) Choose character types")
        print("3) Return to menu")
        print("4) Exit program")
        choice = input("\nEnter choice: ").strip()

        # Choice 1: do_set_length runs and length is replaced
        # Choice 2: do_character_types runs and types_set becomes True.
        # Choice 3: return all current values to main. Choice 4: quit the program.
        if choice == "1":
            length = do_set_length(length)
        elif choice == "2":
            use_lower, use_upper, use_digit, use_symbol = do_character_types(
                use_lower, use_upper, use_digit, use_symbol
            )
            types_set = True
        elif choice == "3":
            return length, types_set, use_lower, use_upper, use_digit, use_symbol
        elif choice == "4":
            exit_program()


# do_set_length: Prompts for password length between 5 and 100; shows a warning and asks for confirmation when the length is short.
# Prerequisites: None.
# Arguments: current_length (int or None) to show as "Current length".
# Returns: int, the new length (or current_length if the user backs out).
def do_set_length(current_length):
    min_length = 5
    max_length = 100
    weak_threshold = 10
    print()
    print("Set Length")
    print("Note: Longer passwords are stronger, but can be harder to type.")
    print("Set password length (5-100)")
    # current_display is the text next to "Current length:".
    # "[not set]" when nothing is set yet, otherwise the numeric value.
    if current_length is None:
        current_display = "[not set]"
    else:
        current_display = str(current_length)
    print("Current length: " + current_display)
    raw = input("\nEnter length: ").strip()

    # Empty input is treated as cancel: length is not changed.
    # Wait for Enter, then return current_length so the caller keeps the same value.
    if raw == "":
        input("\nPress Enter to return to settings...")
        return current_length

    # Loop over each character in raw; if any is not a digit 0-9, set is_number to False.
    # Only strings made entirely of digits are accepted (no minus sign, no letters).
    is_number = True
    for c in raw:
        if c not in "0123456789":
            is_number = False
            break
    # Invalid input: not a number. Do not update length.
    # Wait for Enter and return current_length so nothing changes.
    if not is_number:
        input("\nPress Enter to return to settings...")
        return current_length

    n = int(raw)
    # The number must be between min_length (5) and max_length (100).
    # Outside that range: reject and return current_length unchanged.
    if n < min_length or n > max_length:
        input("\nPress Enter to return to settings...")
        return current_length

    # Lengths below weak_threshold (10) are considered weak.
    # Print a warning and ask "Continue with n? (y/n)"; y is required to accept.
    if n < weak_threshold:
        print()
        print("\nNote: Length " + str(n) + " is a relatively weak password. Recommendation: Use 10+ characters unless a site requires a shorter password.")
        confirm = input("Continue with " + str(n) + "? (y/n): ").strip().lower()
        # Anything other than "y" means decline: do not update length, return current_length.
        if confirm != "y":
            input("\nPress Enter to return to settings...")
            return current_length

    return n


# do_character_types: Lets the user toggle lowercase, uppercase, numbers, and symbols on or off; returns the four flags when the user chooses "Save and return to settings".
# Prerequisites: None.
# Arguments: use_lower, use_upper, use_digit, use_symbol (bool).
# Returns: tuple (use_lower, use_upper, use_digit, use_symbol) after the user saves.
def do_character_types(use_lower, use_upper, use_digit, use_symbol):
    # Loop until option 5 (Save and return) is picked.
    # Options 1-4 flip one of the four flags and the menu is shown again.
    while True:
        print()
        print("Set Character Types")
        print("Note: Some sites reject certain symbols, but adding them can significantly increase password strength.")
        print("Choose which character types to include:\n")
        # Each type is shown as [ON] or [OFF]. Set the label from the current flag
        # (e.g. lower_label is "ON" when use_lower is True).
        if use_lower:
            lower_label = "ON"
        else:
            lower_label = "OFF"
        if use_upper:
            upper_label = "ON"
        else:
            upper_label = "OFF"
        if use_digit:
            digit_label = "ON"
        else:
            digit_label = "OFF"
        if use_symbol:
            symbol_label = "ON"
        else:
            symbol_label = "OFF"
        print("Lowercase letters (a-z): [" + lower_label + "]")
        print("Uppercase letters (A-Z): [" + upper_label + "]")
        print("Numbers (0-9): [" + digit_label + "]")
        print("Symbols (!@#$...): [" + symbol_label + "]")
        print("\n1) Toggle lowercase")
        print("2) Toggle uppercase")
        print("3) Toggle numbers")
        print("4) Toggle symbols")
        print("5) Save and return to settings")
        choice = input("\nEnter choice: ").strip()

        # Options 1-4 flip one flag (e.g. choice 1 flips use_lower).
        # Option 5 returns the four flags to the caller and exits the loop.
        if choice == "1":
            use_lower = not use_lower
        elif choice == "2":
            use_upper = not use_upper
        elif choice == "3":
            use_digit = not use_digit
        elif choice == "4":
            use_symbol = not use_symbol
        elif choice == "5":
            return use_lower, use_upper, use_digit, use_symbol


# generate_password: Builds one random password of the given length using the selected character sets.
# Prerequisites: length >= 1; at least one of use_lower, use_upper, use_digit, use_symbol is True.
# Arguments: length (int), use_lower, use_upper, use_digit, use_symbol (bool).
# Returns: str, the generated password.
def generate_password(length, use_lower, use_upper, use_digit, use_symbol):
    # Start with an empty list and add the character set for each type that is on
    # (e.g. use_lower adds a-z). The pool holds every character allowed in the password.
    pool = []
    if use_lower:
        pool.extend(string.ascii_lowercase)
    if use_upper:
        pool.extend(string.ascii_uppercase)
    if use_digit:
        pool.extend(string.digits)
    if use_symbol:
        pool.extend("!@#$%^&*()_+-=[]{}|;:',.<>?/`~")

    # random.choices(pool, k=length) picks length characters from pool (with replacement).
    # Join into a single string and return it.
    return "".join(random.choices(pool, k=length))


# run_generate_flow: Walks the user through naming a list (first time), setting length and character types
#                    (first time), and then generating passwords. Includes an Edit settings option.
# Prerequisites: all_lists is a dict; the other arguments are the current state from main().
# Arguments: all_lists (dict), current_list_name (str), length (int or None), types_set (bool),
#            use_lower, use_upper, use_digit, use_symbol (bool).
# Returns: tuple (current_list_name, length, types_set, use_lower, use_upper, use_digit, use_symbol).
def run_generate_flow(all_lists, current_list_name, length, types_set, use_lower, use_upper, use_digit, use_symbol):
    # Step 1: if no active list exists yet, force the user to name one.
    if current_list_name == "":
        print()
        print("Before generating passwords, you need to name a password list.")
        print("All generated passwords will be saved into this list.")
        current_list_name = run_name_list_screen(all_lists)
        all_lists[current_list_name] = []
        print("\nList '" + current_list_name + "' created!")

    # Step 2: if length has not been set yet, force the user to set it.
    # Loop until do_set_length returns an actual number (not None).
    if length is None:
        print()
        print("Next, set the password length. You must set this before generating.")
        while length is None:
            length = do_set_length(length)
            if length is None:
                print("\nYou must set a length before generating passwords. Please try again.")

    # Step 3: if character types have not been set yet, force the user to choose them.
    if not types_set:
        print()
        print("Now, choose which character types to include in your passwords.")
        use_lower, use_upper, use_digit, use_symbol = do_character_types(
            use_lower, use_upper, use_digit, use_symbol
        )
        types_set = True

    # Step 4: generate passwords in a loop until the user returns to menu.
    while True:
        print()
        print(format_settings_line(length, types_set, current_list_name, all_lists))
        print("Generated password:")
        pwd = generate_password(length, use_lower, use_upper, use_digit, use_symbol)
        print(pwd)

        # Save this password to the current list.
        save_generated_password(all_lists[current_list_name], pwd, length, use_lower, use_upper, use_digit, use_symbol)

        print("1) Generate new password")
        print("2) Edit settings")
        print("3) Return to menu")
        choice = input("\nEnter choice: ").strip()

        # Choice 1: loop again and show another password.
        # Choice 2: open the settings submenu, then come back to generating.
        # Choice 3: return all updated state to main().
        if choice == "1":
            continue
        elif choice == "2":
            length, types_set, use_lower, use_upper, use_digit, use_symbol = run_settings(
                length, types_set, use_lower, use_upper, use_digit, use_symbol
            )
        elif choice == "3":
            return current_list_name, length, types_set, use_lower, use_upper, use_digit, use_symbol


# run_help_menu: Displays the help menu and runs the selected item (quickstart, length help, character types help) or return to menu or exit.
# Prerequisites: None.
# Arguments: session_token (str).
# Returns: str or None. Returns "session_expired" if the session expired while in the help menu; None on normal return.
def run_help_menu(session_token):
    # Loop until 4 (return to main menu) or 5 (exit) is chosen.
    # After viewing a help screen, this menu is shown again.
    while True:
        # Validate session at the start of each help menu iteration so the user is logged out if expired.
        token_status = validate_session_token(session_token)
        if token_status == "expired":
            return "session_expired"
        if token_status != "ok":
            print("\nSession token service error. Make sure the session token microservice is running.\n")
            exit_program()

        print()
        print("Help Menu")
        print("1) Quickstart guide")
        print("2) Password length help")
        print("3) Character types help")
        print("4) Return to menu")
        print("5) Exit program")
        choice = input("\nEnter choice: ").strip()

        # Choice 1-3: call the corresponding help function (shows text, waits for Enter),
        # then loop and show this menu again. Choice 4: return to main. Choice 5: exit.
        if choice == "1":
            show_quickstart_help()
        elif choice == "2":
            show_length_help()
        elif choice == "3":
            show_character_types_help()
        elif choice == "4":
            return
        elif choice == "5":
            exit_program()


# show_quickstart_help: Displays the quickstart guide (three steps) and waits for Enter to go back.
# Prerequisites: None.
# Arguments: None.
# Returns: None.
def show_quickstart_help():
    print()
    print("Quickstart Guide")
    print("To use this program efficiently, follow these steps in order:")
    print("Step 1/3: Set length")
    print("Step 2/3: Choose character types")
    print("Step 3/3: Generate password")
    input("\nPress Enter to go back: ")


# show_length_help: Displays help for password length (recommended range, allowed range) and waits for Enter to go back.
# Prerequisites: None.
# Arguments: None.
# Returns: None.
def show_length_help():
    print()
    print("Help for Password Length")
    print("When entering the password length, consider:")
    print("Longer passwords are harder to guess.")
    print("Recommended length: 12-20 characters.")
    print("Allowed range in this program: 5-100.")
    input("\nPress Enter to go back: ")


# show_character_types_help: Displays help for character types and waits for Enter to go back.
# Prerequisites: None.
# Arguments: None.
# Returns: None.
def show_character_types_help():
    print()
    print("Help for Password Character Types")
    print("Using more character types usually makes passwords stronger.")
    print("If a site does not allow symbols, toggle symbols OFF.")
    print("You must select at least one type of character to generate a new password.")
    input("\nPress Enter to go back: ")


# exit_program: Exits the application immediately.
# Prerequisites: None.
# Arguments: None.
# Does not return.
def exit_program():
    raise SystemExit(0)


# main: Entry point; shows the welcome once, then runs the main menu loop (generate, lists, help, exit).
# Keeps track of all_lists (dict of named password lists), current_list_name, length, types_set,
# the four character-type flags, and the session token.
# Prerequisites: None.
# Arguments: None.
# Returns: None (runs until exit).
def main():
    show_welcome()

    # Require login before using the app.
    # If the user quits at login, exit the program.
    logged_in = run_login_screen()
    if not logged_in:
        exit_program()

    # After a successful login, request a session token from the session token microservice.
    # The token will be validated before every menu action so the session cannot last forever.
    session_token = create_session_token()
    if session_token is None:
        print("\nSession token service error. Make sure the session token microservice is running.\n")
        exit_program()

    # user_id identifies this user for the data backup microservice.
    user_id = "password-generator-user"

    # all_lists maps each list name to its list of password dicts.
    # current_list_name starts empty; the user will be prompted to name a list
    # the first time they choose "Generate passwords".
    all_lists = {}
    current_list_name = ""

    # length is None and types_set is False until the user goes through the generate flow.
    # The four flags default to lower/upper/digits on and symbols off.
    length = None
    types_set = False
    use_lower = True
    use_upper = True
    use_digit = True
    use_symbol = True

    # Show the main menu, get the choice, then branch.
    # The loop runs until option 4 is chosen and exit_program() is called.
    while True:
        choice = run_main_menu()

        # Before doing anything, validate the session token.
        # If it has expired or is invalid, force the user to log in again.
        token_status = validate_session_token(session_token)

        if token_status == "expired":
            print("\nYour session has expired. Please log in again.\n")
            logged_in = run_login_screen()
            if not logged_in:
                exit_program()
            # After re-login, get a fresh session token.
            session_token = create_session_token()
            if session_token is None:
                print("\nSession token service error. Make sure the session token microservice is running.\n")
                exit_program()
            # Go back to the top of the loop so the user can pick again.
            continue

        if token_status != "ok":
            print("\nSession token service error. Make sure the session token microservice is running.\n")
            exit_program()

        # Choice 1: run the generate flow (handles naming a list and settings on first use).
        # Choice 2: open the password lists submenu (create, switch, backup, find & restore, export).
        # Choice 3: show help menu.
        # Choice 4: exit.
        if choice == "1":
            current_list_name, length, types_set, use_lower, use_upper, use_digit, use_symbol = run_generate_flow(
                all_lists, current_list_name, length, types_set, use_lower, use_upper, use_digit, use_symbol
            )
        elif choice == "2":
            current_list_name, length, types_set, use_lower, use_upper, use_digit, use_symbol = run_password_lists_screen(
                all_lists, current_list_name, user_id, length, types_set, use_lower, use_upper, use_digit, use_symbol
            )
        elif choice == "3":
            help_result = run_help_menu(session_token)
            if help_result == "session_expired":
                print("\nYour session has expired. Please log in again.\n")
                logged_in = run_login_screen()
                if not logged_in:
                    exit_program()
                session_token = create_session_token()
                if session_token is None:
                    print("\nSession token service error. Make sure the session token microservice is running.\n")
                    exit_program()
                continue
        elif choice == "4":
            exit_program()


main()