# 文件名: login_script.py
import os
import time
from playwright.sync_api import sync_playwright

def run_login():
    # 1. 获取账号密码
    username = os.environ.get("GH_USERNAME")
    password = os.environ.get("GH_PASSWORD")
    
    if not username or not password:
        print("❌ 错误: 环境变量中未找到账号或密码。")
        return

    print("🚀 启动浏览器...")
    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(headless=True)
        # 使用较大的视口，确保页面元素加载完整
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        # 2. 打开 ClawCloud 登录页
        target_url = "https://ap-northeast-1.run.claw.cloud/"
        print(f"🌐 正在访问: {target_url}")
        page.goto(target_url)
        page.wait_for_load_state("networkidle")

        # 3. 点击 GitHub 登录按钮
        # 修正：根据您提供的 HTML，使用 button 标签且包含 GitHub 文字的定位方式
        print("🔍 正在寻找 GitHub 按钮...")
        try:
            # 等待按钮出现
            # selector 解释: 寻找一个 button 标签，且它包含文本 "GitHub"
            login_button = page.locator("button:has-text('GitHub')")
            login_button.wait_for(state="visible", timeout=10000)
            
            print("✅ 找到按钮，正在点击...")
            login_button.click()
        except Exception as e:
            print(f"❌ 找不到登录按钮 (超时): {e}")
            page.screenshot(path="error_no_button.png")
            exit(1)

        # 4. 处理 GitHub 登录
        print("⏳ 等待跳转到 GitHub 登录页面...")
        try:
            # 等待 URL 变成 github.com 开头
            page.wait_for_url("**/login**", timeout=15000)
            print("🔒 已到达 GitHub 验证页面。")
            
            # 填写账号
            page.fill("#login_field", username)
            # 填写密码
            page.fill("#password", password)
            # 点击登录
            print("📤 提交登录表单...")
            page.click("input[name='commit']")
            
        except Exception as e:
            # 如果没有跳转到 github.com，可能是已经登录过了，直接跳过
            print(f"ℹ️ 未检测到 GitHub 登录页 (可能已由 Cookie 自动登录): {e}")

        # 4.1 处理可能的 'Authorize App' (应用授权) 页面
        # 如果是第一次在 headless 模式下登录，GitHub 可能会问是否授权
        try:
            # 等待一小会儿看 URL 是否包含 authorize
            page.wait_for_timeout(3000)
            if "authorize" in page.url.lower():
                print("⚠️ 检测到授权请求，尝试点击 Authorize...")
                page.click("button:has-text('Authorize')", timeout=5000)
        except:
            pass

        # 5. 等待跳转回 ClawCloud Dashboard
        print("⏳ 登录完成，等待重定向回 ClawCloud 控制台 (15秒)...")
        
        # 强制等待页面加载，因为 Dashboard 加载可能比较慢
        page.wait_for_timeout(10000) 
        page.wait_for_load_state("networkidle")

        final_url = page.url
        print(f"📍 最终页面 URL: {final_url}")
        
        # 截图保存 (调试用)
        page.screenshot(path="login_result.png")

        # 6. 验证是否成功
        # 根据您的截图，登录成功后页面上会有 "App Launchpad" 这个图标文字
        # 或者 URL 会包含 "private-team" 或 "console"
        
        is_success = False
        
        # 检查点 1: 页面上有 "App Launchpad" 文字 (这是最稳的)
        if page.get_by_text("App Launchpad").count() > 0:
            print("✅ 检测到 'App Launchpad' 文本。")
            is_success = True
        
        # 检查点 2: URL 包含 console 相关的词
        elif "private-team" in final_url or "console" in final_url:
            print("✅ URL 符合控制台特征。")
            is_success = True
            
        # 检查点 3: 排除法，只要不在 signin 页面
        elif "signin" not in final_url and "login" not in final_url and "github" not in final_url:
            print("✅ 已离开登录页，判定为成功。")
            is_success = True

        if is_success:
            print("🎉🎉🎉 恭喜！ClawCloud Run 登录成功！")
        else:
            print("❌ 登录判定失败。请查看 login_result.png 截图分析原因。")
            print("可能原因：GitHub 需要验证码，或者网络延迟过高。")
            exit(1) # 标记 GitHub Action 为失败

        browser.close()

if __name__ == "__main__":
    run_login()
