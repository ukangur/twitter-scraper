from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import csv
import time
from datetime import datetime
import re
from tqdm import tqdm
import subprocess

def get_engagement_numbers(tweet):
    metrics = ["reply", "retweet", "like"]
    engagement_data = {metric: 0 for metric in metrics}
    
    for metric in metrics:
        try:
            metric_element = tweet.find_element(By.CSS_SELECTOR, f'[data-testid="{metric}"]')
            metric_value = metric_element.text
            if metric_value:
                if "K" in metric_value:
                    metric_value = float(metric_value.replace("K", "")) * 1000
                elif "M" in metric_value:
                    metric_value = float(metric_value.replace("M", "")) * 1000000
                engagement_data[metric] = int(metric_value)
            else:
                engagement_data[metric] = 0
        except:
            engagement_data[metric] = 0
            
    return engagement_data

def get_search_results_tweets(browser, search_query, max_scrolls=20):
    search_url = f'https://twitter.com/search?q={search_query}&src=typed_query&f=top'
    browser.get(search_url)
    tweet_details = []
    time.sleep(5)

    for _ in tqdm(range(max_scrolls)):
        browser.execute_script("window.scrollBy(0, window.innerHeight / 2.5);")

        tweets = browser.find_elements(By.CSS_SELECTOR, "article[role='article']")

        for tweet in tweets:
            try:
                tweet_data = {}
                tweet_id_element = tweet.find_element(By.CSS_SELECTOR, "a[href*='/status/']")
                tweet_id = tweet_id_element.get_attribute("href").split("/")[-1]
                tweet_data["Tweet ID"] = tweet_id
                user_name_text = tweet.find_element(By.CSS_SELECTOR, '[data-testid="User-Name"]').text

                name_match = re.search(r'^(.*?)\n(@\w+)', user_name_text)

                if name_match:
                    tweet_data["name"] = name_match.group(1).strip()
                    tweet_data["handle"] = name_match.group(2).strip()
                else:
                    tweet_data["name"] = ""
                    tweet_data["handle"] = ""

                tweet_text_elements = tweet.find_elements(By.CSS_SELECTOR, '[data-testid="tweetText"] > *')
                tweet_text = ""

                for element in tweet_text_elements:
                    if element.tag_name == "img" and "emoji" in element.get_attribute("src"):
                        tweet_text += element.get_attribute("alt")
                    else:
                        tweet_text += element.text

                tweet_data["tweetText"] = tweet_text
                tweet_date = tweet.find_element(By.CSS_SELECTOR, 'time').get_attribute("datetime")
                formatted_date = datetime.fromisoformat(tweet_date.replace("Z", "+00:00")).strftime('%Y-%m-%d %H:%M:%S')
                tweet_data["Date"] = formatted_date

                engagement = get_engagement_numbers(tweet)
                tweet_data.update(engagement)

                tweet_details.append(tweet_data)
            except Exception as e:
                continue

    return tweet_details

def deduplicate_tweets(tweet_details):
    deduplicated_data = {}
    for tweet_data in tweet_details:
        tweet_id = tweet_data["Tweet ID"]
        if tweet_id not in deduplicated_data:
            deduplicated_data[tweet_id] = tweet_data
        else:
            if len(tweet_data["tweetText"]) > len(deduplicated_data[tweet_id]["tweetText"]):
                deduplicated_data[tweet_id]["tweetText"] = tweet_data["tweetText"]

            for metric in ["like", "retweet", "reply"]:
                if tweet_data[metric] > deduplicated_data[tweet_id][metric]:
                    deduplicated_data[tweet_id][metric] = tweet_data[metric]

    return list(deduplicated_data.values())

def save_details_to_csv(data, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        fieldnames = ["Tweet ID", "name", "handle", "tweetText", "Date", "like", "retweet", "reply"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for tweet_data in data:
            writer.writerow(tweet_data)

def get_count(browser, data_testid):
    try:
        metric_element = browser.find_element(By.CSS_SELECTOR, f'[data-testid="{data_testid}"]')
        metric_value = metric_element.text
        if not metric_value:
            return 0
        elif "K" in metric_value:
            return int(float(metric_value.replace('K', '')) * 1000)
        elif "M" in metric_value:
            return int(float(metric_value.replace('M', '')) * 1000000)
        else:
            return int(metric_value.replace(',', ''))
    except NoSuchElementException:
        return 0

def get_tweet_metrics(browser, handle, tweet_id):
    base_url = f"https://twitter.com/{handle}/status/"
    full_url = base_url + tweet_id
    browser.get(full_url)
    browser.execute_script("window.scrollBy(0, document.body.scrollHeight * 0.4);")
    time.sleep(3)

    replies_count = get_count(browser, "reply")
    reposts_count = get_count(browser, "retweet")
    likes_count = get_count(browser, "like")

    return {
        "Replies": replies_count,
        "Reposts": reposts_count,
        "Likes": likes_count
    }

def update_csv_metrics(filename, browser):
    with open(filename, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    for row in tqdm(rows):
        if int(row["reply"]) == 0 or int(row["retweet"]) == 0 or int(row["like"]) == 0:
            handle = row["handle"].replace("@", "")
            tweet_id = row["Tweet ID"]
            metrics = get_tweet_metrics(browser, handle, tweet_id)

            row["reply"] = metrics["Replies"]
            row["retweet"] = metrics["Reposts"]
            row["like"] = metrics["Likes"]

    with open(filename, 'w', newline='', encoding='utf-8') as file:
        fieldnames = ["Tweet ID", "name", "handle", "tweetText", "Date", "like", "retweet", "reply"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def main():
    search_query = input("Enter keyword to scrape here: ")
    command = r'"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222'
    subprocess.Popen(command, shell=True)
    time.sleep(3)
    service = Service("chromedriver.exe")
    options = webdriver.ChromeOptions()
    options.debugger_address = "127.0.0.1:9222"
    browser = webdriver.Chrome(service=service,options=options)

    tweet_details = get_search_results_tweets(browser, search_query, 500)
    tweet_details_deduplicated = deduplicate_tweets(tweet_details)
    save_details_to_csv(tweet_details_deduplicated, f'{search_query}.csv')

    update_csv_metrics(f'{search_query}.csv', browser)

    browser.quit()

if __name__ == "__main__":
    main()