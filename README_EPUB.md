# Hướng dẫn đóng gói EPUB

## Sản phẩm hiện có

| File | Nội dung |
|---|---|
| `dist/600_tu_part1_001-100.epub` | Phần 1 — từ 001 đến 100 |
| `dist/600_tu_part2_101-200.epub` | Phần 2 — từ 101 đến 200 |
| `dist/600_tu_part3_201-300.epub` | Phần 3 — từ 201 đến 300 |
| `dist/600_tu_part4_301-400.epub` | Phần 4 — từ 301 đến 400 |
| `dist/600_tu_part5_401-500.epub` | Phần 5 — từ 401 đến 500 |
| `dist/600_tu_part6_501-600.epub` | Phần 6 — từ 501 đến 600 |
| `All_words/1_100_chi_tiet.md` | Bản Markdown Phần 1 |
| `All_words/101_200_chi_tiet.md` | Bản Markdown Phần 2 |
| `All_words/201_300_chi_tiet.md` | Bản Markdown Phần 3 |
| `All_words/301_400_chi_tiet.md` | Bản Markdown Phần 4 |
| `All_words/401_500_chi_tiet.md` | Bản Markdown Phần 5 |
| `All_words/501_600_chi_tiet.md` | Bản Markdown Phần 6 |
| `styles/eink.css` | Stylesheet tối ưu màn hình E-ink |
| `scripts/build_epub.py` | Script dựng EPUB 3 |

## Đặc điểm của bản EPUB

* **EPUB 3**, có `mimetype` đúng chuẩn (entry đầu tiên, không nén) — mở được trên Kindle (qua Send to Kindle/Calibre), Kobo, Boox, PocketBook, Apple Books.
* **Mục lục điều hướng 2 lớp**: `nav.xhtml` (chuẩn EPUB 3) + `toc.ncx` (tương thích EPUB 2).
  Mỗi từ là **một chương riêng**, nhãn mục lục dạng `101. 车站 — chēzhàn`.
* **Ảnh nhúng offline**: toàn bộ ảnh thứ tự nét được tải về và đóng gói trong ebook, không cần Internet khi đọc.
* **CSS tối ưu E-ink**: chữ đen nền trắng, tương phản cao, không phụ thuộc màu, ảnh giới hạn 60% bề rộng, blockquote đóng khung, chống ngắt khối giữa trang.
* **Mục lục đầu sách**: trang bìa phụ + danh sách 100 từ liên kết trực tiếp.
* **Bóc tách theo thành phần**: mỗi chữ được phân tích theo bộ thủ, chữ con, phần biểu âm/biểu nghĩa và "Ghép lại" — không liệt kê từng nét.
* **Kiến thức văn hóa & lịch sử**: mỗi từ có thêm 1–3 gạch đầu dòng về phong tục, thành ngữ, địa danh, lịch sử hoặc khác biệt Bắc – Nam.

## Cách dựng lại / dựng phần tiếp theo

```powershell
# Phần 1
python scripts/build_epub.py "All_words/1_100_chi_tiet.md" "dist/600_tu_part1_001-100.epub" `
  --title "600 Từ Vựng Tiếng Trung Đầu Tiên — Phần 1 (001–100)" --author "Tài liệu học Hán tự"

# Phần 2
python scripts/build_epub.py "All_words/101_200_chi_tiet.md" "dist/600_tu_part2_101-200.epub" `
  --title "600 Từ Vựng Tiếng Trung Đầu Tiên — Phần 2 (101–200)" --author "Tài liệu học Hán tự"

# Phần 3
python scripts/build_epub.py "All_words/201_300_chi_tiet.md" "dist/600_tu_part3_201-300.epub" `
  --title "600 Từ Vựng Tiếng Trung Đầu Tiên — Phần 3 (201–300)" --author "Tài liệu học Hán tự"

# Phần 4
python scripts/build_epub.py "All_words/301_400_chi_tiet.md" "dist/600_tu_part4_301-400.epub" `
  --title "600 Từ Vựng Tiếng Trung Đầu Tiên — Phần 4 (301–400)" --author "Tài liệu học Hán tự"

# Phần 5
python scripts/build_epub.py "All_words/401_500_chi_tiet.md" "dist/600_tu_part5_401-500.epub" `
  --title "600 Từ Vựng Tiếng Trung Đầu Tiên — Phần 5 (401–500)" --author "Tài liệu học Hán tự"

# Phần 6
python scripts/build_epub.py "All_words/501_600_chi_tiet.md" "dist/600_tu_part6_501-600.epub" `
  --title "600 Từ Vựng Tiếng Trung Đầu Tiên — Phần 6 (501–600)" --author "Tài liệu học Hán tự"
```

Kiểm tra nhanh một bản EPUB sau khi build:

```powershell
python scripts/validate_epub.py "dist/600_tu_part4_301-400.epub"
```

Yêu cầu: Python 3 + `pip install markdown requests`.

## Tuỳ chỉnh hiển thị trên máy đọc sách

Sửa trực tiếp `styles/eink.css` rồi chạy lại lệnh build (script tự nạp file này nếu tồn tại):

* Cỡ chữ tổng thể: `body { font-size: 1em; }`
* Giãn dòng: `body { line-height: 1.68; }`
* Kích thước ảnh nét vẽ: `img { max-width: 60%; }` (nên giữ 50–70% cho màn hình 6–7 inch)
* Khung câu chuyện ghi nhớ: `blockquote { border-left: 6px solid #000; }`
* Muốn tiết kiệm pin / giảm bóng mờ: bỏ `background: #f2f2f2;` trong `blockquote`.

## Ghi chú kỹ thuật

* Số ảnh trong mỗi phần = **tổng số chữ Hán** của 100 từ (từ ghép 2–3 chữ sẽ có 2–3 ảnh).
  Nếu một chữ xuất hiện ở nhiều từ, ảnh chỉ được nhúng **một lần** — vì vậy số ảnh thực tế trong file EPUB luôn **nhỏ hơn hoặc bằng** số thẻ `<img>` trong bản Markdown (vd. Phần 4: 169 thẻ `<img>` → 150 ảnh duy nhất).
* Dựng nhanh cả 6 phần (giữ đúng dấu tiếng Việt trong tiêu đề): `python scripts/build_parts.py` hoặc `python scripts/build_parts.py part6`.
* Ảnh dùng chung giữa các phần được cache tại `.cache/bishun/` nên build lần sau rất nhanh.
* Nếu một ảnh không tải được, script giữ nguyên URL gốc và vẫn build thành công.
