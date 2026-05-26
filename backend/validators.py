import re


def validate_cccd(cccd: str) -> tuple[bool, str]:
    if not cccd or not re.fullmatch(r"\d{12}", cccd):
        return False, "CCCD phải đúng 12 chữ số"
    return True, ""


def validate_so_bao_danh(sbd: str) -> tuple[bool, str]:
    if not sbd or not sbd.strip():
        return False, "Số báo danh không được rỗng"
    return True, ""


def validate_ho_ten(ho_ten: str) -> tuple[bool, str]:
    if not ho_ten or not ho_ten.strip():
        return False, "Họ tên không được rỗng"
    cleaned = ho_ten.replace(" ", "")
    if not all(c.isalpha() or c in "áàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÉÈẺẼẸÊẾỀỂỄỆÍÌỈĨỊÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÚÙỦŨỤƯỨỪỬỮỰÝỲỶỸỴĐ" for c in cleaned):
        return False, "Họ tên chỉ chứa chữ cái và khoảng trắng"
    return True, ""


def validate_dia_chi(dia_chi: str) -> tuple[bool, str]:
    if not dia_chi or not dia_chi.strip():
        return False, "Địa chỉ không được rỗng"
    return True, ""


def validate_diem_mon(diem: float, ten_mon: str) -> tuple[bool, str]:
    try:
        d = float(diem)
    except (ValueError, TypeError):
        return False, f"Điểm {ten_mon} phải là số"
    if d < 0 or d > 10:
        return False, f"Điểm {ten_mon} phải từ 0 đến 10"
    return True, ""


def validate_diem_tu_duy(diem: float) -> tuple[bool, str]:
    try:
        d = float(diem)
    except (ValueError, TypeError):
        return False, "Điểm tư duy phải là số"
    if d < 0 or d > 100:
        return False, "Điểm tư duy phải từ 0 đến 100"
    return True, ""


def validate_khoi(khoi: str) -> tuple[bool, str]:
    if khoi not in ("A", "B"):
        return False, "Khối phải là A hoặc B"
    return True, ""


def validate_thi_sinh_data(data: dict, existing_cccds: set = None, existing_sbds: set = None, exclude_sbd: str = None) -> tuple[bool, list[str]]:
    errors = []
    existing_cccds = existing_cccds or set()
    existing_sbds = existing_sbds or set()

    ok, msg = validate_khoi(data.get("khoi", ""))
    if not ok:
        errors.append(msg)
        return False, errors

    ok, msg = validate_cccd(data.get("cccd", ""))
    if not ok:
        errors.append(msg)
    elif data["cccd"] in existing_cccds:
        errors.append("CCCD đã tồn tại")

    sbd = data.get("so_bao_danh", "")
    ok, msg = validate_so_bao_danh(sbd)
    if not ok:
        errors.append(msg)
    else:
        check_sbds = existing_sbds - {exclude_sbd} if exclude_sbd else existing_sbds
        if sbd in check_sbds:
            errors.append("Số báo danh đã tồn tại")

    ok, msg = validate_ho_ten(data.get("ho_ten", ""))
    if not ok:
        errors.append(msg)

    ok, msg = validate_dia_chi(data.get("dia_chi", ""))
    if not ok:
        errors.append(msg)

    khoi = data["khoi"]
    mon_list = ["toan", "ly", "hoa"] if khoi == "A" else ["toan", "hoa", "sinh"]
    ten_mon_map = {"toan": "Toán", "ly": "Lý", "hoa": "Hóa", "sinh": "Sinh"}

    for mon in mon_list:
        ok, msg = validate_diem_mon(data.get(mon, ""), ten_mon_map[mon])
        if not ok:
            errors.append(msg)

    ok, msg = validate_diem_tu_duy(data.get("diem_tu_duy", ""))
    if not ok:
        errors.append(msg)

    return len(errors) == 0, errors
