#!/usr/bin/env python3
"""
PDF Password Protection Tool (Educational Project)
--------------------------------------------------
This script allows users to add password protection (encryption) to PDF files.
It serves as an educational tool to demonstrate:
  1. Command-line argument parsing with 'argparse'
  2. Secure interactive password entry with 'getpass'
  3. File handling and validation
  4. PDF manipulation and encryption using the 'pypdf' library
  5. Structured exception and error handling in Python
"""

import os
import sys
import argparse
import getpass
from pypdf import PdfReader, PdfWriter

def print_header():
    """Prints a clean, friendly header for the command-line tool."""
    print("==================================================")
    print("        PDF PASSWORD PROTECTOR (pypdf)            ")
    print("==================================================")

def validate_input_pdf(file_path):
    """
    Validates that the input file exists and has a .pdf extension.
    Returns True if valid, raises ValueError with a descriptive message otherwise.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Error: The file '{file_path}' does not exist.")
    
    if not os.path.isfile(file_path):
        raise ValueError(f"Error: '{file_path}' is a directory or special file, not a standard file.")
        
    if not file_path.lower().endswith('.pdf'):
        raise ValueError(f"Error: '{file_path}' does not appear to be a PDF file (missing .pdf extension).")
        
    return True

def encrypt_pdf(input_path, output_path, password):
    """
    Encrypts the input PDF using the provided password and saves it to output_path.
    Uses AES-256 standard encryption via pypdf.
    """
    print(f"\n[1/3] Reading source file: {input_path}")
    
    try:
        reader = PdfReader(input_path)
    except Exception as e:
        raise ValueError(f"Failed to read the PDF file. It might be corrupted. Details: {e}")
        
    # Check if the PDF is already password-protected
    if reader.is_encrypted:
        print("[!] Warning: This PDF file is already encrypted / password-protected.")
        override = input("Do you want to proceed and re-encrypt it? (y/n): ").strip().lower()
        if override != 'y':
            print("Operation cancelled.")
            sys.exit(0)
            
    writer = PdfWriter()
    
    print("[2/3] Processing pages and applying encryption...")
    # Add all pages from the reader to the writer object
    for i, page in enumerate(reader.pages):
        writer.add_page(page)
        
    # Encrypt the output document.
    # user_password: Required to open and view the PDF.
    # algorithm: "AES-256" is the modern secure standard for PDF files.
    writer.encrypt(user_password=password, algorithm="AES-256")
    
    print(f"[3/3] Saving protected file to: {output_path}")
    try:
        with open(output_path, "wb") as output_file:
            writer.write(output_file)
    except PermissionError:
        raise PermissionError(f"Error: Permission denied when writing to '{output_path}'.")
    except Exception as e:
        raise IOError(f"Error writing the encrypted PDF: {e}")

    print("\n[+] Success! Your PDF has been encrypted successfully.")

def run_interactive():
    """Runs the script in interactive mode, prompting the user step-by-step."""
    print_header()
    print("Interactive Mode Active. Follow the prompts below.\n")
    
    # 1. Get input path and validate
    while True:
        input_path = input("Enter the path to the source PDF file: ").strip().strip('"\'')
        if not input_path:
            print("Error: Input path cannot be empty.")
            continue
        try:
            validate_input_pdf(input_path)
            break
        except Exception as e:
            print(e)
            print("Please try again.\n")

    # 2. Get output path
    # Offer a default output name based on the input filename
    dir_name, file_name = os.path.split(input_path)
    base_name, ext = os.path.splitext(file_name)
    default_output = os.path.join(dir_name, f"{base_name}_protected{ext}")
    
    while True:
        output_path = input(f"Enter the destination path [{default_output}]: ").strip().strip('"\'')
        if not output_path:
            output_path = default_output
            
        if not output_path.lower().endswith('.pdf'):
            print("Error: Destination file must end with .pdf extension.")
            continue
            
        # Warn if overwriting the original file
        if os.path.abspath(input_path) == os.path.abspath(output_path):
            confirm = input("[!] Warning: You are overwriting the original PDF file. Proceed? (y/n): ").strip().lower()
            if confirm != 'y':
                print("Please enter a different output path.\n")
                continue
        break

    # 3. Get password securely using getpass
    print("\nSecure password input (characters will not be shown as you type):")
    while True:
        pass1 = getpass.getpass("Enter password: ")
        if not pass1:
            print("Error: Password cannot be empty.")
            continue
            
        pass2 = getpass.getpass("Confirm password: ")
        if pass1 == pass2:
            password = pass1
            break
        else:
            print("Error: Passwords do not match. Please try again.\n")

    # 4. Perform encryption
    try:
        encrypt_pdf(input_path, output_path, password)
    except Exception as e:
        print(f"\n[!] An error occurred during encryption:\n{e}")
        sys.exit(1)

def run_cli():
    """Parses command-line arguments and runs encryption."""
    parser = argparse.ArgumentParser(
        description="A Python CLI tool to encrypt PDF files with password protection."
    )
    parser.add_argument(
        "input_file",
        help="Path to the source PDF file to encrypt."
    )
    parser.add_argument(
        "output_file",
        help="Path to save the resulting encrypted PDF file."
    )
    parser.add_argument(
        "password",
        help="Password for PDF protection."
    )
    
    args = parser.parse_args()
    
    # Validate input file
    try:
        validate_input_pdf(args.input_file)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)
        
    # Perform encryption
    try:
        encrypt_pdf(args.input_file, args.output_file, args.password)
    except Exception as e:
        print(f"\n[!] Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    # If no arguments are provided, switch to the user-friendly interactive mode
    if len(sys.argv) == 1:
        run_interactive()
    else:
        run_cli()

if __name__ == "__main__":
    main()
