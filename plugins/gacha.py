import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from nonebot import on_command, CommandSession


@on_command('gacha', aliases=('十连', '抽十连'), only_to_me=False)
async def gacha(session: CommandSession):
    (characters, rare_characters) = await bilibili_gacha(1)
    num_of_rare = len(rare_characters)
    output_str = '你抽到了：' + ', '.join(characters) +\
                 '\n其中三星是：' + ', '.join(rare_characters) +\
                 '\n共' + str(num_of_rare) + '个.'
    session.send(output_str)

@on_command('gacha10x', aliases=('一井', '抽一井'), only_to_me=False)
async def gacha10x(session: CommandSession):
    (characters, rare_characters) = await bilibili_gacha(30)
    num_of_rare = len(rare_characters)
    output_str = '你抽到了：' + str(num_of_rare) + '个三星'\
                 '\n分别是：' + ', '.join(rare_characters) + '.'
    session.send(output_str)

async def bilibili_gacha(turns: int) -> ([], []):
    # enable browser logging
    d = DesiredCapabilities.CHROME
    d['goog:loggingPrefs'] = {'browser': 'INFO'}
    options = webdriver.ChromeOptions()
    options.add_argument('window-size=1200x600')
    options.add_argument('headless')
    driver = webdriver.Chrome(desired_capabilities=d, options=options)

    # load the desired webpage
    driver.get('https://wiki.biligame.com/pcr/%E6%89%AD%E8%9B%8B%E6%A8%A1%E6%8B%9F%E5%99%A8')

    # wait until page loaded for gacha
    wait = WebDriverWait(driver, 1)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'animechara')))
    gacha_button = driver.find_element_by_id('gacha10')

    # gacha
    for i in range(turns):
        gacha_button.click()
        time.sleep(0.2)
    time.sleep(0.2)

    # get result
    name_reg = '[^到]+(?=\()'
    rarity_reg = '[^(]+(?=\))'
    characters = []
    rare_characters = []
    # get result
    for entry in driver.get_log('browser'):
        name_matches = re.findall(name_reg, entry['message'])
        rarity = re.findall(rarity_reg, entry['message'])
        if len(name_matches) > 0 and len(rarity) > 0:
            characters.append(name_matches[0])
            if rarity[0] == '3星':
                rare_characters.append(name_matches[0])
    driver.close()
    return characters, rare_characters