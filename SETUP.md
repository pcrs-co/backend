# PCRS Backend Setup

> **Note:** Make sure Python 3 is installed on your system.

---

## Step 1: Set Up a Virtual Environment

In the root of the project, run the following command:

```bash
python3 -m venv venv
```

---

## Step 2: Activate the Virtual Environment

Use the appropriate command for your operating system:

- **Linux/macOS:**
  ```bash
  source env/bin/activate
  ```

- **Windows:**
  ```bash
  .\env\Scripts\activate
  ```

You should now see `(env)` in your terminal prompt.

---

## Step 3: Install Dependencies

With the virtual environment activated, run:

```bash
pip install -r requirements.txt
```

---

## Fix: MySQL Client Error

If you get an error related to MySQL during installation, install the necessary development libraries:

- **Ubuntu/Debian:**
  ```bash
  sudo apt update
  sudo apt install libmysqlclient-dev
  ```

- **Fedora/RHEL:**
  ```bash
  sudo dnf install mariadb-devel
  ```

- **Arch/Manjaro:**
  ```bash
  sudo pacman -S mariadb
  ```

- **Windows:**
  Download and install the [MySQL Connector/C](https://dev.mysql.com/downloads/connector/c/)
  
Then try installing dependencies again:

```bash
pip install -r requirements.txt
```

---

## Step 4: Set Up the Database

Log in as the root user:

```bash
sudo mariadb -u root -p
```

Then run the following commands in the MariaDB shell:

```sql
CREATE DATABASE pcrs;
CREATE USER 'pcrs'@'localhost' IDENTIFIED BY 'Pcrs@password3';
GRANT ALL PRIVILEGES ON pcrs.* TO 'pcrs'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

---

## Step 5: Run Migrations

Still inside the virtual environment, run the following:

```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

---

Your backend setup is now complete.

Refer to the [contributing guide](../CONTRIBUTING.md) for next steps or development instructions.

