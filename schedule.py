import time

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.support.ui import Select



def get_course(TIME_PERIOD, SUBJECT_NAME, COURSE_NUMBER):
    first_url = "https://loris.wlu.ca/ssb_prod/bwckschd.p_disp_dyn_sched"

    chrome_opts = webdriver.ChromeOptions()
    chrome_opts.add_argument("--headless")

    driver = webdriver.Chrome(
        executable_path=r"/home/arthur/Programming/LorisBot/chromedriver.linux", chrome_options=chrome_opts)
    driver.maximize_window()
    driver.get(first_url)

    # Select Fall 2018 and Submit form.
    dates_select = Select(driver.find_element_by_id("term_input_id"))
    dates_select.select_by_visible_text(TIME_PERIOD)
    driver.find_element_by_tag_name("form").submit()
    time.sleep(2)

    # Select Subject and Input the course number
    subject_select = Select(driver.find_element_by_id("subj_id"))
    subject_select.select_by_visible_text(SUBJECT_NAME)
    driver.find_element_by_id("crse_id").send_keys(COURSE_NUMBER)
    driver.find_element_by_tag_name("form").submit()
    time.sleep(4)

    soup = BeautifulSoup(driver.find_element_by_xpath(
        "//*").get_attribute("outerHTML"), "html.parser")

    tables = soup.find_all(
        "table", {"summary": "This layout table is used to present the sections found"})

    for table in tables:

        try:
            title = table.find("a").text
            print(title)

            seats_table = table.find_next(
                "table", {"summary": "This layout table is used to present the seating numbers."})

            columns = seats_table.find_all("td")
            print("Capacity: ", columns[1].text)
            print("Actual:   ", columns[2].text)
            print("Remaining:", columns[3].text)

            print("-------------------")
        except:
            pass

    driver.close()


if __name__ == "__main__":
    get_course("Fall 2018", "Business", "481")
