# WMAA Website Redevelopment Project [CITS5206]

## Project Overview
This project focuses on the redevelopment of the WMAA charity website to provide a modern, secure, and user-friendly platform. The website is being rebuilt using Flask to convert a static HTML/CSS/JS site into a structured web application with backend support. The system supports key organisational needs such as information sharing, volunteer engagement, donations, and improved accessibility.


## Group No: 05

| Student Name         | Student ID |
|----------------------|-----------|
| Aneesh Kumar Bandari | 24553634  |
| Neha Pathare         | 24350545  |
| Navdeep Singh        | 24496192  |
| Harpreet Singh       | 24476099  |
| Varun Suresh         | 24500097  |


## Technologies Used
- Frontend: HTML, CSS, JavaScript (Bootstrap)  
- Backend: Python (Flask)  
- Version Control: Git & GitHub  



## Project Structure

```text
WMAA-Website-Project/
├── app.py
├── requirements.txt
├── .gitignore
├── README.md
├── templates/
│   ├── base.html
│   ├── navbar.html
│   ├── index.html
│   └── ... other HTML templates
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── client-meetings/
├── facilitator-meetings/
└── deliverable-1/
```


---

## Setup Instructions (Run Locally)

1. Clone the repository:

```bash
git clone https://github.com/Harpreet-Personal/WMAA-Website-Project/
cd WMAA-Website-Project
```

2. Create virtual environment:

```bash
python3 -m venv venv
```

3. Activate environment:

```bash
# Mac/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Run the application:

```bash
python3 app.py
```

6. Open in browser:

```bash
http://127.0.0.1:5000
```

## Git Workflow
- Do not work directly on `main`  
- Create a feature branch:

git checkout -b feat/your-feature-name

- Commit and push changes:

git add .
git commit -m "feat: your message"
git push

- Create a Pull Request on GitHub  

## Project Rules
- Minimum 2 reviewers required before merging  
- Use proper commit message conventions (`feat`, `fix`, `refactor`)  
- Keep code clean and organised  
- Do not push `venv/`
