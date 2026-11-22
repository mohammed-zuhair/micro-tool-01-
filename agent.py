import os
import re
import sys
import datetime
import google.generativeai as genai

# 1. API Verification
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("CRITICAL ERROR: GEMINI_API_KEY is missing!")
    sys.exit(1)

genai.configure(api_key=api_key)

TOOLS_DIR = "tools"
os.makedirs(TOOLS_DIR, exist_ok=True)

# 2. Smart Model Discovery
def get_active_text_models():
    candidate_models = []
    try:
        for m in genai.list_models():
            name = m.name.lower()
            if any(skip in name for skip in ['tts', 'audio', 'lyria', 'image', 'transcribe', 'robotics', 'computer-use', 'antigravity']):
                continue
            if 'generateContent' in m.supported_generation_methods:
                candidate_models.append(m.name)
    except Exception as e:
        print(f"Model discovery notice: {e}")
    
    priority_models = [
        'models/gemini-2.0-flash',
        'models/gemini-1.5-flash',
        'models/gemini-1.5-pro',
        'models/gemini-flash-latest'
    ]
    
    final_list = [m for m in priority_models if m in candidate_models]
    for m in candidate_models:
        if m not in final_list:
            final_list.append(m)
            
    return final_list if final_list else priority_models

# 3. Targeted Generation: Standalone tool page + Card Snippet only
def generate_incremental_update(roadmap_text):
    existing_tools = os.listdir(TOOLS_DIR) if os.path.exists(TOOLS_DIR) else []
    models = get_active_text_models()
    
    prompt = f"""
أنت مهندس مطور أنظمة ويب (Surgical Incremental Code Architect).
مهمتك:
1. ابتكار أداة مصغرة جديدة فائقة الطلب (Viral High-Demand Tool).
2. توليد صفحة HTML مستقلة خفيفة جداً لهذه الأداة ليتم حفظها في مجلد tools/.
3. توليد قصاصة الكرت (Card Snippet) المخصص لهذه الأداة فقط ليتم حُقنه في الصفحة الرئيسية دون إعادة كتابة index.html.

الأدوات الحالية لمنع التكرار: {existing_tools}
الخطة/الدستور: {roadmap_text}

أخرج المخرجات بالتنسيق الصارم التالي حصراً:

---FILENAME---
[اسم الملف مثل: unit-converter.html]
---TITLE---
[اسم الأداة بالعربية]
---DESC---
[وصف الأداة في سطر واحد]
---TOOL_HTML_START---
[ضع كود صفحة الأداة المستقلة الكامل هنا من <!DOCTYPE html> إلى </html>]
---TOOL_HTML_END---

---CARD_SNIPPET_START---
[ضع هنا كود HTML الخاص ببطاقة الأداة فقط لإضافتها في index.html مثل: <a href="tools/filename.html" class="tool-card">...</a>]
---CARD_SNIPPET_END---

---LOG_START---
[تقرير فني مختصر عن الأداة]
---LOG_END---
"""

    gen_config = genai.GenerationConfig(max_output_tokens=4096, temperature=0.2)

    for model_name in models:
        try:
            print(f"Generating surgical update via {model_name}...")
            model = genai.GenerativeModel(model_name, generation_config=gen_config)
            res = model.generate_content(prompt, request_options={"timeout": 180})
            
            if res and res.text:
                text = res.text.strip()
                file_match = re.search(r'---FILENAME---([\s\S]*?)---TITLE---', text)
                title_match = re.search(r'---TITLE---([\s\S]*?)---DESC---', text)
                desc_match = re.search(r'---DESC---([\s\S]*?)---TOOL_HTML_START---', text)
                tool_html_match = re.search(r'---TOOL_HTML_START---([\s\S]*?)---TOOL_HTML_END---', text)
                card_match = re.search(r'---CARD_SNIPPET_START---([\s\S]*?)---CARD_SNIPPET_END---', text)
                log_match = re.search(r'---LOG_START---([\s\S]*?)---LOG_END---', text)
                
                if file_match and tool_html_match and card_match:
                    filename = file_match.group(1).strip().lower().replace(' ', '-')
                    # تنظيف اسم الملف من أي علامات تنصيص أو رموز زائدة
                    filename = re.sub(r"[^a-zA-Z0-9\-_.]", "", filename)
                    if not filename.endswith('.html'):
                        filename += '.html'
                        
                    title = title_match.group(1).strip() if title_match else "أداة مصغرة"
                    desc = desc_match.group(1).strip() if desc_match else "أداة جديدة"
                    tool_html = tool_html_match.group(1).strip()
                    card_snippet = card_match.group(1).strip()
                    log_text = log_match.group(1).strip() if log_match else "تم إضافة أداة جديدة."
                    
                    # تنظيف الأكواد
                    tool_html = re.sub(r'^```html\s*', '', tool_html, flags=re.IGNORECASE)
                    tool_html = re.sub(r'^```\s*', '', tool_html)
                    tool_html = re.sub(r'\s*```$', '', tool_html).strip()
                    
                    card_snippet = re.sub(r'^```html\s*', '', card_snippet, flags=re.IGNORECASE)
                    card_snippet = re.sub(r'^```\s*', '', card_snippet)
                    card_snippet = re.sub(r'\s*```$', '', card_snippet).strip()
                    
                    if "</html>" in tool_html:
                        return filename, title, desc, tool_html, card_snippet, log_text, model_name
        except Exception as e:
            print(f"Model {model_name} failed: {e}")
            
    return None, None, None, None, None, None, None

# 4. Surgical Injection into index.html (إدراج جراحي دون مسح الملف)
def inject_card_into_index(card_snippet, tool_rel_link):
    if not os.path.exists("index.html"):
        return False
        
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()
        
    # منع تكرار الأداة إذا كانت موجودة مسبقاً
    if tool_rel_link in content:
        print("Tool link already present in index.html. Skipping injection.")
        return True
        
    # البحث عن حاوية الأدوات وإقحام السطر فيها مباشرة
    inserted = False
    if 'id="tools-grid"' in content:
        content = re.sub(r'(<div[^>]*id="tools-grid"[^>]*>)', r'\1\n' + card_snippet, content, count=1)
        inserted = True
    elif 'class="tools-grid"' in content:
        content = re.sub(r'(<div[^>]*class="tools-grid"[^>]*>)', r'\1\n' + card_snippet, content, count=1)
        inserted = True
    elif 'class="grid"' in content:
        content = re.sub(r'(<div[^>]*class="grid"[^>]*>)', r'\1\n' + card_snippet, content, count=1)
        inserted = True
    else:
        # خيار إلحاق احتياطي قبل نهاية body
        if "</body>" in content:
            content = content.replace("</body>", f'<div class="tools-container">\n{card_snippet}\n</div>\n</body>', 1)
            inserted = True
            
    if inserted:
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(content)
        print("SUCCESS: Surgically injected card snippet into index.html")
        return True
    return False

# 5. Main Surgical Execution Gateway
if __name__ == "__main__":
    try:
        roadmap_text = ""
        if os.path.exists("roadmap.txt"):
            with open("roadmap.txt", "r", encoding="utf-8") as rf:
                roadmap_text = rf.read().strip()
                
        filename, title, desc, tool_html, card_snippet, log_text, used_model = generate_incremental_update(roadmap_text)
        
        if not filename or not tool_html or not card_snippet:
            print("NOTICE: Incremental update skipped in this cycle.")
            sys.exit(0)
            
        # أ) حفظ ملف الأداة المستقل في tools/
        tool_path = os.path.join(TOOLS_DIR, filename)
        with open(tool_path, "w", encoding="utf-8") as tf:
            tf.write(tool_html)
        print(f"SUCCESS: Created standalone tool file: {tool_path}")
        
        # ب) حقن السطر/الكرت جراحياً في index.html دون إعادة كتابته
        tool_link = f"tools/{filename}"
        inject_card_into_index(card_snippet, tool_link)
        
        # ج) الإلحاق بأسلوب Append لملف sitemap.xml
        if os.path.exists("sitemap.xml"):
            with open("sitemap.xml", "r", encoding="utf-8") as sf:
                sm_code = sf.read()
            today_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
            new_url_entry = f"  <url>\n    <loc>https://micro-tool-01.vercel.app/tools/{filename}</loc>\n    <lastmod>{today_str}</lastmod>\n    <priority>0.80</priority>\n  </url>"
            if tool_link not in sm_code and "</urlset>" in sm_code:
                sm_code = sm_code.replace("</urlset>", new_url_entry + "\n</urlset>")
                with open("sitemap.xml", "w", encoding="utf-8") as sf:
                    sf.write(sm_code)
                print("SUCCESS: Appended new URL entry to sitemap.xml")

        # د) الإلحاق بأسلوب Append لملف CHANGELOG.md
        now_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        log_entry = (
            f"\n\n## ⚡ تعديل جراحي وتطوير إضافي [{now_utc}]\n"
            f"**النموذج المنفذ:** `{used_model}`\n"
            f"**الأداة المضافة:** [{title}]({tool_link})\n"
            f"**نوع التعديل:** حقن أسطر مخصصة (Surgical Line Patching) دون مسح الملفات.\n\n"
            f"### 📋 التفاصيل الفنية:\n"
            f"{log_text}\n"
            f"\n---\n"
        )
        with open("CHANGELOG.md", "a", encoding="utf-8") as lf:
            lf.write(log_entry)
        print("SUCCESS: Appended log entry to CHANGELOG.md")

    except Exception as err:
        print(f"SURGICAL PIPELINE ERROR: {err}")
        sys.exit(0)
        
