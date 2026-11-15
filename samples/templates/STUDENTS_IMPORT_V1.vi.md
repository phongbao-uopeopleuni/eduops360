# Hướng dẫn CSV học sinh v1

## Phiên bản đã công bố

- Phiên bản: `v1`
- Tệp mẫu: `students_import_template.csv`
- Mã hóa: UTF-8 có BOM; dấu phân cách là dấu phẩy.
- Header chuẩn, đúng thứ tự:
  `student_code,full_name,date_of_birth,gender,academic_year,grade_level,class_code,enrollment_status`
- SHA-256 của tệp v1: `7cabce06705ed7935aad934ae5a2883975fe9900352465b3354da15f6f33d235`

Header của v1 là bất biến. Thêm, bỏ, đổi tên hoặc đổi thứ tự cột phải tạo phiên
bản template mới; không sửa âm thầm v1. Ba dòng dữ liệu trong tệp chỉ là dữ liệu
tổng hợp để minh họa, không dùng dữ liệu học sinh thật.

## Hướng dẫn trường

| Cột | Bắt buộc | Cách điền |
| --- | --- | --- |
| `student_code` | Có | Mã học sinh dạng văn bản, tối đa 40 ký tự; giữ nguyên số `0` đầu. |
| `full_name` | Có | Họ tên UTF-8 tiếng Việt, tối đa 120 ký tự. |
| `date_of_birth` | Có | Ngày theo ISO `YYYY-MM-DD`, không dùng ngày giờ. |
| `gender` | Có | Một trong `Nam`, `Nữ`, `Khác`, `Không khai báo` theo vocabulary demo. |
| `academic_year` | Có | Dạng `YYYY-YYYY`, năm sau phải liền kề năm trước. |
| `grade_level` | Có | Số nguyên từ `1` đến `12`. |
| `class_code` | Có | Mã lớp đã tồn tại trong đúng trường và năm học, ví dụ `8A1`. |
| `enrollment_status` | Có | Một trong `active`, `transferred`, `withdrawn`, `graduated`. |

## Kiểm tra cục bộ

```powershell
python scripts/validate_students_csv.py samples/templates/students_import_template.csv
```

Validator này chỉ kiểm tra file/schema/dòng. Nó không xác thực người dùng, không
kiểm tra lớp hoặc năm học trong PostgreSQL và không import dữ liệu.
