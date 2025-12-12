# Supply Chain Management System using Blockchain

This is a **Supply Chain Management System** built with **Python (Flask)** that leverages **Blockchain technology** to ensure transparent, secure, and immutable tracking of products. It also features a **Data Analytics Dashboard** to visualize supply chain insights.

## 🚀 Key Features

*   **🛡️ Custom Blockchain:** A Proof-of-Work blockchain implementation to record all product transactions immutably.
*   **💾 Data Persistence:** The blockchain state is automatically saved to and loaded from `chain.json`, ensuring data is not lost when the server restarts.
*   **🔐 Digital Signatures:** All transactions are cryptographically signed using **RSA private keys** to prove ownership and authenticity.
*   **🔒 Secure Authentication:** User passwords are securely hashed using **Bcrypt** (via `werkzeug.security`) to prevent unauthorized access.
*   **📊 Data Analytics:** Built-in dashboard using **Pandas** and **Matplotlib** to visualize:
    *   Product Distribution
    *   Transaction History
    *   Products by Location
*   **👥 Role-Based Access:** Supports different roles like Manufacturer, Farmer, Distributor, Retailer, etc.
*   **📦 Product Tracking:** Complete history of a product from registration to current ownership.

## 🛠️ Technologies Used

*   **Backend:** Python, Flask
*   **Blockchain Core:** Python (Custom Implementation), Hashlib, RSA (Crypto)
*   **Data Science:** Pandas, Matplotlib, Numpy
*   **Frontend:** HTML, CSS, Jinja2 Templates

## ⚙️ Installation & Running

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Niwarthana00/supplychain-managment-system.git
    cd supplychain-managment-system
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Application:**
    ```bash
    python app.py
    ```

4.  **Access the Dashboard:**
    Open your browser and navigate to:
    `http://127.0.0.1:5000`

## 📝 Usage Guide

1.  **Register:** Create a new account. Your **Public/Private Keys** are generated automatically.
2.  **Login:** Access your dashboard.
3.  **Register Product:** Add a new product to the chain. This creates a "Genesis Transaction" for that product.
4.  **Track Product:** Use the **Product ID** (Batch ID) to see its entire history on the blockchain.
5.  **Analytics:** View real-time statistics on supply chain performance.

---
*Developed for Interview/Portfolio Demonstration*
