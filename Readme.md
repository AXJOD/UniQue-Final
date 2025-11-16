# 🎓 College AI Portal

This project is a multi-user, role-based web application built with Streamlit, designed to serve the needs of a modern educational institution. It leverages AI, including a Retrieval-Augmented Generation (RAG) engine, to provide intelligent services for students, faculty, and administrators.

## ✨ Overview

The College AI Portal is a comprehensive platform that provides distinct functionalities based on user roles:

-   **Students:** Can interact with an AI chatbot to ask questions, get personalized study notes, and generate practice questions from uploaded course materials.
-   **Faculty:** Can upload course documents (PDFs), manage their materials, and generate quizzes or assignment questions automatically.
-   **Admins:** Have access to a dashboard to manage users, monitor system activity, and view analytics on platform usage.

The application features a secure authentication system and a user-friendly interface for each user type.

## 🚀 Features

-   **Role-Based Access Control:** Separate, tailored portals for Students, Faculty, and Administrators.
-   **Secure User Authentication:** Includes user registration and login functionality with password hashing.
-   **AI-Powered RAG Engine:** Allows users to "chat" with their documents, providing context-aware answers from uploaded materials.
-   **Document Processing:** Faculty can upload PDF documents which are then processed, chunked, and stored in a vector database.
-   **Question Generation:** Capability to generate multiple-choice questions, and other question types from documents.
-   **Admin & Analytics Dashboard:** Provides insights into user management and system usage.

## 🛠️ Tech Stack

-   **Backend Framework:** Python, Streamlit
-   **AI & LLM Orchestration:** LangChain, Hugging Face Transformers
-   **Vector Database:** ChromaDB
-   **Embeddings:** Sentence-Transformers
-   **Document Handling:** PyPDF2, pypdf
-   **Data & Visualization:** Pandas, Plotly
-   **Authentication:** bcrypt for password hashing

## ⚙️ Setup and Installation

Follow these steps to set up the project locally.

1.  **Clone the Repository**
    ```bash
    git clone <repository-url>
    cd Claude+Lovable/Minor
    ```

2.  **Create a Virtual Environment**
    ```bash
    python -m venv venv
    ```

3.  **Activate the Environment**
    -   On Windows:
        ```bash
        .\venv\Scripts\activate
        ```
    -   On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```

4.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Set Up Environment Variables**
    -   Create a file named `.env` in the `Minor` directory.
    -   Add your Hugging Face API token to this file:
        ```
        HUGGINGFACEHUB_API_TOKEN="your_hf_token_here"
        ```

## ▶️ Running the Application

Once the setup is complete, you can run the Streamlit application with the following command from the `Minor` directory:

```bash
streamlit run app.py
```

Open your web browser and navigate to the local URL provided by Streamlit (usually `http://localhost:8501`).

## 📂 Project Structure

```
Minor/
├── app.py                  # Main Streamlit application entry point
├── requirements.txt        # Project dependencies
├── .env                    # Environment variables (needs to be created)
├── config.py               # Application configuration
├── .streamlit/
│   └── config.toml         # Streamlit configuration
├── pages/                  # Different portals for each user role
│   ├── 1_👤_Login.py
│   ├── 2_👨‍💼_Admin_Dashboard.py
│   ├── 3_👨‍🏫_Faculty_Portal.py
│   └── 4_👨‍🎓_Student_Portal.py
├── services/               # Core backend logic and AI services
│   ├── rag_engine.py         # Retrieval-Augmented Generation engine
│   ├── document_processor.py # Handles PDF parsing and chunking
│   ├── database.py           # Database interaction logic
│   └── ...
├── utils/                  # Utility functions
│   ├── auth.py             # Authentication and user management
│   └── session.py          # Session state management
└── data/                   # Data storage
    ├── chroma/             # ChromaDB vector stores
    └── uploads/            # Directory for uploaded files
```
