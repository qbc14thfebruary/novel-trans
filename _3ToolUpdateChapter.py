import os
import re
import json
import shutil
from datetime import datetime

# ---------- Cấu hình ----------
BACKUP_ENABLED = False  # Nếu True, sẽ tạo bản backup trước khi ghi chapters.json
MD_FILE = 'update.md'
BASE_DIR = 'novel'
DATA_JSON = 'data.json'

# ---------- Hàm làm sạch HTML ----------
def clean_chapter_html(raw_html):
    raw_html = raw_html.strip()
    patterns = [
        r'<div[^>]*id=["\']chapter-c["\'][^>]*>(.*?)</div>',
        r'<div[^>]*class=["\'][^"\']*chapter-content-area[^"\']*["\'][^>]*>(.*?)</div>'
    ]
    for pattern in patterns:
        match = re.search(pattern, raw_html, re.DOTALL | re.IGNORECASE)
        if match:
            raw_html = match.group(1)
            break
    lines = [line.strip() for line in raw_html.splitlines() if line.strip()]
    clean_html = '\n'.join(lines)
    # Sửa thẻ p thiếu dấu >
    clean_html = re.sub(r'<p([^>]*)>([^<]*?)(?=<p|$)', r'<p\1>\2</p>', clean_html, flags=re.DOTALL)
    return clean_html

# ---------- Xử lý nội dung: tự động nhận diện HTML hay text ----------
def clean_and_format_content(raw_content):
    content = raw_content.strip()
    if not content:
        return ""

    # Kiểm tra xem có phải HTML không (có thẻ mở)
    if re.search(r'<[^>]+>', content):
        # Đã có HTML
        return clean_chapter_html(content)
    else:
        # Text thuần -> HTML
        paragraphs = re.split(r'\n\s*\n', content)
        html_parts = []
        for para in paragraphs:
            lines = para.splitlines()
            if len(lines) > 1:
                text = '<br>'.join(line.strip() for line in lines if line.strip())
            else:
                text = para.strip()
            if text:
                html_parts.append(f"<p>{text}</p>")
        return '\n'.join(html_parts)

# ---------- Hàm tìm slug từ stt ----------
def get_slug_from_stt(stt, data_path=DATA_JSON):
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Lỗi đọc data.json: {e}")
        return None
    for item in data['truyen']:
        if item.get('stt') == stt:
            return item.get('slug')
    print(f"❌ Không tìm thấy truyện có STT = {stt}")
    return None

# ---------- Cập nhật một chapter ----------
def update_single_chapter(stt, chapter_number, raw_content):
    slug = get_slug_from_stt(stt)
    if not slug:
        return False

    story_path = os.path.join(BASE_DIR, slug)
    chapters_path = os.path.join(story_path, 'chapters.json')

    if not os.path.exists(story_path):
        print(f"❌ Không tìm thấy thư mục: {story_path}")
        return False
    if not os.path.exists(chapters_path):
        print(f"❌ Không tìm thấy chapters.json trong {story_path}")
        return False

    try:
        with open(chapters_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Lỗi đọc JSON: {e}")
        return False

    # Xử lý nội dung (HTML hoặc text)
    final_html = clean_and_format_content(raw_content)

    if BACKUP_ENABLED:
        backup_path = f"{chapters_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        try:
            shutil.copy2(chapters_path, backup_path)
            print(f"💾 Backup: {backup_path}")
        except Exception as e:
            print(f"⚠️ Không backup được: {e}")

    data['chapters'][str(chapter_number)] = final_html
    data['total'] = len(data['chapters'])

    try:
        with open(chapters_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ Cập nhật chương {chapter_number} của truyện STT {stt} (slug: {slug})")
        return True
    except Exception as e:
        print(f"❌ Ghi file thất bại: {e}")
        return False

# ---------- Phân tích file .md ----------
def parse_and_update_md(md_path):
    if not os.path.exists(md_path):
        print(f"⚠️ Không tìm thấy file: {md_path}")
        return

    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    current_stt = None
    current_chapter = None
    content_lines = []
    total_updated = 0

    def flush():
        nonlocal current_stt, current_chapter, content_lines, total_updated
        if current_stt is not None and current_chapter is not None and content_lines:
            raw = ''.join(content_lines).strip()
            if raw:
                if update_single_chapter(current_stt, current_chapter, raw):
                    total_updated += 1
            content_lines = []

    for line in lines:
        stripped = line.strip()

        match_stt = re.match(r'^#\s*STT\s*:\s*(\d+)\s*$', stripped, re.IGNORECASE)
        if match_stt:
            flush()
            current_stt = int(match_stt.group(1))
            current_chapter = None
            continue

        match_chap = re.match(r'^##\s*Chapter\s*:\s*(\d+)\s*$', stripped, re.IGNORECASE)
        if match_chap:
            flush()
            current_chapter = int(match_chap.group(1))
            continue

        # Nội dung
        if current_stt is not None and current_chapter is not None:
            content_lines.append(line)

    flush()
    print(f"🎉 Tổng số chapter đã cập nhật: {total_updated}")

# ---------- Main ----------
def main():
    parse_and_update_md(MD_FILE)

if __name__ == '__main__':
    main()