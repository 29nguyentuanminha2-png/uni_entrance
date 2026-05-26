"""
Module quản lý danh sách thí sinh (ManageStudent).

Lớp ManageStudent đóng vai trò Controller trong mô hình MVC:
- Quản lý CRUD (Create, Read, Update, Delete) thí sinh
- Tính toán điểm, sắp xếp, thống kê
- Đọc/ghi dữ liệu JSON tự động

Sử dụng os.path để xử lý đường dẫn file tương thích đa nền tảng (Windows/Mac/Linux),
đảm bảo chương trình chạy đúng trên mọi hệ điều hành.
"""

import json
import os
import sys

# Thêm thư mục cha vào sys.path để import được module validators
# Điều này cần thiết vì Python không tự động tìm module ở thư mục cha
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from validators import validate_thi_sinh_data

from .student import ThiSinh, ThiSinhKhoiA, ThiSinhKhoiB


class ManageStudent:
    """
    Lớp quản lý toàn bộ danh sách thí sinh.

    Chức năng chính:
    1. CRUD: Thêm, sửa, xóa, tìm kiếm thí sinh
    2. Hiển thị: Lọc theo khối, sắp xếp theo nhiều tiêu chí
    3. Thống kê: Điểm trung bình, không liệt, học bổng
    4. Lưu trữ: Tự động đọc/ghi file JSON

    Attributes:
        data_file (str): Đường dẫn tuyệt đối đến file JSON lưu dữ liệu
        students (list[ThiSinh]): Danh sách các đối tượng thí sinh trong bộ nhớ
    """

    def __init__(self, data_file: str = None):
        """
        Khởi tạo ManageStudent.

        Args:
            data_file: Đường dẫn file JSON. Nếu không truyền, mặc định dùng
                       backend/data/students.json (dùng os.path để tạo đường dẫn
                       tương thích mọi hệ điều hành)
        """
        if data_file is None:
            # os.path.dirname(__file__) → thư mục chứa file này (models/)
            # os.path.join(..., "..", "data", "students.json") → lên 1 cấp rồi vào data/
            # os.path.abspath() → chuyển thành đường dẫn tuyệt đối
            data_file = os.path.join(
                os.path.dirname(__file__), "..", "data", "students.json"
            )
        self.data_file = os.path.abspath(data_file)
        self.students: list[ThiSinh] = []  # Danh sách thí sinh trong bộ nhớ
        self._load()  # Đọc dữ liệu từ file JSON (nếu có)

    # =====================================================================
    # PHẦN 1: ĐỌC/GHI FILE JSON
    # =====================================================================

    def _load(self):
        """
        Đọc dữ liệu thí sinh từ file JSON vào bộ nhớ (self.students).

        Sử dụng os.path.exists() để kiểm tra file có tồn tại không trước khi đọc.
        Nếu file chưa tồn tại (lần đầu chạy), danh sách sẽ rỗng.
        """
        if os.path.exists(self.data_file):
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)  # Đọc JSON → list[dict]
            # Chuyển mỗi dict thành đối tượng ThiSinh (dùng Factory Method)
            self.students = [ThiSinh.from_dict(d) for d in data]

    def _save(self):
        """
        Ghi danh sách thí sinh từ bộ nhớ ra file JSON.

        Sử dụng os.makedirs() với exist_ok=True để tự động tạo thư mục data/
        nếu chưa tồn tại (hữu ích khi chạy lần đầu hoặc trong Docker).
        """
        # Tạo thư mục cha nếu chưa có (ví dụ: backend/data/)
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)

        with open(self.data_file, "w", encoding="utf-8") as f:
            # Chuyển mỗi ThiSinh thành dict rồi ghi ra JSON
            # ensure_ascii=False để giữ nguyên tiếng Việt (không encode thành \uXXXX)
            # indent=2 để JSON dễ đọc khi mở bằng text editor
            json.dump(
                [s.to_dict() for s in self.students],
                f,
                ensure_ascii=False,
                indent=2,
            )

    # =====================================================================
    # PHẦN 2: HÀM HỖ TRỢ NỘI BỘ (private methods, bắt đầu bằng _)
    # =====================================================================

    def _get_existing_cccds(self, exclude_sbd: str = None) -> set:
        """Lấy tập hợp tất cả CCCD hiện có (trừ thí sinh đang sửa)."""
        return {s.cccd for s in self.students if s.so_bao_danh != exclude_sbd}

    def _get_existing_sbds(self) -> set:
        """Lấy tập hợp tất cả số báo danh hiện có."""
        return {s.so_bao_danh for s in self.students}

    def _find_index_by_sbd(self, sbd: str) -> int:
        """
        Tìm vị trí (index) của thí sinh trong danh sách theo số báo danh.

        Returns:
            Index nếu tìm thấy, -1 nếu không tìm thấy
        """
        for i, s in enumerate(self.students):
            if s.so_bao_danh == sbd:
                return i
        return -1

    # =====================================================================
    # PHẦN 3: CRUD - THÊM, SỬA, XÓA THÍ SINH
    # =====================================================================

    def them_thi_sinh(self, data: dict) -> tuple[bool, list[str]]:
        """
        Thêm một thí sinh mới vào danh sách.

        Quy trình:
        1. Validate dữ liệu (kiểm tra CCCD, SBD trùng, điểm hợp lệ...)
        2. Chuyển chuỗi thành số (float) cho các trường điểm
        3. Tạo đối tượng ThiSinh từ dict
        4. Thêm vào danh sách và lưu file

        Args:
            data: dict chứa thông tin thí sinh từ form nhập liệu

        Returns:
            (True, []) nếu thành công
            (False, ["lỗi 1", "lỗi 2"]) nếu có lỗi validation
        """
        # Bước 1: Validate dữ liệu
        ok, errors = validate_thi_sinh_data(
            data,
            existing_cccds=self._get_existing_cccds(),
            existing_sbds=self._get_existing_sbds(),
        )
        if not ok:
            return False, errors

        # Bước 2: Chuyển các trường điểm từ chuỗi sang số thực
        for key in ["toan", "ly", "hoa", "sinh", "diem_tu_duy"]:
            if key in data:
                data[key] = float(data[key])

        # Bước 3: Tạo đối tượng ThiSinh từ dict (Factory Method)
        thi_sinh = ThiSinh.from_dict(data)

        # Bước 4: Thêm vào danh sách và lưu file
        self.students.append(thi_sinh)
        self._save()

        return True, []

    def sua_thi_sinh(self, so_bao_danh: str, data: dict) -> tuple[bool, list[str]]:
        """
        Sửa thông tin thí sinh theo số báo danh.

        Tìm thí sinh cũ → validate dữ liệu mới → thay thế.

        Args:
            so_bao_danh: SBD của thí sinh cần sửa
            data: dict chứa thông tin mới

        Returns:
            (True, []) nếu thành công
            (False, ["lỗi"]) nếu không tìm thấy hoặc dữ liệu không hợp lệ
        """
        # Tìm thí sinh trong danh sách
        idx = self._find_index_by_sbd(so_bao_danh)
        if idx == -1:
            return False, ["Không tìm thấy thí sinh với SBD: " + so_bao_danh]

        # Validate dữ liệu mới (loại trừ SBD/CCCD hiện tại khỏi kiểm tra trùng)
        ok, errors = validate_thi_sinh_data(
            data,
            existing_cccds=self._get_existing_cccds(exclude_sbd=so_bao_danh),
            existing_sbds=self._get_existing_sbds(),
            exclude_sbd=so_bao_danh,
        )
        if not ok:
            return False, errors

        # Chuyển điểm sang số thực
        for key in ["toan", "ly", "hoa", "sinh", "diem_tu_duy"]:
            if key in data:
                data[key] = float(data[key])

        # Thay thế thí sinh cũ bằng thí sinh mới
        self.students[idx] = ThiSinh.from_dict(data)
        self._save()

        return True, []

    def xoa_thi_sinh(self, so_bao_danh: str) -> tuple[bool, str]:
        """
        Xóa thí sinh theo số báo danh.

        Returns:
            (True, "Đã xóa") nếu thành công
            (False, "Không tìm thấy") nếu SBD không tồn tại
        """
        idx = self._find_index_by_sbd(so_bao_danh)
        if idx == -1:
            return False, "Không tìm thấy thí sinh"

        ten = self.students[idx].ho_ten  # Lưu tên để hiển thị thông báo
        self.students.pop(idx)  # Xóa khỏi danh sách
        self._save()  # Lưu lại file

        return True, f"Đã xóa thí sinh {ten}"

    # =====================================================================
    # PHẦN 4: TÌM KIẾM VÀ HIỂN THỊ
    # =====================================================================

    def tim_kiem(self, keyword: str) -> list[ThiSinh]:
        """
        Tìm kiếm thí sinh: ưu tiên tìm theo SBD, nếu không có thì tìm theo CCCD.

        Theo yêu cầu đề bài: "Nếu không có số báo danh thì tìm theo CCCD".

        Args:
            keyword: chuỗi tìm kiếm (SBD hoặc CCCD)

        Returns:
            Danh sách thí sinh tìm được
        """
        keyword = keyword.strip()

        # Thử tìm theo SBD trước
        results = [s for s in self.students if s.so_bao_danh == keyword]

        # Nếu không tìm thấy theo SBD → thử tìm theo CCCD
        if not results:
            results = [s for s in self.students if s.cccd == keyword]

        return results

    def get_by_sbd(self, sbd: str) -> ThiSinh | None:
        """Lấy 1 thí sinh theo SBD. Trả về None nếu không tìm thấy."""
        idx = self._find_index_by_sbd(sbd)
        return self.students[idx] if idx != -1 else None

    def hien_thi_theo_khoi(self, khoi: str) -> list[ThiSinh]:
        """Lọc danh sách thí sinh theo khối ('A' hoặc 'B')."""
        return [s for s in self.students if s.get_khoi() == khoi]

    def get_all(self) -> list[ThiSinh]:
        """Lấy toàn bộ danh sách thí sinh."""
        return self.students

    # =====================================================================
    # PHẦN 5: TÍNH ĐIỂM VÀ TRUNG BÌNH
    # =====================================================================

    def tinh_diem_xet_tuyen(self, so_bao_danh: str) -> float | None:
        """Tính điểm xét tuyển của 1 thí sinh theo SBD."""
        ts = self.get_by_sbd(so_bao_danh)
        return ts.tinh_diem_xet_tuyen() if ts else None

    def danh_sach_diem_xet_tuyen(self, khoi: str = None) -> list[dict]:
        """
        Lấy danh sách điểm xét tuyển (dùng cho API hiển thị).

        Args:
            khoi: 'A', 'B' hoặc None (tất cả)
        """
        students = self.hien_thi_theo_khoi(khoi) if khoi else self.students
        return [
            {
                "so_bao_danh": s.so_bao_danh,
                "ho_ten": s.ho_ten,
                "khoi": s.get_khoi(),
                "diem_xet_tuyen": round(s.tinh_diem_xet_tuyen(), 2),
            }
            for s in students
        ]

    def trung_binh_cong_diem(self) -> dict:
        """
        Tính trung bình cộng điểm xét tuyển của tất cả thí sinh.

        Returns:
            dict với tong_thi_sinh, tong_diem, trung_binh
        """
        if not self.students:
            return {"tong_thi_sinh": 0, "tong_diem": 0, "trung_binh": 0}

        tong = sum(s.tinh_diem_xet_tuyen() for s in self.students)
        return {
            "tong_thi_sinh": len(self.students),
            "tong_diem": round(tong, 2),
            "trung_binh": round(tong / len(self.students), 2),
        }

    # =====================================================================
    # PHẦN 6: SẮP XẾP
    # =====================================================================

    def sap_xep_3_mon(self, khoi: str, giam_dan: bool = True) -> list[ThiSinh]:
        """
        Sắp xếp thí sinh theo tổng điểm 3 môn.

        Args:
            khoi: 'A' hoặc 'B'
            giam_dan: True = cao xuống thấp, False = thấp lên cao
        """
        ds = self.hien_thi_theo_khoi(khoi)
        return sorted(ds, key=lambda s: s.tong_3_mon(), reverse=giam_dan)

    def sap_xep_tu_duy(self, khoi: str, giam_dan: bool = True) -> list[ThiSinh]:
        """Sắp xếp thí sinh theo điểm tư duy."""
        ds = self.hien_thi_theo_khoi(khoi)
        return sorted(ds, key=lambda s: s.get_diem_tu_duy(), reverse=giam_dan)

    def sap_xep_diem_xet_tuyen(
        self, khoi: str = None, giam_dan: bool = True
    ) -> list[ThiSinh]:
        """Sắp xếp theo điểm xét tuyển (có thể lọc theo khối hoặc xem tất cả)."""
        ds = self.hien_thi_theo_khoi(khoi) if khoi else self.students
        return sorted(ds, key=lambda s: s.tinh_diem_xet_tuyen(), reverse=giam_dan)

    # =====================================================================
    # PHẦN 7: THỐNG KÊ - LIỆT VÀ HỌC BỔNG
    # =====================================================================

    def ds_khong_liet(self, khoi: str = None) -> list[ThiSinh]:
        """Danh sách thí sinh KHÔNG bị liệt (điểm >= 2 và tư duy >= 30)."""
        ds = self.hien_thi_theo_khoi(khoi) if khoi else self.students
        return [s for s in ds if not s.is_liet()]

    def ds_co_liet(self, khoi: str = None) -> list[ThiSinh]:
        """Danh sách thí sinh CÓ bị liệt."""
        ds = self.hien_thi_theo_khoi(khoi) if khoi else self.students
        return [s for s in ds if s.is_liet()]

    def ds_hoc_bong(self, khoi: str) -> list[ThiSinh]:
        """
        Danh sách thí sinh đạt học bổng theo từng khối.

        Điều kiện đạt học bổng (theo đề bài):
        1. Điểm xét tuyển >= 32
        2. Điểm tư duy >= 70
        3. Lấy Top 5 cao nhất theo điểm xét tuyển

        Args:
            khoi: 'A' hoặc 'B'

        Returns:
            Tối đa 5 thí sinh đạt điều kiện, sắp xếp giảm dần theo điểm XT
        """
        ds = self.hien_thi_theo_khoi(khoi)

        # Lọc thí sinh đạt cả 2 điều kiện
        eligible = [
            s
            for s in ds
            if s.tinh_diem_xet_tuyen() >= 32 and s.get_diem_tu_duy() >= 70
        ]

        # Sắp xếp giảm dần theo điểm xét tuyển
        eligible.sort(key=lambda s: s.tinh_diem_xet_tuyen(), reverse=True)

        # Chỉ lấy Top 5
        return eligible[:5]

    def ds_dat_hoc_bong_all(self) -> dict:
        """Danh sách học bổng cả 2 khối."""
        return {
            "A": self.ds_hoc_bong("A"),
            "B": self.ds_hoc_bong("B"),
        }

    # =====================================================================
    # PHẦN 8: THỐNG KÊ TỔNG QUAN (cho Dashboard)
    # =====================================================================

    def thong_ke(self) -> dict:
        """
        Tổng hợp thống kê cho Dashboard.

        Returns:
            dict chứa: tổng, khối A/B, không liệt, có liệt, học bổng, trung bình
        """
        tong = len(self.students)
        return {
            "tong": tong,
            "khoi_a": len(self.hien_thi_theo_khoi("A")),
            "khoi_b": len(self.hien_thi_theo_khoi("B")),
            "khong_liet": len(self.ds_khong_liet()),
            "co_liet": len(self.ds_co_liet()),
            "hoc_bong_a": len(self.ds_hoc_bong("A")),
            "hoc_bong_b": len(self.ds_hoc_bong("B")),
            "trung_binh": self.trung_binh_cong_diem(),
        }

    def thong_ke_charts(self) -> dict:
        """
        Dữ liệu chi tiết cho biểu đồ trên Dashboard.

        Trả về dữ liệu cho:
        - Donut chart: phân bổ khối A/B
        - Bar chart: phân bổ điểm xét tuyển theo khoảng
        - Column chart: điểm trung bình từng môn theo khối
        - Thống kê liệt/không liệt
        """
        khoi_a = self.hien_thi_theo_khoi("A")
        khoi_b = self.hien_thi_theo_khoi("B")

        # --- Dữ liệu Donut Chart: Phân bổ theo khối ---
        donut_khoi = [
            {"name": "Khối A", "value": len(khoi_a)},
            {"name": "Khối B", "value": len(khoi_b)},
        ]

        # --- Dữ liệu Donut Chart: Liệt / Không liệt ---
        donut_liet = [
            {"name": "Không liệt", "value": len(self.ds_khong_liet())},
            {"name": "Có liệt", "value": len(self.ds_co_liet())},
        ]

        # --- Dữ liệu Bar Chart: Phân bổ điểm xét tuyển theo khoảng ---
        # Chia điểm XT thành các khoảng để vẽ histogram
        ranges = [
            {"label": "< 30", "min": 0, "max": 30},
            {"label": "30-50", "min": 30, "max": 50},
            {"label": "50-70", "min": 50, "max": 70},
            {"label": "70-90", "min": 70, "max": 90},
            {"label": "90-110", "min": 90, "max": 110},
            {"label": "110-130", "min": 110, "max": 130},
        ]
        bar_diem = []
        for r in ranges:
            count_a = sum(
                1
                for s in khoi_a
                if r["min"] <= s.tinh_diem_xet_tuyen() < r["max"]
            )
            count_b = sum(
                1
                for s in khoi_b
                if r["min"] <= s.tinh_diem_xet_tuyen() < r["max"]
            )
            bar_diem.append(
                {"range": r["label"], "khoi_a": count_a, "khoi_b": count_b}
            )

        # --- Dữ liệu Column Chart: Điểm trung bình từng môn ---
        def avg(values):
            """Hàm tính trung bình, trả về 0 nếu danh sách rỗng."""
            return round(sum(values) / len(values), 2) if values else 0

        column_mon = [
            {
                "mon": "Toán (A)",
                "trung_binh": avg([s.toan for s in khoi_a]),
                "khoi": "A",
            },
            {
                "mon": "Lý (A)",
                "trung_binh": avg([s.ly for s in khoi_a]),
                "khoi": "A",
            },
            {
                "mon": "Hóa (A)",
                "trung_binh": avg([s.hoa for s in khoi_a]),
                "khoi": "A",
            },
            {
                "mon": "Toán (B)",
                "trung_binh": avg([s.toan for s in khoi_b]),
                "khoi": "B",
            },
            {
                "mon": "Hóa (B)",
                "trung_binh": avg([s.hoa for s in khoi_b]),
                "khoi": "B",
            },
            {
                "mon": "Sinh (B)",
                "trung_binh": avg([s.sinh for s in khoi_b]),
                "khoi": "B",
            },
        ]

        # --- Top 10 điểm xét tuyển cao nhất ---
        top10 = sorted(
            self.students, key=lambda s: s.tinh_diem_xet_tuyen(), reverse=True
        )[:10]
        top10_data = [
            {
                "ho_ten": s.ho_ten,
                "khoi": s.get_khoi(),
                "diem_xet_tuyen": round(s.tinh_diem_xet_tuyen(), 2),
            }
            for s in top10
        ]

        # --- Phân bổ điểm tư duy theo khoảng ---
        td_ranges = [
            {"label": "< 30", "min": 0, "max": 30},
            {"label": "30-50", "min": 30, "max": 50},
            {"label": "50-70", "min": 50, "max": 70},
            {"label": "70-90", "min": 70, "max": 90},
            {"label": "90-100", "min": 90, "max": 101},
        ]
        bar_tu_duy = []
        for r in td_ranges:
            count = sum(
                1
                for s in self.students
                if r["min"] <= s.get_diem_tu_duy() < r["max"]
            )
            bar_tu_duy.append({"range": r["label"], "count": count})

        return {
            "donut_khoi": donut_khoi,
            "donut_liet": donut_liet,
            "bar_diem_xt": bar_diem,
            "column_mon": column_mon,
            "top10": top10_data,
            "bar_tu_duy": bar_tu_duy,
        }

    # =====================================================================
    # PHẦN 9: LOAD DỮ LIỆU MẪU
    # =====================================================================

    def load_sample_data(self, sample_file: str = None):
        """
        Load dữ liệu mẫu từ file JSON vào hệ thống.

        Sử dụng os.path để tìm file sample_data.json cùng thư mục data/,
        đảm bảo hoạt động đúng dù chạy từ thư mục nào.

        Args:
            sample_file: Đường dẫn file mẫu. Mặc định: backend/data/sample_data.json
        """
        if sample_file is None:
            sample_file = os.path.join(
                os.path.dirname(__file__), "..", "data", "sample_data.json"
            )

        if os.path.exists(sample_file):
            with open(sample_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.students = [ThiSinh.from_dict(d) for d in data]
            self._save()  # Lưu lại vào students.json
