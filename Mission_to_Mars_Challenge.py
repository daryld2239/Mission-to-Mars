# Import Splinter and Beautiful Soup and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt

def scrape_all():


    # Initiate headless driver for deployment
    executable_path = {'executable_path': '/Users/dushyantkatragadda/.wdm/drivers/chromedriver/mac64/88.0.4324.96/chromedriver'}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

    hemisphere_image_urls = hemisphere(browser)

    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemispheres": hemisphere_image_urls,
        "last_modified": dt.datetime.now()
    }

    # Stop webdriver and return data
    browser.quit()
    return data

def mars_news(browser):

    # Visit the MARS NASA news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('ul.item_list li.slide',wait_time = 1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')
    
    # Add try/except for error handling
    try:
        
    
        slide_elem = news_soup.select_one('ul.item_list li.slide')

        slide_elem.find('div', class_='content_title')

        # Use the parent element to find the first 'a' tag and save it as news_title
        news_title = slide_elem.find('div',class_='content_title').get_text()

        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div',class_='article_teaser_body').text

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
    img_soup = soup(html,'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{img_url_rel}'

    return img_url

def mars_facts():

    # Add try/except for error handling
    try:
        # Use read_html to scrape the facts table into a dataframe
        df = pd.read_html('http://space-facts.com/mars/')[0]

    except BaseException:
        return None

    # Assign columns and set the index for the dataframe
    df.columns=['Description','Value']
    df.set_index('Description',inplace = True)
    
    # Convert the dataframe into HTML format and add bootstrap
    return df.to_html()


def hemisphere(browser):
    # 1. Use browser to visit the URL 
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)


    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # 3. Write code to retrieve the image urls and titles for each hemisphere.

    html_hemis = browser.html

    # Parsing HTML with BeautifulSoup
    hemis_soup = soup(html_hemis,'html.parser')

    # Retrieving the items that contain the info on images and titles
    items = hemis_soup.find_all('div',class_='item')

    # Create the base url for the images
    base_url = 'https://astrogeology.usgs.gov'

    # Retrieving the individual item titles and images
    for item in items:
        # Retrieving the title
        title=item.find('h3').text

        # Retrieve link that leads to the full image website
        partial_img_url = item.find('a',class_='itemLink product-item')['href']

        # Visit the URL to get the full image
        browser.visit(base_url + partial_img_url)

        img_html = browser.html

        img_soup = soup(img_html,'html.parser')

        # Retrieving the link for the jpeg image
        img_url = img_soup.find('a', text='Sample')['href']

        # Appending the results to the list hemisphere_image_urls
        hemisphere_image_urls.append({'img_url': img_url, 'title':title})


    # 4. Print the list that holds the dictionary of each image url and title.
    return hemisphere_image_urls


if __name__ == '__main__':
    # If running as script, print scraped data
    print(scrape_all())





