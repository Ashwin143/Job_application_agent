# Job_application_agent
Implementation of automatic resume and cover letter writing tailored various job roles leveraging Gemini_2.5 flash



This project automatically generates tailored resumes and cover letter based on job descriptions .all user needs to provide is the linkedin job url.

## Features

- Parses job descriptions from HTML files.
- Extracts key information like job title and description.
- Appends job-specific information to a base resume.
- Saves tailored resumes in a designated directory.

## How it Works

The `resume_agent.py` script performs the following steps:

1.  **Reads a base resume:** It starts with a generic resume template named `resume.md`.
2.  **Parses job descriptions:** It iterates through HTML files in the `jobs` directory, which are assumed to be saved job postings.
3.  **Extracts details:** For each job description, it extracts the job title and the full job description text.
4.  **Creates a tailored resume:** It combines the base resume with the extracted job title and description.
5.  **Saves the new resume:** The newly created resume is saved in the `tailored_resumes` directory with a filename corresponding to the company.

## Usage

1.  **Add your base resume:** Create a file named `resume.md` in the root directory of the project. This will be your template.
2.  **Save job descriptions:** Save the HTML of job descriptions you are interested in into the `jobs` directory.
3.  **Run the script:**
    ```bash
    python resume_agent.py
    ```
4.  **Find your tailored resumes:** The generated resumes will be located in the `tailored_resumes` directory.

## Project Structure

```
.
├── saved_pages/
│   └── (job_description_1.html, ...)
├── output/
│   └── (company_name_resume.md, ...)
├── main.py
└── resume.md
└── requirements.txt
└── urls.txt
```
```