// js/main.js

// Biến toàn cục
let allTruyen = [];
let filteredTruyen = [];
let currentDisplay = {
    hot: 6,
    new: 6,
    updated: 6
};
let currentGenre = 'all';
let searchKeyword = '';

// DOM ready
document.addEventListener('DOMContentLoaded', function() {
    loadData();
    setupSearchAndFilter();
    setupHamburger();
    // KHÔNG gọi setupGenreDropdown() ở đây nữa
});

// ---------- Hàm loại bỏ dấu tiếng Việt ----------
function removeVietnameseTones(str) {
    if (!str) return '';
    const map = {
        'àáảãạâầấẩẫậăằắẳẵặ': 'a',
        'èéẻẽẹêềếểễệ': 'e',
        'ìíỉĩị': 'i',
        'òóỏõọôồốổỗộơờớởỡợ': 'o',
        'ùúủũụưừứửữự': 'u',
        'ỳýỷỹỵ': 'y',
        'đ': 'd'
    };
    let result = str.toLowerCase();
    for (const [chars, replacement] of Object.entries(map)) {
        for (const ch of chars) {
            result = result.replaceAll(ch, replacement);
        }
    }
    return result;
}

// ---------- Hàm kiểm tra match ----------
function matchesSearch(item, keyword) {
    if (!keyword) return true;
    const normalizedKeyword = removeVietnameseTones(keyword).toLowerCase();
    const searchFields = [
        item.id || '',
        item.title || '',
        item.slug || '',
        item.description || ''
    ];
    return searchFields.some(field => {
        const normalizedField = removeVietnameseTones(field).toLowerCase();
        return normalizedField.includes(normalizedKeyword);
    });
}

// ---------- Tải dữ liệu ----------
function loadData() {
    fetch('data.json')
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            if (data.truyen && data.truyen.length) {
                allTruyen = data.truyen;
                filteredTruyen = allTruyen;
                renderAll();
                // Gọi setupGenreDropdown sau khi có dữ liệu
                setupGenreDropdown();
            } else {
                throw new Error('Dữ liệu rỗng');
            }
        })
        .catch(error => {
            console.warn('Không thể fetch data.json:', error);
            document.querySelectorAll('.story-grid').forEach(grid => {
                grid.innerHTML = `<p style="color:red; padding:20px;">Không thể tải danh sách truyện. Vui lòng thử lại sau.</p>`;
            });
        });
}

// ---------- Render toàn bộ ----------
function renderAll() {
    const hotList = filterAndSort('hot', 'views', true);
    const newList = filterAndSort('new', 'last_update', false);
    const updatedList = filterAndSort('updated', 'last_update', false);

    renderSection('hot-list', hotList, currentDisplay.hot, 'hot');
    renderSection('new-list', newList, currentDisplay.new, 'new');
    renderSection('updated-list', updatedList, currentDisplay.updated, 'updated');
}

// ---------- Lọc và sắp xếp ----------
function filterAndSort(tag, sortBy, descending) {
    let list = filteredTruyen.filter(t => t.tags && t.tags.includes(tag));
    if (sortBy === 'views') {
        list.sort((a, b) => descending ? b.views - a.views : a.views - b.views);
    } else if (sortBy === 'last_update') {
        list.sort((a, b) => descending ? new Date(b.last_update) - new Date(a.last_update) : new Date(a.last_update) - new Date(b.last_update));
    }
    return list;
}

// ---------- Render một section ----------
function renderSection(containerId, items, displayCount, sectionKey) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const total = items.length;
    const show = Math.min(displayCount, total);
    const visibleItems = items.slice(0, show);

    let html = '';
    visibleItems.forEach(item => {
        const coverUrl = `novel/${item.slug}/${item.cover || 'cover.jpg'}`;
        const link = `novel/${item.slug}/info.html`;
        html += `
            <div class="story-card">
                <a href="${link}">
                    <img class="cover" src="${coverUrl}" alt="${item.title}" loading="lazy" width="220" height="280" onerror="this.src='novel/${item.slug}/cover.jpg'">
                    <div class="info">
                        <div class="title">${item.title}</div>
                        <div class="meta">
                            <span>📖 ${item.chapters} chương</span>
                            <span>👁️ ${item.views ? item.views.toLocaleString() : 0}</span>
                        </div>
                    </div>
                </a>
            </div>
        `;
    });

    if (show < total) {
        html += `<div style="grid-column: 1 / -1; text-align: center; margin-top: 15px;">
            <button class="load-more-btn" data-section="${sectionKey}">Xem thêm (${show}/${total})</button>
        </div>`;
    } else if (total > 0) {
        html += `<div style="grid-column: 1 / -1; text-align: center; color: #777; padding: 10px;">Đã hiển thị tất cả (${total})</div>`;
    } else {
        html = `<p style="padding:20px; color:#777;">Chưa có truyện trong danh mục này.</p>`;
    }

    container.innerHTML = html;

    container.querySelectorAll('.load-more-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            const section = this.dataset.section;
            if (section === 'hot') currentDisplay.hot += 8;
            else if (section === 'new') currentDisplay.new += 8;
            else if (section === 'updated') currentDisplay.updated += 8;
            renderAll();
            const target = document.getElementById(containerId);
            if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        });
    });
}

// ---------- Tìm kiếm và lọc ----------
function setupSearchAndFilter() {
    const searchInput = document.getElementById('search-input');
    const searchBtn = document.getElementById('search-btn');

    function applyFilter() {
        const keyword = searchInput.value.trim();
        searchKeyword = keyword;
        const selectedGenre = currentGenre;

        filteredTruyen = allTruyen.filter(item => {
            const matchSearch = matchesSearch(item, keyword);
            const matchGenre = (selectedGenre === 'all') || (item.genre === selectedGenre);
            return matchSearch && matchGenre;
        });

        currentDisplay = { hot: 8, new: 8, updated: 8 };
        renderAll();
    }

    searchInput.addEventListener('input', applyFilter);
    searchBtn.addEventListener('click', applyFilter);
}

// ---------- Dropdown thể loại ----------
function setupGenreDropdown() {
    const dropdown = document.getElementById('genre-dropdown');
    if (!dropdown) return;

    // Lấy danh sách genre duy nhất, lọc bỏ các giá trị rỗng/null/undefined
    const genres = [...new Set(allTruyen.map(item => item.genre).filter(Boolean))];
    // Sắp xếp theo thứ tự chữ cái
    genres.sort((a, b) => a.localeCompare(b, 'vi'));

    // Xây dựng dropdown
    let html = `<li><a href="#" data-genre="all">📚 Tất cả</a></li>`;
    genres.forEach(g => {
        html += `<li><a href="#" data-genre="${g}">${g}</a></li>`;
    });
    dropdown.innerHTML = html;

    // Sự kiện click
    dropdown.querySelectorAll('a[data-genre]').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const genre = this.dataset.genre;
            currentGenre = genre;
            const searchInput = document.getElementById('search-input');
            const keyword = searchInput.value.trim();
            searchKeyword = keyword;

            filteredTruyen = allTruyen.filter(item => {
                const matchSearch = matchesSearch(item, keyword);
                const matchGenre = (genre === 'all') || (item.genre === genre);
                return matchSearch && matchGenre;
            });

            currentDisplay = { hot: 8, new: 8, updated: 8 };
            renderAll();

            // Đóng dropdown trên mobile
            if (window.innerWidth <= 768) {
                const parent = this.closest('.dropdown');
                if (parent) parent.classList.remove('open');
            }
        });
    });

    console.log(`✅ Đã tải ${genres.length} thể loại:`, genres);
}

// ---------- Hamburger menu ----------
function setupHamburger() {
    const hamburger = document.getElementById('hamburger');
    const navMenu = document.getElementById('nav-menu');

    if (hamburger && navMenu) {
        hamburger.addEventListener('click', function() {
            this.classList.toggle('active');
            navMenu.classList.toggle('active');
        });

        navMenu.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', function() {
                if (window.innerWidth <= 768) {
                    hamburger.classList.remove('active');
                    navMenu.classList.remove('active');
                }
            });
        });
    }

    document.querySelectorAll('.dropdown > a').forEach(parentLink => {
        parentLink.addEventListener('click', function(e) {
            if (window.innerWidth <= 768) {
                e.preventDefault();
                const parent = this.parentElement;
                parent.classList.toggle('open');
            }
        });
    });
}
