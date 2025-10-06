from flask import Flask, render_template, request, jsonify, send_file
import google.generativeai as genai
import os
import pdfplumber
from docx import Document
import io
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    print("Warning: GEMINI_API_KEY not found in environment variables")
genai.configure(api_key=GEMINI_API_KEY)

class LegalAssistant:
    def __init__(self):
        self.legal_context = """
        You are an AI Legal Assistant specializing in:
        - Contract review and analysis
        - Legal document drafting
        - Case law research
        - Legal advice and guidance
        - Document summarization
        - Compliance checking
        
        Always provide accurate, clear, and professional legal information.
        Note: This is for informational purposes only and not a substitute for professional legal advice.
        
        Provide responses in well-structured format with clear headings and bullet points.
        """
        
        # Initialize the model
        try:
            self.model = genai.GenerativeModel('gemini-pro')
            self.model_available = True
        except Exception as e:
            print(f"Error initializing Gemini model: {e}")
            self.model_available = False
    
    def analyze_document(self, text, analysis_type):
        """Analyze legal document based on type"""
        if not self.model_available:
            return "Error: Gemini model not available. Please check your API key."
        
        prompts = {
            'contract_review': f"""
            ACT AS AN EXPERT LEGAL ANALYST. Review this contract and provide a comprehensive analysis with the following sections:

            ## CONTRACT REVIEW ANALYSIS
            
            ### 1. KEY TERMS AND CONDITIONS
            - Identify and list all major terms
            - Explain significant clauses
            - Highlight financial terms and payment conditions
            
            ### 2. POTENTIAL RISKS AND RED FLAGS
            - Unfavorable terms for either party
            - Ambiguous language
            - Missing standard clauses
            - Potential legal conflicts
            
            ### 3. MISSING CLAUSES
            - Essential clauses that should be included
            - Industry-standard provisions
            - Protective clauses for both parties
            
            ### 4. SUGGESTED IMPROVEMENTS
            - Specific language recommendations
            - Additional clauses to consider
            - Negotiation points
            
            ### 5. OVERALL ASSESSMENT
            - Risk level (Low/Medium/High)
            - Recommendations for next steps
            - Key focus areas for negotiation
            
            Contract text to analyze:
            {text}
            """,
            
            'document_summary': f"""
            ACT AS A LEGAL PROFESSIONAL. Summarize this legal document with the following structure:

            ## LEGAL DOCUMENT SUMMARY
            
            ### 1. MAIN PURPOSE AND PARTIES
            - Primary objective of the document
            - Parties involved and their roles
            - Effective dates and duration
            
            ### 2. KEY OBLIGATIONS AND RIGHTS
            - Main responsibilities of each party
            - Rights granted to each party
            - Key deliverables and expectations
            
            ### 3. IMPORTANT DEADLINES AND DATES
            - Critical timelines
            - Milestone dates
            - Termination and renewal dates
            
            ### 4. TERMINATION CONDITIONS
            - Grounds for termination
            - Notice requirements
            - Post-termination obligations
            
            ### 5. KEY LEGAL PROVISIONS
            - Governing law and jurisdiction
            - Dispute resolution mechanisms
            - Confidentiality and intellectual property
            
            Document text:
            {text}
            """,
            
            'compliance_check': f"""
            ACT AS A COMPLIANCE OFFICER. Analyze this document for compliance issues:

            ## COMPLIANCE ANALYSIS REPORT
            
            ### 1. REGULATORY COMPLIANCE RISKS
            - Potential regulatory violations
            - Industry-specific compliance requirements
            - Reporting and documentation obligations
            
            ### 2. DATA PROTECTION ISSUES
            - GDPR/CCPA compliance assessment
            - Data handling and storage concerns
            - Privacy policy adequacy
            
            ### 3. CONTRACT LAW COMPLIANCE
            - Contract formation validity
            - Consideration and mutual assent
            - Capacity and legality assessment
            
            ### 4. INDUSTRY-SPECIFIC REGULATIONS
            - Relevant industry standards
            - Licensing and certification requirements
            - Professional standards compliance
            
            ### 5. RECOMMENDED COMPLIANCE MEASURES
            - Immediate actions required
            - Documentation improvements
            - Monitoring and audit recommendations
            
            Document text:
            {text}
            """,
            
            'legal_advice': f"""
            ACT AS A LEGAL ADVISOR. Provide general legal guidance on this situation:

            ## LEGAL GUIDANCE ANALYSIS
            
            ### 1. RELEVANT LAWS AND REGULATIONS
            - Applicable statutes and regulations
            - Legal principles involved
            - Jurisdictional considerations
            
            ### 2. POTENTIAL LEGAL STRATEGIES
            - Available legal approaches
            - Pros and cons of each strategy
            - Recommended course of action
            
            ### 3. RIGHTS AND OBLIGATIONS
            - Legal rights of involved parties
            - Corresponding obligations
            - Potential liabilities
            
            ### 4. RISK ASSESSMENT
            - Legal risks involved
            - Probability of success
            - Potential consequences
            
            ### 5. NEXT STEPS TO CONSIDER
            - Immediate actions to take
            - Documentation to gather
            - When to consult a licensed attorney
            
            Situation to analyze:
            {text}
            """
        }
        
        try:
            prompt = f"{self.legal_context}\n\n{prompts.get(analysis_type, prompts['document_summary'])}"
            
            # Limit text length for free API
            if len(prompt) > 30000:
                prompt = prompt[:30000] + "\n\n[Document truncated due to length limitations]"
            
            response = self.model.generate_content(prompt)
            
            if response.text:
                return response.text
            else:
                return "Error: No response generated from the AI model. Please try again."
                
        except Exception as e:
            return f"Error analyzing document: {str(e)}. Please check your API key and try again."
    
    def draft_document(self, doc_type, requirements):
        """Draft legal documents based on requirements"""
        if not self.model_available:
            return "Error: Gemini model not available. Please check your API key."
        
        draft_prompts = {
            'nda': f"""
            ACT AS A LEGAL DRAFTING EXPERT. Draft a comprehensive Non-Disclosure Agreement based on these requirements:

            REQUIREMENTS PROVIDED:
            {requirements}

            DRAFT A COMPLETE NON-DISCLOSURE AGREEMENT INCLUDING:

            1. PARTIES INFORMATION
            - Full legal names and addresses
            - Effective date
            - Purpose of disclosure

            2. DEFINITION OF CONFIDENTIAL INFORMATION
            - Specific categories of protected information
            - Exclusions from confidentiality
            - Examples of confidential materials

            3. OBLIGATIONS OF RECEIVING PARTY
            - Duty to maintain confidentiality
            - Permitted uses of information
            - Security measures required
            - Return/destruction of information

            4. TERM AND TERMINATION
            - Duration of confidentiality
            - Termination conditions
            - Survival of obligations

            5. REMEDIES AND JURISDICTION
            - Legal remedies for breach
            - Injunctive relief provisions
            - Governing law and jurisdiction
            - Dispute resolution process

            6. MISCELLANEOUS PROVISIONS
            - Entire agreement clause
            - Severability
            - Notices
            - Assignment restrictions

            Provide the complete agreement in proper legal format with appropriate section headings.
            """,
            
            'employment_contract': f"""
            ACT AS AN EMPLOYMENT LAW SPECIALIST. Draft a comprehensive Employment Contract based on these requirements:

            REQUIREMENTS PROVIDED:
            {requirements}

            DRAFT A COMPLETE EMPLOYMENT CONTRACT INCLUDING:

            1. POSITION AND DUTIES
            - Job title and description
            - Reporting structure
            - Primary responsibilities
            - Work location requirements

            2. COMPENSATION AND BENEFITS
            - Salary and payment schedule
            - Bonus structure if applicable
            - Benefits package details
            - Expense reimbursement

            3. WORKING HOURS AND LOCATION
            - Standard working hours
            - Overtime policies
            - Remote work provisions
            - Travel requirements

            4. CONFIDENTIALITY AND IP
            - Confidentiality obligations
            - Intellectual property assignment
            - Non-compete provisions (if applicable)
            - Non-solicitation clauses

            5. TERMINATION CONDITIONS
            - Notice periods
            - Grounds for termination
            - Severance provisions
            - Return of company property

            6. GENERAL PROVISIONS
            - At-will employment statement (if applicable)
            - Governing law
            - Entire agreement clause
            - Amendment procedures

            Provide the complete contract in proper legal format.
            """,
            
            'lease_agreement': f"""
            ACT AS A REAL ESTATE ATTORNEY. Draft a comprehensive Residential Lease Agreement based on these requirements:

            REQUIREMENTS PROVIDED:
            {requirements}

            DRAFT A COMPLETE RESIDENTIAL LEASE AGREEMENT INCLUDING:

            1. PROPERTY DESCRIPTION
            - Complete address and unit details
            - Included furnishings and appliances
            - Common areas and exclusive use spaces

            2. LEASE TERM AND RENT
            - Lease commencement and end dates
            - Monthly rent amount and due date
            - Late payment penalties
            - Security deposit details

            3. MAINTENANCE RESPONSIBILITIES
            - Tenant maintenance obligations
            - Landlord repair responsibilities
            - Emergency procedures
            - Alteration restrictions

            4. HOUSE RULES AND REGULATIONS
            - Occupancy limits
            - Pet policies (if any)
            - Noise restrictions
            - Smoking policies

            5. DEFAULT AND TERMINATION
            - Default conditions
            - Eviction procedures
            - Early termination options
            - Renewal procedures

            6. LEGAL PROVISIONS
            - Governing state law
            - Notice requirements
            - Security deposit return procedures
            - Dispute resolution

            Provide the complete lease agreement in proper legal format.
            """,
            
            'service_agreement': f"""
            ACT AS A CONTRACT LAW EXPERT. Draft a comprehensive Service Agreement based on these requirements:

            REQUIREMENTS PROVIDED:
            {requirements}

            DRAFT A COMPLETE SERVICE AGREEMENT INCLUDING:

            1. SERVICES TO BE PROVIDED
            - Detailed description of services
            - Performance standards
            - Deliverables timeline
            - Acceptance criteria

            2. PAYMENT TERMS
            - Fee structure and amounts
            - Payment schedule
            - Expense reimbursement
            - Tax responsibilities

            3. TIMELINE AND DELIVERABLES
            - Project milestones
            - Delivery dates
            - Performance metrics
            - Reporting requirements

            4. INTELLECTUAL PROPERTY RIGHTS
            - Pre-existing IP ownership
            - New IP creation and ownership
            - License grants
            - IP protection obligations

            5. LIABILITY AND INDEMNIFICATION
            - Limitation of liability
            - Indemnification provisions
            - Insurance requirements
            - Warranty disclaimers

            6. TERM AND TERMINATION
            - Agreement duration
            - Termination for cause
            - Termination for convenience
            - Post-termination obligations

            Provide the complete service agreement in proper legal format.
            """
        }
        
        try:
            prompt = f"{self.legal_context}\n\n{draft_prompts.get(doc_type, draft_prompts['service_agreement'])}"
            
            response = self.model.generate_content(prompt)
            
            if response.text:
                return response.text
            else:
                return "Error: No response generated from the AI model. Please try again."
                
        except Exception as e:
            return f"Error drafting document: {str(e)}. Please check your API key and try again."

# Initialize the legal assistant
legal_assistant = LegalAssistant()

def extract_text_from_pdf(file):
    """Extract text from PDF file"""
    text = ""
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error extracting PDF text: {e}")
        return f"Error extracting text from PDF: {str(e)}"
    return text

def extract_text_from_docx(file):
    """Extract text from DOCX file"""
    text = ""
    try:
        doc = Document(file)
        for paragraph in doc.paragraphs:
            if paragraph.text:
                text += paragraph.text + "\n"
    except Exception as e:
        print(f"Error extracting DOCX text: {e}")
        return f"Error extracting text from DOCX: {str(e)}"
    return text

@app.route('/')
def index():
    """Main application page"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_document():
    """Analyze uploaded document"""
    try:
        analysis_type = request.form.get('analysis_type', 'document_summary')
        text = request.form.get('text', '')
        file = request.files.get('file')
        
        print(f"Analysis type: {analysis_type}")
        print(f"Text length: {len(text)}")
        print(f"File uploaded: {file.filename if file else 'None'}")
        
        if file and file.filename:
            filename = file.filename.lower()
            if filename.endswith('.pdf'):
                text = extract_text_from_pdf(file)
                print(f"PDF text extracted, length: {len(text)}")
            elif filename.endswith('.docx'):
                text = extract_text_from_docx(file)
                print(f"DOCX text extracted, length: {len(text)}")
            elif filename.endswith('.txt'):
                text = file.read().decode('utf-8')
                print(f"TXT text extracted, length: {len(text)}")
            else:
                return jsonify({'error': 'Unsupported file format. Please upload PDF, DOCX, or TXT.'})
        
        if not text or not text.strip():
            return jsonify({'error': 'No text provided for analysis. Please upload a file or paste text.'})
        
        # Limit text length for free API
        if len(text) > 10000:
            original_length = len(text)
            text = text[:10000] + f"\n\n[Document truncated from {original_length} to 10000 characters due to length limitations]"
            print(f"Text truncated from {original_length} to 10000 characters")
        
        print(f"Starting analysis with text length: {len(text)}")
        result = legal_assistant.analyze_document(text, analysis_type)
        print("Analysis completed successfully")
        
        return jsonify({
            'success': True,
            'result': result,
            'analysis_type': analysis_type,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        print(f"Analysis error: {str(e)}")
        return jsonify({'error': f'Analysis failed: {str(e)}'})

@app.route('/draft', methods=['POST'])
def draft_document():
    """Draft legal document"""
    try:
        doc_type = request.form.get('doc_type', 'service_agreement')
        requirements = request.form.get('requirements', '')
        
        print(f"Document type: {doc_type}")
        print(f"Requirements length: {len(requirements)}")
        
        if not requirements.strip():
            return jsonify({'error': 'Please provide requirements for the document.'})
        
        print("Starting document drafting...")
        result = legal_assistant.draft_document(doc_type, requirements)
        print("Document drafting completed")
        
        return jsonify({
            'success': True,
            'result': result,
            'doc_type': doc_type,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        print(f"Drafting error: {str(e)}")
        return jsonify({'error': f'Document drafting failed: {str(e)}'})

@app.route('/download_draft', methods=['POST'])
def download_draft():
    """Download drafted document as text file"""
    try:
        content = request.json.get('content', '')
        if not content:
            return jsonify({'error': 'No content provided for download.'})
        
        filename = f"legal_document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        # Create in-memory file
        output = io.BytesIO()
        output.write(content.encode('utf-8'))
        output.seek(0)
        
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype='text/plain'
        )
    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'})

@app.route('/health')
def health_check():
    """Health check endpoint"""
    model_status = "available" if legal_assistant.model_available else "unavailable"
    return jsonify({
        'status': 'healthy', 
        'model_status': model_status,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/test')
def test_page():
    """Test page to verify everything is working"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Page</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; }
            .success { color: green; }
            .error { color: red; }
        </style>
    </head>
    <body>
        <h1>AI Legal Assistant - Test Page</h1>
        <p class="success">✓ Flask server is running</p>
        <p class="success">✓ Templates are working</p>
        <p>Model status: <strong>{}</strong></p>
        <a href="/">Go to Main Application</a>
    </body>
    </html>
    '''.format("Available" if legal_assistant.model_available else "Unavailable - Check API Key")

if __name__ == '__main__':
    print("Starting AI Legal Assistant...")
    print(f"Gemini API Key: {'Set' if GEMINI_API_KEY else 'Not Set'}")
    print(f"Model Available: {legal_assistant.model_available}")
    app.run(debug=True, host='0.0.0.0', port=5000)