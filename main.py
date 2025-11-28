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
                            print(f"[{clicked_count}] 已点击 Send Proposal 按钮")
                            time.sleep(0.5)
                            
                            # 在弹窗中选择 Public Commission
                            select_public_commission()
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


def select_public_commission():
    """
    在弹窗的 iframe 中选择 Public Commission 选项
    """
    try:
        time.sleep(1)  # 等待弹窗完全加载
        
        # 查找 iframe 并切换进去
        iframe = tab.ele('css:iframe[data-testid="uicl-modal-iframe-content"]', timeout=3)
        if not iframe:
            print("  -> 未找到弹窗 iframe")
            return False
        
        # 切换到 iframe 内部
        iframe_tab = iframe.ele('text:Public Commission', timeout=5)
        if iframe_tab:
            iframe_tab.click(by_js=True)
            print("  -> 已选择 Public Commission")
            time.sleep(0.5)
            return True
        
        # 备用方案：在 iframe 中用 CSS 选择器查找
        options = iframe.eles('css:div.text-ellipsis')
        for opt in options:
            if 'Public Commission' in opt.text:
                opt.click(by_js=True)
                print("  -> 已选择 Public Commission")
                time.sleep(0.5)
                return True
            
        print("  -> 未找到 Public Commission 选项")
        return False
            
    except Exception as e:
        print(f"  -> 选择 Public Commission 失败: {e}")
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
