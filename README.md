# AI Legal Assistant

An intelligent Flask-based web application that provides AI-powered legal document analysis and drafting capabilities.

## Features

### 📄 Document Analysis
- **Contract Review**: Identify key terms, risks, and missing clauses
- **Document Summary**: Extract main points and important provisions
- **Compliance Check**: Analyze regulatory compliance issues
- **Legal Advice**: Provide general legal guidance

### 📝 Document Drafting
- **Non-Disclosure Agreements (NDA)**
- **Employment Contracts**
- **Lease Agreements**
- **Service Agreements**

### 🔧 Technical Features
- File upload support (PDF, DOCX)
- Real-time text analysis
- Download generated documents
- Responsive web interface

## Installation

1. **Get Gemini API Key**:
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a free account and generate an API key
   - The free tier has generous limits for personal use

2. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd AI-Legal-Assistant