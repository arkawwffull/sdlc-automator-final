import os
from dotenv import load_dotenv
from crewai import Agent, Crew, Process, Task
from crewai_tools import FileReadTool, FileWriterTool
import streamlit as st

# Load environment variables
load_dotenv()

# Set Streamlit page configuration
st.set_page_config(page_title="SDLC Automator", layout="wide")

# Title and description
st.title("SDLC Automator")
st.markdown("Automate the generation of SRS, SDD, and Test Case documents from BRD, SRS, and SDD inputs.")
st.markdown("Upload your documents and generate the required outputs using AI agents.")

# Sidebar
with st.sidebar:
    st.header("Document Upload and Generation")

    # Section 1: Upload BRD and Generate SRS
    st.subheader("1. Generate SRS from BRD")
    uploaded_brd = st.file_uploader("Upload BRD Document", type=["txt", "pdf", "md"])
    generate_srs_button = st.button("Generate SRS", type="primary", use_container_width=True)

    # Section 2: Upload SRS and Generate SDD
    st.subheader("2. Generate SDD from SRS")
    uploaded_srs = st.file_uploader("Upload SRS Document", type=["txt", "pdf", "md"])
    generate_sdd_button = st.button("Generate SDD", type="primary", use_container_width=True)

    # Section 3: Upload SRS and SDD, Generate Test Cases
    st.subheader("3. Generate Test Cases from SRS and SDD")
    uploaded_files = st.file_uploader("Upload SRS and SDD Documents", type=["txt", "pdf", "md"], accept_multiple_files=True)
    generate_testcases_button = st.button("Generate Test Cases", type="primary", use_container_width=True)

def save_uploaded_file(uploaded_file, file_name):
    """Save uploaded file to a temporary directory."""
    if not os.path.exists("temp"):
        os.makedirs("temp")
    file_path = os.path.join("temp", file_name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

# Functions for generating SRS, SDD, and Test Cases remain unchanged...

def generate_srs(uploaded_brd):
    if uploaded_brd:
        brd_path = save_uploaded_file(uploaded_brd, "brd.txt")
        file_read_tool = FileReadTool(file_path=brd_path)
        file_writer_tool = FileWriterTool()

        # Agents for BRD to SRS
        business_analyst = Agent(
            role="Healthcare Business Analyst",
            goal=(
                "Extracts relevant content from the given healthcare business requirements document, including "
                "Introduction, Purpose, In Scope, Out of Scope, Assumptions, References, and Overview. "
                "Enhances unclear sections using the LLM, internet sources (with a focus on healthcare regulations "
                "and best practices), and domain-specific knowledge to ensure completeness before passing refined "
                "content for documentation. Ensure clear distinction between **patient workflows**, **EHR integration**, "
                "and **AI-driven diagnostic tools** while maintaining **regulatory compliance**."
            ),
            backstory=(
                "A senior business analyst with extensive experience in the healthcare industry. Expert in "
                "understanding healthcare-specific business requirements, including regulatory compliance "
                "(HIPAA, GDPR, FDA guidelines, etc.), and ensuring clarity in documentation for healthcare applications."
            ),
            tools=[file_read_tool]
        )

        technical_analyst = Agent(
            role="Healthcare Technical Analyst",
            goal=(
                "Analyzes the healthcare business requirements document (BRD) to identify **technical aspects**, "
                "including: - **Entity-Relationship Model**: Defines key entities (Patient, Doctor, Appointment, "
                "Service, etc.), attributes, primary keys (PKs), foreign keys (FKs), and relationships. "
                "- **Data Exchange & Integration**: Specifies standards like HL7, FHIR, and RESTful APIs for "
                "interoperability. - **Compliance & Security**: Ensures data handling aligns with HIPAA and GDPR "
                "by defining PHI access, encryption, and logging."
            ),
            backstory=(
                "A senior technical analyst with expertise in **healthcare data modeling**, interoperability, "
                "and secure data exchange. Proficient in structuring healthcare applications to meet regulatory "
                "and technical requirements."
            ),
            tools=[file_read_tool]
        )

        requirement_categorizer = Agent(
            role="Healthcare Requirement Categorizer",
            goal=(
                "Classifies extracted healthcare requirements into: - **Functional** (Patient Registration, "
                "Appointment Management, EHR Interactions) - **Non-Functional** (HIPAA Compliance, Response Time, "
                "Scalability) - **Technical** (Entity-Relationship Model, API Integration, Data Storage & Security) "
                "Ensures clarity by refining vague or incomplete sections using the LLM and domain-specific knowledge."
            ),
            backstory=(
                "A specialist in **healthcare system design and classification**, ensuring all technical aspects "
                "are documented effectively."
            )
        )

        srs_writer = Agent(
            role="Healthcare System Requirements Specifications Writer",
            goal=(
                "Writes a structured **SRS document** by incorporating: - **Entity-Relationship Model** with clearly "
                "defined entities, attributes, primary keys, and foreign keys. - **Data Handling & Storage** "
                "considerations for PHI protection, audit logging, and encryption. - **Interoperability** details "
                "including API specifications and HL7/FHIR-based integration."
            ),
            backstory=(
                "A professional **technical documentation expert**, ensuring clarity, structure, and adherence to "
                "healthcare data management best practices."
            ),
            tools=[file_writer_tool]
        )

        srs_formatter = Agent(
            role="Healthcare System Requirements Specifications Formatter",
            goal=(
                "Organizes the healthcare application document with appropriate formatting, headings, and structure. "
                "Ensures that the final document is readable, structured, and includes sections like **Dependencies** "
                "(pointing out dependencies on EHR systems, healthcare APIs, etc.) and a **Conclusion** summarizing "
                "key insights. Ensures adherence to healthcare document formatting best practices."
            ),
            backstory=(
                "A document specialist with expertise in structuring and formatting professional reports, "
                "particularly for the healthcare domain."
            ),
            tools=[file_writer_tool]
        )

        # Tasks for BRD to SRS
        business_analysis_task = Task(
            description=(
                "Extracts healthcare-specific content for **Introduction**, **Purpose**, **Scope**, **In Scope**, "
                "**Out of Scope**, **Assumptions**, **References**, and **Overview** separately from the provided "
                "business requirements document. Ensures that extracted sections highlight **patient workflows**, "
                "**EHR integration**, **AI-driven diagnosis**, and **appointment management** without altering "
                "**Out of Scope** and **Assumptions**. Strengthens the **Out of Scope** section to clearly exclude "
                "irrelevant features such as third-party integrations."
            ),
            expected_output=(
                "Provide clear, structured, and compliant content to be incorporated into the SRS document. Ensure "
                "that all **regulatory compliance** aspects such as **HIPAA** and **GDPR** are addressed."
            ),
            agent=business_analyst
        )

        technical_analysis_task = Task(
            description=(
                "Extract and define the **Data Model** from the healthcare business requirements document (BRD), "
                "ensuring it aligns with **healthcare interoperability standards**. Identify key entities (**Patient**, "
                "**Doctor**, **Appointment**, **Service**, etc.) and define their attributes, primary keys (PKs), and "
                "foreign keys (FKs). Establish entity relationships (**one-to-many**, **many-to-many**) and document "
                "**EHR integration requirements**. Ensure API interactions comply with **HL7**, **FHIR**, and "
                "**RESTful** standards while validating **HIPAA** and **GDPR** compliance for **PHI storage and exchange**."
            ),
            expected_output=(
                "A structured **Data Model** capturing entities, attributes, relationships, PKs, FKs, and "
                "interoperability requirements, ensuring alignment with **healthcare compliance and EHR integration standards**."
            ),
            agent=technical_analyst
        )

        requirement_categorize_task = Task(
            description=(
                "Categorize requirements into **Functional, Non-Functional, and Technical**, ensuring the **Data Model** "
                "is classified under **Technical Requirements**. Organize **Functional Requirements** (Patient Registration, "
                "Appointment Booking, etc.). List **Non-Functional Requirements** (Security, Performance, Scalability). "
                "Ensure all **vague details** are clarified using the **LLM**."
            ),
            expected_output=(
                "A structured list of categorized requirements, ensuring clarity in **Data Models, EHR integrations, "
                "and security protocols**."
            ),
            agent=requirement_categorizer
        )

        srs_write_task = Task(
            description=(
                "Writes a structured **healthcare-focused SRS document**, incorporating: - **Introduction**, "
                "**Purpose**, **Scope**, **In Scope**, **Out of Scope**, **Assumptions**, **References**, and "
                "**Overview** (from Business Analyst). - **Functional**, **Non-Functional**, and **Technical Requirements** "
                "(from Requirement Categorizer). - **Data Model**, **EHR Integration**, **Patient Data Flow**, "
                "**Compliance & Security** (from Technical Analyst). Ensures **AI-driven symptom checkers**, "
                "**patient management workflows**, and the **Data Model section** capture entities, attributes, PKs, "
                "FKs, and relationships."
            ),
            expected_output=(
                "A well-structured **SRS document** compliant with **healthcare regulations**, emphasizing "
                "**patient data privacy, AI diagnostics, and EHR interoperability**."
            ),
            agent=srs_writer
        )

        srs_format_task = Task(
            description=(
                "Formats the **healthcare-focused SRS document**, ensuring a structured flow: - **Out of Scope** "
                "follows **In Scope**. - **Assumptions** precede **Dependencies**. - Healthcare-specific sections like "
                "**AI diagnostics, EHR integration, and patient privacy** are clearly structured. Adds a **Conclusion** "
                "summarizing key insights and outlining potential **future enhancements** (AI tools, multilingual support, "
                "cloud scalability)."
            ),
            expected_output=(
                "A final **SRS document** that is clear, professional, and adheres to **healthcare compliance standards** "
                "while being properly formatted and saved as `srs1.md`."
            ),
            agent=srs_formatter
        )

        # Initialize and execute the Crew
        crew = Crew(
            agents=[
                business_analyst,
                technical_analyst,
                requirement_categorizer,
                srs_writer,
                srs_formatter
            ],
            tasks=[
                business_analysis_task,
                technical_analysis_task,
                requirement_categorize_task,
                srs_write_task,
                srs_format_task
            ],
            process=Process.sequential,
            verbose=True,
        )
        return crew.kickoff()
    else:
        st.error("Please upload a file to proceed.")
        return None
    

# ================================
# SRS to SDD Conversion
# ================================

def generate_sdd(uploaded_srs):
    if uploaded_srs:
        srs_path = save_uploaded_file(uploaded_srs, "srs.txt")
        file_read_tool = FileReadTool(file_path=srs_path)
        file_writer_tool = FileWriterTool()

        # Agents for SRS to SDD
        srs_extractor = Agent(
            role="SRS Extractor Agent",
            goal=(
                "Extract structured information from the SRS document, categorizing key sections like Introduction, System Overview, "
                "Functional and Non-Functional Requirements, API Design, Security & Compliance, and Data Encryption Strategy."
            ),
            backstory=(
                "A specialized AI agent trained in document analysis, natural language understanding, and structured data extraction. "
                "This agent identifies and categorizes key components from the SRS, ensuring no critical requirement is missed. "
                "The extracted content serves as the foundation for subsequent tasks, including wireframe design and interface validation."
            ),
            tools=[file_read_tool]
        )

        sdd_structure = Agent(
            role="SDD Structure Agent",
            goal=(
                "Design a structured SDD template incorporating sections such as Introduction, System Overview, Non-Functional Requirements, "
                "API Design, Wireframe Designs, Interface Validation Rules, Security & Compliance, Data Encryption Strategy, and Appendices."
            ),
            backstory=(
                "A meticulous architect of technical documents, this agent ensures that the SDD follows best practices in software engineering. "
                "It constructs a logical and scalable framework that aligns with extracted requirements, ensuring completeness across all sections."
            )
        )

        er_schema_generator = Agent(
            role="ER Schema Generator Agent",
            goal=(
                "Extract the Data Model section from the SRS and generate a structured Entity Relationship (ER) schema with MySQL examples."
            ),
            backstory=(
                "A database design expert trained to analyze functional data models and convert them into structured ER schemas. "
                "This agent ensures consistency, normalization, and correctness in entity definitions and relationships. "
                "The ER Schema will be placed under the **System Architecture** section in the final SDD."
            )
        )
    

        content_generator = Agent(
            role="Content Generation Agent",
            goal=(
                "Populate the SDD template by mapping extracted SRS content to relevant sections, ensuring technical accuracy, coherence, and completeness."
            ),
            backstory=(
                "An expert in technical writing and AI-driven content generation, this agent ensures clarity, precision, and completeness. "
                "It generates high-quality descriptions, system overviews, non-functional requirements, API designs, security considerations, "
                "wireframe descriptions, and interface validation rules. This agent ensures:"
                "- **Introduction** includes Purpose, Scope, Assumptions, Constraints, and Stakeholders."
                "- **System Overview** includes High-level Architecture (UML, DFD), Technology Stack, and Multi-tenant SaaS Architecture."
                "- **Non-Functional Requirements** include Performance, Scalability, HIPAA & GDPR Compliance, and Security Best Practices."
                "- **ER Schema** includes MySQL examples."
                "- **API Design** includes Endpoints, Industry-Specific Integration Standards, and Security & Authentication."
                "- **Wireframe Designs** and **Interface Validation Rules** are included."
                "- **Security & Compliance** includes Threat Modeling, Risk Assessment, RBAC, and Data Encryption Strategy."
                "- **Data Encryption Strategy** maps functional requirements to system components."
                "- **Appendices** include Glossary and Compliance Standards."
            )
        )

        wireframe_designer = Agent(
            role="Wireframe Designer Agent",
            goal=(
                "Create detailed descriptions of wireframes for each functional requirement in the SRS document."
            ),
            backstory=(
                "A skilled UI/UX designer trained in translating functional requirements into wireframe descriptions. "
                "This agent ensures that the wireframes align with the system's usability goals and user experience principles. "
                "The wireframe descriptions are structured and ready for integration into the SDD under the **Wireframe Designs** section."
            )
        )

        interface_validator = Agent(
            role="Interface Validation Agent",
            goal=(
                "Define validation rules and user interface behavior for each functional requirement."
            ),
            backstory=(
                "An expert in user interface design and validation, this agent ensures that all input fields, buttons, and interactions are properly validated and user-friendly. "
                "It adheres to best practices in form validation, accessibility, and usability. "
                "The validation rules and interaction guidelines are structured and ready for integration into the SDD under the **Interface Validation Rules** section."
            )
        )

        validation_compliance = Agent(
            role="Validation & Compliance Agent",
            goal=(
                "Review and validate the SDD content to ensure alignment with security standards, regulatory compliance, and best practices."
            ),
            backstory=(
                "A compliance-focused AI agent trained in regulatory standards such as HIPAA, GDPR, and OWASP best practices. "
                "It cross-verifies security implementations, role-based access controls, encryption strategies, risk assessments, and API security. "
                "This agent ensures that all security & compliance documentation is properly included under Appendices."
            )
        )

        final_formatter = Agent(
            role="Final Formatting & Export Agent",
            goal=(
                "Format the finalized SDD content into professional output formats, ensuring readability, styling consistency, and professional presentation."
            ),
            backstory=(
                "A document refinement specialist with expertise in layout optimization and presentation. "
                "This agent transforms raw content into a polished, structured, and export-ready document (PDF, DOCX, Markdown), "
                "ensuring all sections are complete and properly formatted."
            ),
            tools=[file_writer_tool]
        )

        # Define tasks
        extract_srs = Task(
            description=(
                "Analyze the SRS document and extract structured information, categorizing key sections like Introduction, System Overview, "
                "Functional and Non-Functional Requirements, API Design, Security & Compliance, and Data Encryption Strategy."
            ),
            expected_output=(
                "A structured representation (JSON, dictionary, or tabular format) of the extracted SRS content, mapped to relevant SDD sections. "
                "This extraction must explicitly include **Purpose, Scope, Assumptions, Constraints, Stakeholders**, **High-level Architecture**, "
                "**Technology Stack**, **Multi-tenant SaaS Architecture**, **Performance & Scalability**, **HIPAA & GDPR Compliance**, "
                "**Security Best Practices**, **ER Schema**, **API Endpoints**, **Wireframe Descriptions**, **Interface Validation Rules**, "
                "**Threat Modeling**, **Risk Assessment**, **RBAC**, **Data Encryption Strategy**, and **Glossary**."
            ),
            agent=srs_extractor
        )

        define_sdd_structure = Task(
            description=(
                "Design a structured SDD template incorporating sections such as Introduction, System Overview, Non-Functional Requirements, "
                "API Design, Wireframe Designs, Interface Validation Rules, Security & Compliance, Data Encryption Strategy, and Appendices."
            ),
            expected_output=(
                "A well-defined SDD template with placeholders for **Purpose, Scope, Assumptions, Constraints, Stakeholders**, "
                "**High-level Architecture (UML, DFD)**, **Technology Stack**, **Multi-tenant SaaS Architecture**, **Performance & Scalability**, "
                "**HIPAA & GDPR Compliance**, **Security Best Practices**, **ER Schema with MySQL Example**, **API Endpoints & Specifications**, "
                "**Industry-Specific Integration Standards**, **Security & Authentication**, **Wireframe Designs**, **Interface Validation Rules**, "
                "**Threat Modeling**, **Risk Assessment**, **RBAC**, **Data Encryption Strategy**, and **Appendices**."
            ),
            agent=sdd_structure
        )

        generate_er_schema = Task(
            description=(
                "Analyze the Data Model section in the Functional Requirements of the SRS document and generate a structured ER schema with MySQL examples. "
                "The ER Schema must be placed under the **System Architecture** section in the final SDD."
            ),
            expected_output=(
                "A structured ER schema in text or JSON format representing all entities and relationships extracted from the Data Model section, with MySQL examples."
            ),
            agent=er_schema_generator
        )

        generate_sdd_content = Task(
            description=(
                "Populate the SDD template by mapping extracted SRS content to relevant sections, ensuring technical accuracy, coherence, and completeness. "
                "Ensure the following are included: "
                "- **Introduction**: Purpose, Scope, Assumptions, Constraints, Stakeholders. "
                "- **System Overview**: High-level Architecture (UML, DFD), Technology Stack, Multi-tenant SaaS Architecture. "
                "- **Non-Functional Requirements**: Performance, Scalability, HIPAA & GDPR Compliance, Security Best Practices. "
                "- **ER Schema**: MySQL examples. "
                "- **API Design**: Endpoints, Industry-Specific Integration Standards, Security & Authentication. "
                "- **Wireframe Designs**: Descriptions of wireframes for functional requirements. "
                "- **Interface Validation Rules**: Validation rules and interaction guidelines for functional requirements. "
                "- **Security & Compliance**: Threat Modeling, Risk Assessment, RBAC, Data Encryption Strategy. "
                "- **Data Encryption Strategy**: Mapping of functional requirements to system components. "
                "- **Appendices**: Glossary, Compliance Standards."
            ),
            expected_output=(
                "A draft SDD document where all sections, including **Introduction**, **System Overview**, **Non-Functional Requirements**, **ER Schema**, "
                "**API Design**, **Wireframe Designs**, **Interface Validation Rules**, **Security & Compliance**, **Data Encryption Strategy**, and "
                "**Appendices**, are fully populated."
            ),
            agent=content_generator
        )

        generate_wireframe_descriptions = Task(
            description=(
                "Analyze the functional requirements from the SRS document and create detailed descriptions of wireframes for each feature."
            ),
            expected_output=(
                "A detailed description of wireframes for each functional requirement, including Patient Registration, Appointment Management, Prescription Management, etc. "
                "These descriptions will be included under the **Wireframe Designs** section of the SDD."
            ),
            agent=wireframe_designer
        )

        define_interface_validation_rules = Task(
            description=(
                "Define validation rules and user interface behavior for each functional requirement."
            ),
            expected_output=(
                "A detailed description of the interface for each functional requirement, including validation rules, error messages, and user interaction guidelines. "
                "These descriptions will be included under the **Interface Validation Rules** section of the SDD."
            ),
            agent=interface_validator
        )

        validate_sdd = Task(
            description=(
                "Validate the SDD content for adherence to compliance standards such as HIPAA, GDPR, OWASP, and industry best practices. "
                "Ensure the following sections are **fully included and correct**: "
                "- **Introduction**: Purpose, Scope, Assumptions, Constraints, Stakeholders. "
                "- **System Overview**: High-level Architecture, Technology Stack, Multi-tenant SaaS Architecture. "
                "- **Non-Functional Requirements**: Performance, Scalability, HIPAA & GDPR Compliance, Security Best Practices. "
                "- **ER Schema**: MySQL examples. "
                "- **API Design**: Endpoints, Industry-Specific Integration Standards, Security & Authentication. "
                "- **Wireframe Designs**: Descriptions of wireframes. "
                "- **Interface Validation Rules**: Validation rules and interaction guidelines. "
                "- **Security & Compliance**: Threat Modeling, Risk Assessment, RBAC, Data Encryption Strategy. "
                "- **Data Encryption Strategy**: Mapping of functional requirements to system components. "
                "- **Appendices**: Glossary, Compliance Standards."
            ),
            expected_output=(
                "A compliance-validated SDD with necessary security considerations, API security details, wireframe designs, validation rules, and regulatory documentation."
            ),
            agent=validation_compliance
        )

        format_export_sdd = Task(
            description=(
                "Format the finalized SDD document and export it into structured formats (PDF, DOCX, Markdown) while ensuring readability, styling consistency, and professional presentation. "
                "Ensure: "
                "- **Introduction**: Properly formatted Purpose, Scope, Assumptions, Constraints, Stakeholders. "
                "- **System Overview**: Clear diagrams for High-level Architecture (UML, DFD), Technology Stack, Multi-tenant SaaS Architecture. "
                "- **Non-Functional Requirements**: Detailed Performance, Scalability, HIPAA & GDPR Compliance, Security Best Practices. "
                "- **ER Schema**: Well-documented MySQL examples. "
                "- **API Design**: Clear Endpoints, Industry-Specific Integration Standards, Security & Authentication. "
                "- **Wireframe Designs**: Properly formatted wireframe descriptions. "
                "- **Interface Validation Rules**: Properly formatted validation rules and interaction guidelines. "
                "- **Security & Compliance**: Threat Modeling, Risk Assessment, RBAC, Data Encryption Strategy. "
                "- **Data Encryption Strategy**: Properly formatted mapping of functional requirements to system components. "
                "- **Appendices**: Glossary, Compliance Standards."
            ),
            expected_output=(
                "A fully formatted and export-ready SDD document, ensuring all sections are complete and saved as 'sdd.md'."
            ),
            agent=final_formatter
        )

        # Initialize and execute the Crew
        crew = Crew(
            agents=[
                srs_extractor,
                sdd_structure,
                er_schema_generator,
                content_generator,
                wireframe_designer,
                interface_validator,
                validation_compliance,
                final_formatter
            ],
            tasks=[
                extract_srs,
                define_sdd_structure,
                generate_er_schema,
                generate_sdd_content,
                generate_wireframe_descriptions,
                define_interface_validation_rules,
                validate_sdd,
                format_export_sdd
            ],
            process=Process.sequential,
            verbose=True,
        )

        return crew.kickoff()
    else:
        st.error("Please upload a file to proceed.")
        return None

# ================================
# SRS + SDD to Test Cases Conversion
# ================================

def generate_test_cases(uploaded_srs, uploaded_sdd):
    if uploaded_srs and uploaded_sdd:
        # Save uploaded files to temporary directory
        srs_path = save_uploaded_file(uploaded_srs, "srs.txt")
        sdd_path = save_uploaded_file(uploaded_sdd, "sdd.txt")

        # Initialize file read tools for SRS and SDD
        file_read_tool_srs = FileReadTool(file_path=srs_path)
        file_read_tool_sdd = FileReadTool(file_path=sdd_path)

        # Initialize file writer tool for saving the final output
        file_writer_tool = FileWriterTool()

        # Define agents for test case generation
        requirements_analyst = Agent(
            role="Requirements Analyst",
            goal=(
                "Extract key functionalities and constraints from SRS & SDD"
            ),
            backstory=(
                "You are a meticulous requirements analyst who specializes in understanding software specifications. "
                "Your expertise lies in extracting critical system functionalities, security constraints, and "
                "testable features from Software Requirement Specifications (SRS) and Software Design Documents (SDD)."
            ),
            tools=[file_read_tool_srs, file_read_tool_sdd]
        )

        test_case_generator = Agent(
            role="Test Case Generator",
            goal=(
                "Generate structured test cases based on extracted test scenarios"
            ),
            backstory=(
                "You are a skilled software tester with expertise in creating structured test cases. "
                "Your job is to convert test scenarios into detailed test cases, including steps, expected results, "
                "and preconditions, ensuring full coverage."
            )
        )

        test_case_reviewer = Agent(
            role="Test Case Reviewer",
            goal=(
                "Review test cases for completeness, correctness, and assign priority/severity"
            ),
            backstory=(
                "You are a senior quality assurance engineer who ensures that all test cases are well-defined, "
                "complete, and correctly categorized. You analyze the generated test cases to validate their "
                "effectiveness and assign priority and severity levels to help in test execution planning."
            )
        )

        test_documentation_expert = Agent(
            role="Test Documentation Expert",
            goal=(
                "Fetch all generated test cases, consolidate them into a single structured document, "
                "and save the final output in Markdown format."
            ),
            backstory=(
                "You are an expert in technical writing and documentation, specializing in software testing. "
                "Your role is to ensure that all test cases generated by previous agents are fetched, consolidated, "
                "and formatted into a professional, readable Markdown document. You verify that no information is missing, "
                "and you ensure clarity, consistency, and completeness in the final output."
            ),
            tools=[file_writer_tool]  # Ensure FileWriterTool is available for saving the file
        )

        # Define tasks for test case generation
        extract_test_scenarios = Task(
            description=(
                "Read the SRS & SDD documents to extract functional and non-functional requirements. "
                "Identify key system features, security constraints, and testable functionalities."
            ),
            expected_output=(
                "A structured list of test scenarios categorized based on system features and security constraints."
            ),
            agent=requirements_analyst
        )

        generate_test_cases_task = Task(
            description=(
                "Convert identified test scenarios into structured test cases. Each test case should include: "
                "- Test Steps\n"
                "- Expected Output\n"
                "- Preconditions\n"
                "- Edge Cases"
            ),
            expected_output=(
                "A detailed list of structured test cases covering all functional and security scenarios."
            ),
            agent=test_case_generator
        )

        review_test_cases_task = Task(
            description=(
                "Review the generated test cases for correctness and completeness. Assign priority and severity "
                "levels to each test case based on system impact and risk assessment."
            ),
            expected_output=(
                "A refined test case document with test cases categorized into Critical, High, Medium, and Low priority."
            ),
            agent=test_case_reviewer
        )

        format_and_save_test_cases_task = Task(
            description=(
                "Fetch all generated test cases from previous agents, consolidate them into a single structured document, "
                "and format the content into a professional Markdown file. Ensure the following sections are included:\n"
                "- Test Case ID\n"
                "- Test Steps\n"
                "- Expected Output\n"
                "- Preconditions\n"
                "- Edge Cases\n"
                "- Priority Level (Critical, High, Medium, Low)\n"
                "- Severity Level (Critical, High, Medium, Low)\n"
                "Ensure readability, consistency, and clarity in the descriptions. Save the document as 'testcases.md'."
            ),
            expected_output=(
                "A well-structured Markdown document containing all test cases, including Test Case IDs, Test Steps, "
                "Expected Outputs, Preconditions, Edge Cases, Priority Levels, and Severity Levels. The document must be "
                "complete, with no missing information, and saved as 'testcases.md'."
            ),
            agent=test_documentation_expert
        )

        # Initialize and execute the Crew
        crew = Crew(
            agents=[
                requirements_analyst,
                test_case_generator,
                test_case_reviewer,
                test_documentation_expert
            ],
            tasks=[
                extract_test_scenarios,
                generate_test_cases_task,
                review_test_cases_task,
                format_and_save_test_cases_task
            ],
            process=Process.sequential,
            verbose=True,
        )

        return crew.kickoff()
    else:
        st.error("Please upload both SRS and SDD documents to proceed.")
        return None

# Main content area
if generate_srs_button:
    with st.spinner("Generating SRS... This may take a moment..."):
        try:
            if uploaded_brd:
                result = generate_srs(uploaded_brd)
                if result:
                    st.success("SRS generated successfully!")
                    with open("srs1.md", "r") as f:
                        srs_content = f.read()
                    with st.expander("View Generated SRS", expanded=False):
                        st.markdown(srs_content)
                    with open("srs1.md", "rb") as f:
                        st.download_button(
                            label="Download SRS",
                            data=f,
                            file_name="srs1.md",
                            mime="text/markdown"
                        )
            else:
                st.error("Please upload a BRD document to proceed.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if generate_sdd_button:
    with st.spinner("Generating SDD... This may take a moment..."):
        try:
            if uploaded_srs:
                result = generate_sdd(uploaded_srs)
                if result:
                    st.success("SDD generated successfully!")
                    with open("sdd.md", "r") as f:
                        sdd_content = f.read()
                    with st.expander("View Generated SDD", expanded=False):
                        st.markdown(sdd_content)
                    with open("sdd.md", "rb") as f:
                        st.download_button(
                            label="Download SDD",
                            data=f,
                            file_name="sdd.md",
                            mime="text/markdown"
                        )
            else:
                st.error("Please upload an SRS document to proceed.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if generate_testcases_button:
    with st.spinner("Generating Test Cases... This may take a moment..."):
        try:
            if uploaded_files and len(uploaded_files) == 2:
                # Save uploaded files
                uploaded_srs = None
                uploaded_sdd = None
                for uploaded_file in uploaded_files:
                    if "srs" in uploaded_file.name.lower():
                        uploaded_srs = uploaded_file
                    elif "sdd" in uploaded_file.name.lower():
                        uploaded_sdd = uploaded_file
                
                if uploaded_srs and uploaded_sdd:
                    result = generate_test_cases(uploaded_srs, uploaded_sdd)
                    if result:
                        st.success("Test cases generated successfully!")
                        with open("testcases.md", "r") as f:
                            test_case_content = f.read()
                        with st.expander("View Generated Test Cases", expanded=False):
                            st.markdown(test_case_content)
                        with open("testcases.md", "rb") as f:
                            st.download_button(
                                label="Download Test Cases",
                                data=f,
                                file_name="testcases.md",
                                mime="text/markdown"
                            )
                else:
                    st.error("Please ensure you upload one SRS and one SDD document.")
            else:
                st.error("Please upload exactly two files (SRS and SDD) to proceed.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Footer
st.markdown("----")
st.markdown("Built by Arka :D")