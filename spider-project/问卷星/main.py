import json
import time

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from question_type_enum import QuestionType
import random


class WJXHelper:
    def __init__(self, url, config_path, min_suspend_time=5, max_suspend_time=10, min_completion_time=110,
                 max_completion_time=170):
        self.config = None
        self.driver = None
        self.url = url
        self.config_path = config_path
        self.min_suspend_time = min_suspend_time
        self.max_suspend_time = max_suspend_time
        self.min_completion_time = min_completion_time
        self.max_completion_time = max_completion_time
        self.init_driver()

    # 创建webdriver
    def init_driver(self):
        service = Service(executable_path='./chromedriver')
        option = webdriver.ChromeOptions()
        # 滑块防止检测
        option.add_experimental_option('excludeSwitches', ['enable-automation'])
        option.add_experimental_option('useAutomationExtension', False)
        self.driver = webdriver.Chrome(service=service, options=option)
        # 将webdriver属性置为undefined
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument',
                                    {'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'})

    def load_config(self):
        with open(self.config_path) as fp:
            self.config = json.load(fp)

    def save_config(self):
        with open(self.config_path, 'w') as fp:
            json.dump(self.config, fp)

    # 处理单选
    def process_radio_question(self, question_index, question_element):
        config = self.config[str(question_index + 1)]['config']
        # 拿到所有的选项
        option_ls = question_element.find_elements(by=By.CLASS_NAME, value='ui-radio')
        # 随机选中一个选项
        if len(config) == 0:
            return None
        key = random.choice(list(config.keys()))
        option_ls[eval(key) - 1].click()
        # 更新该选项的剩余数量
        config[key] -= 1
        # 如果当前选项选完了，就清除这个选项
        if config[key] == 0:
            del config[key]

    # 处理多选
    def process_control_group(self, question_index, question_element):
        config = self.config[str(question_index + 1)]['config']
        # 拿到所有的选项
        option_ls = question_element.find_elements(by=By.CLASS_NAME, value='ui-checkbox')
        # 随机选中一个选项
        if len(config) == 0:
            return None
        key = random.choice(list(config.keys()))
        for option_index in tuple(eval(key)):
            option_ls[option_index - 1].click()
        config[key] -= 1
        # 如果当前选项选完了，就清除这个选项
        if config[key] == 0:
            del config[key]

    # 处理评分题
    def process_scoring(self, question_index, question_element):
        config = self.config[str(question_index + 1)]['config']
        # 获取整个table
        table_element = question_element.find_element(by=By.TAG_NAME, value='tbody')
        # 获取所有题目
        sub_question_ls = table_element.find_elements(by=By.CSS_SELECTOR, value="[tp='d']")
        # 遍历所有题目
        for sub_question_index, sub_question_data in enumerate(sub_question_ls):
            # 获取所有选项
            option_ls = sub_question_data.find_elements(by=By.TAG_NAME, value='a')
            sub_config = config[str(sub_question_index + 1)]
            if len(sub_config) == 0:
                return None
            key = random.choice(list(sub_config.keys()))
            option_ls[eval(key) - 1].click()
            # 更新该选项的剩余数量
            sub_config[key] -= 1
            # 如果当前选项选完了，就清除这个选项
            if sub_config[key] == 0:
                del sub_config[key]

    def submit_answer(self):
        # submit_button = self.driver.find_element(by=By.ID, value='ctlNext')
        # submit_button.click()
        submit = self.driver.find_element(By.XPATH, "//*[@id='ctlNext']")  # 网页源代码的xpath
        submit.click()
        # 延时 太快会被检测是脚本
        time.sleep(3)

        # 智能验证
        try:
            first_ls = self.driver.find_elements(By.XPATH, '//*[@id="layui-layer1"]/div[3]/a[1]')
            if len(first_ls) > 0:
                print('触发智能验证1')
                # 先点确认
                first_ls[0].click()
                # 再点智能验证提示框，进行智能验证
                time.sleep(3)
                second_button = self.driver.find_element(By.XPATH, '//*[@id="SM_BTN_WRAPPER_1"]')
                if second_button is not None:
                    second_button.click()
            second_button = self.driver.find_element(By.XPATH, '//*[@id="SM_BTN_WRAPPER_1"]')
            if second_button is not None:
                print('触发智能验证2')
                second_button.click()
                time.sleep(3)

            # 滑块验证
            # 找到滑块
            # Hk = self.driver.find_element_by_css_selector("#nc_1_n1z")
            # # 整个div滑块
            # div_Hk = self.driver.find_element_by_css_selector("#nc_1__scale_text")
            # time.sleep(2)
            # ActionChains(self.driver).drag_and_drop_by_offset(Hk, div_Hk.size["width"],
            #                                                       -div_Hk.size["height"]).perform()
            # second_button = self.driver.find_element(By.XPATH, '//*[@id="SM_BTN_WRAPPER_1"]')
            # if second_button is not None:
            #     print('触发智能验证2')
            #     second_button.click()
            #     time.sleep(3)
        except Exception as e:
            pass

        try:
            self.driver.find_element(By.XPATH, "//*[@id='ctlNext']")  # 网页源代码的xpath
        except Exception as e:
            return None
        raise Exception("触发不可处理的验证")

    def submit_answer_v2(self):
        while True:
            try:
                self.driver.find_element(By.XPATH, "//*[@id='ctlNext']")  # 网页源代码的xpath
            except:
                break


    # 获取当前页面题数
    def process_question(self, question_ls):
        for question_index, question_element in enumerate(question_ls):
            element_type = eval(question_element.get_attribute("type"))
            # print(element_type, type(element_type))
            if element_type == QuestionType.Radio.value:
                self.process_radio_question(question_index, question_element)
            if element_type == QuestionType.ControlGroup.value:
                self.process_control_group(question_index, question_element)
            if element_type == QuestionType.Scoring.value:
                self.process_scoring(question_index, question_element)

    # 关闭浏览器
    def close_browser(self):
        self.driver.close()
        self.driver.quit()

    def random_suspend_time(self):
        return time.sleep(random.randint(self.min_suspend_time, self.max_suspend_time))

    def random_completion_time(self):
        random_time = random.randint(self.min_completion_time, self.max_completion_time)
        print('随机等待时间:', random_time)
        return time.sleep(random_time)

    def run(self):
        num = 0
        while True:
            self.load_config()
            # 打开问卷页面
            self.driver.get(self.url)
            # 随机暂停一段时间开始下一份问卷
            self.random_suspend_time()
            # 获取当前页面题数
            question_ls = self.driver.find_elements(by=By.CLASS_NAME, value='ui-field-contain')
            self.process_question(question_ls)
            # 随机在页面停留时间
            self.random_completion_time()
            # 提交问卷
            # self.submit_answer_v2()
            self.submit_answer()
            self.save_config()
            num += 1
            print(num)
            time.sleep(3)


if __name__ == '__main__':
    url = "https://www.wjx.cn/vm/OWuqcJB.aspx# "
    helper = WJXHelper(url, './config.json')
    helper.run()
