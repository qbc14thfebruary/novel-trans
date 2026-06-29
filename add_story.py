import os
import json
import re
import subprocess
from datetime import datetime
import shutil

# ---------- Hàm chuẩn hóa ----------
def slugify(title):
    """Tạo slug từ tên truyện (chữ thường, bỏ dấu, thay khoảng trắng bằng -)"""
    # Chuyển sang chữ thường
    s = title.lower()
    # Loại bỏ dấu tiếng Việt
    map = {
        'à': 'a', 'á': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a',
        'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
        'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
        'đ': 'd',
        'è': 'e', 'é': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e',
        'ê': 'e', 'ề': 'e', 'ế': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
        'ì': 'i', 'í': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
        'ò': 'o', 'ó': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o',
        'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o',
        'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
        'ù': 'u', 'ú': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u',
        'ư': 'u', 'ừ': 'u', 'ứ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u',
        'ỳ': 'y', 'ý': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y'
    }
    for k, v in map.items():
        s = s.replace(k, v)
    # Thay khoảng trắng và ký tự đặc biệt bằng dấu gạch ngang
    s = re.sub(r'[^a-z0-9]+', '-', s).strip('-')
    return s

def generate_id(title):
    """Tạo ID từ tên (có thể dùng slug)"""
    return slugify(title)

def get_current_time():
    return datetime.now().isoformat() + 'Z'

# ---------- Hàm đọc data.json ----------
def load_data():
    with open('data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ---------- Hàm chính ----------
def main():
    print("📚 NHẬP THÔNG TIN TRUYỆN MỚI")
    print("-" * 40)

    # Nhập thông tin
    title = input("Tên truyện (VD: CHỐNG TỐI LÀ ỐNG CHỦ CỦA BẠN HỌC): ").strip()
    if not title:
        print("❌ Tên truyện không được để trống!")
        return

    # Tự động tạo slug và id
    slug = slugify(title)
    story_id = generate_id(title)

    author = input("Tác giả (Để trống = 'Đang cập nhật'): ").strip()
    if not author:
        author = "Đang cập nhật"

    genre = input("Thể loại (VD: Tiên hiệp, Ngôn tình, ...): ").strip()
    if not genre:
        genre = "Uncategorized"

    chapters = input("Số chương: ").strip()
    try:
        chapters = int(chapters)
        if chapters <= 0:
            raise ValueError
    except:
        print("❌ Số chương phải là số nguyên dương!")
        return

    description = input("Mô tả truyện (Để trống nếu không có): ").strip()
    if not description:
        description = ""

    views = 0  # mặc định

    status = input("Tình trạng (Đang ra/Đã hoàn thành/Tạm ngưng) [Đang ra]: ").strip()
    if not status:
        status = "Đang ra"

    tags_input = input("Tags (cách nhau bằng dấu phẩy, VD: hot,new) [hot]: ").strip()
    if tags_input:
        tags = [t.strip() for t in tags_input.split(',') if t.strip()]
    else:
        tags = ["hot"]

    # Tạo đối tượng truyện mới
    new_story = {
        "id": story_id,
        "title": title,
        "slug": slug,
        "cover": "cover.jpg",  # mặc định, script generate sẽ tạo ảnh
        "views": views,
        "chapters": chapters,
        "status": status,
        "last_update": get_current_time(),
        "tags": tags,
        "genre": genre,
        "author": author,
        "description": description
    }

    # Hiển thị preview
    print("\n📋 THÔNG TIN SẼ TẠO:")
    print(json.dumps(new_story, ensure_ascii=False, indent=2))
    confirm = input("\n✅ Xác nhận thêm truyện này? (y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ Đã hủy.")
        return

    # Đọc data.json hiện tại
    data = load_data()
    # Kiểm tra trùng slug
    existing_slugs = [item['slug'] for item in data['truyen']]
    if slug in existing_slugs:
        print(f"⚠️ Slug '{slug}' đã tồn tại! Vui lòng đổi tên truyện hoặc sửa slug thủ công.")
        return

    # Thêm vào data
    data['truyen'].append(new_story)
    save_data(data)
    print(f"✅ Đã thêm truyện '{title}' vào data.json")

    # Gọi script generate_stories.py để tạo folder và file
    print("🔄 Đang tạo thư mục và file cho truyện mới...")
    try:
        # Chạy generate_stories.py (chỉ tạo truyện mới, không --full)
        result = subprocess.run(
            ['python', 'generate_stories.py'],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            print("✅ Tạo thư mục và file thành công!")
            print(result.stdout)
        else:
            print("❌ Lỗi khi chạy generate_stories.py:")
            print(result.stderr)
    except Exception as e:
        print(f"❌ Không thể chạy generate_stories.py: {e}")

    print("\n🎉 Hoàn tất! Bạn có thể commit và push lên GitHub.")

if __name__ == "__main__":
    main()