# AI-Resume-Critiquer

This web application leverages Meta's open-source LLM, Llama, to provide constructive resume feedback. Outputs can be changed depending on the job description, creativity level, response length, and depth of analysis.


## Setup Instructions

1. **Install Python** (if not already installed):  
   Download and install Python from [python.org](https://www.python.org/downloads/).

2. **Install required Python dependencies:**  
   Open a terminal in the project directory and run:  
   ```bash
   pip install streamlit
    ```
3. **Install Ollama**
   Install your prefered Ollama model  [here](https://ollama.com/) (recommended Llama 3.2-3B)

## Running the App
Once all the dependencies are installed and Ollama has been successfully configured, type
``` bash
streamlit run main.py
```
in your terminal and hit Enter. The app should open automatically in your browser, ready for use. 