import os
import json
import shutil
import argparse
from datetime import datetime

# ---------- Hàm tạo stt tự động ----------
def get_next_stt(data):
    """Tìm stt lớn nhất hiện có và trả về stt tiếp theo"""
    if not data['truyen']:
        return 1
    max_stt = max(item.get('stt', 0) for item in data['truyen'])
    return max_stt + 1

# ---------- Đọc data.json ----------
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Tạo thư mục novel nếu chưa có
os.makedirs('novel', exist_ok=True)

# ---------- Template (giữ nguyên) ----------
# ... (INFO_TEMPLATE, READ_TEMPLATE như cũ) ...

# ---------- Xử lý tham số dòng lệnh ----------
parser = argparse.ArgumentParser(description='Tạo thư mục truyện từ data.json')
parser.add_argument('--full', action='store_true', help='Chạy full: tạo lại tất cả (có xác nhận)')
args = parser.parse_args()

# ---------- Kiểm tra trạng thái ----------
existing_folders = set(os.listdir('novel')) if os.path.exists('novel') else set()
all_slugs = {item['slug'] for item in data['truyen']}
new_slugs = all_slugs - existing_folders

if not new_slugs and not args.full:
    print("✅ Không có truyện mới. Bạn có thể chạy với --full để tạo lại tất cả.")
    exit()

if args.full:
    print(f"⚠️ Bạn đang chạy chế độ FULL. Sẽ tạo lại tất cả {len(all_slugs)} truyện.")
    confirm = input("Bạn có chắc chắn? (y/n): ")
    if confirm.lower() != 'y':
        print("Đã hủy.")
        exit()
    process_slugs = all_slugs
else:
    print(f"📝 Phát hiện {len(new_slugs)} truyện mới: {', '.join(new_slugs)}")
    process_slugs = new_slugs

# ---------- Hàm tạo ảnh mặc định ----------
def create_default_cover(folder):
    cover_path = os.path.join(folder, 'cover.jpg')
    if not os.path.exists(cover_path):
        if os.path.exists('default-cover.jpg'):
            shutil.copy('default-cover.jpg', cover_path)
            print(f'   📷 Đã copy ảnh mặc định vào {folder}')
        else:
            try:
                from PIL import Image
                img = Image.new('RGB', (200, 260), color=(220, 220, 220))
                img.save(cover_path)
                print(f'   📷 Đã tạo ảnh trắng mặc định vào {folder}')
            except ImportError:
                print(f'   ⚠️ Không tạo được ảnh mặc định. Vui lòng thêm ảnh thủ công vào {folder}')

# ---------- Xử lý từng truyện ----------
for slug in process_slugs:
    item = next((x for x in data['truyen'] if x['slug'] == slug), None)
    if not item:
        print(f"⚠️ Không tìm thấy thông tin cho slug: {slug}")
        continue

    # Nếu truyện mới chưa có stt, gán stt tự động
    if 'stt' not in item or item['stt'] is None:
        item['stt'] = get_next_stt(data)
        print(f"   🆔 Gán STT {item['stt']} cho truyện '{slug}'")

    total_chaps = item['chapters']
    folder = os.path.join('novel', slug)
    os.makedirs(folder, exist_ok=True)

    # Config
    config_path = os.path.join(folder, 'config.json')
    if not os.path.exists(config_path) or args.full:
        config = {
            "title": item['title'],
            "totalChapters": total_chaps,
            "chapters": {str(i): {"locked": False, "aff_link": ""} for i in range(1, total_chaps+1)}
        }
        for i in range(1, total_chaps+1):
            if i % 2 == 0:
                config["chapters"][str(i)]["locked"] = True
                config["chapters"][str(i)]["aff_link"] = f"https://affiliate.com/{slug}-chap{i}"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

    # info.html và read.html (giữ nguyên)
    # ... (tạo info.html, read.html như cũ) ...

    # chapters.json
    chapters_path = os.path.join(folder, 'chapters.json')
    if not os.path.exists(chapters_path) or args.full:
        chapters_data = {"total": total_chaps, "chapters": {}}
        for i in range(1, total_chaps+1):
            content = f"<h2>Chương {i}</h2><p>Nội dung chương {i} sẽ được thêm vào đây.</p>"
            chapters_data["chapters"][str(i)] = content
        with open(chapters_path, 'w', encoding='utf-8') as f:
            json.dump(chapters_data, f, ensure_ascii=False, indent=2)

    # Ảnh bìa
    create_default_cover(folder)

    print(f'✅ Đã xử lý xong: {slug} (STT: {item["stt"]}, {total_chaps} chương)')

# Lưu lại data.json sau khi gán stt
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("💾 Đã cập nhật data.json với STT mới.")

print('🎉 Hoàn thành!')