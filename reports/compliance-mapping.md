# Compliance mapping — điền trong checkpoint 5

| Nguồn / yêu cầu | Control đã làm | Evidence file:dòng | Giới hạn |
|---|---|---|---|
| Luật 91/2025/QH15 | PII gate phát hiện và redact CCCD, SĐT, STK, Email trước khi qua boundary; phân loại dữ liệu restricted; kiểm soát thẩm quyền theo vai trò. | `agent/pii.py:14-55`, `agent/policy.py:34-70` | Dùng regex mô phỏng, chưa dùng NER tiếng Việt đầy đủ; principal giả lập qua JSON chưa nối IdP production. |
| NĐ 356/2025/NĐ-CP | Audit Ledger dạng tamper-evident hash chain ghi nhận toàn bộ hoạt động gọi tool, quyết định allow/deny, reason, timestamp và ID người dùng phục vụ thanh tra. | `agent/ledger.py:18-72`, `agent/runner.py:38-54`, `agent/runner.py:89-106` | Hash chain lưu file cục bộ, chưa đồng bộ WORM storage hoặc bên thứ 3 có mốc thời gian độc lập. |
| Luật AI 134/2025/QH15 | Trách nhiệm giải trình và an toàn AI: OBO ràng buộc quyền hạn người dùng; Trifecta Split chia tách 2 Run ngăn prompt injection điều khiển agent hành động ngoài ý muốn. | `agent/policy.py:34-78`, `agent/runner.py:27-142` | Đánh giá trên môi trường mô phỏng MockLLM; chưa đối phó toàn diện các vector tấn công jailbreak đa phương thức. |
| OWASP ASI01, ASI03, ASI04 | ASI01 (Prompt Injection): Trifecta split ngăn free text tiếp cận store/egress. ASI03 (Excessive Agency): PEP giới hạn tool theo principal/purpose, cấm egress với data restricted. ASI04 (Supply Chain): Gitleaks quét commit, pre-commit hook pin rev, hash lock. | `agent/runner.py:59-139`, `agent/policy.py:34-78`, `.pre-commit-config.yaml:1-6` | Egress allowlist cố định localhost; cần firewall mạng thực tế khi triển khai production. |

Chỉ ghi điều khoản cụ thể khi đã đối chiếu văn bản gốc. Mô phỏng kỹ thuật không tự chứng minh tuân thủ pháp luật.
