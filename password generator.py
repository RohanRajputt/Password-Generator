import secrets
import string
import tkinter as tk
from tkinter import messagebox
from cryptography.fernet import Fernet
import re
import json
import os

# Password strength checker function
def check_password_strength(password):
    strength = 0
    feedback = []

    if len(password) >= 12:
        strength += 1
    else:
        feedback.append("Password should be at least 12 characters long.")

    if re.search(r'[A-Z]', password):
        strength += 1
    else:
        feedback.append("Password should include uppercase letters.")

    if re.search(r'[a-z]', password):
        strength += 1
    else:
        feedback.append("Password should include lowercase letters.")

    if re.search(r'[0-9]', password):
        strength += 1
    else:
        feedback.append("Password should include digits.")

    if re.search(r'[^a-zA-Z0-9]', password):
        strength += 1
    else:
        feedback.append("Password should include special characters.")

    common_patterns = ['123', 'abc', 'password', 'qwerty']
    if any(pattern in password.lower() for pattern in common_patterns):
        strength -= 1
        feedback.append("Avoid common patterns like '123', 'abc', or 'password'.")

    strength_levels = ["Very Weak", "Weak", "Moderate", "Strong", "Very Strong"]
    return strength_levels[strength], feedback

# Generate a passphrase-style password using a wordlist
def generate_passphrase(num_words=4):
    with open("wordlist.txt", "r") as file:
        words = [line.strip() for line in file.readlines()]
    return " ".join(secrets.choice(words) for _ in range(num_words))

# Generate a standard password
def generate_password(length, use_uppercase, use_lowercase, use_numbers, use_special):
    uppercase = string.ascii_uppercase if use_uppercase else ""
    lowercase = string.ascii_lowercase if use_lowercase else ""
    numbers = string.digits if use_numbers else ""
    special = string.punctuation if use_special else ""

    all_characters = uppercase + lowercase + numbers + special
    if not all_characters:
        messagebox.showerror("Error", "At least one character type must be selected!")
        return None

    password = [secrets.choice(all_characters) for _ in range(length)]
    return ''.join(password)

# Secure storage and encryption
def load_key():
    if not os.path.exists("secret.key"):
        key = Fernet.generate_key()
        with open("secret.key", "wb") as key_file:
            key_file.write(key)
    else:
        with open("secret.key", "rb") as key_file:
            key = key_file.read()
    return key

def encrypt_password(password):
    key = load_key()
    fernet = Fernet(key)
    return fernet.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password):
    key = load_key()
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_password.encode()).decode()

def save_password(name, password):
    encrypted_password = encrypt_password(password)
    if not os.path.exists("passwords.json"):
        with open("passwords.json", "w") as file:
            json.dump({}, file)
    with open("passwords.json", "r+") as file:
        data = json.load(file)
        data[name] = encrypted_password
        file.seek(0)
        json.dump(data, file, indent=4)

def load_passwords():
    if not os.path.exists("passwords.json"):
        return {}
    with open("passwords.json", "r") as file:
        data = json.load(file)
        return {name: decrypt_password(password) for name, password in data.items()}

# Tkinter GUI setup
def generate_password_clicked():
    try:
        length = int(length_entry.get())
        use_uppercase = uppercase_var.get()
        use_lowercase = lowercase_var.get()
        use_numbers = numbers_var.get()
        use_special = special_var.get()

        password = generate_password(length, use_uppercase, use_lowercase, use_numbers, use_special)
        if password:
            strength, feedback = check_password_strength(password)
            result_entry.delete(0, tk.END)
            result_entry.insert(0, password)
            strength_label.config(text=f"Strength: {strength}")
            if feedback:
                feedback_text = "\n".join(feedback)
                messagebox.showinfo("Feedback", feedback_text)
    except ValueError:
        messagebox.showerror("Error", "Invalid input for password length!")

def save_password_clicked():
    name = name_entry.get()
    password = result_entry.get()
    if name and password:
        save_password(name, password)
        messagebox.showinfo("Success", "Password saved securely.")
    else:
        messagebox.showerror("Error", "Please enter a password name and generate a password.")

def view_passwords():
    passwords = load_passwords()
    if passwords:
        passwords_str = "\n".join([f"{name}: {password}" for name, password in passwords.items()])
        messagebox.showinfo("Stored Passwords", passwords_str)
    else:
        messagebox.showinfo("Stored Passwords", "No passwords stored yet.")

def generate_passphrase_clicked():
    passphrase = generate_passphrase()
    result_entry.delete(0, tk.END)
    result_entry.insert(0, passphrase)
    strength_label.config(text="Strength: Very Strong")

# GUI setup
root = tk.Tk()
root.title("Advanced Password Generator")

# Password length
length_label = tk.Label(root, text="Password Length:")
length_label.grid(row=0, column=0, padx=5, pady=5)
length_entry = tk.Entry(root)
length_entry.grid(row=0, column=1, padx=5, pady=5)

# Checkbox options
uppercase_var = tk.BooleanVar()
lowercase_var = tk.BooleanVar()
numbers_var = tk.BooleanVar()
special_var = tk.BooleanVar()

uppercase_check = tk.Checkbutton(root, text="Include Uppercase", variable=uppercase_var)
uppercase_check.grid(row=1, column=0, columnspan=2, sticky="w", padx=5)

lowercase_check = tk.Checkbutton(root, text="Include Lowercase", variable=lowercase_var)
lowercase_check.grid(row=2, column=0, columnspan=2, sticky="w", padx=5)

numbers_check = tk.Checkbutton(root, text="Include Numbers", variable=numbers_var)
numbers_check.grid(row=3, column=0, columnspan=2, sticky="w", padx=5)

special_check = tk.Checkbutton(root, text="Include Special Characters", variable=special_var)
special_check.grid(row=4, column=0, columnspan=2, sticky="w", padx=5)

# Generate buttons
generate_button = tk.Button(root, text="Generate Password", command=generate_password_clicked)
generate_button.grid(row=5, column=0, columnspan=2, pady=10)

passphrase_button = tk.Button(root, text="Generate Passphrase", command=generate_passphrase_clicked)
passphrase_button.grid(row=6, column=0, columnspan=2, pady=10)

# Result display
result_label = tk.Label(root, text="Generated Password:")
result_label.grid(row=7, column=0, padx=5, pady=5)
result_entry = tk.Entry(root, width=40)
result_entry.grid(row=7, column=1, padx=5, pady=5)

# Password strength
strength_label = tk.Label(root, text="")
strength_label.grid(row=8, column=0, columnspan=2, padx=5, pady=5)

# Save password
name_label = tk.Label(root, text="Password Name:")
name_label.grid(row=9, column=0, padx=5, pady=5)
name_entry = tk.Entry(root)
name_entry.grid(row=9, column=1, padx=5, pady=5)

save_button = tk.Button(root, text="Save Password", command=save_password_clicked)
save_button.grid(row=10, column=0, columnspan=2, pady=10)

# View stored passwords
view_button = tk.Button(root, text="View Stored Passwords", command=view_passwords)
view_button.grid(row=11, column=0, columnspan=2, pady=10)

# Run the application
root.mainloop()
