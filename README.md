# CV Sorting System using Free-Tier LLMs

A comprehensive resume sorting and ranking system that leverages free-tier Large Language Model APIs to intelligently match candidates with job requirements.

## 🚀 Features

- **Intelligent Resume Parsing**: Extract structured data from PDF, DOCX, and TXT resumes
- **AI-Powered Job Analysis**: Automatically parse job descriptions to identify key requirements
- **Smart Candidate Matching**: Use LLMs to perform semantic matching between candidates and jobs
- **Comprehensive Ranking**: Multi-factor scoring system with customizable weights
- **Interactive Dashboard**: User-friendly web interface built with Streamlit
- **Detailed Analytics**: Visual insights and comprehensive reporting
- **Export Capabilities**: Download results in CSV and JSON formats

## 🛠️ Technology Stack

- **Backend**: Python 3.8+
- **LLM APIs**: OpenRouter (free tier), Hugging Face Inference API
- **NLP**: spaCy, NLTK
- **Web Framework**: Streamlit
- **Document Processing**: PyPDF2, python-docx
- **Data Analysis**: pandas, numpy
- **Visualization**: plotly
- **Configuration**: YAML, python-dotenv

## 📋 Prerequisites

- Python 3.8 or higher
- Free API keys from:
  - [OpenRouter](https://openrouter.ai) (free tier available)
  - [Hugging Face](https://huggingface.co) (free inference API)

## 🔧 Installation

1. **Clone the repository**:
git clone <repository-url>
cd cv_sorting_llm
2. **Create virtual environment**:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activat
3. **Install dependencies**:
pip install -r requirements.txt
4. **Download spaCy model**
python -m spacy download en_core_web_sm 
5. **Set up environment variables**:
Create a .env file in the project root:
OPENROUTER_API_KEY=your_openrouter_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here

6.**Configure the system:Review and modify config.yaml as needed for your specific requirements.**
7.**streamlit run main.py**




cv_sorting_llm/
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── config.yaml                # System configuration
├── .env                       # Environment variables (create this)
├── README.md                  # This file
├── docker-compose.yml         # Docker configuration
├── src/
│   ├── parsers/
│   │   ├── resume_parser.py   # Resume parsing logic
│   │   └── job_parser.py      # Job description parsing
│   ├── matching/
│   │   ├── llm_matcher.py     # LLM-based matching
│   │   └── scorer.py          # Scoring and ranking
│   ├── llm_client/
│   │   └── client.py          # LLM API client
│   └── ui/
│       └── streamlit_app.py   # Web interface
├── data/
│   ├── sample_resumes/        # Sample resume files
│   └── sample_jobs/           # Sample job descriptions
└── outputs/                   # Generated reports and exports
