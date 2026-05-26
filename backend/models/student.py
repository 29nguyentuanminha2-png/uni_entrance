"""
Module định nghĩa các lớp Thí sinh theo mô hình OOP.

Sử dụng tính kế thừa (Inheritance) và đa hình (Polymorphism):
- ThiSinh: lớp cha trừu tượng (Abstract Base Class)
- ThiSinhKhoiA: thí sinh khối A (Toán, Lý, Hóa)
- ThiSinhKhoiB: thí sinh khối B (Toán, Hóa, Sinh)
"""

from abc import ABC, abstractmethod


class ThiSinh(ABC):
    """
    Lớp trừu tượng đại diện cho một thí sinh dự thi đại học.

    Thuộc tính:
        cccd (str): Căn cước công dân (12 chữ số)
        so_bao_danh (str): Số báo danh (mã định danh duy nhất)
        ho_ten (str): Họ và tên đầy đủ
        dia_chi (str): Địa chỉ thường trú

    Lớp này không thể khởi tạo trực tiếp, phải dùng ThiSinhKhoiA hoặc ThiSinhKhoiB.
    """

    def __init__(self, cccd: str, so_bao_danh: str, ho_ten: str, dia_chi: str):
        self.cccd = cccd
        self.so_bao_danh = so_bao_danh
        self.ho_ten = ho_ten
        self.dia_chi = dia_chi

    # --- Các phương thức trừu tượng (bắt buộc lớp con phải cài đặt) ---

    @abstractmethod
    def tinh_diem_xet_tuyen(self) -> float:
        """Tính tổng điểm xét tuyển đại học theo công thức riêng của từng khối."""
        pass

    @abstractmethod
    def get_khoi(self) -> str:
        """Trả về tên khối thi: 'A' hoặc 'B'."""
        pass

    @abstractmethod
    def get_diem_mon(self) -> dict:
        """Trả về dict điểm các môn thi, ví dụ: {'Toán': 8.5, 'Lý': 7.0, 'Hóa': 8.0}."""
        pass

    @abstractmethod
    def get_diem_tu_duy(self) -> float:
        """Trả về điểm đánh giá tư duy (thang 100)."""
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        """Chuyển đổi thí sinh thành dictionary để lưu file JSON."""
        pass

    # --- Các phương thức chung cho tất cả thí sinh ---

    def is_liet(self) -> bool:
        """
        Kiểm tra thí sinh có bị liệt không.

        Điều kiện liệt:
        - Có ít nhất 1 môn thi dưới 2 điểm, HOẶC
        - Điểm đánh giá tư duy dưới 30 điểm (theo khối)

        Returns:
            True nếu bị liệt, False nếu không
        """
        # Kiểm tra từng môn thi
        for ten_mon, diem in self.get_diem_mon().items():
            if diem < 2:
                return True  # Có môn dưới 2 điểm → liệt

        # Kiểm tra điểm tư duy
        if self.get_diem_tu_duy() < 30:
            return True  # Tư duy dưới 30 → liệt

        return False  # Không bị liệt

    def tong_3_mon(self) -> float:
        """Tính tổng điểm 3 môn thi (không nhân hệ số, không cộng tư duy)."""
        return sum(self.get_diem_mon().values())

    @classmethod
    def from_dict(cls, data: dict) -> "ThiSinh":
        """
        Tạo đối tượng ThiSinh từ dictionary (đọc từ file JSON).

        Đây là Factory Method Pattern: tự động tạo đúng loại thí sinh
        dựa vào trường 'khoi' trong data.

        Args:
            data: dictionary chứa thông tin thí sinh

        Returns:
            ThiSinhKhoiA hoặc ThiSinhKhoiB tương ứng

        Raises:
            ValueError: nếu khối không phải 'A' hoặc 'B'
        """
        khoi = data.get("khoi")

        if khoi == "A":
            return ThiSinhKhoiA(
                cccd=data["cccd"],
                so_bao_danh=data["so_bao_danh"],
                ho_ten=data["ho_ten"],
                dia_chi=data["dia_chi"],
                toan=data["toan"],
                ly=data["ly"],
                hoa=data["hoa"],
                diem_tu_duy=data["diem_tu_duy"],
            )
        elif khoi == "B":
            return ThiSinhKhoiB(
                cccd=data["cccd"],
                so_bao_danh=data["so_bao_danh"],
                ho_ten=data["ho_ten"],
                dia_chi=data["dia_chi"],
                toan=data["toan"],
                hoa=data["hoa"],
                sinh=data["sinh"],
                diem_tu_duy=data["diem_tu_duy"],
            )

        raise ValueError(f"Khối không hợp lệ: {khoi}. Chỉ chấp nhận 'A' hoặc 'B'.")

    def __str__(self) -> str:
        """Hiển thị thông tin thí sinh dạng chuỗi (dùng cho Console)."""
        mon_str = ", ".join(f"{k}: {v}" for k, v in self.get_diem_mon().items())
        return (
            f"[{self.get_khoi()}] {self.so_bao_danh} - {self.ho_ten} | "
            f"CCCD: {self.cccd} | {mon_str} | "
            f"Tư duy: {self.get_diem_tu_duy()} | "
            f"Điểm XT: {self.tinh_diem_xet_tuyen():.2f}"
        )


class ThiSinhKhoiA(ThiSinh):
    """
    Thí sinh khối A: thi các môn Toán, Lý, Hóa.

    Công thức điểm xét tuyển:
        Điểm XT = Toán × 1.5 + Lý + Hóa + Điểm tư duy

    Thuộc tính bổ sung:
        toan (float): Điểm Toán (0-10)
        ly (float): Điểm Lý (0-10)
        hoa (float): Điểm Hóa (0-10)
        diem_tu_duy (float): Điểm đánh giá tư duy (0-100)
    """

    def __init__(
        self,
        cccd: str,
        so_bao_danh: str,
        ho_ten: str,
        dia_chi: str,
        toan: float,
        ly: float,
        hoa: float,
        diem_tu_duy: float,
    ):
        # Gọi constructor của lớp cha để khởi tạo thông tin chung
        super().__init__(cccd, so_bao_danh, ho_ten, dia_chi)
        self.toan = toan
        self.ly = ly
        self.hoa = hoa
        self.diem_tu_duy = diem_tu_duy

    def tinh_diem_xet_tuyen(self) -> float:
        """Khối A: Toán × 1.5 + Lý + Hóa + Điểm tư duy."""
        return self.toan * 1.5 + self.ly + self.hoa + self.diem_tu_duy

    def get_khoi(self) -> str:
        return "A"

    def get_diem_mon(self) -> dict:
        return {"Toán": self.toan, "Lý": self.ly, "Hóa": self.hoa}

    def get_diem_tu_duy(self) -> float:
        return self.diem_tu_duy

    def to_dict(self) -> dict:
        """Chuyển thành dictionary để lưu JSON."""
        return {
            "khoi": "A",
            "cccd": self.cccd,
            "so_bao_danh": self.so_bao_danh,
            "ho_ten": self.ho_ten,
            "dia_chi": self.dia_chi,
            "toan": self.toan,
            "ly": self.ly,
            "hoa": self.hoa,
            "diem_tu_duy": self.diem_tu_duy,
        }


class ThiSinhKhoiB(ThiSinh):
    """
    Thí sinh khối B: thi các môn Toán, Hóa, Sinh.

    Công thức điểm xét tuyển:
        Điểm XT = Toán + Hóa × 1.5 + Sinh + Điểm tư duy

    Thuộc tính bổ sung:
        toan (float): Điểm Toán (0-10)
        hoa (float): Điểm Hóa (0-10)
        sinh (float): Điểm Sinh (0-10)
        diem_tu_duy (float): Điểm đánh giá tư duy (0-100)
    """

    def __init__(
        self,
        cccd: str,
        so_bao_danh: str,
        ho_ten: str,
        dia_chi: str,
        toan: float,
        hoa: float,
        sinh: float,
        diem_tu_duy: float,
    ):
        # Gọi constructor của lớp cha
        super().__init__(cccd, so_bao_danh, ho_ten, dia_chi)
        self.toan = toan
        self.hoa = hoa
        self.sinh = sinh
        self.diem_tu_duy = diem_tu_duy

    def tinh_diem_xet_tuyen(self) -> float:
        """Khối B: Toán + Hóa × 1.5 + Sinh + Điểm tư duy."""
        return self.toan + self.hoa * 1.5 + self.sinh + self.diem_tu_duy

    def get_khoi(self) -> str:
        return "B"

    def get_diem_mon(self) -> dict:
        return {"Toán": self.toan, "Hóa": self.hoa, "Sinh": self.sinh}

    def get_diem_tu_duy(self) -> float:
        return self.diem_tu_duy

    def to_dict(self) -> dict:
        """Chuyển thành dictionary để lưu JSON."""
        return {
            "khoi": "B",
            "cccd": self.cccd,
            "so_bao_danh": self.so_bao_danh,
            "ho_ten": self.ho_ten,
            "dia_chi": self.dia_chi,
            "toan": self.toan,
            "hoa": self.hoa,
            "sinh": self.sinh,
            "diem_tu_duy": self.diem_tu_duy,
        }
