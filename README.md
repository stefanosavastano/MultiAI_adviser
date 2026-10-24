# Angel vs Demon: The Promotion Competition

Angel vs Demon is a multi-agent conversational AI application where the user interacts with two rival spiritual entities: Sunny (the Angel) and Crowley (the Demon). Both agents compete for a corporate promotion within their respective realms, and the only way to achieve it is by persuading you to make choices aligned with their faction during complex moral dilemmas.

The application features an interactive chat interface, a dynamic soul-tracking alignment system, and an automated Judge that evaluates your final arguments to shift the balance of power.

---

## Setup and Execution Instructions

### Prerequisites
Ensure Python 3.9+ is installed on your system.

### 1. Clone the Repository
Navigate to the project directory using your terminal:

cd your_directory

### 2. Install Dependencies

Install the required packages specified in the requirements file:

pip install -r requirements.txt

### 3. Environment Configuration
Paste your personal OpenAI API key using:

echo "OPENAI_API_KEY=your_actual_api_key_here" > .env

### 4. Run the Application
Launch the web interface by running the Streamlit server:

streamlit run app.py