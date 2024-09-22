from typing import List
from playwright.async_api import Page, Locator, ElementHandle
from res.configs import Config
from res.progress import move_mouse
import time


async def optimize_page(page: Page, config: Config) -> None:
    try:
        await page.evaluate(config.pop_js)
        hour = time.localtime().tm_hour
        if hour >= 18 or hour < 7:
            await page.wait_for_selector(".Patternbtn-div")
            await page.evaluate(config.night_js)
        await page.wait_for_selector(".ai-show-icon.ai-icon-appear")
        await page.evaluate(config.remove_assist)
        await page.evaluate(config.no_hint)
        await page.evaluate(config.gzh_pop)
        await page.wait_for_selector(".warn-box", timeout=1500)
        await page.evaluate(config.close_gjh)
    except TimeoutError:
        return


async def get_lesson_name(page: Page) -> str:
    title_ele = await page.wait_for_selector("#lessonOrder")
    await page.wait_for_timeout(500)
    title_ = await title_ele.get_attribute("title")
    return title_


async def video_optimize(page: Page, config: Config) -> None:
    try:
        await move_mouse(page)
        await page.evaluate(config.volume_none)
        await page.evaluate(config.set_none_icon)
        await page.evaluate(config.revise_speed)
        await page.evaluate(config.revise_speed_name)
    except Exception as e:
        print(f"\n[Warn]{repr(e)}")


async def get_filtered_class(page: Page, enableRepeat=False) -> List[Locator]:
    try:
        await page.wait_for_selector(".time_icofinish", timeout=1000)
    except TimeoutError:
        pass
    all_class = await page.locator(".clearfix.video").all()
    if enableRepeat:
        return all_class
    else:
        new_class = []
        for each in all_class:
            isDone = await each.locator(".time_icofinish").count()
            if not isDone:
                new_class.append(each)
        return new_class