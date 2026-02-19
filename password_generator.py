# Password Generator - A terminal application for generating secure, random passwords with custom settings.
# Includes:
# - Login microservice call (port 5001)
# - Export microservice call (port 5002) to write saved passwords to a CSV file

import random
import string
import requests


# attempt_login: Sends username/password to the login microservice and returns the status string.
# Prerequisites: login microservice is running on LOGIN_URL.
# Arguments: username (str), password (str).
# Returns: str, one of "ok", "locked", "invalid_format", "invalid_credentials", or "service_error".
def attempt_login(username, password):
    LOGIN_URL = "http://127.0.0.1:5001/login"

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


# run_login_screen: Prompts the user to log in until success or they quit.
# Prerequisites: None.
# Arguments: None.
# Returns: bool, True if user logged in; False if user chose to quit.
def run_login_screen():
    while True:
        print()
        print("Login Required")
        print("Enter your username and password to continue.")
        print("Press Enter on username to quit.\n")

        username = input("Username: ").strip()

        # Blank username means quit.
        if username == "":
            return False

        password = input("Password: ").strip()

        # Call the microservice to validate credentials.
        status = attempt_login(username, password)

        # Handle the possible responses.
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
    # Store one record as a dictionary so the export microservice can make CSV columns from the keys.
    record = {
        "password": password,
        "length": length,
        "lowercase": use_lower,
        "uppercase": use_upper,
        "numbers": use_digit,
        "symbols": use_symbol
    }
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
# Prerequisites: length is either None (not set) or an integer; types_set is a boolean.
# Arguments: length (int or None), types_set (bool).
# Returns: str, the formatted line.
def format_settings_line(length, types_set):
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
    return "Settings: Length = " + length_str + " | Types = " + types_str + \
    "\n" + "MUST SET LENGTH AND CHARACTER TYPES FIRST!" + "\n"


# run_main_menu: Shows the main menu and returns the user's choice.
# Prerequisites: length and types_set reflect current settings.
# Arguments: length (int or None), types_set (bool).
# Returns: str, one of "1", "2", "3", "4", "5".
def run_main_menu(length, types_set):
    print()
    print(format_settings_line(length, types_set))
    print("Menu")
    print("1) Generate password")
    print("2) Edit password settings")
    print("3) I need help!")
    print("4) Export saved passwords to CSV")
    print("5) Exit program")
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


# run_generate_screen: Shows the Generate Password / Show Result screen until user returns to menu or exits.
# Prerequisites: length and types_set are set; at least one character type is on.
# Arguments: length, types_set, the four use_* flags, and saved_passwords list.
# Returns: None (returns to main menu via loop in main).
def run_generate_screen(length, types_set, use_lower, use_upper, use_digit, use_symbol, saved_passwords):
    # Each time through the loop: one password and the three options are shown.
    # Exit only when 2 (return to main menu) or 3 (exit program) is chosen.
    # Option 1 means loop again and show another password.
    while True:
        print()
        print(format_settings_line(length, types_set))
        print("Generated password:")
        pwd = generate_password(length, use_lower, use_upper, use_digit, use_symbol)
        print(pwd)

        # Save this password to the list so the user can export later.
        save_generated_password(saved_passwords, pwd, length, use_lower, use_upper, use_digit, use_symbol)

        print("1) Generate new password")
        print("2) Return to menu")
        print("3) Exit program")
        choice = input("\nEnter choice: ").strip()

        # Choice 1: continue the loop and show another password.
        # Choice 2: return so control goes back to main and the main menu appears.
        # Choice 3: exit the program.
        if choice == "1":
            continue
        if choice == "2":
            return
        if choice == "3":
            exit_program()


# show_settings_required_message: Displays a message that length and character types must be set first, then waits for Enter.
# Prerequisites: None.
# Arguments: None.
# Returns: None.
def show_settings_required_message():
    print()
    print("Set length and character types first in Edit password settings.")
    input("\nPress Enter to return to menu: ")


# run_help_menu: Displays the help menu and runs the selected item (quickstart, length help, character types help) or return to menu or exit.
# Prerequisites: None.
# Arguments: None.
# Returns: None.
def run_help_menu():
    # Loop until 4 (return to main menu) or 5 (exit) is chosen.
    # After viewing a help screen, this menu is shown again.
    while True:
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


# main: Entry point; shows the welcome once, then runs the main menu loop (generate, settings, help, export, exit).
# Keeps track of length, types_set, the four character-type flags, and saved passwords for exporting.
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

    # saved_passwords stores every generated password record so the user can export later.
    saved_passwords = []

    # length is None and types_set is False so the status line shows "not set"
    # until the settings menu is used. The four flags default to lower/upper/digits on
    # and symbols off so the first generation uses letters and numbers unless changed.
    length = None
    types_set = False
    use_lower = True
    use_upper = True
    use_digit = True
    use_symbol = False

    # Show the main menu, get the choice, then branch.
    # The loop runs until option 5 is chosen and exit_program() is called.
    while True:
        choice = run_main_menu(length, types_set)

        # Choice 1: generate password only when length and types are set;
        # otherwise show the "set length and character types first" message.
        # Choice 2: open settings and update length, types_set, and the four flags.
        # Choice 3: show help menu.
        # Choice 4: export saved passwords to a CSV file using the export microservice.
        # Choice 5: exit.
        if choice == "1":
            # Generate was chosen but nothing is set yet: show the reminder and wait for Enter.
            # Otherwise run the generate screen with the current settings.
            if length is None or not types_set:
                show_settings_required_message()
            else:
                run_generate_screen(length, types_set, use_lower, use_upper, use_digit, use_symbol, saved_passwords)
        elif choice == "2":
            length, types_set, use_lower, use_upper, use_digit, use_symbol = run_settings(
                length, types_set, use_lower, use_upper, use_digit, use_symbol
            )
        elif choice == "3":
            run_help_menu()
        elif choice == "4":
            run_export_screen(saved_passwords)
        elif choice == "5":
            exit_program()


main()