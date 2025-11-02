# 🧠 CodeSense AI

AI-powered code explanation and visualization tool to help students understand programming concepts better.

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](/LICENSE)

---

## About

**CodeSense AI** helps you understand code by providing:
- Line-by-line explanations at different skill levels
- AI-powered bug detection with suggestions
- Visual step-by-step execution for arrays and variables

I built this as a learning project during my 3rd year to explore full-stack development and AI integration.

---

## Features

- 📝 **Code Explanations** - Choose from ELI5, Beginner, Intermediate, or Expert level
- 🐛 **Bug Detection** - Find issues and get AI-suggested fixes
- 🎬 **Visual Execution** - Watch your code run step-by-step (Python only for now)
- ⚡ **Multiple Languages** - Python, JavaScript, Java, C++ support for explanations

---

## Demo

*Screenshots coming soon - setting up the project locally to capture them*

---

## Tech Stack

**Backend:**
- FastAPI (Python)
- Google Gemini AI API
- Python AST for code parsing

**Frontend:**
- React.js
- Custom CSS with animations
- Lucide icons

---

## Getting Started

### What You'll Need

- Python 3.8+
- Node.js 14+
- Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

**1. Clone the repo**
```bash
git clone https://github.com/saileed05/codesense-ai.git
cd codesense-ai
```

**2. Backend setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file:
```
GEMINI_API_KEY=your_key_here
ALLOWED_ORIGINS=http://localhost:3000
PORT=8000
```

Start the server:
```bash
python main.py
```

**3. Frontend setup** (open new terminal)
```bash
cd frontend
npm install
npm start
```

Visit **http://localhost:3000** 🎉

---

## How It Works

1. Paste your code in the editor
2. Select language and expertise level
3. Click "Explain Code" for detailed breakdowns
4. Click "Find Bugs" to detect issues
5. Click "Visual Execution" to see arrays/variables animate (Python only)

---

## Project Structure
```
codesense-ai/
├── backend/
│   ├── main.py              # API endpoints
│   ├── code_analyzer.py     # AST parsing logic
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   └── App.js
│   └── package.json
└── README.md
```

---

## What I Learned

Building this taught me:
- How to integrate AI APIs (Gemini) into applications
- Python's AST module for code parsing
- FastAPI for building REST APIs
- React state management and component design
- Handling rate limiting and error responses

---

## Known Limitations

- Visual execution only works for Python right now
- Doesn't handle recursion or complex nested functions yet
- Rate limited to prevent API cost overruns (10 req/min)
- Code length capped at 10,000 characters

---

## Future Improvements

Things I want to add:
- [ ] Support JavaScript/TypeScript visualization
- [ ] Recursive function tracking
- [ ] Better error handling
- [ ] User accounts to save code history
- [ ] Deploy to a live URL

---

## Contributing

Found a bug? Have a suggestion? Feel free to open an issue or submit a pull request!

---

## Author

**Sailee Desai**  
3rd Year CS Student

- GitHub: [@saileed05](https://github.com/saileed05)
- Open to internship opportunities and feedback!

---

## License

MIT License - feel free to use this for learning!

---

## Acknowledgments

- Google Gemini AI for the API
- Inspired by Python Tutor's visualization approach
- Thanks to Stack Overflow for debugging help 😅

---

**⭐ If you found this helpful, consider starring the repo!**