# PTIT Store - Website bán văn phòng phẩm

Dự án bài tập lớn sử dụng Python, Django, SQLite và Bootstrap. Mô hình cửa hàng đơn lẻ gồm khách hàng và quản trị viên; 


## Chạy trên Windows
Mở CMD/Terminal tại thư mục có `manage.py`, sau đó chạy:

```bash
py -m pip install -r requirements.txt
py manage.py migrate
py manage.py runserver
```
Mở http://127.0.0.1:8000/.


## muốn mở tài khoản Admin thì vào web
http://127.0.0.1:8000/admin/ 
TK:    adminptit
MK:    Truong123@

## Chức năng
- Xem, tìm kiếm, lọc và sắp xếp sản phẩm.
- Giỏ hàng lưu theo phiên; giá được lấy lại từ cơ sở dữ liệu khi tính tiền.
- Đặt hàng, xem trạng thái đơn hàng của tài khoản đã đăng nhập.
- Đặt hàng với tư cách khách vẫn được hỗ trợ; đơn không gắn tài khoản sẽ được quản trị viên quản lý trong trang admin.
- Admin quản lý sản phẩm, danh mục và trạng thái đơn hàng.

## Tạo tài khoản quản trị
```bash
py manage.py createsuperuser
```