# twitter-scraper

# Twitter Scraper using Selenium: A Step-by-Step Tutorial

In this tutorial, we'll walk you through how to scrape Twitter using Selenium. The script captures tweet details based on a given search keyword and saves the results to a CSV file. This code only works on Windows machines at the moment.

## Prerequisites:

### 1. Python
Ensure you have Python installed. If not, download and install Python from [python.org](https://www.python.org/downloads/).

### 2. Google Chrome
You need to have Google Chrome installed since the script uses Chrome as its browser. Download it [here](https://www.google.com/chrome/).

### 3. ChromeDriver
Download ChromeDriver which is necessary for Selenium to interface with the Chrome browser. Make sure to download a version that matches your Chrome browser version from [this link](https://sites.google.com/chromium.org/driver/).

### 4. Required Python Libraries
Install the necessary libraries using `pip`:

```bash
pip install selenium tqdm
```
## Setting up:
### Clone the Repository or Download the Script:
If you're using git, you can clone the repository. If you're not, simply download the script and save it to a preferred directory.

### Move ChromeDriver:
After downloading ChromeDriver, place the chromedriver.exe (Windows) into the same directory as the code.

## Execution:
### Run the Script:
Navigate to the directory containing the script in your terminal or command prompt, then run:

```bash
py keywordtweets.py
```
Replace script_name.py with the name you saved the script as.

### Input Keyword:
You'll be prompted to enter a search keyword. This keyword is what the script will use to find and scrape tweets from Twitter.

### Wait:
The script will launch a Chrome instance, navigate to Twitter, and begin the scraping process. This might take a while depending on the number of tweets it finds and processes. Usual running time is 30 minutes per keyword.

### Results:

Once completed, you'll find a CSV file named after your keyword in the same directory. This file contains the scraped tweet details.

## Important Notes:
The script uses Chrome's remote debugging port to interface with an existing Chrome session. Ensure no other processes are using port 9222.
