from flask import Flask, request, jsonify
from flask_cors import CORS
from models.manage_student import ManageStudent

app = Flask(__name__)
CORS(app)

manager = ManageStudent()

if not manager.get_all():
    manager.load_sample_data()


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/api/students", methods=["GET"])
def get_students():
    khoi = request.args.get("khoi")
    if khoi:
        students = manager.hien_thi_theo_khoi(khoi.upper())
    else:
        students = manager.get_all()
    return jsonify([s.to_dict() for s in students])


@app.route("/api/students", methods=["POST"])
def add_student():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "errors": ["Dữ liệu không hợp lệ"]}), 400
    ok, errors = manager.them_thi_sinh(data)
    if not ok:
        return jsonify({"success": False, "errors": errors}), 400
    return jsonify({"success": True, "message": "Thêm thí sinh thành công"}), 201


@app.route("/api/students/<sbd>", methods=["GET"])
def get_student(sbd):
    ts = manager.get_by_sbd(sbd)
    if not ts:
        return jsonify({"error": "Không tìm thấy thí sinh"}), 404
    return jsonify(ts.to_dict())


@app.route("/api/students/<sbd>", methods=["PUT"])
def update_student(sbd):
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "errors": ["Dữ liệu không hợp lệ"]}), 400
    ok, errors = manager.sua_thi_sinh(sbd, data)
    if not ok:
        return jsonify({"success": False, "errors": errors}), 400
    return jsonify({"success": True, "message": "Cập nhật thành công"})


@app.route("/api/students/<sbd>", methods=["DELETE"])
def delete_student(sbd):
    ok, msg = manager.xoa_thi_sinh(sbd)
    if not ok:
        return jsonify({"success": False, "error": msg}), 404
    return jsonify({"success": True, "message": msg})


@app.route("/api/students/search", methods=["GET"])
def search_students():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify([])
    results = manager.tim_kiem(q)
    return jsonify([s.to_dict() for s in results])


@app.route("/api/reports/diem-xet-tuyen", methods=["GET"])
def report_diem_xet_tuyen():
    khoi = request.args.get("khoi")
    return jsonify(manager.danh_sach_diem_xet_tuyen(khoi.upper() if khoi else None))


@app.route("/api/reports/trung-binh", methods=["GET"])
def report_trung_binh():
    return jsonify(manager.trung_binh_cong_diem())


@app.route("/api/reports/sap-xep-3-mon", methods=["GET"])
def report_sap_xep_3_mon():
    khoi = request.args.get("khoi", "A").upper()
    order = request.args.get("order", "desc")
    giam_dan = order != "asc"
    results = manager.sap_xep_3_mon(khoi, giam_dan)
    return jsonify([
        {**s.to_dict(), "tong_3_mon": round(s.tong_3_mon(), 2), "diem_xet_tuyen": round(s.tinh_diem_xet_tuyen(), 2)}
        for s in results
    ])


@app.route("/api/reports/sap-xep-tu-duy", methods=["GET"])
def report_sap_xep_tu_duy():
    khoi = request.args.get("khoi", "A").upper()
    order = request.args.get("order", "desc")
    giam_dan = order != "asc"
    results = manager.sap_xep_tu_duy(khoi, giam_dan)
    return jsonify([
        {**s.to_dict(), "diem_xet_tuyen": round(s.tinh_diem_xet_tuyen(), 2)}
        for s in results
    ])


@app.route("/api/reports/sap-xep-diem-xet-tuyen", methods=["GET"])
def report_sap_xep_diem_xet_tuyen():
    khoi = request.args.get("khoi")
    order = request.args.get("order", "desc")
    giam_dan = order != "asc"
    results = manager.sap_xep_diem_xet_tuyen(khoi.upper() if khoi else None, giam_dan)
    return jsonify([
        {**s.to_dict(), "diem_xet_tuyen": round(s.tinh_diem_xet_tuyen(), 2)}
        for s in results
    ])


@app.route("/api/reports/khong-liet", methods=["GET"])
def report_khong_liet():
    khoi = request.args.get("khoi")
    results = manager.ds_khong_liet(khoi.upper() if khoi else None)
    return jsonify([
        {**s.to_dict(), "diem_xet_tuyen": round(s.tinh_diem_xet_tuyen(), 2)}
        for s in results
    ])


@app.route("/api/reports/hoc-bong", methods=["GET"])
def report_hoc_bong():
    khoi = request.args.get("khoi")
    if khoi:
        results = manager.ds_hoc_bong(khoi.upper())
        return jsonify([
            {**s.to_dict(), "diem_xet_tuyen": round(s.tinh_diem_xet_tuyen(), 2)}
            for s in results
        ])
    all_hb = manager.ds_dat_hoc_bong_all()
    return jsonify({
        k: [
            {**s.to_dict(), "diem_xet_tuyen": round(s.tinh_diem_xet_tuyen(), 2)}
            for s in v
        ]
        for k, v in all_hb.items()
    })


@app.route("/api/reports/thong-ke", methods=["GET"])
def report_thong_ke():
    return jsonify(manager.thong_ke())


@app.route("/api/reports/charts", methods=["GET"])
def report_charts():
    """API trả về dữ liệu cho các biểu đồ trên Dashboard."""
    return jsonify(manager.thong_ke_charts())


@app.route("/api/students/all-with-scores", methods=["GET"])
def get_all_with_scores():
    """API trả về tất cả thí sinh kèm điểm xét tuyển (cho bảng tổng hợp)."""
    students = manager.get_all()
    return jsonify([
        {
            **s.to_dict(),
            "diem_xet_tuyen": round(s.tinh_diem_xet_tuyen(), 2),
            "tong_3_mon": round(s.tong_3_mon(), 2),
            "is_liet": s.is_liet(),
        }
        for s in students
    ])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
