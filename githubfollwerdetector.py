import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import streamlit as st
import pandas as pd
from base64 import b64encode
from tqdm import tqdm
import time  # Added for a brief delay to show progress

# Function to scrape follower details and calculate total followers
def scrape_followers(base_url, num_pages, scrape_until_end, progress_bar):
    follower_data = []
    total_followers = 0

    with st.spinner("Calculating total followers..."):
        if scrape_until_end:
            current_page = 1
            while True:
                page_url = f"{base_url}{current_page}"
                response = requests.get(page_url)
                soup = BeautifulSoup(response.content, 'html.parser')

                follower_links = soup.find_all('a', class_='d-inline-block no-underline mb-1')
                if not follower_links:
                    break

                total_followers += len(follower_links)
                current_page += 1

        else:
            for page_number in tqdm(range(1, num_pages + 1), desc="Scraping pages"):
                page_url = f"{base_url}{page_number}"
                response = requests.get(page_url)
                soup = BeautifulSoup(response.content, 'html.parser')

                follower_links = soup.find_all('a', class_='d-inline-block no-underline mb-1')
                total_followers += len(follower_links)

    st.text(f"Total Followers: {total_followers}")

    # Now scrape follower details
    st.text("Scraping follower details...")
    with tqdm(total=total_followers, desc="Scraping followers") as pbar:
        if scrape_until_end:
            current_page = 1
            while True:
                page_url = f"{base_url}{current_page}"
                response = requests.get(page_url)
                soup = BeautifulSoup(response.content, 'html.parser')

                follower_links = soup.find_all('a', class_='d-inline-block no-underline mb-1')
                if not follower_links:
                    break

                for link in follower_links:
                    username = link['href'].split('/')[-1]
                    profile_url = urljoin(base_url, link['href'])
                    # Extract repository URL
                    repo_url = f"https://github.com/{username}?tab=repositories"
                    follower_data.append((username, profile_url, repo_url))
                    pbar.update(1)
                    progress_bar.progress(pbar.n / pbar.total)  # Update Streamlit progress bar
                    time.sleep(0.01)  # Add a brief delay to show progress
                current_page += 1

        else:
            for page_number in tqdm(range(1, num_pages + 1), desc="Scraping pages"):
                page_url = f"{base_url}{page_number}"
                response = requests.get(page_url)
                soup = BeautifulSoup(response.content, 'html.parser')

                follower_links = soup.find_all('a', class_='d-inline-block no-underline mb-1')
                for link in follower_links:
                    username = link['href'].split('/')[-1]
                    profile_url = urljoin(base_url, link['href'])
                    # Extract repository URL
                    repo_url = f"https://github.com/{username}?tab=repositories"
                    follower_data.append((username, profile_url, repo_url))
                    pbar.update(1)
                    progress_bar.progress(pbar.n / pbar.total)  # Update Streamlit progress bar
                    time.sleep(0.01)  # Add a brief delay to show progress

    return follower_data

# Function to generate download link
def get_table_download_link(df, file_format):
    if file_format == "HTML":
        df_html = df.to_html(escape=False, index=False)
        filename = f"{github_username}_followers.html"
        href = f'<a href="data:text/html;base64,{b64encode(df_html.encode()).decode()}" download="{filename}">Download HTML</a>'
    elif file_format == "XLSX":
        filename = f"{github_username}_followers.xlsx"
        df.to_excel(filename, index=False)
        href = f'<a href="{filename}" download="{filename}">Download XLSX</a>'
    else:
        href = ""

    return href

# Streamlit app
st.title("GitHub Follower Scraper")

# Input for GitHub username
github_username = st.text_input("Enter GitHub Username:")
base_url = f"https://github.com/{github_username}?tab=followers&page="

# Input for the number of pages to scrape or scraping until the end
scrape_options = st.radio("Scrape:", ("Specific Number of Pages", "Scrape Until End Page"))
if scrape_options == "Specific Number of Pages":
    num_pages_input = st.text_input("Enter the number of pages to scrape:")
    if num_pages_input.isnumeric():
        num_pages = int(num_pages_input)
    else:
        num_pages = 1  # Default to 1 page if invalid input
else:
    num_pages = None

if st.button("Scrape Followers"):
    st.info("Scraping in progress... Please wait.")
    progress_bar = st.progress(0)  # Initialize Streamlit progress bar
    follower_data = scrape_followers(base_url, num_pages, scrape_options == "Scrape Until End Page", progress_bar)

    # Display the scraped data in a table
    df = pd.DataFrame(follower_data, columns=["Username", "Profile URL", "Repository URL"])
    st.write(df)

    # Download buttons for HTML and XLSX
    st.markdown(get_table_download_link(df, "HTML"), unsafe_allow_html=True)
    st.markdown(get_table_download_link(df, "XLSX"), unsafe_allow_html=True)

# Add a hyperlink to the external URL
st.markdown("[Visit GitHub Assignment Detector](https://githuubassignmentdetector.streamlit.app/)")
