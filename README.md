# 🧠 Article Distribution System (LangChain AI Agent)

This project uses AI agents and LangChain to automate the intelligent allocation of jacket articles to various store locations based on historical supply, store capacity, and available godown stock. It ensures articles are not reallocated to the same store in 2024 and respects per-store quantity limits.

---

## 🚀 Project Objective

To develop an AI-powered planning tool that:
- Avoids article duplication across stores
- Respects store-wise maximum quantity limits
- Allocates only articles available in godown stock
- Integrates with `.pdf` and `.csv` inputs for real-world usability


---

## ⚙️ Technologies Used

- **Python 3.10+**
- **LangChain**
- **OpenAI API** (GPT-based reasoning)
- **Anthropic API** (Claude integration)
- **Hugging Face API**
- **Streamlit** (for interactive UI)
- **PyMuPDF** / `fitz` (for PDF parsing)
- **Pandas** (data processing)

---

## 📥 Input Files

- `5_Jacket_Stock.pdf`: Contains jacket article numbers and available stock in godown
- `5_Jacket_Supply_24.pdf`: Contains which articles were supplied to which stores in 2024
- `5_Max_Pcs.pdf`: Contains max jacket limit per store

---

## 📤 Output

- A `.csv` file listing new allocations, ensuring:
  - No repeats from 2024
  - Articles are within stock
  - Each store stays within its limit

---

## 🔐 Environment Variables

Create a `.env` file like this:

```env
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
HF_TOKEN=your_huggingface_key_here
```

---

## 🧪 Running the App

1. Create virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the Streamlit app:

```bash
streamlit run app.py
```

---

## 📈 Future Enhancements

* Add Excel export support
* Integrate with ERP platforms (SAP B1, Odoo)
* Automate PDF uploads via n8n or Make.com
* Add user authentication & logging

---

## 👨‍💻 Author

**Arshjot Singh**
Computer Engineering | Thapar Institute of Engineering and Technology

> Passionate about AI agents, ERP automation, and solving real-world business problems.

---

## 🛡️ Disclaimer

This tool is meant for internal planning use. Ensure any sensitive data (like API keys) is handled securely and excluded from version control.

---

## 📄 License

MIT License — feel free to use and adapt with attribution.
