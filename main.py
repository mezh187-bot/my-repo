from DrissionPage import Chromium
import time

browser = Chromium()
tab = browser.latest_tab


def main():
    url = 'https://app.impact.com/secure/mediapartner/marketplace/new-campaign-marketplace-flow.ihtml?execution=e1s1#sortBy=salepercent&sortOrder=DESC'
    tab.get(url)
    # 等待页面加载
    tab.wait.doc_loaded()
    # 查找人机验证元素
    人机验证 = tab.ele('text=请完成以下操作，验证您是真人。')
    if 人机验证:
        print("检测到人机验证，正在尝试点击...")
        # 人机验证.click()
    else:
        print("未检测到人机验证。")
    # tab.get(url=url)


def extract_send_proposal_buttons():
    """
    循环点击页面上所有的 Send Proposal 按钮
    点击后关闭弹窗，继续点击下一个
    """
    url = 'https://app.impact.com/secure/advertiser/discover/radius/fr/partner_discover.ihtml?page=marketplace&slideout_id_type=partner#businessModels=all&sizeRating=large%2Cextra_large&sortBy=reachRating&sortOrder=DESC'
    tab.get(url)
    tab.wait.doc_loaded()
    
    # 等待用户操作完成（如登录、人机验证等）
    print("\n" + "=" * 50)
    print("浏览器已打开，请完成以下操作：")
    print("1. 登录账号（如果需要）")
    print("2. 完成人机验证（如果出现）")
    print("3. 确保页面已正常加载")
    print("=" * 50)
    input("\n操作完成后，按 Enter 键继续...")
    
    clicked_count = 0
    total_scrolls = 0
    max_scrolls = 50  # 最大滚动次数，防止无限循环
    
    print("\n开始循环点击 Send Proposal 按钮...")
    
    while total_scrolls < max_scrolls:
        # 查找当前可见的所有 Send Proposal 按钮
        buttons = tab.eles('css:button[data-testid="uicl-button"]')
        send_proposal_buttons = [btn for btn in buttons if 'Send Proposal' in btn.text]
        
        if not send_proposal_buttons:
            print("当前页面没有 Send Proposal 按钮，滚动加载更多...")
            tab.scroll.down(500)
            time.sleep(1)
            total_scrolls += 1
            continue
        
        # 遍历当前可见的按钮并点击
        for btn in send_proposal_buttons:
            try:
                # 先获取 selected-tab 的值（在点击按钮之前）
                selected_tab = get_selected_tab_value(btn)
                
                # 向上查找父元素并悬停
                parent = btn.parent()
                for _ in range(10):
                    if parent:
                        try:
                            tab.scroll.to_see(parent)
                            time.sleep(0.2)
                            parent.hover()
                            time.sleep(0.3)
                            
                            # 点击 Send Proposal 按钮
                            btn.click()
                            clicked_count += 1
                            print(f"[{clicked_count}] 已点击 Send Proposal 按钮 (类别: {selected_tab})")
                            time.sleep(0.5)
                            
                            # 在弹窗中选择 Public Commission，并传入 selected_tab 值
                            select_public_commission(selected_tab)
                            break
                        except Exception:
                            parent = parent.parent()
                    else:
                        break
            except Exception as e:
                print(f"点击按钮时出错: {e}")
                continue
        
        # 滚动加载更多
        tab.scroll.down(500)
        time.sleep(1)
        total_scrolls += 1
        print(f"滚动第 {total_scrolls} 次，已点击 {clicked_count} 个按钮")
    
    print(f"\n===== 完成！共点击了 {clicked_count} 个 Send Proposal 按钮 =====")
    return clicked_count


def get_selected_tab_value(btn):
    """
    获取按钮所在行的 selected-tab 值
    """
    try:
        # 向上查找包含 selected-tab 的父元素
        parent = btn.parent()
        for _ in range(20):  # 最多向上查找20层
            if parent:
                selected_tab_ele = parent.ele('css:.selected-tab', timeout=0.1)
                if selected_tab_ele:
                    value = selected_tab_ele.text.strip()
                    return value
                parent = parent.parent()
            else:
                break
        
        # 备用方案：直接在页面查找
        selected_tab_ele = tab.ele('css:.selected-tab', timeout=0.5)
        if selected_tab_ele:
            value = selected_tab_ele.text.strip()
            return value
            
    except Exception as e:
        print(f"  -> 获取 selected-tab 失败: {e}")
    return None


def select_public_commission(selected_tab=None):
    """
    在弹窗的 iframe 中选择 Public Commission 选项，输入 tag，然后选择日期，最后填写留言
    """
    try:
        time.sleep(1)  # 等待弹窗完全加载
        
        # 查找 iframe 并切换进去
        iframe = tab.ele('css:iframe[data-testid="uicl-modal-iframe-content"]', timeout=3)
        if not iframe:
            print("  -> 未找到弹窗 iframe")
            return False
        
        # 在 iframe 中查找并点击 Public Commission
        option = iframe.ele('text:Public Commission', timeout=5)
        if option:
            option.click(by_js=True)
            print("  -> 已选择 Public Commission")
            time.sleep(0.5)
            
            # 如果有 selected_tab 值，在 tag-input 中输入并选择
            if selected_tab:
                input_tag_and_select(iframe, selected_tab)
            
            # 选择日期（第二天）
            select_tomorrow_date(iframe)
            
            # 填写留言
            input_comment(iframe)
            
            # 点击提交按钮
            submit_proposal(iframe)
            return True
        
        # 备用方案：在 iframe 中用 CSS 选择器查找
        options = iframe.eles('css:div.text-ellipsis')
        for opt in options:
            if 'Public Commission' in opt.text:
                opt.click(by_js=True)
                print("  -> 已选择 Public Commission")
                time.sleep(0.5)
                
                # 如果有 selected_tab 值，在 tag-input 中输入并选择
                if selected_tab:
                    input_tag_and_select(iframe, selected_tab)
                
                # 选择日期（第二天）
                select_tomorrow_date(iframe)
                
                # 填写留言
                input_comment(iframe)
                
                # 点击提交按钮
                submit_proposal(iframe)
                return True
            
        print("  -> 未找到 Public Commission 选项")
        return False
            
    except Exception as e:
        print(f"  -> 选择 Public Commission 失败: {e}")
    return False


def input_tag_and_select(iframe, selected_tab):
    """
    在 tag-input 中输入值并从下拉列表中选择
    """
    try:
        # 处理 selected_tab 值，去掉所有空格
        # "Content / Reviews" -> "Content/Reviews"
        search_text = selected_tab.replace(" ", "")
        
        # 查找 tag-input 输入框
        tag_input = iframe.ele('css:input[data-testid="uicl-tag-input-text-input"]', timeout=3)
        if not tag_input:
            raise Exception("未找到 tag-input 输入框")
        
        # 点击输入框
        tag_input.click(by_js=True)
        time.sleep(0.3)
        
        # 输入搜索文本
        tag_input.input(search_text)
        print(f"  -> 已输入 tag: {search_text}")
        time.sleep(0.5)
        
        # 等待下拉列表出现并选择匹配项
        dropdown = iframe.ele('css:[data-testid="uicl-tag-input-dropdown"]', timeout=3)
        if not dropdown:
            raise Exception("未找到下拉列表，输入后没有出现填充项")
        
        # 查找下拉列表中的选项文本（如 "Content/Reviews (136819)"）
        option_div = dropdown.ele('css:div._4-15-1_Baf2T', timeout=2)
        if not option_div:
            # 备用方案：查找 li 元素
            options = dropdown.eles('css:li')
            if not options:
                raise Exception("下拉列表中没有选项")
            option_div = options[0]
        
        option_text = option_div.text.strip()
        print(f"  -> 下拉选项文本: {option_text}")
        
        # 提取选项中的类别名称（去掉括号中的数字）
        # "Content/Reviews (136819)" -> "Content/Reviews"
        import re
        option_category = re.sub(r'\s*\(\d+\)\s*$', '', option_text).replace(" ", "")
        
        # 验证输入的值和下拉选项是否匹配
        if search_text.lower() != option_category.lower():
            raise Exception(f"输入值 '{search_text}' 与下拉选项 '{option_category}' 不匹配")
        
        # 点击选项
        option_div.click(by_js=True)
        print(f"  -> 已选择下拉选项: {option_text}")
        time.sleep(0.3)
        
        # 验证选择是否成功（检查输入框或 hidden input 的值）
        # 查找 tag 容器，确认已添加
        tag_container = iframe.ele('css:.iui-tag-input', timeout=1)
        if tag_container:
            # 检查是否有已选中的 tag
            selected_tags = tag_container.eles('css:.tag, [class*="tag"]')
            if selected_tags:
                print(f"  -> 验证成功，已选择 tag")
                return True
        
        return True
            
    except Exception as e:
        print(f"  -> 输入 tag 并选择失败: {e}")
        raise  # 重新抛出异常


def select_tomorrow_date(iframe):
    """
    在 iframe 中选择日期（第二天）
    """
    try:
        # 点击日期输入按钮打开日期选择器
        date_btn = iframe.ele('css:button[data-testid="uicl-date-input"]', timeout=3)
        if date_btn:
            date_btn.click(by_js=True)
            print("  -> 已打开日期选择器")
            time.sleep(0.5)
            
            # 查找并点击明天的日期
            # 日期选择器通常会高亮今天，明天是下一个可选日期
            # 查找日期选择器中的日期按钮
            from datetime import datetime, timedelta
            tomorrow = datetime.now() + timedelta(days=1)
            tomorrow_day = str(tomorrow.day)
            
            # 查找包含明天日期的按钮/元素
            # 通常日期选择器的日期是按钮或可点击的 div
            date_cells = iframe.eles('css:td, .day, [class*="day"], [class*="date"]')
            for cell in date_cells:
                if cell.text.strip() == tomorrow_day:
                    cell.click(by_js=True)
                    print(f"  -> 已选择日期: {tomorrow.strftime('%Y-%m-%d')}")
                    time.sleep(0.3)
                    return True
            
            # 备用方案：通过文本查找
            date_ele = iframe.ele(f'text={tomorrow_day}', timeout=2)
            if date_ele:
                date_ele.click(by_js=True)
                print(f"  -> 已选择日期: {tomorrow.strftime('%Y-%m-%d')}")
                time.sleep(0.3)
                return True
                
            print("  -> 未找到明天的日期")
            return False
        else:
            print("  -> 未找到日期输入按钮")
            return False
            
    except Exception as e:
        print(f"  -> 选择日期失败: {e}")
    return False


# 留言模板
COMMENT_TEMPLATE = """Dear Partner,

I'm Jade, manager of the Trucktok Affiliate Program (ID: 44072).

TruckTok is a trusted brand specializing in high-demand diesel delete kits and all-in-one intake & exhaust systems for Ford Powerstroke, GM Duramax, and RAM Cummins.

As a specialized leader in the diesel performance market, our strong brand recognition translates directly into high conversion rates—and significant earning potential for you.

We offer:
- Up to 15% commission on all sales
- High-performing creatives and full support
- Strong conversion rates backed by consumer trust
Our website: https://www.trucktok.com/

We believe this is a powerful opportunity and would love for you to join us!

Best, 
Trucktok Affiliate Team"""


def input_comment(iframe):
    """
    在 textarea 中输入留言内容
    """
    try:
        # 查找 textarea
        textarea = iframe.ele('css:textarea[data-testid="uicl-textarea"]', timeout=3)
        if not textarea:
            textarea = iframe.ele('css:textarea[name="comment"]', timeout=2)
        
        if not textarea:
            print("  -> 未找到留言输入框")
            return False
        
        # 清空并输入内容
        textarea.click(by_js=True)
        time.sleep(0.2)
        textarea.clear()
        textarea.input(COMMENT_TEMPLATE)
        print("  -> 已填写留言内容")
        time.sleep(0.3)
        return True
        
    except Exception as e:
        print(f"  -> 填写留言失败: {e}")
    return False


def submit_proposal(iframe):
    """
    点击提交按钮提交 Proposal
    """
    try:
        # 查找 iframe 中的 Send Proposal 提交按钮
        submit_btn = iframe.ele('css:button[data-testid="uicl-button"]', timeout=3)
        if submit_btn and 'Send Proposal' in submit_btn.text:
            submit_btn.click(by_js=True)
            print("  -> 已点击提交按钮")
            time.sleep(1)
            
            # 点击确认按钮
            click_understand_button(iframe)
            return True
        
        # 备用方案：通过文本查找
        submit_btn = iframe.ele('text:Send Proposal', timeout=2)
        if submit_btn and submit_btn.tag == 'button':
            submit_btn.click(by_js=True)
            print("  -> 已点击提交按钮")
            time.sleep(1)
            
            # 点击确认按钮
            click_understand_button(iframe)
            return True
        
        # 备用方案2：查找所有按钮
        buttons = iframe.eles('css:button[data-testid="uicl-button"]')
        for btn in buttons:
            if 'Send Proposal' in btn.text:
                btn.click(by_js=True)
                print("  -> 已点击提交按钮")
                time.sleep(1)
                
                # 点击确认按钮
                click_understand_button(iframe)
                return True
        
        print("  -> 未找到提交按钮")
        return False
        
    except Exception as e:
        print(f"  -> 点击提交按钮失败: {e}")
    return False


def click_understand_button(iframe):
    """
    点击 'I understand' 确认按钮
    """
    try:
        time.sleep(0.5)  # 等待弹窗出现
        
        # 在 iframe 中查找 I understand 按钮
        understand_btn = iframe.ele('text:I understand', timeout=3)
        if understand_btn and understand_btn.tag == 'button':
            understand_btn.click(by_js=True)
            print("  -> 已点击 'I understand' 确认按钮")
            time.sleep(0.5)
            return True
        
        # 备用方案：查找所有按钮
        buttons = iframe.eles('css:button[data-testid="uicl-button"]')
        for btn in buttons:
            if 'I understand' in btn.text:
                btn.click(by_js=True)
                print("  -> 已点击 'I understand' 确认按钮")
                time.sleep(0.5)
                return True
        
        # 备用方案2：在主页面查找（可能弹窗不在 iframe 内）
        understand_btn = tab.ele('text:I understand', timeout=2)
        if understand_btn and understand_btn.tag == 'button':
            understand_btn.click(by_js=True)
            print("  -> 已点击 'I understand' 确认按钮")
            time.sleep(0.5)
            return True
        
        print("  -> 未找到 'I understand' 按钮")
        return False
        
    except Exception as e:
        print(f"  -> 点击确认按钮失败: {e}")
    return False


def close_modal():
    """
    关闭弹窗
    """
    try:
        # 查找关闭按钮
        close_btn = tab.ele('css:button[data-testid="uicl-modal-close-button"]', timeout=2)
        if close_btn:
            close_btn.click()
            print("  -> 已关闭弹窗")
            time.sleep(0.3)
            return True
    except Exception as e:
        print(f"  -> 关闭弹窗失败: {e}")
    return False


def extract_buttons_with_hover():
    """
    通过悬停列表项来显示 Send Proposal 按钮，然后提取
    """
    url = 'https://app.impact.com/secure/mediapartner/marketplace/new-campaign-marketplace-flow.ihtml?execution=e1s1#sortBy=salepercent&sortOrder=DESC'
    tab.get(url)
    tab.wait.doc_loaded()
    time.sleep(2)  # 等待页面完全加载
    
    all_buttons = []
    last_count = 0
    no_change_count = 0
    max_no_change = 3
    
    print("开始滚动页面并通过悬停提取 Send Proposal 按钮...")
    
    while no_change_count < max_no_change:
        # 查找页面上的卡片/列表项元素（根据实际页面结构调整选择器）
        cards = tab.eles('css:.campaign-card, .list-item, [class*="card"], [class*="item"]')
        
        if not cards:
            # 如果没有找到，尝试其他选择器
            cards = tab.eles('css:div[class*="row"], tr, li')
        
        for card in cards:
            try:
                # 悬停在卡片上以显示按钮
                card.hover()
                time.sleep(0.3)  # 等待按钮显示
                
                # 在当前卡片中查找 Send Proposal 按钮
                btn = card.ele('xpath:.//button[contains(text(), "Send Proposal")]', timeout=0.5)
                if btn:
                    btn_html = btn.html
                    if btn_html not in [b['html'] for b in all_buttons]:
                        all_buttons.append({
                            'html': btn_html,
                            'text': btn.text,
                        })
                        print(f"找到按钮 {len(all_buttons)}: {btn.text}")
            except Exception as e:
                continue
        
        # 检查是否有新元素
        if len(all_buttons) == last_count:
            no_change_count += 1
        else:
            no_change_count = 0
            last_count = len(all_buttons)
        
        # 滚动页面
        tab.scroll.down(500)
        time.sleep(1)
    
    print(f"\n===== 共找到 {len(all_buttons)} 个 Send Proposal 按钮 =====\n")
    
    for i, btn_info in enumerate(all_buttons, 1):
        print(f"按钮 {i}:")
        print(btn_info['html'])
        print("-" * 50)
    
    return all_buttons


def goto_work_web():
    url = ''


if __name__ == "__main__":
    # main()
    # 提取 Send Proposal 按钮
    extract_send_proposal_buttons()
    # 或者使用悬停方式提取
    # extract_buttons_with_hover()
