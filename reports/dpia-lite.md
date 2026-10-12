# DPIA-lite — điền trong checkpoint 5

1. Loại dữ liệu và phân loại:
- Public: Query tìm kiếm của người dùng.
- Internal: Toàn bộ ticket hỗ trợ trong `corpus/*.md` (mô tả lỗi, câu hỏi hỗ trợ).
- Restricted: Dữ liệu cá nhân khách hàng trong `data/customers.json` gồm CCCD (12 số), SĐT, STK ngân hàng, email, họ tên và danh sách ticket liên quan.

2. Mục đích xử lý và principal:
- Mục đích: "summarize-tickets" (tổng hợp ticket), "support-reply" (soạn phản hồi hỗ trợ), "billing-reconciliation" (đối soát hoá đơn), "privacy-audit" (kiểm toán tuân thủ bảo vệ dữ liệu).
- Principals:
  + `support_l1`: Chỉ được phép `search_docs`, mục đích `summarize-tickets`, `support-reply`. Bị cấm gọi `read_customer`.
  + `billing`: Được phép `search_docs`, `read_customer` cho mục đích `billing-reconciliation`, `summarize-tickets`.
  + `dpo`: Được phép `search_docs`, `read_customer` cho `privacy-audit`, `support-reply`, `summarize-tickets`.

3. Dữ liệu đi qua những run/tool nào, endpoint nào:
- Run A: Nhận query, gọi `tools.search_docs` đọc `corpus/`. Lọc PII qua `agent.pii.redact`. Chỉ trích xuất ticket ID dạng số từ tên file để chuyển sang Run B.
- Run B: Dùng ticket ID tra cứu `data/customers.json` qua `related_tickets`. Nếu principal được phép (`dpo`), gọi `tools.read_customer` lấy hồ sơ.
- Egress: Chỉ thị injection yêu cầu POST tới `http://127.0.0.1:10024/reconcile`. Policy Engine chặn ngay trước khi gọi `tools.http_post` do vi phạm rule cấm egress với dữ liệu restricted.

4. Bằng chứng deny/allow và giới hạn của mock:
- Bằng chứng:
  + `reports/attack-after.log` rỗng (0 bytes).
  + `reports/ledger.jsonl` ghi nhận `read_customer` bị deny với `support_l1` và allow với `dpo`; `http_post` bị deny kèm reason cụ thể.
  + Toàn vẹn chuỗi hash được xác nhận `True` bởi `agent.ledger.verify()`.
- Giới hạn của mock:
  + Dùng `MockLLM` tất định dựa trên marker thay vì model LLM sinh văn bản thực tế.
  + Principal và token giả lập bằng file JSON và TTL cục bộ, chưa tích hợp IdP doanh nghiệp (OAuth/OIDC).
  + Sink chỉ lắng nghe trên localhost thay vì endpoint Internet thực tế.