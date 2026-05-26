export interface StudentBase {
  khoi: 'A' | 'B';
  cccd: string;
  so_bao_danh: string;
  ho_ten: string;
  dia_chi: string;
  toan: number;
  diem_tu_duy: number;
}

export interface StudentA extends StudentBase {
  khoi: 'A';
  ly: number;
  hoa: number;
}

export interface StudentB extends StudentBase {
  khoi: 'B';
  hoa: number;
  sinh: number;
}

export type Student = StudentA | StudentB;

export type StudentWithScore = Student & {
  diem_xet_tuyen?: number;
  tong_3_mon?: number;
  is_liet?: boolean;
};

export interface ThongKe {
  tong: number;
  khoi_a: number;
  khoi_b: number;
  khong_liet: number;
  co_liet: number;
  hoc_bong_a: number;
  hoc_bong_b: number;
  trung_binh: {
    tong_thi_sinh: number;
    tong_diem: number;
    trung_binh: number;
  };
}

export interface ChartData {
  donut_khoi: { name: string; value: number }[];
  donut_liet: { name: string; value: number }[];
  bar_diem_xt: { range: string; khoi_a: number; khoi_b: number }[];
  column_mon: { mon: string; trung_binh: number; khoi: string }[];
  top10: { ho_ten: string; khoi: string; diem_xet_tuyen: number }[];
  bar_tu_duy: { range: string; count: number }[];
}

export interface ApiResponse {
  success: boolean;
  message?: string;
  errors?: string[];
  error?: string;
}
