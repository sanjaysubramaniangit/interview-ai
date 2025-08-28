# AI Interview Prep Assistant

## Overview

The **AI Interview Prep Assistant** is a web application designed to help users excel in technical interviews by generating personalized questions, providing AI-driven feedback, and tracking progress.  

Powered by **Gemini AI**, it features a user-friendly interface styled with **TailwindCSS**, a robust **FastAPI** backend, and **MongoDB** for efficient data storage. Users can input their role and experience to receive tailored questions, submit answers for feedback, and monitor improvement via a progress dashboard.  

The app also leverages job descriptions to ensure questions are relevant to specific roles.

---

## 🚀 Tech Stack

| **Component** | **Technology** |
|--------------|----------------|
| **Frontend** | ReactJS + Vite |
| **Backend** | FastAPI |
| **Styling** | TailwindCSS |
| **Database** | MongoDB |
| **AI** | Gemini AI |
| **Tools** | Motor (MongoDB async), Axios |

---

## 🧠 AI Feature Implementation

### 1. Prompting
- **How It's Used:** Sends targeted instructions to Gemini AI to generate interview questions and feedback customized to the user's role, experience, and domain.  
  Example: `"Generate 5 questions for a Senior Python Developer"`.
- **Why It Works:** Ensures questions and feedback are relevant and specific, with responses stored in MongoDB for quick access.
- **Scalability & Efficiency:** Caching common prompts reduces Gemini AI calls, ensuring fast response times even with many users.

---

### 2. RAG (Retrieval-Augmented Generation)
- **How It's Used:** Retrieves job descriptions or sample questions from MongoDB (or optionally from Glassdoor/Indeed APIs) to provide context for generating job-specific questions.
- **Why It Works:** Makes questions highly relevant to real-world job requirements, enhancing preparation quality.
- **Scalability & Efficiency:** MongoDB's fast queries and indexing ensure quick context retrieval, supporting large datasets and high traffic.

---

### 3. Structured Output
- **How It's Used:** Gemini AI responses are formatted as consistent JSON data (e.g., `question`, `difficulty`, `topic`) for easy display and storage in MongoDB.
- **Why It Works:** Provides clean, predictable data for the frontend, improving user experience and data handling.
- **Scalability & Efficiency:** Structured formats streamline processing, and MongoDB's flexible schema handles large volumes of data.

---

### 4. Function Calling
- **How It's Used:** Gemini AI triggers backend actions, like saving user answers or fetching progress, by calling FastAPI endpoints that interact with MongoDB.
- **Why It Works:** Enables seamless data management, ensuring user progress is accurately tracked and retrievable.
- **Scalability & Efficiency:** Async MongoDB operations and FastAPI's performance support multiple users with minimal latency.

---

## 📜 License
This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.
