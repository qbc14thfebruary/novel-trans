import os
import json
import shutil
import argparse
from PIL import Image  # Nếu không có PIL, bạn có thể comment hoặc cài pip install Pillow

# ---------- Đọc dữ liệu ----------
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

os.makedirs('novel', exist_ok=True)

# ---------- Các template ----------
INFO_TEMPLATE = '''<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title id="story-title">Thông tin truyện</title>
    <link rel="stylesheet" href="../css/style.css">
    <style>
        .story-info-container {
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background: #fff;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .story-info-header {
            display: flex;
            gap: 30px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        .story-info-header .cover {
            width: 200px;
            height: 260px;
            object-fit: cover;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            flex-shrink: 0;
            background: #eee;
        }
        .story-info-header .details {
            flex: 1;
            min-width: 250px;
        }
        .story-info-header .details h1 {
            font-size: 2rem;
            color: #2c3e50;
            margin-bottom: 15px;
        }
        .story-info-header .details .meta-item {
            margin-bottom: 8px;
            font-size: 1rem;
            color: #555;
        }
        .story-info-header .details .meta-item strong {
            color: #2c3e50;
            min-width: 80px;
            display: inline-block;
        }
        .story-description {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            line-height: 1.8;
            border-left: 4px solid #e67e22;
        }
        .chapter-list {
            margin-top: 30px;
        }
        .chapter-list h3 {
            font-size: 1.3rem;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 10px;
            margin-bottom: 15px;
            color: #2c3e50;
        }
        .chapter-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
            gap: 10px;
        }
        .chapter-grid a {
            display: block;
            padding: 10px 15px;
            background: #f8f9fa;
            border-radius: 5px;
            text-decoration: none;
            color: #2c3e50;
            transition: all 0.25s ease;
            text-align: center;
            font-size: 0.95rem;
            border: 1px solid #e9ecef;
            position: relative;
        }
        .chapter-grid a:hover {
            background: #e67e22;
            color: #fff;
            transform: translateY(-3px);
            box-shadow: 0 6px 16px rgba(230, 126, 34, 0.3);
            border-color: #e67e22;
        }
        .chapter-grid a.locked {
            background: #fef9e7;
            border-color: #f39c12;
        }
        .chapter-grid a.locked:hover {
            background: #f39c12;
            color: #fff;
            border-color: #f39c12;
            box-shadow: 0 6px 16px rgba(243, 156, 18, 0.4);
        }
        .chapter-grid a.locked::after {
            content: " 🔒";
            font-size: 0.75rem;
            opacity: 0.7;
        }
        .pagination {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-top: 20px;
            flex-wrap: wrap;
        }
        .pagination button {
            padding: 8px 20px;
            border: 1px solid #ddd;
            background: #fff;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .pagination button:hover:not(:disabled) {
            background: #3498db;
            color: #fff;
            border-color: #3498db;
        }
        .pagination button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        .pagination .page-info {
            padding: 8px 15px;
            background: #ecf0f1;
            border-radius: 5px;
            color: #2c3e50;
        }
        .back-home {
            display: inline-block;
            margin-bottom: 20px;
            color: #3498db;
            text-decoration: none;
            font-weight: bold;
        }
        .back-home:hover {
            text-decoration: underline;
        }
        @media (max-width: 600px) {
            .story-info-header {
                flex-direction: column;
                align-items: center;
                text-align: center;
            }
            .story-info-header .cover {
                width: 160px;
                height: 210px;
            }
            .story-info-header .details h1 {
                font-size: 1.5rem;
            }
            .story-info-header .details .meta-item strong {
                min-width: 60px;
            }
            .chapter-grid {
                grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
            }
        }
    </style>
</head>
<body>
    <div class="container story-info-container">
        <a href="../../index.html" class="back-home">⬅ Quay lại trang chủ</a>
        <div id="story-content">
            <p>Đang tải thông tin...</p>
        </div>
    </div>
    <script>
        const pathParts = window.location.pathname.split('/');
        const slug = pathParts[pathParts.length - 2] || '';
        let storyData = null;
        let configData = null;
        let currentPage = 1;
        const ITEMS_PER_PAGE = 20;
        const contentDiv = document.getElementById('story-content');

        async function loadData() {
            try {
                const configRes = await fetch('config.json');
                if (configRes.ok) configData = await configRes.json();
                const dataRes = await fetch('../../data.json');
                if (!dataRes.ok) throw new Error('Không tải được data.json');
                const data = await dataRes.json();
                storyData = data.truyen.find(item => item.slug === slug);
                if (!storyData) {
                    contentDiv.innerHTML = '<p style="color:red;">Không tìm thấy thông tin truyện.</p>';
                    return;
                }
                renderStory();
            } catch (error) {
                console.error('Lỗi:', error);
                contentDiv.innerHTML = '<p style="color:red;">Không thể tải thông tin truyện.</p>';
            }
        }

        function renderStory() {
            const { title, cover, author, genre, status, description, chapters, views } = storyData;
            document.getElementById('story-title').textContent = title;
            const coverPath = cover ? `./${cover}` : './cover.jpg';
            let html = `
                <div class="story-info-header">
                    <img class="cover" src="${coverPath}" alt="${title}" onerror="this.src='./cover.jpg'">
                    <div class="details">
                        <h1>${title}</h1>
                        <div class="meta-item"><strong>Tác giả:</strong> ${author || 'Đang cập nhật'}</div>
                        <div class="meta-item"><strong>Thể loại:</strong> ${genre || 'Uncategorized'}</div>
                        <div class="meta-item"><strong>Tình trạng:</strong> ${status || 'Đang ra'}</div>
                        <div class="meta-item"><strong>Lượt xem:</strong> ${views ? views.toLocaleString() : 0}</div>
                        <div class="meta-item"><strong>Số chương:</strong> ${chapters}</div>
                    </div>
                </div>
            `;
            if (description) html += `<div class="story-description">${description}</div>`;
            html += `<div class="chapter-list"><h3>📖 DANH SÁCH CHƯƠNG</h3>`;
            html += renderChapters(currentPage);
            html += `</div>`;
            contentDiv.innerHTML = html;
        }

        function renderChapters(page) {
            const total = storyData.chapters;
            const totalPages = Math.ceil(total / ITEMS_PER_PAGE);
            const start = (page - 1) * ITEMS_PER_PAGE + 1;
            const end = Math.min(page * ITEMS_PER_PAGE, total);
            let html = `<div class="chapter-grid">`;
            for (let i = start; i <= end; i++) {
                const isLocked = configData && configData.chapters && configData.chapters[i] && configData.chapters[i].locked === true;
                const lockedClass = isLocked ? 'locked' : '';
                html += `<a href="read.html?chap=${i}" class="${lockedClass}">Chương ${i}</a>`;
            }
            html += `</div>`;
            html += `<div class="pagination">`;
            html += `<button onclick="goToPage(${page - 1})" ${page <= 1 ? 'disabled' : ''}>⬅ Trước</button>`;
            html += `<span class="page-info">${page} / ${totalPages}</span>`;
            html += `<button onclick="goToPage(${page + 1})" ${page >= totalPages ? 'disabled' : ''}>Sau ➡</button>`;
            html += `</div>`;
            return html;
        }

        function goToPage(page) {
            const total = storyData.chapters;
            const totalPages = Math.ceil(total / ITEMS_PER_PAGE);
            if (page < 1 || page > totalPages) return;
            currentPage = page;
            renderStory();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }

        loadData();
    </script>
</body>
</html>'''

READ_TEMPLATE = '''<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Đọc truyện</title>
    <link rel="stylesheet" href="../css/style.css">
    <style>
        .reader-container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: #fff;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            position: relative;
        }
        .chapter-nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 20px 0;
        }
        .chapter-nav button {
            padding: 10px 25px;
            border: none;
            background: #3498db;
            color: #fff;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1rem;
            transition: background 0.2s;
        }
        .chapter-nav button:hover:not(:disabled) {
            background: #2980b9;
        }
        .chapter-nav button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        .chapter-title {
            font-size: 1.8rem;
            text-align: center;
            margin: 10px 0 20px;
        }
        #chapter-content {
            min-height: 300px;
            padding: 10px 0;
            line-height: 1.8;
            font-size: 1.1rem;
        }
        #lock-overlay {
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.85);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            flex-direction: column;
            color: white;
            text-align: center;
        }
        #lock-overlay.show {
            display: flex;
        }
        #lock-overlay h2 {
            font-size: 2.5rem;
            margin-bottom: 20px;
        }
        #lock-overlay p {
            font-size: 1.2rem;
            margin-bottom: 30px;
        }
        .btn-aff {
            display: inline-block;
            background: #e67e22;
            color: #fff;
            padding: 15px 40px;
            border-radius: 50px;
            font-size: 1.3rem;
            font-weight: bold;
            text-decoration: none;
            transition: background 0.2s;
        }
        .btn-aff:hover {
            background: #d35400;
        }
        @media (max-width: 600px) {
            .reader-container { padding: 15px; }
            .chapter-title { font-size: 1.4rem; }
            #chapter-content { font-size: 1rem; }
            .chapter-nav button { padding: 8px 15px; font-size: 0.9rem; }
        }
        .back-info {
            display: inline-block;
            margin-bottom: 15px;
            color: #3498db;
            text-decoration: none;
            font-weight: bold;
        }
        .back-info:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container reader-container">
        <a href="info.html" class="back-info">⬅ Quay lại thông tin truyện</a>
        <h1 class="chapter-title" id="chapter-title">Chương 1</h1>
        <div id="chapter-content">
            <p>Đang tải nội dung...</p>
        </div>
        <div class="chapter-nav">
            <button id="prev-btn" disabled>⬅ Prev</button>
            <span id="chap-info">1 / 13</span>
            <button id="next-btn">Next ➡</button>
        </div>
    </div>
    <div id="lock-overlay">
        <h2>🔒 Truyện đã bị khóa</h2>
        <p>Nhấn nút bên dưới để mở khóa và đọc tiếp</p>
        <a href="#" id="aff-link" class="btn-aff" target="_blank">👉 Mở khóa ngay</a>
    </div>
    <script>
        const urlParams = new URLSearchParams(window.location.search);
        let currentChap = parseInt(urlParams.get('chap')) || 1;
        let configData = null;
        let totalChapters = 0;
        const contentDiv = document.getElementById('chapter-content');
        const titleEl = document.getElementById('chapter-title');
        const prevBtn = document.getElementById('prev-btn');
        const nextBtn = document.getElementById('next-btn');
        const chapInfo = document.getElementById('chap-info');
        const overlay = document.getElementById('lock-overlay');
        const affLink = document.getElementById('aff-link');

        function loadConfig() {
            return fetch('config.json')
                .then(res => { if (!res.ok) throw new Error('Không tải được config'); return res.json(); })
                .then(data => { configData = data; totalChapters = data.totalChapters; })
                .catch(err => { console.error('Lỗi config:', err); contentDiv.innerHTML = '<p style="color:red;">Không thể tải cấu hình truyện.</p>'; });
        }

        function loadChapter(chap) {
            if (chap < 1) chap = 1;
            if (chap > totalChapters) chap = totalChapters;
            currentChap = chap;
            const newUrl = window.location.pathname + '?chap=' + chap;
            window.history.pushState({ path: newUrl }, '', newUrl);
            titleEl.textContent = `Chương ${chap}`;
            chapInfo.textContent = `${chap} / ${totalChapters}`;
            prevBtn.disabled = (chap === 1);
            nextBtn.disabled = (chap === totalChapters);
            fetch(`chapter${chap}.html`)
                .then(res => { if (!res.ok) throw new Error('Không tìm thấy chapter'); return res.text(); })
                .then(html => { contentDiv.innerHTML = html; checkLock(chap); })
                .catch(err => { contentDiv.innerHTML = `<p style="color:red;">Lỗi tải chương: ${err.message}</p>`; });
        }

        function checkLock(chap) {
            if (!configData) return;
            const chapterConfig = configData.chapters[chap.toString()];
            const isLocked = chapterConfig && chapterConfig.locked === true;
            const aff = chapterConfig ? chapterConfig.aff_link : '';
            if (isLocked && aff) { affLink.href = aff; overlay.classList.add('show'); }
            else { overlay.classList.remove('show'); }
        }

        function unlock() { overlay.classList.remove('show'); }
        affLink.addEventListener('click', unlock);
        prevBtn.addEventListener('click', function() { if (currentChap > 1) loadChapter(currentChap - 1); });
        nextBtn.addEventListener('click', function() { if (currentChap < totalChapters) loadChapter(currentChap + 1); });
        window.addEventListener('popstate', function(e) {
            const chap = new URLSearchParams(window.location.search).get('chap');
            if (chap) loadChapter(parseInt(chap)); else loadChapter(1);
        });
        loadConfig().then(() => { if (configData) loadChapter(currentChap); });
    </script>
</body>
</html>'''

CHAPTER_TEMPLATE = '''<script>
    (function() {{
        if (window.top === window.self) {{
            var chap = window.location.pathname.match(/chapter(\\d+)\\.html/);
            if (chap) window.location.href = 'info.html?chap=' + chap[1];
            else window.location.href = 'info.html';
        }}
    }})();
</script>
<h2>Chương {chap_num}</h2>
<p>Nội dung chương {chap_num} sẽ được thêm vào đây.</p>'''

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

    # info.html
    info_path = os.path.join(folder, 'info.html')
    if not os.path.exists(info_path) or args.full:
        with open(info_path, 'w', encoding='utf-8') as f:
            f.write(INFO_TEMPLATE)

    # read.html
    read_path = os.path.join(folder, 'read.html')
    if not os.path.exists(read_path) or args.full:
        with open(read_path, 'w', encoding='utf-8') as f:
            f.write(READ_TEMPLATE)

    # chapter files
    for i in range(1, total_chaps+1):
        chap_file = os.path.join(folder, f'chapter{i}.html')
        if not os.path.exists(chap_file) or args.full:
            chap_content = CHAPTER_TEMPLATE.format(chap_num=i)
            with open(chap_file, 'w', encoding='utf-8') as f:
                f.write(chap_content)

    # ảnh bìa
    create_default_cover(folder)

    print(f'✅ Đã xử lý xong: {slug} (tổng {total_chaps} chương)')

print('🎉 Hoàn thành!')


# ---------- Run full: python generate_stories.py --full ----------
# ---------- Run new : python generate_stories.py        ----------