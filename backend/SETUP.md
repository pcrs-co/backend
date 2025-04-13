# PCRS Backend Set-Up

## **NOTE** - Ensure you have Python installed on your system.

To get started, follow the steps below:

### 1. **Create a Virtual Environment**

Run the following command (while in project root) to create a virtual environment inside backend folder:

```bash
cd backend
python3 -m venv env
```

### 2. **Activate the Virtual Environment**

After creating the virtual environment, activate it by running the appropriate command based on your operating system:

- **On Linux/macOS**:

  ```bash
  source env/bin/activate
  ```

- **On Windows**:

  ```bash
  .\env\Scripts\activate
  ```

Once activated, your shell prompt should change, showing the virtual environment's name in parentheses (e.g., `(env)`).

### 3. **Install Project Dependencies**

After activating the virtual environment, install the necessary dependencies:

```bash
pip install -r requirements.txt
```

### 4. **Move the requirements.txt**

After activating the virtual environment, install the necessary dependencies:

```bash
mv requirements.txt /backend
cd backend
```

## **NOTE**

If you encounter an error while installing project dependencies, it might be because MySQL client libraries are missing. To fix this, follow the instructions below for your operating system:

### **For Linux**

- **Ubuntu/Debian-based systems:**

  ```bash
  sudo apt-get update
  sudo apt-get install libmysqlclient-dev
  ```

- **Fedora/RHEL-based systems:**

  ```bash
  sudo dnf install mariadb-devel
  ```

- **Arch/Manjaro-based systems:**

  ```bash
  sudo pacman -S mariadb
  ```

### **For Windows**

If you encounter issues on Windows, ensure that the necessary MySQL or MariaDB client libraries are installed. You can download the MySQL Connector/C from [here](https://dev.mysql.com/downloads/connector/c/), and then install it by following the instructions provided on the site.

Once installed, retry the dependency installation using:

```bash
pip install -r requirements.txt
```

---

### 5. **SETTING UP THE DATABASE**
  ```bash
  mysql -u root -p
  ```
  Enter your password

  ```bash
  CREATE DATABASE pcrs;
  CREATE USER 'pcrs'@'localhost' IDENTIFIED BY 'Pcrs@password3';
  GRANT ALL PRIVILEGES ON pcrs.* TO 'pcrs'@'localhost';
  FLUSH PRIVILEGES;
  ```

### 6. **RUNNING THE BACKEND**

```bash
  python3 manage.py makemigrations
  python3 manage.py migrate
  ```

With these steps, you should be able to set up and run the project. If you have any issues or need further assistance, feel free to reach out.

### Go on with [contributing](../CONTRIBUTING.md)!
