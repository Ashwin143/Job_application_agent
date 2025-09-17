import os,re
import time
from google import genai
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv


# --- Configuration ---
# This line reads the .env file and loads the variables into the environment
load_dotenv()

# Set up the Gemini API key


URLS_FILE = "urls.txt"
BASE_RESUME_FILE = "resume.md"
OUTPUT_DIR = "output"

# --- NEW: LinkedIn Login Function ---
def login_to_linkedin(driver, email, password):
    """Navigates to LinkedIn and logs in using provided credentials."""
    try:
        print("Logging into LinkedIn...")
        driver.get("https://www.linkedin.com/login")
        time.sleep(3) # Wait for the login page to load

        # Find email and password fields and enter credentials
        email_field = driver.find_element(By.ID, "username")
        email_field.send_keys(email)
        
        password_field = driver.find_element(By.ID, "password")
        password_field.send_keys(password)

        # Click the login button
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        
        print("Login successful.")
        time.sleep(5) # Wait for the homepage to load after login
        return True

    except Exception as e:
        print(f"Error during login: {e}")
        print("Login failed. This could be due to incorrect credentials, a CAPTCHA, or 2FA.")
        return False



# --- MODIFIED: Web Scraping with Selenium ---
def scrape_job_details(url, email, password, save_folder="saved_pages"):
    """
    Logs into LinkedIn, navigates to a job URL, saves the page as HTML,
    and then scrapes job details from the saved file.
    """
    print(f"Starting process for job URL: {url}")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    
    try:
        # 1. Log in to LinkedIn
        if not login_to_linkedin(driver, email, password):
            return None # Stop if login fails

        # 2. Navigate to the job URL
        driver.get(url)
        print("Navigated to job page. Waiting for content to load...")
        
        # Wait for the main job details container to be present (more reliable than time.sleep)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "job-details"))
        )
        print("Job page content loaded.")

        # 3. Save the fully rendered page to an HTML file
        page_source = driver.page_source
        
        # Create a safe filename from the job URL
        job_id = re.search(r'/view/(\d+)/', url)
        filename = f"job_{job_id.group(1) if job_id else 'details'}.html"
        
        # Create the save folder if it doesn't exist
        os.makedirs(save_folder, exist_ok=True)
        file_path = os.path.join(save_folder, filename)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(page_source)
        print(f"✅ Page successfully saved as: {file_path}")

        # 4. Scrape the necessary text from the SAVED HTML FILE
        print(f"Parsing data from the saved file: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            saved_html = f.read()
        
        soup = BeautifulSoup(saved_html, 'lxml')
        if soup.title and soup.title.string:
            title_text = soup.title.string
           
            parts = title_text.split('|')
    
            if len(parts) >= 2:
            
                job_title = parts[0].strip()
                company = parts[1].strip()
        

        
        details_container = soup.find('div', id='job-details')
        
        job_description = "Job Description not found in saved file."
        if details_container:
            job_description = details_container.get_text(strip=True)
            print("✅ Successfully extracted job details.")
        
        return {
            "source_file": file_path,
            "company": company,
            "title": job_title,
            "description": job_description
        }

    except Exception as e:
        print(f"An error occurred during the process: {e}")
        return None
    finally:
        if 'driver' in locals():
            driver.quit()
            print("Browser closed.")



# --- File Handling (Unchanged) ---
def read_file_content(filepath):
    """Reads and returns the content of a file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def save_output(filename, content):
    """Saves content to a file in the output directory."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    with open(os.path.join(OUTPUT_DIR, filename), "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Successfully saved: {filename}")

# --- LLM-Powered Generation (Unchanged) ---
def tailor_resume(model, base_resume, job_details):
    """Uses Gemini to tailor a resume for a specific job."""
    print(f"Tailoring resume for {job_details['title']} at {job_details['company']}...")
    prompt = f"""
    You are an expert career coach and resume writer.
    Your task is to tailor the following base resume to perfectly match the provided job description.

    **Base Resume:**
    ---
    {base_resume}
    ---

    **Job Description:**
    ---
    Company: {job_details['company']}
    Job Title: {job_details['title']}
    Description: {job_details['description']}
    ---

    **Instructions:**
    1.  Rewrite the 'Summary' section to be a powerful, concise pitch directly addressing the key requirements of the job description.
    2.  In the 'Experience' section, rephrase bullet points to highlight the achievements and skills most relevant to the job. Use keywords from the job description naturally. Quantify achievements where possible (e.g., "increased performance by 30%").
    3.  Adjust the 'Skills' section to feature the most relevant skills from the job description at the top.
    4.  Maintain a professional tone and the original Markdown formatting.
    5.  Do not add any information that is not present in the base resume. Only rephrase and reorder existing information.

    Return only the tailored resume in Markdown format.
    """
    response = model.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return response.text

def generate_cover_letter(model, tailored_resume, job_details):
    """Uses Gemini to generate a cover letter."""
    print(f"Generating cover letter for {job_details['title']} at {job_details['company']}...")
    prompt = f"""
    You are a professional cover letter writer.
    Your task is to write a compelling and concise cover letter based on the tailored resume and the job description.

    **Tailored Resume:**
    ---
    {tailored_resume}
    ---

    **Job Description:**
    ---
    Company: {job_details['company']}
    Job Title: {job_details['title']}
    Description: {job_details['description']}
    ---

    **Instructions:**
    1.  Structure the cover letter with a clear introduction, body, and conclusion.
    2.  In the introduction, state the position you are applying for and where you saw it. Express enthusiasm for the company.
    3.  In the body, highlight 2-3 key experiences or skills from the resume that directly align with the most important requirements in the job description. Do not just list skills; explain how you used them to achieve results.
    4.  In the conclusion, reiterate your interest, express your confidence in your ability to contribute, and include a call to action (e.g., "I am eager to discuss my qualifications further...").
    5.  The tone should be professional, confident, and tailored to the company. Keep it to about 3-4 paragraphs.
    6.  Address it to the "Hiring Manager" if no specific name is available.
    7.  Should not be more than 1000 words.

    Return only the cover letter text.
    """
    response = model.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return response.text
  

# --- MODIFIED: Main Execution ---
def main():
    """The main function to run the agent."""
    # Load LinkedIn credentials from environment
    linkedin_email = "ashwinparthasarathy30@gmail.com"
    linkedin_password = "@Germany4money"

    if not linkedin_email or not linkedin_password:
        print("Error: LINKEDIN_EMAIL and LINKEDIN_PASSWORD must be set in your .env file.")
        return

    gemini_model = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    base_resume_content = read_file_content(BASE_RESUME_FILE)
    
    with open(URLS_FILE, "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    for url in urls:
        # Pass credentials to the scraping function
        job_details = scrape_job_details(url, linkedin_email, linkedin_password)
        
        if job_details != "N/A":
         
            # # Generate tailored content
            tailored_resume = tailor_resume(gemini_model, base_resume_content, job_details)
            cover_letter = generate_cover_letter(gemini_model, tailored_resume, job_details)

            # Save the files
            sanitized_company = "".join(c for c in job_details['company'] if c.isalnum() or c in (' ', '_')).rstrip()
            sanitized_title = "".join(c for c in job_details['title'] if c.isalnum() or c in (' ', '_')).rstrip()
            
            resume_filename = f"{sanitized_company} - {sanitized_title} - Resume.md"
            cover_letter_filename = f"{sanitized_company} - {sanitized_title} - Cover Letter.md"



            save_output(resume_filename, tailored_resume)
            save_output(cover_letter_filename, cover_letter)
            print("-" * 40)
        else:
            print(f"Skipping URL due to scraping error: {url}")
            print("-" * 40)

if __name__ == "__main__":
    main()