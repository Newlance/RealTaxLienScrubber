from fileinput import filename
from bs4 import BeautifulSoup as bs
import pandas as pd
import requests
import os

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
# US english
LANGUAGE = "en-US,en;q=0.5"
perfMode = True
counties = ["columbiafl","dixiefl","duvalfl","gadsdenfl","gilchristfl","hendryfl","hernandofl","highlandsfl","lafayettefl","leefl","orangefl","palmbeachfl","polkfl","putnamfl","sarasotafl","seminolefl","suwanneefl","taylorfl"]
def post_soup(url,body):
    """Constructs and returns a soup using the HTML content of `url` passed"""
    
    # initialize a session
    session = requests.Session()
    # set the User-Agent as a regular browser
    session.headers['User-Agent'] = USER_AGENT
    # request for english content (optional)
    session.headers['Accept-Language'] = LANGUAGE
    session.headers['Content-Language'] = LANGUAGE
    # make the request
    html = requests.post(url, data = body)
    # return the soup
    return bs(html.content, "html.parser")

def get_soup(url):
    """Constructs and returns a soup using the HTML content of `url` passed"""
    # initialize a session
    session = requests.Session()
    # set the User-Agent as a regular browser
    session.headers['User-Agent'] = USER_AGENT
    # request for english content (optional)
    session.headers['Accept-Language'] = LANGUAGE
    session.headers['Content-Language'] = LANGUAGE
    # make the request
    html = requests.get(url)
    # return the soup
    return bs(html.content, "html.parser")


def get_all_tables(soup):
    """Extracts and returns all tables in a soup object"""
    return soup.find_all("table")

def verifyFolder(path):
    isExist = os.path.exists(path)

    if not isExist:    
        # Create a new directory because it does not exist 
        os.makedirs(path)
        print("The new directory is created!")

    return path

def get_table_headers(table):
    """Given a table soup, returns all the headers"""
    headers = []
    for th in table.find("tr").find_all("td"):
        headers.append(th.text.strip())
    headers.pop(10)
    headers.pop(9)
    headers.pop(7)
    headers.pop(6)
    headers.pop(2)
    headers.pop(1)
    headers.append("address")
    headers.append("USE")
    headers.append("Year Built")
    headers.append("Construction type")
    headers.append("beds")
    headers.append("Baths")
    headers.append("Sale Date")
    headers.append("Sale Price")
    headers.append("Gross Sq Ft")
    headers.append("Tax area")
    headers.append("Area")
    headers.append("Living sq ft")
    headers.append("Legal Description")
    headers.append("Section")
    headers.append("Township")
    headers.append("Range")
    return headers


def get_table_rows(table,details):
    """Given a table, returns all its rows"""
    rows = []
    for tr in table.find_all("tr")[1:]:
        certid = str(tr.get('id'))[-7:]
        body = {'certID': certid,
            'page': 'certpop-property-details.cfm',}
        cells = []
        # grab all td tags in this table row
        tds = tr.find_all("td")

        # use regular td tags
        i=0

        while i<len(tds):
            if i==3:
                try:                        
                    h = tds[i].find('a').get('href')
                    cells.append(h)                        
                except:
                    cells.append(tds[i].text.strip())
            elif i==5:
                if perfMode == False or tds[i].text.strip()=="Active":
                    #print("Pass")
                    cells.append(tds[i].text.strip())                    
                    try:
                        detailsPage = post_soup(details,body)
                        detailsTable = get_all_tables(detailsPage)[1]
                        ##add address
                        cells.append(detailsTable.find_all("tr")[2].find_all("td")[1].text.strip())
                        ##add use code
                        cells.append(detailsTable.find_all("tr")[3].find_all("td")[1].text.strip())
                        ##Year Built
                        cells.append(detailsTable.find_all("tr")[4].find_all("td")[1].text.strip())
                        ##Construction type
                        cells.append(detailsTable.find_all("tr")[5].find_all("td")[1].text.strip())
                        ##beds
                        cells.append(detailsTable.find_all("tr")[6].find_all("td")[1].text.strip())
                        ##Baths
                        cells.append(detailsTable.find_all("tr")[7].find_all("td")[1].text.strip())
                        #Sale Date
                        cells.append(detailsTable.find_all("tr")[8].find_all("td")[1].text.strip())
                        #Sale Price
                        cells.append(detailsTable.find_all("tr")[9].find_all("td")[1].text.strip())
                        #Gross Sq Ft
                        cells.append(detailsTable.find_all("tr")[10].find_all("td")[1].text.strip())
                        #Tax area
                        cells.append(detailsTable.find_all("tr")[11].find_all("td")[1].text.strip())
                        #Area
                        cells.append(detailsTable.find_all("tr")[12].find_all("td")[1].text.strip())
                        #Living sq ft
                        cells.append(detailsTable.find_all("tr")[13].find_all("td")[1].text.strip())
                        #Legal Description
                        cells.append(detailsTable.find_all("tr")[14].find_all("td")[1].text.strip())
                        #Section
                        cells.append(detailsTable.find_all("tr")[15].find_all("td")[1].text.strip())
                        #Township
                        cells.append(detailsTable.find_all("tr")[16].find_all("td")[1].text.strip())
                        #Range
                        cells.append(detailsTable.find_all("tr")[17].find_all("td")[1].text.strip())
                    except:
                        i=0
                        while i<16:
                            cells.append("N/A")
                            i=i+1
                    
                else:
                    cells.append(tds[i].text.strip())
                    i=0
                    while i<16:
                        cells.append("N/A")
                        i=i+1
                    
            else:
                cells.append(tds[i].text.strip())    
            i=i+1    
        rows.append(cells)
    rows.pop(2)
    rows.pop(1)
    rows.pop(0)  
    return rows


def save_as_csv(table_name, headers, rows):
    pd.DataFrame(rows, columns=headers).to_csv(f"{table_name}.csv")



def main():    
    # get the soup
    for county in counties:
        url = f"https://{county}.realtaxlien.com/index.cfm?folder=previewitems"
        details = f"https://{county}.realtaxlien.com/popup/popup-certificates.cfm"        
        soup = get_soup(url)  
        try:
            numPages = len(soup.find('select'))
        except:
            continue
        page=1
        all_rows = []
            
        while page <= numPages:
            body = {'pageNum': page,
                'orderBy': 'AdvNum',
                'orderDir': 'asc',
                'gotoPageNum': '1',
                'gotoPageNum': '1'}
            soup = post_soup(url,body)
            # extract all the tables from the web page    
            tables = get_all_tables(soup)               
            # get the table headers
            headers = get_table_headers(tables[0])            
            # get all the rows of the table
            rows = get_table_rows(tables[0],details)                             
            all_rows = all_rows + rows  
            print(f"[+] Scraping {county} page {page} complete")
            page=page+1

            # save table as csv file
        folderName = verifyFolder("./output/")
        fileName = county+" county - realtaxlien"        
        fullFile = folderName + fileName
        print(f"[+] Saving {fullFile}")
        save_as_csv(fullFile, headers, all_rows)




if __name__ == "__main__":
    import sys
    #try:              
        #county = sys.argv[1]
    #except IndexError:
        #county = ["orangefl","sarasotafl","duvalfl"]
        #print("Please specify a URL.\nUsage: python html_table_extractor.py [URL]")
       # exit(1)
    main()