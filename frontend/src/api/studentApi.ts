import axios from 'axios';
import type { Student, StudentWithScore, ThongKe, ChartData, ApiResponse } from '../types/student';

const api = axios.create({ baseURL: '/api' });

export const studentApi = {
  // === CRUD ===
  getAll: (khoi?: string) =>
    api.get<Student[]>('/students', { params: khoi ? { khoi } : {} }).then(r => r.data),

  getAllWithScores: () =>
    api.get<StudentWithScore[]>('/students/all-with-scores').then(r => r.data),

  getOne: (sbd: string) =>
    api.get<Student>(`/students/${sbd}`).then(r => r.data),

  create: (data: Partial<Student>) =>
    api.post<ApiResponse>('/students', data).then(r => r.data),

  update: (sbd: string, data: Partial<Student>) =>
    api.put<ApiResponse>(`/students/${sbd}`, data).then(r => r.data),

  delete: (sbd: string) =>
    api.delete<ApiResponse>(`/students/${sbd}`).then(r => r.data),

  search: (q: string) =>
    api.get<Student[]>('/students/search', { params: { q } }).then(r => r.data),

  // === Reports ===
  getThongKe: () =>
    api.get<ThongKe>('/reports/thong-ke').then(r => r.data),

  getCharts: () =>
    api.get<ChartData>('/reports/charts').then(r => r.data),

  getHocBong: (khoi?: string) =>
    api.get('/reports/hoc-bong', { params: khoi ? { khoi } : {} }).then(r => r.data),

  sapXepDiemXT: (khoi?: string, order: string = 'desc') =>
    api.get<StudentWithScore[]>('/reports/sap-xep-diem-xet-tuyen', { params: { ...(khoi ? { khoi } : {}), order } }).then(r => r.data),
};
