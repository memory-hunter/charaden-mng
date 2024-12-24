import os
import argparse
import backend

def handle_command(command):
    if command == 'l':
        backend.print_list()
    elif command == 'i':
        backend.insert()
    elif command == 'd':
        backend.print_list()
        try:
            index = int(input("Enter the index of the Chara-den to delete: ").strip())
            backend.delete(index)
            print(f"Deleted the Chara-den with position {index}.")
        except ValueError:
            print("Invalid index. Please enter a number.")

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
        help='Path to the AVATAR.MNG file.'
    )

    args = parser.parse_args()
    
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

    print("This is an interactive mode. What do you want to do?")
        
    handle_interactive_mode()
    
    if backend.change_made:
        decision = input("Changes have been made. Do you want to write the final list of Chara-dens to the file? (y/N)")
        while True:
            if decision == '' or decision == 'n' or decision == 'N':
                print("Changes have not been written. The AVATAR.MNG is the same as before.")
                break
            if decision == 'y' or decision == 'Y':
                print("Changes have been written to AVATAR.MNG. Please make sure to replace the exact .CFD files inside the Chara-den folder and swap in the AVATAR.MNG.")

if __name__ == '__main__':
    main()
