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
    提取页面上所有的 Send Proposal 按钮
    通过滚动加载更多元素，并悬停显示按钮
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
    print("\n开始提取 Send Proposal 按钮...")
    
    # 直接查找所有 Send Proposal 按钮（通过 data-testid）
    buttons = tab.eles('css:button[data-testid="uicl-button"]')
    send_proposal_buttons = [btn for btn in buttons if 'Send Proposal' in btn.text]
    
    print(f"找到 {len(send_proposal_buttons)} 个 Send Proposal 按钮")
    
    if send_proposal_buttons:
        # 获取第一个按钮
        first_btn = send_proposal_buttons[0]
        
        # 向上查找父元素并悬停（触发按钮可见）
        # 尝试找到包含按钮的可悬停容器
        parent = first_btn.parent()
        for _ in range(10):  # 最多向上查找10层
            if parent:
                try:
                    # 尝试悬停
                    tab.scroll.to_see(parent)
                    time.sleep(0.2)
                    parent.hover()
                    time.sleep(0.3)
                    
                    # 检查按钮是否可点击
                    print(f"正在尝试点击按钮...")
                    first_btn.click()
                    print("已点击第一个 Send Proposal 按钮！")
                    time.sleep(1)
                    return True
                except Exception as e:
                    print(f"尝试失败: {e}")
                    parent = parent.parent()
            else:
                break
        
        # 如果常规点击失败，尝试 JS 点击
        print("尝试使用 JS 点击...")
        try:
            tab.run_js('arguments[0].click()', first_btn)
            print("已通过 JS 点击第一个 Send Proposal 按钮！")
            return True
        except Exception as e:
            print(f"JS 点击失败: {e}")
    
    print("未能点击任何 Send Proposal 按钮")
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
