# PCRS Frontend Setup

> **Note:** Make sure Node.js and npm are installed on your system.

---

## Step 1: Install Project Dependencies

Navigate to the frontend folder and install all required packages:

```bash
cd frontend
npm install
```

```bash
npm install axios react-router-dom jwt-decode
```

```bash
npm install react-toastify
npm install bootstrap
npm install intl-tel-input
npm install intl-tel-input/build/css/intlTelInput.css
```

if warning errors of old verion occur do the following:

```bash
sudo npm install -g n
sudo n 22
```

```bash
sudo n 22
```

```bash
node -v
```

---

## Step 2: Start the Development Server

Start the development server by running:

```bash
npm run dev
```

After the server starts, the application will be available at:

[http://localhost:5173](http://localhost:5173)

---

For next steps, see the [contributing guide](../CONTRIBUTING.md).
