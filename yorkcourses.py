import requests
from bs4 import BeautifulSoup
import json
import re

# List of URLs to scrape
URLS = [
   "https://apps1.sis.yorku.ca/WebObjects/cdm.woa/Contents/WebServerResources/FW2024LE.html",
   "https://apps1.sis.yorku.ca/WebObjects/cdm.woa/Contents/WebServerResources/FW2024AP.html",
   "https://apps1.sis.yorku.ca/WebObjects/cdm.woa/Contents/WebServerResources/FW2024SC.html",
   "https://apps1.sis.yorku.ca/WebObjects/cdm.woa/Contents/WebServerResources/FW2024SB.html"
]

courses = []

pages = []
for url in URLS:
    response = requests.get(url)
    if response.status_code == 200:
        pages.append(response)
    else:
        print(f"Failed to fetch {url}, Status Code: {response.status_code}")

soups = [BeautifulSoup(page.content, 'html5lib') for page in pages]

for i, soup in enumerate(soups):
    print(f"Processing URL: {URLS[i]}")
    session_year = URLS[i].split("/")[-1].split(".")[0]
    session = session_year[:2]
    year = session_year[2:6]
    table = soup.find('tbody')

    if table:
        rows = table.find_all(True, recursive=False)
        if len(rows) > 2:
            rows.pop(0)
            course = {}
            section = {}
            term = ""
            
            for row in rows:
                columns = row.find_all(True, recursive=False)
                
                if row.find(class_='bodytext'):
                    course = {
                        "faculty": columns[0].get_text().strip(),
                        "subject": columns[1].get_text().strip(),
                        "name": columns[3].get_text().strip(),
                        "section": []
                    }
                    if course not in courses:
                        courses.append(course)
                    term = columns[2].get_text().strip()
                
                # Check for sections with 3 columns split
                elif len(columns[1].get_text().strip().split()) == 3:
                    # Make sure column data exists
                    if len(columns) >= 8:
                        for br in columns[4].find_all("br"):
                            br.replace_with("\n")
                        for br in columns[6].find_all("br"):
                            br.replace_with("\n")

                        num_credit_sect = columns[0].get_text().strip().split()
                        course["number"] = num_credit_sect[0]
                        course["credits"] = num_credit_sect[1]
                        course["language"] = columns[1].get_text().strip()
                        section = {
                            "letter": num_credit_sect[2],
                            "term": term,
                            "session": session,
                            "year": year,
                            "director": "",
                            "offering": []
                        }
                        course["section"].append(section)
                        notes = columns[7].get_text().strip().replace("Expanded Course Description", "").replace("Course Outline", "")
                        
                        offering = {
                            "type": columns[2].get_text().strip(),
                            "number": columns[3].get_text().strip(),
                            "instructor": [" ".join(instr.strip().split()) for instr in columns[6].get_text().strip().splitlines()],
                            "time": [],
                            "catalogueCode": [" ".join(cat.strip().split()) for cat in columns[4].get_text().strip().splitlines()],
                            "notes": notes
                        }
                        section["offering"].append(offering)

                        # Parse time data
                        time_rows = columns[5].find_all("tr")
                        for time_row in time_rows:
                            time_details = time_row.find_all(True, recursive=False)
                            if time_details and len(time_details) >= 4 and time_details[0].get_text().strip().isalpha():
                                time = {
                                    "day": time_details[0].get_text().strip(),
                                    "startTime": time_details[1].get_text().strip(),
                                    "duration": int(time_details[2].get_text().strip()),
                                    "location": time_details[3].get_text().strip(),
                                }
                                offering["time"].append(time)
                    
                # Handling other section structures
                else:
                    if len(columns) >= 6:
                        for br in columns[4].find_all("br"):
                            br.replace_with("\n")
                        for br in columns[2].find_all("br"):
                            br.replace_with("\n")
                        
                        notes = columns[5].get_text().strip().replace("Expanded Course Description", "").replace("Course Outline", "")
                        offering = {
                            "type": columns[0].get_text().strip(),
                            "number": columns[1].get_text().strip(),
                            "instructor": [" ".join(instr.strip().split()) for instr in columns[4].get_text().strip().splitlines()],
                            "time": [],
                            "catalogueCode": [" ".join(cat.strip().split()) for cat in columns[2].get_text().strip().splitlines()],
                            "notes": notes
                        }
                        section["offering"].append(offering)

                        # Parse time data
                        time_rows = columns[3].find_all("tr")
                        for time_row in time_rows:
                            time_details = time_row.find_all(True, recursive=False)
                            if time_details and len(time_details) >= 4 and time_details[0].get_text().strip().isalpha():
                                time = {
                                    "day": time_details[0].get_text().strip(),
                                    "startTime": time_details[1].get_text().strip(),
                                    "duration": int(time_details[2].get_text().strip()),
                                    "location": time_details[3].get_text().strip(),
                                }
                                offering["time"].append(time)

    else:
        print(f"No table found for URL: {URLS[i]}")

# Step 4: Save the results to a JSON file
with open('courses.json', 'w') as outfile:
    json.dump(courses, outfile, indent=4)

print("Scraping completed and saved to 'courses.json'")
