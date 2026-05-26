import { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import { studentApi } from './api/studentApi';
import type { StudentWithScore } from './types/student';

interface Props {
  student: StudentWithScore | null;
  onSuccess: () => void;
  onCancel: () => void;
}

export default function StudentForm({ student, onSuccess, onCancel }: Props) {
  const isEdit = !!student;

  const [khoi, setKhoi] = useState<'A' | 'B'>(student?.khoi || 'A');
  const [cccd, setCccd] = useState(student?.cccd || '');
  const [sbd, setSbd] = useState(student?.so_bao_danh || '');
  const [hoTen, setHoTen] = useState(student?.ho_ten || '');
  const [diaChi, setDiaChi] = useState(student?.dia_chi || '');
  const [toan, setToan] = useState(student?.toan?.toString() || '');
  const [mon2, setMon2] = useState('');
  const [mon3, setMon3] = useState('');
  const [tuDuy, setTuDuy] = useState(student?.diem_tu_duy?.toString() || '');
  const [errors, setErrors] = useState<string[]>([]);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (student) {
      if (student.khoi === 'A') {
        setMon2((student as any).ly?.toString() || '');
        setMon3((student as any).hoa?.toString() || '');
      } else {
        setMon2((student as any).hoa?.toString() || '');
        setMon3((student as any).sinh?.toString() || '');
      }
    }
  }, [student]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors([]);
    setSubmitting(true);

    const data: any = {
      khoi, cccd, so_bao_danh: sbd, ho_ten: hoTen, dia_chi: diaChi,
      toan: parseFloat(toan), diem_tu_duy: parseFloat(tuDuy),
    };
    if (khoi === 'A') { data.ly = parseFloat(mon2); data.hoa = parseFloat(mon3); }
    else { data.hoa = parseFloat(mon2); data.sinh = parseFloat(mon3); }

    try {
      const res = isEdit
        ? await studentApi.update(student!.so_bao_danh, data)
        : await studentApi.create(data);
      if (res.success) { toast.success(res.message || 'Thành công!'); onSuccess(); }
      else { setErrors(res.errors || [res.error || 'Lỗi']); }
    } catch (err: any) {
      const errData = err?.response?.data;
      setErrors(errData?.errors || [errData?.error || 'Lỗi kết nối server']);
    } finally {
      setSubmitting(false);
    }
  };

  const inputClass = "w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent";
  const labelClass = "block text-xs font-medium text-slate-600 mb-1";

  return (
    <form onSubmit={handleSubmit} className="p-5 space-y-4">
      {errors.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3">
          {errors.map((err, i) => <p key={i} className="text-sm text-red-600">{err}</p>)}
        </div>
      )}

      {/* Khối */}
      <div>
        <label className={labelClass}>Khối thi</label>
        <div className="flex gap-2">
          {(['A', 'B'] as const).map(k => (
            <button key={k} type="button" onClick={() => setKhoi(k)}
              className={`flex-1 py-2 text-sm font-medium rounded-lg border transition-colors ${
                khoi === k ? 'bg-blue-50 border-blue-300 text-blue-700' : 'bg-white border-slate-200 text-slate-500 hover:bg-slate-50'
              }`}>
              Khối {k} ({k === 'A' ? 'Toán, Lý, Hóa' : 'Toán, Hóa, Sinh'})
            </button>
          ))}
        </div>
      </div>

      {/* Info */}
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className={labelClass}>CCCD (12 số)</label>
          <input value={cccd} onChange={e => setCccd(e.target.value)} className={inputClass} placeholder="001234567890" />
        </div>
        <div>
          <label className={labelClass}>Số báo danh</label>
          <input value={sbd} onChange={e => setSbd(e.target.value)} className={inputClass} placeholder="TS001" disabled={isEdit} />
        </div>
      </div>

      <div>
        <label className={labelClass}>Họ và tên</label>
        <input value={hoTen} onChange={e => setHoTen(e.target.value)} className={inputClass} placeholder="Nguyễn Văn A" />
      </div>

      <div>
        <label className={labelClass}>Địa chỉ</label>
        <input value={diaChi} onChange={e => setDiaChi(e.target.value)} className={inputClass} placeholder="Hà Nội" />
      </div>

      {/* Scores */}
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className={labelClass}>Toán (0-10)</label>
          <input type="number" step="0.1" min="0" max="10" value={toan} onChange={e => setToan(e.target.value)} className={inputClass} />
        </div>
        <div>
          <label className={labelClass}>{khoi === 'A' ? 'Lý' : 'Hóa'} (0-10)</label>
          <input type="number" step="0.1" min="0" max="10" value={mon2} onChange={e => setMon2(e.target.value)} className={inputClass} />
        </div>
        <div>
          <label className={labelClass}>{khoi === 'A' ? 'Hóa' : 'Sinh'} (0-10)</label>
          <input type="number" step="0.1" min="0" max="10" value={mon3} onChange={e => setMon3(e.target.value)} className={inputClass} />
        </div>
        <div>
          <label className={labelClass}>Tư duy (0-100)</label>
          <input type="number" step="0.1" min="0" max="100" value={tuDuy} onChange={e => setTuDuy(e.target.value)} className={inputClass} />
        </div>
      </div>

      {/* Buttons */}
      <div className="flex gap-3 pt-2">
        <button type="button" onClick={onCancel}
          className="flex-1 py-2.5 text-sm font-medium text-slate-600 bg-slate-100 rounded-lg hover:bg-slate-200 transition-colors">
          Hủy
        </button>
        <button type="submit" disabled={submitting}
          className="flex-1 py-2.5 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors">
          {submitting ? 'Đang xử lý...' : isEdit ? 'Cập nhật' : 'Thêm mới'}
        </button>
      </div>
    </form>
  );
}
