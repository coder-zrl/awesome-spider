import json

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from question_type_enum import QuestionType


def read_config():
    return json.load(open('config.json'))


def save_config(config):
    with open('config.json') as fp:
        json.dump(fp,config)


# 处理单选
def process_radio_question(question_index, question_element):
    # 拿到所有的选项
    option_ls = question_element.find_elements(by=By.CLASS_NAME, value='ui-radio')
    # 选中一个选项
    option_ls[0].click()


# 处理多选
def process_control_group(question_index, question_element):
    # 拿到所有的选项
    option_ls = question_element.find_elements(by=By.CLASS_NAME, value='ui-checkbox')
    option_ls[0].click()


# 处理评分题
def process_scoring(question_index, question_element):
    # 获取整个table
    table_element = question_element.find_element(by=By.TAG_NAME, value='tbody')
    # 获取所有题目
    sub_question_ls = table_element.find_elements(by=By.CSS_SELECTOR, value="[tp='d']")
    for sub_question_index, sub_question_data in enumerate(sub_question_ls):
        # 获取所有选项
        option_ls = sub_question_data.find_elements(by=By.TAG_NAME, value='a')
        option_ls[0].click()


def submit_answer(root_driver):
    root_driver.find_element(by=By.ID, value='ctlNext').click()


# 创建webdriver
service = Service(executable_path='./geckodriver')
driver = webdriver.Firefox(service=service)

url = "https://www.wjx.cn/vm/OFR6wqY.aspx"
driver.get(url)

# 获取当前页面题数
question_ls = driver.find_elements(by=By.CLASS_NAME, value='ui-field-contain')
for question_index, question_element in enumerate(question_ls):
    element_type = eval(question_element.get_attribute("type"))
    # print(element_type, type(element_type))
    if element_type == QuestionType.Radio.value:
        process_radio_question(question_index, question_element)
    if element_type == QuestionType.ControlGroup.value:
        process_control_group(question_index, question_element)
    if element_type == QuestionType.Scoring.value:
        process_scoring(question_index, question_element)
# 提交问卷
submit_answer(driver)

# 关闭浏览器
driver.close()
driver.quit()
