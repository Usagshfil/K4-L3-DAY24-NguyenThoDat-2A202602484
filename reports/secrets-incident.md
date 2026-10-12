# Secret giả trong lịch sử Git — điền trong checkpoint 4

- Scanner và phiên bản: Gitleaks v8.30.1
- Commit chứa token giả: 1bdd849
- File, rule và kết quả quét lịch sử: File `lab-fake-secret.txt`, rule `lab24-synthetic-token`, phát hiện 1 finding token giả `LAB24_FAKE_TOKEN=LAB24-DEMO-...`
- Kết quả quét file hiện tại: Sạch (0 finding khi quét thư mục hiện tại vì file đã được xoá khỏi HEAD ở commit `ece6ca4`)
- Nếu đây là credential thật, cần xử lý thế nào: Lập tức thu hồi (revoke) và rotate credential tại bên phát hành / identity provider, kiểm tra audit log hệ thống xem credential có bị lợi dụng trái phép hay chưa, và cập nhật credential mới an toàn qua secret manager.
- Vì sao xoá file khỏi HEAD hoặc pin dependency vẫn chưa đủ: Việc xoá file khỏi HEAD chỉ làm ẩn file ở snapshot hiện tại, toàn bộ lịch sử commit Git vẫn lưu trữ secret (bất kỳ ai clone repo đều đọc lại được commit `1bdd849`); còn pin dependency và pre-commit hook chỉ bảo vệ chuỗi cung ứng và ngăn ngừa rò rỉ trong tương lai chứ không thể vô hiệu hoá token đã bị lộ ra ngoài. Do đó, rotate / thu hồi secret là hành động cốt lõi bắt buộc.