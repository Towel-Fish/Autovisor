# encoding=utf-8
import asyncio
import traceback
import time
from os import getcwd,environ
from typing import Tuple
from res.configs import Config
from res.progress import get_progress, show_progress
from playwright.async_api import async_playwright, Playwright, Page, Browser
from playwright.async_api import TimeoutError
from playwright._impl._errors import TargetClosedError
from res.support import show_donate
from res.utils import optimize_page, get_lesson_name, video_optimize, get_filtered_class

# 获取全局事件循环
event_loop_verify = asyncio.Event()
event_loop_answer = asyncio.Event()

#删除chorme或edge中的cookies
async def del_brower_config(brower: Browser, driver):
    if driver == "msedge":
        
        setting = (
            'edge://settings/clearBrowserData',          #设置清除的界面
            "div[role = dialog] input[type = checkbox]", #复选框
            '#clear-now',                                #清除按钮
                   )
    elif driver == "chrome":
        setting = (
            'chrome://settings/clearBrowserData', 
            'div#basic-tab div#checkbox', 
            '#clearButton',
                   )

    page_setting = await brower.new_page()
    await page_setting.goto(setting[0])

    All_checkboxs = await page_setting.query_selector_all(setting[1])
    for checkboxs in All_checkboxs:
        await checkboxs.set_checked(checked=True)

    #选择“所有时间”
    if driver == "msedge":
        await page_setting.locator('div[role = dialog] button[aria-haspopup]').click()
        await page_setting.locator('div[role = dialog] div[role = option]:nth-child(5)').click()
    elif driver == "chrome":
        await page_setting.locator('div#basic-tab select#dropdownMenu').select_option(label='时间不限')  
            
    await page_setting.locator(setting[2]).click()
    await page_setting.close()

    return

async def auto_login(config: Config, page: Page):
    await page.goto(config.login_url)
    await page.locator('#lUsername').fill(config.username)
    await page.locator('#lPassword').fill(config.password)
    await page.wait_for_timeout(500)
    await page.evaluate(config.login_js)
    await page.wait_for_selector(".wall-main", state="hidden")


async def init_page(p: Playwright, config: Config) -> Tuple[Page, Browser]:
    driver = "msedge" if config.driver == "edge" else config.driver

    print(f"正在启动{config.driver}浏览器...")
    browser = await p.chromium.launch_persistent_context(
        user_data_dir = getcwd() + r"\user_data\{}".format(driver),
        executable_path = config.exe_path if config.exe_path else None,
        channel = driver,
        headless = False,
        )
    
    page = browser.pages[0]
    page.set_default_timeout(24 * 3600 * 1000)
    viewsize = await page.evaluate(
        '''() => {
            return {width: window.screen.availWidth, height: window.screen.availHeight};
        }'''
    )
    viewsize["height"] -= 50
    await page.set_viewport_size(viewsize)
    return page, browser, driver


async def tail_work(page: Page, start_time, all_class, title) -> bool:
    reachTimeLimit = False
    page.set_default_timeout(24 * 3600 * 1000)
    time_period = (time.time() - start_time) / 60
    if 0 < config.limitMaxTime <= time_period:
        print(f"\n当前课程已达时限:{config.limitMaxTime}min\n即将进入下门课程!")
        reachTimeLimit = True
    else:
        class_name = await all_class[-1].get_attribute('class')
        if "current_play" in class_name:
            print("\n已学完本课程全部内容!")
            print("==" * 10)
        else:
            print(f"\"{title}\" Done !")
            print(f"本次课程已学习:{time_period:.1f} min")
    return reachTimeLimit


async def play_video(page: Page) -> None:
    while True:
        try:
            await asyncio.sleep(0.5)
            playing = await page.query_selector(".pauseButton")
            if not playing:
                print("[Info]检测到被暂停,正在尝试播放.", end="\r")
                canvas = await page.wait_for_selector(".videoArea", state="attached")
                await canvas.click()
                print("\n", end="\r")
        except TimeoutError:
            continue


async def skip_questions(page: Page, event_loop) -> None:
    while True:
        try:
            await asyncio.sleep(0.5)
            await page.wait_for_selector(".topic-item", state="attached", timeout=1000)
            if not await page.query_selector(".answer"):
                choices = await page.locator(".topic-item").all()
                for each in choices:
                    await each.click()
                    await page.wait_for_timeout(200)
            await page.evaluate(config.close_ques)
            event_loop.set()
        except TimeoutError:
            continue


async def wait_for_verify(page: Page, event_loop) -> None:
    while True:
        try:
            await asyncio.sleep(1)
            await page.wait_for_selector(".yidun_modal__title", state="attached", timeout=1000)
            print("\n检测到安全验证,请手动点击完成...")
            await page.wait_for_selector(".yidun_modal__title", state="hidden", timeout=24 * 3600 * 1000)
            event_loop.set()
            print("\n安全验证已完成,继续播放...")
        except TimeoutError:
            continue


async def learning_loop(page: Page, config: Config):
    title_selector = await page.wait_for_selector(".source-name")
    course_title = await title_selector.text_content()
    print(f"当前课程:<<{course_title}>>")
    await page.wait_for_selector(".clearfix.video", state="attached")
    all_class = await get_filtered_class(page)
    start_time = time.time()
    cur_index = 0
    while cur_index < len(all_class):
        await all_class[cur_index].click()
        await page.wait_for_selector(".current_play", state="attached")
        await page.wait_for_timeout(1000)
        title = await get_lesson_name(page)
        print("正在学习:%s" % title)
        page.set_default_timeout(10000)
        try:
            await video_optimize(page, config)
        except TimeoutError:
            if await page.query_selector(".yidun_modal__title"):
                await event_loop_verify.wait()
        curtime, total_time = await get_progress(page)
        timer = 0
        while curtime != "100%":
            try:
                time_period = (time.time() - start_time) / 60
                timer += 1
                if 0 < config.limitMaxTime <= time_period:
                    break
                elif timer % 5 == 0:
                    curtime, total_time = await get_progress(page)
                    show_progress(desc="完成进度:", cur_str=curtime)
            except TimeoutError as e:
                if await page.query_selector(".yidun_modal__title"):
                    await event_loop_verify.wait()
                elif await page.query_selector(".topic-title"):
                    await event_loop_answer.wait()
                else:
                    print(f"\n[Warn]{repr(e)}")
        if "current_play" in await all_class[cur_index].get_attribute('class'):
            cur_index += 1
        reachTimeLimit = await tail_work(page, start_time, all_class, title)
        if reachTimeLimit:
            return


async def reviewing_loop(page: Page, config: Config):
    title_selector = await page.wait_for_selector(".source-name")
    course_title = await title_selector.text_content()
    print(f"当前课程:<<{course_title}>>")
    await page.wait_for_selector(".clearfix.video", state="attached")
    all_class = await get_filtered_class(page, enableRepeat=True)
    course_start_time = time.time()
    cur_index = 0
    while cur_index < len(all_class):
        await all_class[cur_index].click()
        await page.wait_for_selector(".current_play", state="attached")
        await page.wait_for_timeout(1000)
        title = await get_lesson_name(page)
        print("\n正在学习:%s" % title)
        page.set_default_timeout(10000)
        try:
            await video_optimize(page, config)
        except TimeoutError:
            if await page.query_selector(".yidun_modal__title"):
                await event_loop_verify.wait()
        curtime, total_time = await get_progress(page)
        start_time = time.time()
        timer = 0
        while True:
            est_time = (time.time() - start_time) * config.limitSpeed
            if est_time > total_time:
                break
            try:
                time_period = (time.time() - course_start_time) / 60
                timer += 1
                if 0 < config.limitMaxTime <= time_period:
                    break
                elif timer % 5 == 0:
                    curtime, total_time = await get_progress(page)
                    show_progress(desc="完成进度:", cur_str=curtime)
            except TimeoutError as e:
                if await page.query_selector(".yidun_modal__title"):
                    await event_loop_verify.wait()
                elif await page.query_selector(".topic-title"):
                    await event_loop_answer.wait()
                else:
                    print(f"\n[Warn]{repr(e)}")
        if "current_play" in await all_class[cur_index].get_attribute('class'):
            cur_index += 1
        reachTimeLimit = await tail_work(page, course_start_time, all_class, title)
        if reachTimeLimit:
            return


async def entrance(config: Config):
    tasks = []
    try:
        async with async_playwright() as p:
            page, browser, driver = await init_page(p, config)
            # 进行登录
            if not config.username or not config.password:
                print("请手动输入账号密码...")
            print("等待登录完成...")
            #删除cookies同时加载登陆界面
            auto_login_task = asyncio.create_task(auto_login(config, page))
            del_config_task = asyncio.create_task(del_brower_config(browser, driver))
            tasks.extend([auto_login_task, del_config_task])
            await asyncio.gather(*tasks, return_exceptions=True)
            tasks = []
            # 启动协程任务
            skip_ques_task = asyncio.create_task(skip_questions(page, event_loop_answer))
            play_video_task = asyncio.create_task(play_video(page))
            verify_task = asyncio.create_task(wait_for_verify(page, event_loop_verify))
            tasks.extend([skip_ques_task, play_video_task, verify_task])
            # 遍历所有课程,加载网页
            for course_url in config.course_urls:
                print("开始加载播放页...")
                await page.goto(course_url)
                await page.wait_for_selector(".studytime-div")
                # 关闭弹窗,优化页面体验
                await optimize_page(page, config)
                # 启动课程主循环
                if config.enableRepeat:
                    await reviewing_loop(page, config)
                else:
                    await learning_loop(page, config)
        print("==" * 10)
        print("所有课程学习完毕!")
        show_donate("res/QRcode.jpg")
    except Exception as e:
        print(f"\n[Error]:{repr(e)}")
        if isinstance(e, TargetClosedError):
            print("[Error]检测到网页关闭,正在退出程序...")
    finally:
        # 结束所有协程任务
        await asyncio.gather(*tasks, return_exceptions=True) if tasks else None
        time.sleep(3)


if __name__ == "__main__":
    print("Github:CXRunfree All Rights Reserved.")
    print("===== Runtime Log =====")
    try:
        print("正在载入数据...")
        config = Config()
        asyncio.run(entrance(config))
    except Exception as e:
        if isinstance(e, KeyError):
            input("[Error]可能是account文件的配置出错!")
        elif isinstance(e, UserWarning):
            input("[Error]是不是忘记填账号密码了?")
        elif isinstance(e, FileNotFoundError):
            print(f"文件缺失: {e.filename}")
            input("[Error]程序缺失依赖文件,请重新安装程序!")
        elif isinstance(e, TargetClosedError):
            input("[Error]糟糕,网页关闭了!")
        elif isinstance(e, UnicodeDecodeError):
            print("configs配置文件编码有误,保存时请选择utf-8或gbk!")
            input(f"[Error]{e}")
        else:
            print(f"[Error]{e}")
            with open("log.txt", "w", encoding="utf-8") as log:
                log.write(traceback.format_exc())
            print("错误日志已保存至:log.txt")
            input("系统出错,请检查后重新启动!")
