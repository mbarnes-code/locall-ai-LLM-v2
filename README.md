🧠 Self-Hosted LLM Server
A secure, self-hosted AI server using Docker, FastAPI, Nginx, and Ollama with GPU acceleration.
Supports LLM inference, ChromaDB, Redis caching, and monitoring.

🚀 Features
✔ FastAPI-based AI API with GPU acceleration ⚡
✔ Secure reverse proxy (Nginx) with HTTPS and authentication 🔐
✔ Dockerized services (Ollama, Redis, ChromaDB, Grafana, FAISS, N8N) 🐳
✔ Secrets management using Docker secrets 🛡️
✔ Supports both CPU and GPU inference 🎮
✔ Remote access via a hosted web server 🌍

🔧 Setup & Installation
1️⃣ Prerequisites
  🐳 Docker & Docker Compose installed (Get Docker)
  ✅ Nvidia GPU (optional, but recommended)
  🔐 Domain name + SSL certificate (for secure remote access)
2️⃣ Clone the Repository
3️⃣ Configure Environment Variables
4️⃣ Set Up Secrets
5️⃣ Start Services
🎯 Future Improvements
🔹 Add OAuth authentication for the LLM API
🔹 Implement rate limiting to prevent abuse
🔹 Improve logging & monitoring
📜 License
MIT License. Feel free to use and modify! 😊🚀
