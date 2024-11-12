# Scholarships
Web Scraping for NSW University Scholarships

The following git repo contains a task for Scholarships Operations Group in which we research the scholarships being offered at the following universities:
- UNSW - **Done**
- USYD - The final boss 
- Charles Sturt - **Done** 
- University of Wollongong - **Done** 
- University of Newcaslte - **Done**
- Maquarie University - **Done**
- UTS - **Done**

The main goal is to collect information on their Equity, High Potential and Humanitarian Scholarships. For now, some have been done manually when convenient
while others have been automated using web scrapping. 

<br> 

### Updates

- All cleaning (bar asylum seeker) has been down for all universities except for USYD. Only 360 (LOL) to go. Some of these will be deleted but omg. 

<br> 

### USYD

USYD has $480$ URLs (currently) across $19$ pages. The scrip `usyd_urls.py` iterates over these pages and collects all hrefs from the page, concatonates the reference
with the base USYD URL and saves the resulting list in a pickle object. Additionally, a check has been made to ensure only new URLs are added to the list. 

<br>

The scholarships pages on USYD are inconsistent in the formatting and a number of the pages are inactive, which leaves us with roughly $430$ pages in total. In 
`USY_scrape.py`, I have decided to start the code from scratch. Integrating code from the other university scraping scripts was not feasible. 

<br>

USYD is a nightmare with this method. Get what we can with the level of the degree and then bite the bullet and fix manually. 
