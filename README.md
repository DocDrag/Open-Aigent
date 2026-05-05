# 🚀 Open-Aigent (Agentic IDE)

**Open-Aigent** is an Open-Source Agentic IDE designed to transform AI into your personal "Software Engineer." It's not just a chatbot; it's an autonomous Agent capable of **Planning, Web Searching, and Executing code changes** directly on your local machine—100% under your control.

Developed by **Doc Drag** (Pair-programming with AI).

---

## [English] 🇺🇸

### ✨ Key Features

- **🌍 Universal LLM Gateway**: Connects to **Ollama** (Local) for maximum privacy, or use Cloud LLMs as needed.
- **🧠 Agentic Core**: An AI Agent that thinks for itself. It can read/write files and manage project structures.
- **🌐 Web Search & Browsing**: Searches the internet for the latest data (market prices, news, new libraries) to write accurate, up-to-date code.
- **⚡ Real-time IDE**: Built-in File Explorer and Code Viewer to see changes happen instantly.
- **🛡️ User Approval System**: Every file modification requires your explicit approval for security.

### ⚠️ Disclaimer

**Open-Aigent is currently in the Prototype/Experimental stage.** 
- **Use at your own risk**: The AI Agent has the capability to modify files on your local machine. While there is an approval system, AI can still make mistakes that might break your code or result in data loss.
- **Backup your data**: Always use **Git** or maintain backups of your workspace before allowing the Agent to make changes.
- The developers (Doc Drag) are not responsible for any damage caused by the use of this software.

### 🤔 Why Open-Aigent? (and Alternatives)

Let's be honest: If you're looking for a professional-grade, rock-solid AI coding experience, you should probably use **[Cline (formerly Claude Dev)](https://github.com/cline/cline)** or **[Cursor](https://www.cursor.com/)**. They are amazing and highly stable.

**So why use Open-Aigent?**
- **Standalone**: No IDE required. Run it on a server and access it via any browser.
- **Local-First**: Deeply integrated with Ollama for 100% private, local agentic loops.
- **Educational**: Designed for those who want to see *how* an Agentic IDE works under the hood. It's transparent and fully customizable.
- **Fun**: It's a project created for the community, by the community (and a lot of AI help).



### 🛠️ Installation Guide

#### 1. Prerequisites

- **Docker & Docker Compose**: Required to run the Backend and Frontend services.
  - [Download Docker Desktop](https://www.docker.com/products/docker-desktop/)
- **Ollama** (Recommended for Local LLMs):
  - [Download Ollama](https://ollama.com/download)
  - After installation, run your preferred model (e.g., `qwen3.5:9b` or `gemma4:e4b`):
    ```bash
    ollama run qwen3.5:9b
    ```


#### 2. Project Setup

1.  **Clone Project**:
    ```bash
    git clone https://github.com/DocDrag/Open-Aigent.git
    cd Open-Aigent
    ```

2.  **Config Environment**:
    Create a `.env` file in the `backend/` folder (copy from the example):
    ```bash
    cp backend/.env.example backend/.env
    ```

#### 3. Launch

Run this command to start everything:
```bash
docker-compose up --build
```

- **Frontend UI**: [http://localhost:3000](http://localhost:3000)
- **Backend API**: [http://localhost:8000](http://localhost:8000)

### 📖 How to Use

1.  Open [http://localhost:3000](http://localhost:3000)
2.  **Set Workspace**: Enter the folder path you want the AI to work in (default is `./workspace`).
3.  **Select Model**: Pick your installed Ollama model.
4.  **Describe Task**: Type your request in the chat, for example:
    - *"Create a Python script that scrapes today's gold price and displays it."*
    - *"Find and fix the bugs in main.py."*
5.  **Approve**: When the AI generates code, a confirmation card will appear. Review and click **Approve** to apply changes.

### 📜 License

MIT License - Created by **Doc Drag**.

---

## [ภาษาไทย] 🇹🇭

### ✨ ความสามารถหลัก

- **🌍 Universal LLM Gateway**: เชื่อมต่อกับ **Ollama** (Local) เพื่อความเป็นส่วนตัวสูงสุด หรือใช้ Cloud LLM ได้ตามต้องการ
- **🧠 Agentic Core**: AI Agent ที่คิดและตัดสินใจเองได้ สามารถอ่านไฟล์, เขียนไฟล์, และจัดการโครงสร้างโฟลเดอร์
- **🌐 Web Search & Browsing**: ค้นหาข้อมูลล่าสุดจากอินเทอร์เน็ต เพื่อนำมาเขียนโค้ดได้แม่นยำและเป็นปัจจุบัน
- **⚡ Real-time IDE**: มี File Explorer และ Code Viewer ในตัว เห็นการเปลี่ยนแปลงของโค้ดแบบวินาทีต่อวินาที
- **🛡️ User Approval System**: ทุกการแก้ไขไฟล์ Agent จะต้องขออนุญาตจากคุณก่อนเสมอ เพื่อความปลอดภัย

### ⚠️ ข้อควรระวัง (Disclaimer)

**Open-Aigent ยังอยู่ในช่วงการพัฒนา (Prototype/Experimental)**
- **ใช้งานด้วยความระมัดระวัง**: AI Agent มีความสามารถในการแก้ไขไฟล์ในเครื่องของคุณ แม้จะมีระบบยืนยันตัวตน แต่ AI ก็อาจทำงานผิดพลาดที่ส่งผลให้โค้ดพังหรือข้อมูลสูญหายได้
- **สำรองข้อมูลเสมอ**: ควรใช้งานร่วมกับ **Git** หรือทำการสำรองข้อมูล (Backup) พื้นที่ทำงานของคุณเสมอก่อนอนุญาตให้ Agent แก้ไขโค้ด
- ผู้พัฒนา (Doc Drag) จะไม่รับผิดชอบต่อความเสียหายใด ๆ ที่เกิดจากการใช้งานซอฟต์แวร์นี้

### 🤔 ทำไมต้องใช้ Open-Aigent? (และทางเลือกอื่น)

พูดกันตรง ๆ: ถ้าคุณกำลังมองหาประสบการณ์การเขียนโค้ดด้วย AI ที่มีความเสถียรสูงและเป็นมืออาชีพที่สุด เราขอแนะนำให้คุณไปใช้ **[Cline (Claude Dev)](https://github.com/cline/cline)** หรือ **[Cursor](https://www.cursor.com/)** ครับ พวกเขาทำไว้ได้ยอดเยี่ยมมาก ๆ

**แล้ว Open-Aigent มีไว้ทำไม?**
- **Standalone**: ไม่จำเป็นต้องมี IDE (เช่น VS Code) คุณสามารถรันบนเซิร์ฟเวอร์แล้วเข้าใช้งานผ่านเบราว์เซอร์จากที่ไหนก็ได้
- **Local-First**: เน้นการเชื่อมต่อกับ Ollama แบบ 100% เพื่อความเป็นส่วนตัวสูงสุดในการรัน Agent
- **เพื่อการศึกษา**: เหมาะสำหรับคนที่อยากเห็นว่า "เบื้องหลัง" ของ Agentic IDE ทำงานยังไง โค้ดของเราโปร่งใสและปรับแต่งได้ทุกบรรทัด
- **ความสนุก**: มันคือโปรเจกต์ที่สร้างขึ้นโดยชุมชน เพื่อชุมชน (และได้รับความช่วยเหลืออย่างมากจาก AI)



### 🛠️ การติดตั้ง

#### 1. เตรียมความพร้อม

- **Docker & Docker Compose**: จำเป็นสำหรับการรันระบบ Backend และ Frontend
  - [ดาวน์โหลด Docker Desktop](https://www.docker.com/products/docker-desktop/)
- **Ollama** (แนะนำสำหรับสาย Local):
  - [ดาวน์โหลด Ollama](https://ollama.com/download)
  - หลังจากติดตั้ง ให้รันโมเดลที่ต้องการ (ตัวอย่างเช่น `qwen3.5:9b` หรือ `gemma4:e4b`):
    ```bash
    ollama run qwen3.5:9b
    ```


#### 2. ตั้งค่าโครงการ

1.  **Clone Project**:
    ```bash
    git clone https://github.com/DocDrag/Open-Aigent.git
    cd Open-Aigent
    ```

2.  **ตั้งค่า Environment**:
    สร้างไฟล์ `.env` ในโฟลเดอร์ `backend/`:
    ```bash
    cp backend/.env.example backend/.env
    ```

#### 3. เริ่มต้นใช้งาน

รันคำสั่ง:
```bash
docker-compose up --build
```

### 📖 วิธีใช้งาน

1.  เปิด [http://localhost:3000](http://localhost:3000)
2.  **ตั้งค่า Workspace**: ระบุ Path โฟลเดอร์ที่ต้องการแก้ไขงาน
3.  **สั่งงาน**: พิมพ์คำสั่งในช่อง Chat เช่น *"ช่วยเขียนโค้ดดึงข้อมูลราคาทองวันนี้มาทำสรุปหน้าเว็บ"*
4.  **ยืนยัน**: ตรวจสอบโค้ดที่ AI ร่างขึ้นมา แล้วกด **Approve** เพื่อยืนยันการแก้ไข

---