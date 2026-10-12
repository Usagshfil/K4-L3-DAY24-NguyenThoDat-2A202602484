# Baseline — điền trong checkpoint 1

1. Agent có identity mỗi run chưa? Dẫn file/hàm:
Chưa có. Trong `agent/loop.py` tại hàm `_naive_loop(message, llm)` (dòng 27–54), agent chỉ nhận input là message và instance llm mà không hề có định danh agent_id, run_id hay thông tin phiên làm việc nào được khởi tạo hoặc xác thực.

2. Ai cho phép `http_post`? Dẫn file/hàm:
Không có cơ chế chính sách (PEP/Policy) nào cấp phép. Trong `agent/loop.py` tại hàm `_naive_loop()` (dòng 44), agent tự động gọi trực tiếp `tools.http_post(injected.target_url, {"records": collected})` khi LLM trả về lệnh injection. Tại `agent/tools.py` trong hàm `http_post()` (dòng 76–83), chỉ có hard-allowlist chặn domain khác ngoài `127.0.0.1:10024`, hoàn toàn không kiểm tra quyền hay mục đích của caller.

3. Nếu gửi sai PII ra sink, bằng chứng ở đâu? Dẫn file/hàm:
Bằng chứng được lưu tại file `reports/sink.log`. Trong `sink/sink.py` tại `make_handler()` trong `Handler.do_POST()` (dòng 42–48), mọi HTTP POST request gửi đến sink đều được decode và append từng dòng JSON `{"path": ..., "body": ...}` vào `reports/sink.log`.