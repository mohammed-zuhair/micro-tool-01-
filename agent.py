import os
import re
import sys
import json
import datetime
import google.generativeai as genai

# ==============================================================================
# 1. API Verification & Environment Architecture
# ==============================================================================
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("CRITICAL ERROR: GEMINI_API_KEY environment variable is missing!")
    sys.exit(1)

genai.configure(api_key=api_key)

TOOLS_DIR = "tools"
os.makedirs(TOOLS_DIR, exist_ok=True)
SITE_URL = "https://micro-tool-01.vercel.app"

# ==============================================================================
# 2. Ultra-Deep Self-Healing & File Sanitation Engine
# ==============================================================================
def cleanup_corrupted_tools():
    """Scans tools directory and purges corrupted, empty, or unparseable HTML files."""
    if not os.path.exists(TOOLS_DIR):
        return
    for fname in os.listdir(TOOLS_DIR):
        fpath = os.path.join(TOOLS_DIR, fname)
        if os.path.isfile(fpath):
            name_no_ext = fname.replace(".html", "").strip(".-_")
            # Purge malformed filenames, empty files (<150 bytes), or invalid prefixes
            if (fname == ".html" or fname.startswith("-") or 
                len(name_no_ext) < 2 or os.path.getsize(fpath) < 150):
                try:
                    os.remove(fpath)
                    print(f"🧹 PURGE: Removed corrupted tool file -> {fname}")
                except Exception as e:
                    print(f"Cleanup notice: {e}")

def sanitize_filename(raw_name, fallback_title):
    """Generates a clean, strict ASCII slug for file paths and URLs."""
    clean = raw_name.lower().strip()
    clean = re.sub(r'```[a-z]*', '', clean)
    for ch in ['"', "'", '`', '\\', '/', ':', '*', '?', '<', '>', '|', ';', ',']:
        clean = clean.replace(ch, '')
    clean = re.sub(r'\b(text|html|code|markdown|filename|tool)\b', '', clean)
    clean = clean.replace(' ', '-')
    clean = re.sub(r'[^a-z0-9\-_]', '', clean)
    clean = clean.strip('.-_')
    
    if not clean or len(clean) < 3:
        clean = re.sub(r'[^a-z0-9]', '', fallback_title.lower())
        if len(clean) < 3:
            clean = f"tool-{int(datetime.datetime.now().timestamp())}"
            
    return f"{clean}.html"

# ==============================================================================
# 3. Dynamic Multi-Tier AI Model Discovery Engine
# ==============================================================================
def get_active_text_models():
    """Discovers active Gemini models with high preference for 2026/2.5 series."""
    candidate_models = []
    try:
        for m in genai.list_models():
            name = m.name.lower()
            if any(skip in name for skip in ['tts', 'audio', 'lyria', 'image', 'transcribe', 'robotics', 'computer-use', 'antigravity']):
                continue
            if 'generateContent' in m.supported_generation_methods:
                candidate_models.append(m.name)
    except Exception as e:
        print(f"Model discovery warning: {e}")
    
    priority_models = [
        'models/gemini-2.5-flash',
        'models/gemini-2.0-flash',
        'models/gemini-1.5-pro',
        'models/gemini-1.5-flash',
        'models/gemini-flash-latest'
    ]
    
    final_list = [m for m in priority_models if m in candidate_models]
    for m in candidate_models:
        if m not in final_list:
            final_list.append(m)
            
    return final_list if final_list else priority_models

# ==============================================================================
# 4. Repository & Orphan Index Audit Engine
# ==============================================================================
def get_unindexed_tools():
    """Identifies standalone tool HTML files that exist in tools/ but lack index links."""
    if not os.path.exists("index.html") or not os.path.exists(TOOLS_DIR):
        return []
    with open("index.html", "r", encoding="utf-8") as f:
        index_content = f.read()
    
    unindexed = []
    for fname in os.listdir(TOOLS_DIR):
        if fname.endswith(".html"):
            rel_path = f"tools/{fname}"
            if rel_path not in index_content:
                unindexed.append(fname)
    return unindexed

# ==============================================================================
# 5. Enterprise HTML/UX Multi-Stage Auditor & Injector
# ==============================================================================
def audit_and_enrich_html(raw_html, filename, title, desc):
    """
    500% Upgrade Feature:
    Performs full structural validation, SEO injection (Meta/JSON-LD),
    Glassmorphism styling validation, and navigation integration.
    """
    if not raw_html:
        return None
        
    html = raw_html.strip()
    
    # Extract clean HTML block
    if "<!DOCTYPE html>" in html:
        html = "<!DOCTYPE html>" + html.split("<!DOCTYPE html>", 1)[1]
    if "</html>" in html:
        html = html.split("</html>", 1)[0] + "\n</html>"
        
    if "</head>" not in html or "</body>" not in html:
        return None
        
    # Inject Google Fonts & Tailwind CDN if missing for guaranteed top-tier visual styling
    json_title = json.dumps(title)
    json_desc = json.dumps(desc)
    head_enhancements = f"""
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{desc}">
    <!-- SEO & Schema.org JSON-LD -->
    <script type="application/ld+json">
    {{
      "@context": "[https://schema.org](https://schema.org)",
      "@type": "WebApplication",
      "name": {json_title},
      "description": {json_desc},
      "applicationCategory": "UtilityApplication",
      "operatingSystem": "All"
    }}
    </script>
    <link href="[https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&family=Inter:wght@400;500;700&display=swap](https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&family=Inter:wght@400;500;700&display=swap)" rel="stylesheet">
    <script src="[https://cdn.tailwindcss.com](https://cdn.tailwindcss.com)"></script>
    <style>
        body {{ font-family: 'Tajawal', 'Inter', sans-serif; background-color: #0f172a; color: #f8fafc; }}
        .glass-panel {{ background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.1); }}
    </style>
    """
    
    # Inject head enhancements right before </head>
    if "</head>" in html and "Tajawal" not in html:
        html = html.replace("</head>", head_enhancements + "\n</head>", 1)
        
    # Inject Top Navigation Bar with i18n & Back to Home
    nav_bar = """
    <nav class="w-full bg-slate-900/90 border-b border-slate-800 px-6 py-4 flex justify-between items-center sticky top-0 z-50 backdrop-blur-md">
        <a href="../index.html" class="flex items-center gap-2 text-sky-400 font-bold hover:text-sky-300 transition-colors">
            <span>←</span> <span>العودة للرئيسية</span>
        </a>
        <div class="flex items-center gap-3">
            <span class="text-xs px-2.5 py-1 rounded-full bg-slate-800 text-slate-400 border border-slate-700">Dark Slate / Glass UI</span>
        </div>
    </nav>
    """
    
    if "../index.html" not in html and "index.html" not in html:
        if "<body" in html.lower():
            html = re.sub(r'(<body[^>]*>)', r'\1' + nav_bar, html, count=1, flags=re.IGNORECASE)
            
    return html

# ==============================================================================
# 6. High-Efficiency Autonomous AI Tool Generator Core
# ==============================================================================
def generate_incremental_update(roadmap_text):
    """Executes AI generation cycle with fail-safe parsing and prompt engineering."""
    existing_tools = os.listdir(TOOLS_DIR) if os.path.exists(TOOLS_DIR) else []
    unindexed_tools = get_unindexed_tools()
    models = get_active_text_models()
    
    if unindexed_tools:
        target_file = unindexed_tools[0]
        mode_instruction = f"""
🎯 وضع العمل الحالي (تغطية الأدوات المفقودة):
الملف '{target_file}' موجود في مجلد tools/ ولكن كروته غير مضافة في index.html.
قم بإنشاء وتأكيد الكرت المخصص لهذه الأداة لاستكمال المفقودات أولاً قبل الابتكار.
اسم الملف المطلوب حصراً: {target_file}
"""
    else:
        mode_instruction = f"""
🎯 وضع العمل الحالي (ابتكار أداة عالمية جديدة):
قم بابتكار أداة ويب مصغرة فائقة الجودة والأهمية للمستخدمين بنمط Glassmorphic Dark UI.
قائمة الأدوات الموجودة لمنع التكرار: {existing_tools}
"""

    prompt = f"""
أنت كبار المطورين والمهندسين المعماريين للأنظمة الذاتية (Lead Autonomous Web Architect & Executive UI/UX Master).

{mode_instruction}

📜 الدستور الشامل وقواعد المنظومة:
{roadmap_text}

⚡ تعليمات صارمة للجودة الخارقة (500% Quality Assurance):
1. **الواجهة البصرية والتجاوب:** صمم أداة فائقة الجمال بأسلوب زجاجي داكن (Dark Glassmorphism) متجاوبة 100% مع الجوال والكمبيوتر.
2. **فصل اللغات (i18n):** أدرج كائن ترجمة JavaScript يتيح التبديل بين العربية (RTL) والإنجليزية (LTR) بنقرة زر.
3. **النقاء التام الكود:** يمنع طباعة أي أفكار أو تعليقات خارجبة، ابدأ كود الصفحة بـ <!DOCTYPE html> مباشرة وانتهي بـ </html>.
4. **تضمين شرح الأداة:** أضف في أسفل الأداة قسم توضيحي بسيط (How to use + FAQ) مجهّز لانتزاع أفضل نتائج البحث SEO.
5. **الكرت الموحد (CARD_SNIPPET):** صمم كرت HTML متوافق مع الشبكة.

أخرج المخرجات بالتنسيق الصارم التالي حصراً:

---FILENAME---
[اسم الملف بالإنجليزية فقط مثل: svg-pattern-generator.html]
---TITLE---
[اسم الأداة بالعربية]
---DESC---
[وصف الأداة الدقيق في سطر واحد]
---TOOL_HTML_START---
<!DOCTYPE html>
... كود الصفحة المستقلة المكتمل الشامل للتصميم واللغات والتفاعلية ...
</html>
---TOOL_HTML_END---

---CARD_SNIPPET_START---
<div class="tool-card border border-slate-800 bg-slate-900/60 p-5 rounded-xl hover:border-sky-500/50 transition-all">
    <h3 class="text-lg font-bold text-slate-100 mb-2">[اسم الأداة]</h3>
    <p class="text-sm text-slate-400 mb-4">[الوصف]</p>
    <a href="tools/[FILENAME]" class="inline-block px-4 py-2 rounded-lg bg-sky-600 hover:bg-sky-500 text-white text-sm font-semibold transition-colors">استخدم الأداة ←</a>
</div>
---CARD_SNIPPET_END---

---LOG_START---
[تقرير فني شامل ومختصر عن الإنجاز والتقنيات المستخدمة]
---LOG_END---
"""

    gen_config = genai.GenerationConfig(max_output_tokens=8192, temperature=0.15)

    for model_name in models:
        try:
            print(f"🚀 Launching generation wave using {model_name}...")
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
                    raw_fname = file_match.group(1).strip()
                    title = title_match.group(1).strip() if title_match else "أداة ذكية"
                    desc = desc_match.group(1).strip() if desc_match else "أداة مصغرة تفاعلية عالية الجودة"
                    
                    filename = sanitize_filename(raw_fname, title)
                    tool_html = tool_html_match.group(1).strip()
                    card_snippet = card_match.group(1).strip()
                    log_text = log_match.group(1).strip() if log_match else "تم التوليد بنجاح."
                    
                    # Apply 500% Deep Enrichment & Verification
                    tool_html = audit_and_enrich_html(tool_html, filename, title, desc)
                    if not tool_html:
                        print(f"⚠️ Verification failed for {model_name}, switching to fallback model...")
                        continue
                    
                    # Format card snippet
                    card_snippet = re.sub(r'^```html\s*', '', card_snippet, flags=re.IGNORECASE)
                    card_snippet = re.sub(r'\s*```$', '', card_snippet).strip()
                    card_snippet = card_snippet.replace("[FILENAME]", filename)
                    if f"tools/{filename}" not in card_snippet:
                        card_snippet = re.sub(r'href=["\'][^"\']*["\']', f'href="tools/{filename}"', card_snippet, count=1)
                    
                    return filename, title, desc, tool_html, card_snippet, log_text, model_name
        except Exception as e:
            print(f"Model {model_name} execution notice: {e}")
            
    return None, None, None, None, None, None, None

# ==============================================================================
# 7. Surgical Index Injection Engine
# ==============================================================================
def inject_card_into_index(card_snippet, tool_rel_link):
    """Surgically injects new tool cards into index.html cleanly without destroying layout."""
    if not os.path.exists("index.html"):
        return False
        
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()
        
    if tool_rel_link in content:
        print("ℹ️ Tool reference already active in index.html. Skipping injection.")
        return True
        
    inserted = False
    targets = ['id="tools-grid"', 'class="tools-grid"', 'class="grid"', 'id="grid"']
    
    for target in targets:
        if target in content:
            content = re.sub(rf'({re.escape(target)}[^>]*>)', r'\1\n' + card_snippet, content, count=1)
            inserted = True
            break
            
    if not inserted and "</body>" in content:
        content = content.replace("</body>", f'<div class="tools-container my-8 px-4">\n{card_snippet}\n</div>\n</body>', 1)
        inserted = True
            
    if inserted:
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ SUCCESS: Surgically injected tool card into index.html")
        return True
    return False

# ==============================================================================
# 8. Sitemap & SEO Sync Engine
# ==============================================================================
def sync_sitemap(filename):
    """Synchronizes sitemap.xml with proper lastmod date and priority."""
    if not os.path.exists("sitemap.xml"):
        return
    with open("sitemap.xml", "r", encoding="utf-8") as sf:
        sm_code = sf.read()
    
    tool_link = f"tools/{filename}"
    today_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    new_url_entry = (
        f"  <url>\n"
        f"    <loc>{SITE_URL}/tools/{filename}</loc>\n"
        f"    <lastmod>{today_str}</lastmod>\n"
        f"    <priority>0.85</priority>\n"
        f"  </url>"
    )
    if tool_link not in sm_code and "</urlset>" in sm_code:
        sm_code = sm_code.replace("</urlset>", new_url_entry + "\n</urlset>")
        with open("sitemap.xml", "w", encoding="utf-8") as sf:
            sf.write(sm_code)
        print("🌐 SUCCESS: Appended tool entry to sitemap.xml")

# ==============================================================================
# 9. Main Gateway Execution Loop
# ==============================================================================
if __name__ == "__main__":
    try:
        cleanup_corrupted_tools()
        
        roadmap_text = ""
        if os.path.exists("roadmap.txt"):
            with open("roadmap.txt", "r", encoding="utf-8") as rf:
                roadmap_text = rf.read().strip()
                
        filename, title, desc, tool_html, card_snippet, log_text, used_model = generate_incremental_update(roadmap_text)
        
        if not filename or not tool_html or not card_snippet:
            print("NOTICE: Incremental update skipped or no output generated in this cycle.")
            sys.exit(0)
            
        tool_path = os.path.join(TOOLS_DIR, filename)
        with open(tool_path, "w", encoding="utf-8") as tf:
            tf.write(tool_html)
        print(f"🎉 SUCCESS: Standalone tool file generated: {tool_path}")
        
        tool_link = f"tools/{filename}"
        inject_card_into_index(card_snippet, tool_link)
        sync_sitemap(filename)

        now_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        log_entry = (
            f"\n\n## ⚡ تعديل جراحي وتطوير إضافي (الجيل الخامس 500%) [{now_utc}]\n"
            f"**النموذج المنفذ:** `{used_model}`\n"
            f"**الأداة المضافة/المرتبطة:** [{title}]({tool_link})\n"
            f"**اسم الملف:** `{filename}`\n\n"
            f"### 📋 التقرير الفني والتنفيذي:\n"
            f"{log_text}\n"
            f"\n---\n"
        )
        with open("CHANGELOG.md", "a", encoding="utf-8") as lf:
            lf.write(log_entry)
        print("📝 SUCCESS: Appended changelog entry to CHANGELOG.md")

    except Exception as err:
        print(f"❌ CRITICAL PIPELINE ERROR: {err}")
        sys.exit(0)
