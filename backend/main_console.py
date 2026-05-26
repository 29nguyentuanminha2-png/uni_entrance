import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from models.manage_student import ManageStudent


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def pause():
    input("\nNhấn Enter để tiếp tục...")


def print_header(title: str):
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_students(students, show_index=False):
    if not students:
        print("  (Không có thí sinh nào)")
        return
    for i, s in enumerate(students, 1):
        prefix = f"{i}. " if show_index else "  "
        print(f"{prefix}{s}")


def nhap_khoi() -> str:
    while True:
        khoi = input("Chọn khối (A/B): ").strip().upper()
        if khoi in ("A", "B"):
            return khoi
        print("Khối không hợp lệ! Vui lòng nhập A hoặc B.")


def nhap_diem(prompt: str, max_val: float = 10.0) -> float:
    while True:
        try:
            val = float(input(prompt))
            if 0 <= val <= max_val:
                return val
            print(f"Điểm phải từ 0 đến {max_val}")
        except ValueError:
            print("Vui lòng nhập số!")


def nhap_thi_sinh() -> dict:
    print("\n--- Nhập thông tin thí sinh ---")
    khoi = nhap_khoi()
    cccd = input("CCCD (12 số): ").strip()
    sbd = input("Số báo danh: ").strip()
    ho_ten = input("Họ tên: ").strip()
    dia_chi = input("Địa chỉ: ").strip()
    toan = nhap_diem("Điểm Toán (0-10): ")

    data = {
        "khoi": khoi,
        "cccd": cccd,
        "so_bao_danh": sbd,
        "ho_ten": ho_ten,
        "dia_chi": dia_chi,
        "toan": toan,
    }

    if khoi == "A":
        data["ly"] = nhap_diem("Điểm Lý (0-10): ")
        data["hoa"] = nhap_diem("Điểm Hóa (0-10): ")
    else:
        data["hoa"] = nhap_diem("Điểm Hóa (0-10): ")
        data["sinh"] = nhap_diem("Điểm Sinh (0-10): ")

    data["diem_tu_duy"] = nhap_diem("Điểm tư duy (0-100): ", 100)
    return data


def menu():
    print_header("HỆ THỐNG QUẢN LÝ THÍ SINH DỰ THI ĐẠI HỌC")
    print("  1.  Thêm mới thí sinh")
    print("  2.  Sửa thông tin thí sinh")
    print("  3.  Xóa thí sinh")
    print("  4.  Tìm kiếm thí sinh")
    print("  5.  Hiển thị danh sách theo khối")
    print("  6.  Hiển thị điểm xét tuyển")
    print("  7.  Tính trung bình cộng điểm")
    print("  8.  Sắp xếp theo tổng 3 môn")
    print("  9.  Sắp xếp theo điểm tư duy")
    print("  10. Thống kê không liệt môn")
    print("  11. Danh sách đạt học bổng")
    print("  12. Danh sách không liệt môn nào")
    print("  13. Hiển thị danh sách không liệt môn")
    print("  14. Load dữ liệu mẫu")
    print("  0.  Thoát chương trình")
    print("-" * 60)


def main():
    manager = ManageStudent()

    while True:
        clear_screen()
        menu()
        choice = input("Chọn chức năng: ").strip()

        if choice == "1":
            data = nhap_thi_sinh()
            ok, errors = manager.them_thi_sinh(data)
            if ok:
                print("\n✓ Thêm thí sinh thành công!")
            else:
                print("\n✗ Lỗi:")
                for e in errors:
                    print(f"  - {e}")
            pause()

        elif choice == "2":
            sbd = input("Nhập SBD thí sinh cần sửa: ").strip()
            ts = manager.get_by_sbd(sbd)
            if not ts:
                print("Không tìm thấy thí sinh!")
            else:
                print(f"Thông tin hiện tại: {ts}")
                data = nhap_thi_sinh()
                ok, errors = manager.sua_thi_sinh(sbd, data)
                if ok:
                    print("\n✓ Cập nhật thành công!")
                else:
                    print("\n✗ Lỗi:")
                    for e in errors:
                        print(f"  - {e}")
            pause()

        elif choice == "3":
            sbd = input("Nhập SBD thí sinh cần xóa: ").strip()
            ok, msg = manager.xoa_thi_sinh(sbd)
            print(f"\n{'✓' if ok else '✗'} {msg}")
            pause()

        elif choice == "4":
            keyword = input("Nhập SBD hoặc CCCD: ").strip()
            results = manager.tim_kiem(keyword)
            print(f"\nKết quả ({len(results)} thí sinh):")
            print_students(results)
            pause()

        elif choice == "5":
            khoi = nhap_khoi()
            students = manager.hien_thi_theo_khoi(khoi)
            print(f"\nDanh sách khối {khoi} ({len(students)} thí sinh):")
            print_students(students, show_index=True)
            pause()

        elif choice == "6":
            khoi = input("Chọn khối (A/B hoặc Enter để xem tất cả): ").strip().upper()
            ds = manager.danh_sach_diem_xet_tuyen(khoi if khoi in ("A", "B") else None)
            print(f"\nĐiểm xét tuyển ({len(ds)} thí sinh):")
            for d in ds:
                print(f"  [{d['khoi']}] {d['so_bao_danh']} - {d['ho_ten']}: {d['diem_xet_tuyen']}")
            pause()

        elif choice == "7":
            tb = manager.trung_binh_cong_diem()
            print(f"\nTổng thí sinh: {tb.get('tong_thi_sinh', 0)}")
            print(f"Tổng điểm: {tb.get('tong_diem', 0)}")
            print(f"Trung bình: {tb.get('trung_binh', 0)}")
            pause()

        elif choice == "8":
            khoi = nhap_khoi()
            order = input("Thứ tự (1: Cao→Thấp, 2: Thấp→Cao): ").strip()
            giam_dan = order != "2"
            results = manager.sap_xep_3_mon(khoi, giam_dan)
            print(f"\nSắp xếp theo tổng 3 môn - Khối {khoi}:")
            for i, s in enumerate(results, 1):
                print(f"  {i}. {s} | Tổng 3 môn: {s.tong_3_mon():.1f}")
            pause()

        elif choice == "9":
            khoi = nhap_khoi()
            order = input("Thứ tự (1: Cao→Thấp, 2: Thấp→Cao): ").strip()
            giam_dan = order != "2"
            results = manager.sap_xep_tu_duy(khoi, giam_dan)
            print(f"\nSắp xếp theo điểm tư duy - Khối {khoi}:")
            for i, s in enumerate(results, 1):
                print(f"  {i}. {s}")
            pause()

        elif choice == "10":
            khoi = input("Chọn khối (A/B hoặc Enter cho tất cả): ").strip().upper()
            results = manager.ds_khong_liet(khoi if khoi in ("A", "B") else None)
            print(f"\nThí sinh không liệt ({len(results)}):")
            print_students(results, show_index=True)
            pause()

        elif choice == "11":
            print("\nDanh sách đạt học bổng:")
            for khoi in ("A", "B"):
                hb = manager.ds_hoc_bong(khoi)
                print(f"\n  Khối {khoi} (Top {len(hb)}):")
                if not hb:
                    print("    (Không có)")
                for i, s in enumerate(hb, 1):
                    print(f"    {i}. {s}")
            pause()

        elif choice == "12":
            results = manager.ds_khong_liet()
            print(f"\nThí sinh không liệt môn nào ({len(results)}):")
            print_students(results, show_index=True)
            pause()

        elif choice == "13":
            results = manager.ds_co_liet()
            print(f"\nThí sinh có liệt môn ({len(results)}):")
            print_students(results, show_index=True)
            pause()

        elif choice == "14":
            manager.load_sample_data()
            print(f"\n✓ Đã load {len(manager.get_all())} thí sinh mẫu!")
            pause()

        elif choice == "0":
            print("\nTạm biệt!")
            break

        else:
            print("Lựa chọn không hợp lệ!")
            pause()


if __name__ == "__main__":
    main()
