import { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Toaster, toast } from 'react-hot-toast';
import {
  Users, GraduationCap, Award, AlertTriangle,
  Search, Filter, TrendingUp, BarChart3,
  Plus, X, ChevronDown, ChevronUp, ArrowUpDown
} from 'lucide-react';
import {
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, Legend, ResponsiveContainer, LabelList
} from 'recharts';
import { studentApi } from './api/studentApi';
import type { StudentWithScore, ThongKe, ChartData } from './types/student';
import StudentForm from './StudentForm';

/* ===== Bảng màu ===== */
const COLORS = {
  blue: '#3b82f6', indigo: '#6366f1', green: '#22c55e',
  red: '#ef4444', amber: '#f59e0b', purple: '#a855f7',
  teal: '#14b8a6', pink: '#ec4899',
};
const DONUT_COLORS = ['#3b82f6', '#6366f1', '#22c55e', '#f59e0b', '#ef4444', '#a855f7'];

/* Label hiện số bên trong từng phần donut */
const renderInsideLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, value }: any) => {
  const RADIAN = Math.PI / 180;
  const radius = (innerRadius + outerRadius) / 2;
  const x = cx + radius * Math.cos(-midAngle * RADIAN);
  const y = cy + radius * Math.sin(-midAngle * RADIAN);
  return (
    <text x={x} y={y} fill="#fff" textAnchor="middle" dominantBaseline="central" fontSize={13} fontWeight={700}>
      {value}
    </text>
  );
};

/* ===== Tabs cho bảng dữ liệu ===== */
type TabType = 'all' | 'khong_liet' | 'liet' | 'hoc_bong';

function App() {
  /* ===== State ===== */
  const [students, setStudents] = useState<StudentWithScore[]>([]);
  const [thongKe, setThongKe] = useState<ThongKe | null>(null);
  const [chartData, setChartData] = useState<ChartData | null>(null);
  const [hocBong, setHocBong] = useState<StudentWithScore[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters & Sort
  const [searchQuery, setSearchQuery] = useState('');
  const [khoiFilter, setKhoiFilter] = useState<'' | 'A' | 'B'>('');
  const [sortBy, setSortBy] = useState<'diem_xet_tuyen' | 'tong_3_mon' | 'trung_binh' | 'diem_tu_duy' | 'ho_ten'>('diem_xet_tuyen');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  // Tab hiện tại
  const [activeTab, setActiveTab] = useState<TabType>('all');

  // Modal
  const [showForm, setShowForm] = useState(false);
  const [editStudent, setEditStudent] = useState<StudentWithScore | null>(null);

  /* ===== Lấy dữ liệu ===== */
  const fetchData = async () => {
    try {
      setLoading(true);
      const [studentsData, statsData, chartsData, hocBongData] = await Promise.all([
        studentApi.getAllWithScores(),
        studentApi.getThongKe(),
        studentApi.getCharts(),
        studentApi.getHocBong(),
      ]);
      setStudents(studentsData);
      setThongKe(statsData);
      setChartData(chartsData);
      // Gộp học bổng 2 khối + tính thêm tong_3_mon nếu chưa có
      const hbAll: StudentWithScore[] = [...(hocBongData.A || []), ...(hocBongData.B || [])].map(s => ({
        ...s,
        tong_3_mon: s.tong_3_mon ?? (s.khoi === 'A'
          ? s.toan + (s as any).ly + (s as any).hoa
          : s.toan + (s as any).hoa + (s as any).sinh),
        is_liet: s.is_liet ?? false,
      }));
      setHocBong(hbAll);
    } catch (err) {
      toast.error('Lỗi tải dữ liệu!');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  /* ===== Lọc theo tab + bộ lọc + sắp xếp ===== */
  const filteredStudents = useMemo(() => {
    // Bước 1: Lọc theo tab
    let result: StudentWithScore[];
    if (activeTab === 'hoc_bong') {
      result = [...hocBong];
    } else if (activeTab === 'liet') {
      result = students.filter(s => s.is_liet);
    } else if (activeTab === 'khong_liet') {
      result = students.filter(s => !s.is_liet);
    } else {
      result = [...students];
    }

    // Bước 2: Lọc theo khối
    if (khoiFilter) result = result.filter(s => s.khoi === khoiFilter);

    // Bước 3: Tìm kiếm
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      result = result.filter(s =>
        s.ho_ten.toLowerCase().includes(q) || s.so_bao_danh.includes(q) || s.cccd.includes(q)
      );
    }

    // Bước 4: Sắp xếp
    result.sort((a, b) => {
      let valA: number | string = 0, valB: number | string = 0;
      if (sortBy === 'diem_xet_tuyen') { valA = a.diem_xet_tuyen || 0; valB = b.diem_xet_tuyen || 0; }
      else if (sortBy === 'tong_3_mon') { valA = a.tong_3_mon || 0; valB = b.tong_3_mon || 0; }
      else if (sortBy === 'trung_binh') { valA = (a.tong_3_mon || 0) / 3; valB = (b.tong_3_mon || 0) / 3; }
      else if (sortBy === 'diem_tu_duy') { valA = a.diem_tu_duy; valB = b.diem_tu_duy; }
      else if (sortBy === 'ho_ten') { valA = a.ho_ten; valB = b.ho_ten; }
      if (typeof valA === 'string') return sortOrder === 'asc' ? valA.localeCompare(valB as string) : (valB as string).localeCompare(valA);
      return sortOrder === 'asc' ? (valA as number) - (valB as number) : (valB as number) - (valA as number);
    });
    return result;
  }, [students, hocBong, activeTab, khoiFilter, searchQuery, sortBy, sortOrder]);

  /* ===== Handlers ===== */
  const handleDelete = async (sbd: string) => {
    if (!confirm(`Xóa thí sinh ${sbd}?`)) return;
    try {
      await studentApi.delete(sbd);
      toast.success('Đã xóa thí sinh');
      fetchData();
    } catch { toast.error('Lỗi khi xóa'); }
  };

  const handleFormSuccess = () => { setShowForm(false); setEditStudent(null); fetchData(); };

  const toggleSort = (field: typeof sortBy) => {
    if (sortBy === field) setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc');
    else { setSortBy(field); setSortOrder('desc'); }
  };

  /* ===== Loading ===== */
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: 'linear' }}
          className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  /* ===== Tab info ===== */
  const tabs: { key: TabType; label: string; icon: React.ReactNode }[] = [
    { key: 'all', label: 'Tất cả', icon: <Users className="w-3.5 h-3.5" /> },
    { key: 'khong_liet', label: 'Không liệt', icon: <BarChart3 className="w-3.5 h-3.5" /> },
    { key: 'liet', label: 'Bị liệt', icon: <AlertTriangle className="w-3.5 h-3.5" /> },
    { key: 'hoc_bong', label: 'Học bổng', icon: <Award className="w-3.5 h-3.5" /> },
  ];

  return (
    <div className="min-h-screen bg-slate-50">
      <Toaster position="top-right" />

      {/* ===== HEADER ===== */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-40">
        <div style={{ maxWidth: 1440 }} className="mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center">
              <GraduationCap className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-slate-900">Quản Lý Thí Sinh</h1>
              <p className="text-xs text-slate-500">Hệ thống xét tuyển đại học</p>
            </div>
          </div>
          <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
            onClick={() => { setEditStudent(null); setShowForm(true); }}
            className="flex items-center gap-2 px-4 py-2.5 bg-blue-600 text-white rounded-lg font-medium text-sm hover:bg-blue-700 transition-colors">
            <Plus className="w-4 h-4" /> Thêm thí sinh
          </motion.button>
        </div>
      </header>

      <main style={{ maxWidth: 1440 }} className="mx-auto px-6 py-6 space-y-6">
        {/* ===== STAT CARDS ===== */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard icon={<Users className="w-5 h-5" />} label="Tổng thí sinh" value={thongKe?.tong || 0} color="blue" />
          <StatCard icon={<BarChart3 className="w-5 h-5" />} label="Không liệt" value={thongKe?.khong_liet || 0} color="green" />
          <StatCard icon={<AlertTriangle className="w-5 h-5" />} label="Bị liệt" value={thongKe?.co_liet || 0} color="red" />
          <StatCard icon={<Award className="w-5 h-5" />} label="Học bổng" value={(thongKe?.hoc_bong_a || 0) + (thongKe?.hoc_bong_b || 0)} color="amber" />
        </div>

        {/* ===== CHARTS ROW 1 ===== */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <ChartCard title="Phân bố khối thi" delay={0.1}>
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={chartData?.donut_khoi || []} cx="50%" cy="50%" innerRadius={45} outerRadius={78}
                  dataKey="value" nameKey="name" paddingAngle={3} label={renderInsideLabel} labelLine={false}>
                  {(chartData?.donut_khoi || []).map((_, i) => (
                    <Cell key={i} fill={DONUT_COLORS[i % DONUT_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip /><Legend />
              </PieChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard title="Tỷ lệ liệt / không liệt" delay={0.2}>
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={chartData?.donut_liet || []} cx="50%" cy="50%" innerRadius={45} outerRadius={78}
                  dataKey="value" nameKey="name" paddingAngle={3} label={renderInsideLabel} labelLine={false}>
                  <Cell fill={COLORS.green} /><Cell fill={COLORS.red} />
                </Pie>
                <Tooltip /><Legend />
              </PieChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard title="Phân bố điểm tư duy" delay={0.3}>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={chartData?.bar_tu_duy || []} margin={{ top: 20, right: 10, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="range" tick={{ fontSize: 11 }} /><YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="count" fill={COLORS.indigo} radius={[4, 4, 0, 0]} name="Số lượng">
                  <LabelList dataKey="count" position="top" fontSize={11} fontWeight={600} fill="#475569" />
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>
        </div>

        {/* ===== CHARTS ROW 2 ===== */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <ChartCard title="Điểm trung bình theo môn" delay={0.4}>
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={chartData?.column_mon || []} margin={{ top: 20, right: 10, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="mon" tick={{ fontSize: 11 }} /><YAxis domain={[0, 10]} tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="trung_binh" fill={COLORS.teal} radius={[4, 4, 0, 0]} name="Trung bình">
                  <LabelList dataKey="trung_binh" position="top" fontSize={11} fontWeight={600} fill="#475569" />
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard title="Phân bố điểm xét tuyển theo khối" delay={0.5}>
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={chartData?.bar_diem_xt || []} margin={{ top: 20, right: 10, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="range" tick={{ fontSize: 11 }} /><YAxis tick={{ fontSize: 11 }} />
                <Tooltip /><Legend />
                <Bar dataKey="khoi_a" fill={COLORS.blue} radius={[4, 4, 0, 0]} name="Khối A">
                  <LabelList dataKey="khoi_a" position="top" fontSize={10} fontWeight={600} fill="#475569" />
                </Bar>
                <Bar dataKey="khoi_b" fill={COLORS.purple} radius={[4, 4, 0, 0]} name="Khối B">
                  <LabelList dataKey="khoi_b" position="top" fontSize={10} fontWeight={600} fill="#475569" />
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>
        </div>

        {/* ===== TABS + FILTER BAR ===== */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}
          className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">

          {/* Tabs */}
          <div className="flex border-b border-slate-200 px-5 gap-6">
            {tabs.map(tab => (
              <button key={tab.key} onClick={() => setActiveTab(tab.key)}
                className={`flex items-center gap-1.5 py-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab.key
                    ? 'text-slate-900 border-slate-900'
                    : 'text-slate-400 border-transparent hover:text-slate-600'
                }`}>
                {tab.icon}
                {tab.label}
              </button>
            ))}
          </div>

          {/* Filter Bar */}
          <div className="p-4 border-b border-slate-100 bg-slate-50/50">
            <div className="flex flex-wrap items-center gap-3">
              {/* Search */}
              <div className="relative flex-1" style={{ minWidth: 200 }}>
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <input type="text" placeholder="Tìm theo tên, SBD, CCCD..."
                  value={searchQuery} onChange={e => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 text-sm border border-slate-200 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent" />
              </div>

              {/* Lọc khối */}
              <div className="flex items-center gap-1">
                <Filter className="w-4 h-4 text-slate-400" />
                <select value={khoiFilter} onChange={e => setKhoiFilter(e.target.value as '' | 'A' | 'B')}
                  className="text-sm border border-slate-200 rounded-lg px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500">
                  <option value="">Tất cả khối</option>
                  <option value="A">Khối A</option>
                  <option value="B">Khối B</option>
                </select>
              </div>

              {/* Sắp xếp theo */}
              <div className="flex items-center gap-1">
                <ArrowUpDown className="w-4 h-4 text-slate-400" />
                <select value={sortBy} onChange={e => setSortBy(e.target.value as typeof sortBy)}
                  className="text-sm border border-slate-200 rounded-lg px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500">
                  <option value="diem_xet_tuyen">Điểm xét tuyển</option>
                  <option value="tong_3_mon">Tổng 3 môn</option>
                  <option value="trung_binh">Trung bình cộng</option>
                  <option value="diem_tu_duy">Điểm tư duy</option>
                  <option value="ho_ten">Họ tên (A-Z)</option>
                </select>
              </div>

              {/* Thứ tự */}
              <button onClick={() => setSortOrder(prev => prev === 'desc' ? 'asc' : 'desc')}
                className="flex items-center gap-1 px-3 py-2 text-sm border border-slate-200 rounded-lg bg-white hover:bg-slate-50 transition-colors">
                {sortOrder === 'desc' ? (
                  <><ChevronDown className="w-4 h-4 text-slate-500" /><span className="text-slate-600">Cao → Thấp</span></>
                ) : (
                  <><ChevronUp className="w-4 h-4 text-slate-500" /><span className="text-slate-600">Thấp → Cao</span></>
                )}
              </button>

              {/* Count */}
              <span className="text-xs text-slate-500 ml-auto">
                {filteredStudents.length} thí sinh
              </span>
            </div>
          </div>

          {/* ===== DATA TABLE ===== */}
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="px-3 py-3 text-left font-semibold text-slate-600 w-10">#</th>
                  <th className="px-3 py-3 text-left font-semibold text-slate-600">SBD</th>
                  <th className="px-3 py-3 text-left font-semibold text-slate-600 cursor-pointer hover:text-blue-600"
                    onClick={() => toggleSort('ho_ten')}>
                    <span className="flex items-center gap-1">Họ tên {sortBy === 'ho_ten' && <SortIcon order={sortOrder} />}</span>
                  </th>
                  <th className="px-3 py-3 text-center font-semibold text-slate-600">Khối</th>
                  <th className="px-3 py-3 text-center font-semibold text-slate-600">Toán</th>
                  <th className="px-3 py-3 text-center font-semibold text-slate-600">Môn 2</th>
                  <th className="px-3 py-3 text-center font-semibold text-slate-600">Môn 3</th>
                  <th className="px-3 py-3 text-center font-semibold text-slate-600 cursor-pointer hover:text-blue-600"
                    onClick={() => toggleSort('diem_tu_duy')}>
                    <span className="flex items-center justify-center gap-1">Tư duy {sortBy === 'diem_tu_duy' && <SortIcon order={sortOrder} />}</span>
                  </th>
                  <th className="px-3 py-3 text-center font-semibold text-slate-600 cursor-pointer hover:text-blue-600"
                    onClick={() => toggleSort('tong_3_mon')}>
                    <span className="flex items-center justify-center gap-1">Tổng 3 môn {sortBy === 'tong_3_mon' && <SortIcon order={sortOrder} />}</span>
                  </th>
                  <th className="px-3 py-3 text-center font-semibold text-slate-600 cursor-pointer hover:text-blue-600 bg-blue-50/50"
                    onClick={() => toggleSort('trung_binh')}>
                    <span className="flex items-center justify-center gap-1">TB cộng {sortBy === 'trung_binh' && <SortIcon order={sortOrder} />}</span>
                  </th>
                  <th className="px-3 py-3 text-center font-semibold text-slate-600 cursor-pointer hover:text-blue-600"
                    onClick={() => toggleSort('diem_xet_tuyen')}>
                    <span className="flex items-center justify-center gap-1">
                      <TrendingUp className="w-3 h-3" /> ĐXT {sortBy === 'diem_xet_tuyen' && <SortIcon order={sortOrder} />}
                    </span>
                  </th>
                  <th className="px-3 py-3 text-center font-semibold text-slate-600">Trạng thái</th>
                  <th className="px-3 py-3 text-center font-semibold text-slate-600">Thao tác</th>
                </tr>
              </thead>
              <tbody>
                {filteredStudents.map((s, idx) => {
                  const trungBinh = (s.tong_3_mon || 0) / 3;
                  return (
                    <tr key={s.so_bao_danh} className="border-b border-slate-100 hover:bg-blue-50/30 transition-colors">
                      <td className="px-3 py-2.5 text-slate-400 text-xs">{idx + 1}</td>
                      <td className="px-3 py-2.5 font-mono text-xs text-slate-600">{s.so_bao_danh}</td>
                      <td className="px-3 py-2.5 font-medium text-slate-800">{s.ho_ten}</td>
                      <td className="px-3 py-2.5 text-center">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                          s.khoi === 'A' ? 'bg-blue-100 text-blue-700' : 'bg-purple-100 text-purple-700'
                        }`}>{s.khoi}</span>
                      </td>
                      <td className="px-3 py-2.5 text-center">{s.toan}</td>
                      <td className="px-3 py-2.5 text-center">{s.khoi === 'A' ? (s as any).ly : (s as any).hoa}</td>
                      <td className="px-3 py-2.5 text-center">{s.khoi === 'A' ? (s as any).hoa : (s as any).sinh}</td>
                      <td className="px-3 py-2.5 text-center text-slate-700">{s.diem_tu_duy}</td>
                      <td className="px-3 py-2.5 text-center font-medium">{s.tong_3_mon?.toFixed(1)}</td>
                      <td className="px-3 py-2.5 text-center font-medium bg-blue-50/30 text-indigo-700">{trungBinh.toFixed(2)}</td>
                      <td className="px-3 py-2.5 text-center font-bold text-blue-600">{s.diem_xet_tuyen?.toFixed(2)}</td>
                      <td className="px-3 py-2.5 text-center">
                        {activeTab === 'hoc_bong' ? (
                          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-700">Học bổng</span>
                        ) : s.is_liet ? (
                          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-700">Liệt</span>
                        ) : (
                          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-700">Đạt</span>
                        )}
                      </td>
                      <td className="px-3 py-2.5 text-center">
                        <div className="flex items-center justify-center gap-1">
                          <button onClick={() => { setEditStudent(s); setShowForm(true); }}
                            className="px-2 py-1 text-xs text-blue-600 hover:bg-blue-50 rounded transition-colors">Sửa</button>
                          <button onClick={() => handleDelete(s.so_bao_danh)}
                            className="px-2 py-1 text-xs text-red-600 hover:bg-red-50 rounded transition-colors">Xóa</button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          {filteredStudents.length === 0 && (
            <div className="py-12 text-center text-slate-400">
              <Users className="w-12 h-12 mx-auto mb-3 opacity-50" /><p>Không tìm thấy thí sinh nào</p>
            </div>
          )}
        </motion.div>
      </main>

      {/* ===== MODAL ===== */}
      <AnimatePresence>
        {showForm && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4"
            onClick={() => setShowForm(false)}>
            <motion.div initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.95, opacity: 0 }}
              onClick={e => e.stopPropagation()} className="bg-white rounded-2xl shadow-2xl w-full max-h-[90vh] overflow-y-auto" style={{ maxWidth: 480 }}>
              <div className="flex items-center justify-between p-5 border-b border-slate-200">
                <h2 className="text-lg font-bold text-slate-800">{editStudent ? 'Sửa thí sinh' : 'Thêm thí sinh mới'}</h2>
                <button onClick={() => setShowForm(false)} className="p-1 hover:bg-slate-100 rounded-lg">
                  <X className="w-5 h-5 text-slate-500" />
                </button>
              </div>
              <StudentForm student={editStudent} onSuccess={handleFormSuccess} onCancel={() => setShowForm(false)} />
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

/* ===== Sub-components ===== */

function StatCard({ icon, label, value, color }: { icon: React.ReactNode; label: string; value: number; color: string }) {
  const colorMap: Record<string, string> = {
    blue: 'bg-blue-50 text-blue-600', green: 'bg-green-50 text-green-600',
    red: 'bg-red-50 text-red-600', amber: 'bg-amber-50 text-amber-600',
  };
  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-xl p-4 border border-slate-200 shadow-sm flex items-center gap-4">
      <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${colorMap[color]}`}>{icon}</div>
      <div>
        <p className="text-2xl font-bold text-slate-800">{value}</p>
        <p className="text-xs text-slate-500">{label}</p>
      </div>
    </motion.div>
  );
}

function ChartCard({ title, delay, children }: { title: string; delay: number; children: React.ReactNode }) {
  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay }}
      className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm">
      <h3 className="text-sm font-semibold text-slate-700 mb-3">{title}</h3>
      {children}
    </motion.div>
  );
}

function SortIcon({ order }: { order: string }) {
  return order === 'asc' ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />;
}

export default App;
