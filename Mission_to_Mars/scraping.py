# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager


def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemispheres": hemispheres(browser),
    }

    # Stop webdriver and return data
    browser.quit()
    return data


def mars_news(browser):

    # Scrape Mars News
    # Visit the mars nasa news site
    url = 'https://data-class-mars.s3.amazonaws.com/Mars/index.html'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None

    return news_title, news_p

def featured_image(browser):
    # Visit URL
    url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base url to create an absolute url
    img_url = f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{img_url_rel}'

    return img_url

def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('https://data-class-mars-facts.s3.amazonaws.com/Mars_Facts/index.html')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")

def hemispheres(browser):
    #Visit URL
    url ='https://marshemispheres.com/'
    browser.visit(url)
     #Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    #2a, create a list to hold the titles of the images
    results=img_soup.find_all('div', class_="collapsible results")
    results_titles=results[0].find_all('h3')

    #2b, iterate through the list to get the titles
    mars_titles=[]
    for title in results_titles:
        mars_titles.append(title.text)  

    #2c find the links to the thumbnails
    find_images=results[0].find_all('a')
    image_links=[]
    for images in find_images:
        if(images.img):
            image_url= url+ images['href']
            image_links.append(image_url)

    # 2d putting the url's of the images into a new list called url_local
    url_local=[]
    for url in image_links:
        url_local.append(url)

    # 2e iterate through the url_local list and obtain the .jpeg's from the url_local websites 
    jpeg_links=[]
    url_jpeg='https://marshemispheres.com/'    
    for url in url_local:
        browser.visit(url)
        html = browser.html
        img_soup = soup(html, 'html.parser')
        images=img_soup.find('img', class_='wide-image').get('src')
        jpeg_links.append(url_jpeg+images)
        #images=img_soup.find('div', class_='downloads')
        #jpegs=images.find('a')['href']
        #jpeg_links.append(url_jpeg+jpegs)

        #images=img_soup.find('img', class_='wide-image').get('src')
        #jpeg_links.append(url_jpeg+images)

    # 3. Write code to retrieve the image urls and titles for each hemisphere.
    hemisphere_image_urls=[]
    zip_files=zip(jpeg_links,mars_titles)
    for pics, titles in zip_files:
        dict={}
        dict['image_url']= pics
        dict['title']= titles
        hemisphere_image_urls.append(dict)
    return hemisphere_image_urls

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())
