import os
from pathlib import Path
import argparse
import backend

def input_charaden_fields() -> dict:
    while True:
        name = input("Enter name: ")
        if name:
            name = name.encode("shift-jis")
            break
        print("Name cannot be empty.")

    while True:
        title = input("Enter title: ")
        if title:
            title = title.encode("shift-jis")
            if len(title) > 36:
                print("Title too long in bytes.")
            else:
                break
        else:
            print("Title cannot be empty.")

    path = None
    size_of_file = None
    while True:
        path = input("Enter path to the file:").strip().replace("'", "").replace('"', "")
        if os.path.isfile(path):
            size_of_file = os.path.getsize(path)
            path = backend.IN_PHONE_PATH + Path(path).as_posix().split('/')[-1]
            break
        print("Invalid file path.")

    while True:
        try:
            width = int(input("Enter width (integer): "))
            if width > 0:
                break
            else:
                print("Width must be a positive integer.")
        except ValueError:
            print("Invalid input. Please enter an integer.")

    while True:
        try:
            height = int(input("Enter height (integer): "))
            if height > 0:
                break
            else:
                print("Height must be a positive integer.")
        except ValueError:
            print("Invalid input. Please enter an integer.")

    print("Chara-den successfully added.")
    return backend.Charaden(name, title, size_of_file, path, width, height)

def handle_command(command):
    if command == 'l':
        backend.print_list()
    elif command == 'i':
        backend.insert(input_charaden_fields())
    elif command == 'd':
        backend.print_list()
        try:
            index = int(input("Enter the position of the Chara-den to delete: ").strip())
            backend.delete(index - 1)
            print(f"Deleted the Chara-den with position {index}.")
        except ValueError:
            print("Invalid position. Please enter a number.")

def handle_interactive_mode():
    while True:
        command = input("""l - List all Chara-den
i - Insert a Chara-den
d - Delete a Chara-den
q - Quit
Enter your choice: """).strip().lower()
        if command == 'q' or command == 'quit':
            print("Exiting interactive mode.")
            break
        elif command in ['l', 'i', 'd']:
            handle_command(command)
        else:
            print("Invalid choice. Please choose l, i, d, or q.")

def main():
    parser = argparse.ArgumentParser(
        prog='Charaden List Manager',
        description='Modifies AVATAR.MNG found in FOMA phones to load Charaden properly.'
    )

    parser.add_argument(
        'avatar_mng_file',
        type=str,
        nargs='?',
        default=None,
        help='Path to the AVATAR.MNG file (leave empty to create new).'
    )

    args = parser.parse_args()

    if args.avatar_mng_file:
        backend.AVATAR_MNG_PATH = args.avatar_mng_file

        try:
            assert(backend.AVATAR_MNG_PATH.find("AVATAR.MNG") != -1)
        except AssertionError:
            print("The file isn't AVATAR.MNG.")

        try:
            assert(os.path.getsize(backend.AVATAR_MNG_PATH) == backend.AVATAR_MNG_SZ)
        except AssertionError:
            print(f"The file isn't {backend.AVATAR_MNG_SZ}")

        backend.read_list()
    else:
        print("No AVATAR.MNG file provided. A new file will be created.")

    print("This is an interactive mode. What do you want to do?")

    handle_interactive_mode()

    if backend.change_made:
        decision = input("Changes have been made. Do you want to write the final list of Chara-dens to the file? (y/N)")
        while True:
            if decision == '' or decision == 'n' or decision == 'N':
                print("Changes have not been written.")
                break
            if decision == 'y' or decision == 'Y':
                if not args.avatar_mng_file:
                    output_path = input("Enter the path to save the AVATAR.MNG file at: ").strip()
                    output_path = os.path.join(output_path, '')
                    output_path = os.path.expanduser(output_path)
                    directory = os.path.dirname(output_path)
                    if not os.path.exists(directory):
                        os.makedirs(directory, exist_ok=True)
                    backend.AVATAR_MNG_PATH = output_path + "AVATAR.MNG"
                backend.write_avatar_mng_file()
                print("Changes have been written. Please make sure to replace the exact .CFD files inside the Chara-den folder and swap in the AVATAR.MNG.")
                break

if __name__ == '__main__':
    main()
