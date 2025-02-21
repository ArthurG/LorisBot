import time

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.support.ui import Select

from selenium.webdriver import FirefoxOptions
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

import requests

from pyvirtualdisplay import Display

WEBHOOK = ""

def get_course_details(time_period, subject_name, course_number):
    first_url = "https://loris.wlu.ca/ssb_prod/bwckschd.p_disp_dyn_sched"

    chrome_opts = webdriver.ChromeOptions()
    chrome_opts.add_argument("--headless")

    opts = FirefoxOptions()
    opts.add_argument("--headless")

    binary = FirefoxBinary('/usr/bin/firefox')


    driver = webdriver.Firefox(firefox_binary=binary, firefox_options=opts, executable_path='/usr/bin/geckodriver')
    driver.get(first_url)

    # Select Fall 2018 and Submit form.
    dates_select = Select(driver.find_element_by_id("term_input_id"))
    dates_select.select_by_visible_text(time_period)
    driver.find_element_by_tag_name("form").submit()
    time.sleep(2)

    # Select Subject and Input the course number
    subject_select = Select(driver.find_element_by_id("subj_id"))
    subject_select.select_by_visible_text(subject_name)
    driver.find_element_by_id("crse_id").send_keys(course_number)
    driver.find_element_by_tag_name("form").submit()
    time.sleep(4)

    soup = BeautifulSoup(driver.find_element_by_xpath(
        "//*").get_attribute("outerHTML"), "html.parser")

    tables = soup.find_all(
        "table", {"summary": "This layout table is used to present the sections found"})

    course_data = {}
    for table in tables:

        try:
            course = {}
            title = table.find("a").text
            course["title"] = title

            print(title)
            seats_table = table.find_next(
                "table", {"summary": "This layout table is used to present the seating numbers."})

            columns = seats_table.find_all("td")
            course["capacity"] = columns[1].text
            course["actual"] = columns[2].text
            course["remaining"] = columns[3].text
            course_data[title] = course
        except:
            pass
    driver.close()
    return course_data

def notify_if_needed(course_data, good_sections):
    for sec in good_sections:
        if int(course_data[sec]["remaining"]) > 0:
            requests.post(WEBHOOK, {"content": "Found open course: {}, Remaining spots: {}, Filled spots: {}"
                .format(sec, course_data[sec]["remaining"], course_data[sec]["actual"])})

def main():

    display = Display(visible=0, size=(800, 600))
    display.start()

    #course_data = get_course_details("Fall 2018", "Business", "481")
    #good_sections = ["Business Policy I - 56 - BU 481 - C", "Business Policy I - 1021 - BU 481 - G", "Business Policy I - 1660 - BU 481 - K"]
    #notify_if_needed(course_data, good_sections)

    course_data = get_course_details("Spring 2019", "Business", "491")
    good_sections = ["Business Policy II - 71 - BU 491 - P", "Business Policy II - 72 - BU 491 - Q"]
    notify_if_needed(course_data, good_sections)

    course_data = get_course_details("Spring 2019", "Business", "493U")
    good_sections = ["Fin Markets & Security Trading - 480 - BU 493U - H"]
    notify_if_needed(course_data, good_sections)

    display.stop()

if __name__ == "__main__":
    main()
