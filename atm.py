import sqlite3
import hashlib

# ================= DATABASE SETUP =================
def initialize_database():
    conn = sqlite3.connect('atm.db')
    c = conn.cursor()
    
    # Create users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE,
                  password TEXT,
                  balance REAL DEFAULT 0,
                  is_admin BOOLEAN DEFAULT FALSE)''')
    
    # Create admin if not exists
    try:
        hashed_password = hashlib.sha256('admin123'.encode()).hexdigest()
        c.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)",
                  ('admin', hashed_password, True))
    except sqlite3.IntegrityError:
        pass
    
    conn.commit()
    conn.close()

# ================= HELPER FUNCTIONS =================
def get_user(username):
    conn = sqlite3.connect('atm.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()
    return user

def update_balance(username, amount):
    conn = sqlite3.connect('atm.db')
    c = conn.cursor()
    c.execute("UPDATE users SET balance = balance + ? WHERE username=?", (amount, username))
    conn.commit()
    conn.close()

def add_user(username, password, is_admin=False):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    conn = sqlite3.connect('atm.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)",
                  (username, hashed_password, is_admin))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def delete_user(username):
    conn = sqlite3.connect('atm.db')
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE username=?", (username,))
    affected = c.rowcount
    conn.commit()
    conn.close()
    return affected > 0

def get_all_users():
    conn = sqlite3.connect('atm.db')
    c = conn.cursor()
    c.execute("SELECT id, username, balance, is_admin FROM users")
    users = c.fetchall()
    conn.close()
    return users

# ================= AUTHENTICATION =================
def login():
    while True:
        print("\n=== ATM Login ===")
        username = input("Username: ")
        password = hashlib.sha256(input("Password: ").encode()).hexdigest()
        
        user = get_user(username)
        
        if user and user[2] == password:
            return user  # (id, username, password, balance, is_admin)
        print("Invalid credentials. Try again.")

# ================= USER INTERFACE =================
def user_menu(username):
    while True:
        print("\n=== User Menu ===")
        print("1. Check Balance")
        print("2. Deposit")
        print("3. Withdraw")
        print("4. Logout")
        
        choice = input("Enter choice: ")
        
        if choice == '1':
            user = get_user(username)
            print(f"Your balance: ${user[3]:.2f}")
            
        elif choice == '2':
            amount = float(input("Deposit amount: $"))
            update_balance(username, amount)
            print("Deposit successful!")
            
        elif choice == '3':
            amount = float(input("Withdraw amount: $"))
            user = get_user(username)
            if user[3] >= amount:
                update_balance(username, -amount)
                print("Withdrawal successful!")
            else:
                print("Insufficient funds!")
                
        elif choice == '4':
            break
            
        else:
            print("Invalid choice!")

def admin_menu():
    while True:
        print("\n=== Admin Menu ===")
        print("1. Add User")
        print("2. Delete User")
        print("3. View All Users")
        print("4. Logout")
        
        choice = input("Enter choice: ")
        
        if choice == '1':
            username = input("New username: ")
            password = input("New password: ")
            if add_user(username, password):
                print("User added successfully!")
            else:
                print("Username already exists!")
                
        elif choice == '2':
            username = input("Username to delete: ")
            if delete_user(username):
                print("User deleted successfully!")
            else:
                print("User not found!")
                
        elif choice == '3':
            users = get_all_users()
            print("\n=== All Users ===")
            for user in users:
                role = "Admin" if user[3] else "User"
                print(f"ID: {user[0]} | Username: {user[1]:<15} | Balance: ${user[2]:<10.2f} | Role: {role}")
                
        elif choice == '4':
            break
            
        else:
            print("Invalid choice! Please enter 1-4")

# ================= MAIN PROGRAM =================
def main():
    initialize_database()
    while True:
        user = login()
        if user[4]:  # is_admin
            admin_menu()
        else:
            user_menu(user[1])

if __name__ == "__main__":
    main()