from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait 

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import json
from multiprocessing import Pool
import time

url="https://portal.ncbar.gov/verification/search.aspx"

def get_lawyers(start_id, batch_size=1000):
    start = time.time()
    lawyers=[]
    browser = webdriver.Firefox()
    for bar_id in range(start_id, start_id+batch_size):
        try:
            browser.get(url)
            assert 'North Carolina State Bar' in browser.title

            elem = WebDriverWait(browser, 2).until(lambda x: x.find_element(By.NAME, 'ctl00$Content$txtLicNum'))  # Find the search box
            elem.clear()
            elem.send_keys(str(bar_id) + Keys.RETURN)

            tabl = WebDriverWait(browser, 2).until(lambda x: x.find_element(By.TAG_NAME, 'tbody'))
            link = tabl.find_element(By.TAG_NAME, "a")
            link.click()

            pan = WebDriverWait(browser, 2).until(lambda x: x.find_element(By.CLASS_NAME, 'panel-body'))
            keys = [dt.text.strip(':') for dt in pan.find_elements(By.XPATH, ".//dt")]
            vals = [dd.text for dd in pan.find_elements(By.XPATH, ".//dd")]

            lawyer = dict(zip(keys, vals))
            del lawyer[''] # cleanup
            lawyers.append(lawyer)
        except Exception as e:
            print(str(bar_id) + " failed.")
    browser.quit()
    with open(f"nc_lawyers_test_{start_id}-{start_id+batch_size-1}.json", 'w') as outfile:
        json.dump(lawyers, outfile, indent=4)
    print(f"finished batch {start_id}-{start_id+batch_size} in {time.time()-start}s")

if __name__=="__main__":
    with Pool(5) as p:
        p.map(get_lawyers, list(range(1,58800, 1000)))