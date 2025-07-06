# 🧠 IITI-GPT

An intelligent assistant web app tailored for **IIT Indore**, integrating a conversational chatbot, user login, reminder system, and navigation. The chatbot is powered by **Cohere’s Large Language Model (LLM)** and enhanced with real-time information retrieval using the **Tavily Search API**.

![Chatbot Screenshot](https://github.com/Siddharththakur3617/IITI-GPT/blob/main/assets/chatbot_demo.jpg)
![Reminder Screenshot](https://github.com/Siddharththakur3617/IITI-GPT/blob/main/assets/reminder_demo.jpg)

---

## 🚀 Features

### ✅ User Authentication
- Secure login/logout functionality with session tracking.
- Redirects unauthenticated users appropriately.

### 💬 AI-Powered Chatbot
- Uses **Cohere LLM** for natural and intelligent responses.
- Integrates **Tavily Search API** for up-to-date, contextually relevant web results.
- Handles campus-specific questions (e.g., hostels, emergency numbers).

### ⏰ Smart Reminder System
- Users can create reminders with custom text and datetime.
- Stores and displays reminders with real-time notification support.

### 🧭 Navigation System
- Clean user interface with Bootstrap-based routing between Home, Chatbot, and Reminder modules.

---

## 🛠️ Tech Stack

| Category         | Technologies Used                                      |
|------------------|--------------------------------------------------------|
| **Frontend**     | HTML, CSS, JavaScript, Bootstrap                       |
| **Backend**      | Django (Python Framework)                              |
| **Database**     | SQLite (Default Django DB)                             |
| **Authentication** | Django’s built-in auth system                         |
| **Chatbot Logic**| Cohere LLM, Tavily Search API, custom routing logic    |
| **Notifications**| Browser Notification API (for reminders)               |
| **Deployment**   | Localhost / Deployable on Heroku, Render, etc.         |

---

## 🧩 Project Structure

