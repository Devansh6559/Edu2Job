# Edu2Job

Edu2Job is a **career prediction system** that recommends suitable job roles for students based on their academic profile and skills using a **trained machine learning pipeline** and predefined job–role mappings.

The repository is structured into clearly separated **backend**, **frontend**, **core ML logic**, and **model artifact** modules, enabling modular development and easy maintenance.

---

## ✨ Features

- 🎯 Predicts a **primary job recommendation** with an associated confidence score  
- 🔁 Displays **alternative career paths**, ranked by prediction confidence  
- 🧪 Supports:
  - Single-student job prediction
  - Batch/demo predictions via a **menu-driven CLI**
- 🧠 Includes a complete **ML pipeline** with:
  - Data preprocessing
  - Encoding utilities
  - Model inference
- 🧩 Modular backend architecture covering:
  - Authentication
  - Database integration
  - Validation and utilities



## 📁 Project Structure

High-level directory layout of the repository:

Edu2Job/
├── backend/ # Backend modules: auth, database, ML utilities, preprocessing, validators
├── frontend/ # Frontend UI layer
├── src/ # Core prediction logic (used by main.py)
├── models/ # Trained ML models and encoders (e.g., .pkl files)
├── data/ # Datasets and supporting files
├── database/ # Database-related scripts/configurations
├── config/ # Configuration files
├── instance/ # Runtime / instance-specific files
├── main.py # CLI entry point for running predictions
└── README.md


## 🧠 How Edu2Job Works

1. Student profile data (education, skills, etc.) is collected  
2. Input data is preprocessed and encoded  
3. A trained ML model predicts the most suitable job role  
4. The system outputs:
   - Primary job recommendation
   - Confidence score
   - Alternative job roles ranked by probability  

---

## ⚙️ Requirements

Backend dependencies are listed in:

backend/requirements.txt


## 🛠 Setup

### 1️⃣ Clone the Repository
git clone https://github.com/Devansh6559/Edu2Job.git
cd Edu2Job
2️⃣ Backend Setup (Python)
bash
Copy code
cd backend
pip install -r requirements.txt
3️⃣ Run the Application
From the project root:



python main.py
This will launch the menu-driven CLI for job prediction and demo runs.

🧪 Usage
Use the CLI to:

Enter a single student profile and get predictions

Run demo/batch predictions

View predicted job roles along with confidence scores

🔮 Future Enhancements
Web-based prediction interface integration

Advanced visualization of prediction insights

Model retraining pipeline

Role-based access and admin dashboard

Deployment using Docker / Cloud platforms

🤝 Contribution Guidelines
Contributions are welcome!

Fork repository

Create a feature branch

Commit your changes with clear messages

Push the branch and open a Pull Request

Please maintain clean code, proper documentation, and consistent formatting.

📄 License
This project is licensed under the MIT License.

👤 Author
Devansh Namdev
GitHub: Devansh6559

