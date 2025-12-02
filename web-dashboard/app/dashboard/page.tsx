"use client";

import { useState, useEffect } from "react";
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer, 
  PieChart, 
  Pie, 
  Cell 
} from 'recharts';
import { AlertCircle, Activity, Clock, Server, Wifi, WifiOff, Eye, ShieldAlert, MapPin, Camera, Siren, Moon, Sun, Shield } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import FloorPlanMap from "@/components/dashboard/FloorPlanMap";

// ============================================
// SECURITY MODE TYPES & MOCK STATE
// ============================================
type SecurityMode = "operational" | "night_sentry" | "breach_detected";

interface SecurityState {
  mode: SecurityMode;
  isNightMode: boolean;
  breachDetected: boolean;
  lastBreachTime?: string;
  breachLocation?: string;
  intruderCount?: number;
}

// Simulate working hours check (06:00 - 18:00)
const getIsWorkingHours = (): boolean => {
  const hour = new Date().getHours();
  return hour >= 6 && hour < 18;
};

// --- MOCK DATA (Updated Language) ---

const SHIFT_DATA = [
  { name: 'Pagi (06-14)', aman: 420, pelanggaran: 12 },
  { name: 'Siang (14-22)', aman: 380, pelanggaran: 25 },
  { name: 'Malam (22-06)', aman: 150, pelanggaran: 5 },
];

const VIOLATION_TYPE_DATA = [
  { name: 'Tanpa Helm', value: 45, color: '#EF4444' },
  { name: 'Tanpa Rompi', value: 30, color: '#F97316' },
  { name: 'Sepatu Safety', value: 15, color: '#EAB308' },
  { name: 'Zona Terlarang', value: 10, color: '#6366F1' },
];

const EQUIPMENT_STATUS = [
  { id: "CAM-01", loc: "Gerbang Utama", status: "online", ping: "12ms", ai: "98%" },
  { id: "CAM-02", loc: "Perakitan A", status: "online", ping: "45ms", ai: "96%" },
  { id: "CAM-03", loc: "Perakitan B", status: "offline", ping: "-", ai: "-" },
  { id: "CAM-04", loc: "Gudang Utama", status: "online", ping: "22ms", ai: "99%" },
  { id: "CAM-05", loc: "Area Kimia", status: "online", ping: "18ms", ai: "97%" },
];

const REALTIME_LOGS = [
  { time: "10:42:05", cam: "CAM-02", msg: "AMAN: Helm Terdeteksi", type: "safe" },
  { time: "10:42:12", cam: "CAM-04", msg: "PELANGGARAN: Tidak Ada Rompi", type: "danger" },
  { time: "10:43:01", cam: "CAM-01", msg: "INFO: Personil di Zona Hijau", type: "info" },
  { time: "10:43:15", cam: "CAM-05", msg: "SISTEM: Model AI Diperbarui", type: "system" },
  { time: "10:43:42", cam: "CAM-02", msg: "AMAN: Sepatu Safety Terdeteksi", type: "safe" },
];

// --- COMPONENTS ---

const WidgetHeader = ({ title, icon: Icon }: { title: string, icon: any }) => (
  <div className="flex items-center gap-3 border-b border-slate-200 dark:border-slate-700/50 px-5 py-4 bg-slate-50/80 dark:bg-slate-800/40 backdrop-blur-sm rounded-t-xl">
    <div className="p-1.5 bg-slate-200 dark:bg-slate-700/50 rounded-lg">
      <Icon className="w-4 h-4 text-slate-600 dark:text-slate-300" />
    </div>
    <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-300">{title}</h3>
  </div>
);

const StatusIndicator = ({ status }: { status: string }) => (
  <div className="flex items-center gap-2">
    <div className={`h-2.5 w-2.5 rounded-full shadow-lg ${status === 'online' ? 'bg-emerald-500 shadow-emerald-500/50 animate-pulse' : 'bg-red-500 shadow-red-500/50'}`} />
    <span className={`text-xs font-bold tracking-wide ${status === 'online' ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-600 dark:text-red-400'}`}>
      {status === 'online' ? 'AKTIF' : 'MATI'}
    </span>
  </div>
);

// ============================================
// SECURITY STATUS WIDGET COMPONENT
// ============================================
const SecurityStatusWidget = ({ securityState }: { securityState: SecurityState }) => {
  const { mode, breachLocation, intruderCount } = securityState;

  // Police light animation for breach
  const policeAnimation = {
    animate: {
      backgroundColor: ["#dc2626", "#2563eb", "#dc2626"],
      boxShadow: [
        "0 0 30px rgba(220, 38, 38, 0.8)",
        "0 0 30px rgba(37, 99, 235, 0.8)",
        "0 0 30px rgba(220, 38, 38, 0.8)"
      ]
    },
    transition: {
      duration: 0.5,
      repeat: Infinity,
      ease: "linear"
    }
  };

  return (
    <div className={`relative overflow-hidden rounded-xl border shadow-lg transition-all duration-300 ${
      mode === "breach_detected" 
        ? "border-red-500 bg-red-950/50" 
        : mode === "night_sentry"
        ? "border-indigo-500/50 bg-indigo-950/30"
        : "border-emerald-500/50 bg-emerald-950/30"
    }`}>
      {/* Police Light Bar for Breach */}
      {mode === "breach_detected" && (
        <motion.div 
          className="absolute top-0 left-0 right-0 h-2"
          {...policeAnimation}
        />
      )}

      <div className="p-5">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            {mode === "breach_detected" ? (
              <motion.div
                animate={{ scale: [1, 1.2, 1], rotate: [0, 10, -10, 0] }}
                transition={{ duration: 0.5, repeat: Infinity }}
                className="p-2 bg-red-500 rounded-lg"
              >
                <Siren className="w-6 h-6 text-white" />
              </motion.div>
            ) : mode === "night_sentry" ? (
              <div className="p-2 bg-indigo-500/20 rounded-lg border border-indigo-500/30">
                <Moon className="w-6 h-6 text-indigo-400" />
              </div>
            ) : (
              <div className="p-2 bg-emerald-500/20 rounded-lg border border-emerald-500/30">
                <Shield className="w-6 h-6 text-emerald-400" />
              </div>
            )}
            <div>
              <p className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Site Security</p>
              <h3 className="text-sm font-bold text-white">Status Keamanan</h3>
            </div>
          </div>
        </div>

        {/* Status Display */}
        <AnimatePresence mode="wait">
          {mode === "breach_detected" && (
            <motion.div
              key="breach"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="space-y-3"
            >
              <motion.div 
                className="flex items-center gap-3 p-3 rounded-lg"
                animate={{ 
                  backgroundColor: ["rgba(220, 38, 38, 0.3)", "rgba(37, 99, 235, 0.3)", "rgba(220, 38, 38, 0.3)"]
                }}
                transition={{ duration: 0.5, repeat: Infinity }}
              >
                <span className="text-3xl">🚨</span>
                <div>
                  <p className="text-lg font-black text-white tracking-wide">BREACH DETECTED</p>
                  <p className="text-xs text-red-300">INTRUDER ALERT - SECURITY COMPROMISED</p>
                </div>
              </motion.div>
              
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="bg-red-900/30 p-2 rounded border border-red-500/20">
                  <p className="text-red-400">Lokasi</p>
                  <p className="text-white font-bold">{breachLocation || "Zone A"}</p>
                </div>
                <div className="bg-red-900/30 p-2 rounded border border-red-500/20">
                  <p className="text-red-400">Jumlah Intruder</p>
                  <p className="text-white font-bold">{intruderCount || 1} Terdeteksi</p>
                </div>
              </div>

              <button className="w-full py-2 bg-red-600 hover:bg-red-700 text-white font-bold rounded-lg text-sm transition-colors flex items-center justify-center gap-2">
                <Siren className="w-4 h-4" />
                PANGGIL SECURITY
              </button>
            </motion.div>
          )}

          {mode === "night_sentry" && (
            <motion.div
              key="night"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-3"
            >
              <div className="flex items-center gap-3 p-3 bg-indigo-900/30 rounded-lg border border-indigo-500/20">
                <span className="text-3xl">🌙</span>
                <div>
                  <p className="text-lg font-bold text-indigo-300">NIGHT SENTRY MODE</p>
                  <p className="text-xs text-indigo-400">Pengawasan diluar jam kerja aktif</p>
                </div>
              </div>
              
              <div className="flex items-center justify-between text-xs bg-indigo-900/20 p-2 rounded">
                <span className="text-indigo-400">Mode Aktif Sejak</span>
                <span className="text-white font-mono">18:00 WIB</span>
              </div>
              
              <div className="flex items-center gap-2 text-xs text-indigo-300">
                <div className="w-2 h-2 bg-indigo-500 rounded-full animate-pulse" />
                Semua pergerakan akan dicatat sebagai potensi ancaman
              </div>
            </motion.div>
          )}

          {mode === "operational" && (
            <motion.div
              key="operational"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-3"
            >
              <div className="flex items-center gap-3 p-3 bg-emerald-900/30 rounded-lg border border-emerald-500/20">
                <span className="text-3xl">🟢</span>
                <div>
                  <p className="text-lg font-bold text-emerald-300">OPERATIONAL MODE</p>
                  <p className="text-xs text-emerald-400">Jam kerja normal - Semua sistem aktif</p>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="bg-emerald-900/20 p-2 rounded">
                  <p className="text-emerald-500">Shift Saat Ini</p>
                  <p className="text-white font-bold">Pagi (06:00-14:00)</p>
                </div>
                <div className="bg-emerald-900/20 p-2 rounded">
                  <p className="text-emerald-500">Pekerja Aktif</p>
                  <p className="text-white font-bold">47 Orang</p>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

// --- MAIN DASHBOARD PAGE ---

export default function DashboardPage() {
  // ============================================
  // SECURITY STATE MANAGEMENT
  // ============================================
  const [securityState, setSecurityState] = useState<SecurityState>({
    mode: "operational",
    isNightMode: false,
    breachDetected: false,
  });

  // Simulate security mode based on time & random breach
  useEffect(() => {
    const updateSecurityMode = () => {
      const isWorkingHours = getIsWorkingHours();
      
      // Simulate random breach (5% chance every check)
      const randomBreach = Math.random() < 0.05;
      
      if (randomBreach) {
        setSecurityState({
          mode: "breach_detected",
          isNightMode: !isWorkingHours,
          breachDetected: true,
          lastBreachTime: new Date().toLocaleTimeString('id-ID'),
          breachLocation: ["Gudang A", "Gerbang Belakang", "Area Parkir", "Zona Kimia"][Math.floor(Math.random() * 4)],
          intruderCount: Math.floor(Math.random() * 3) + 1,
        });
        
        // Auto-clear breach after 30 seconds for demo
        setTimeout(() => {
          setSecurityState(prev => ({
            ...prev,
            mode: isWorkingHours ? "operational" : "night_sentry",
            breachDetected: false,
          }));
        }, 30000);
      } else {
        setSecurityState(prev => ({
          ...prev,
          mode: isWorkingHours ? "operational" : "night_sentry",
          isNightMode: !isWorkingHours,
        }));
      }
    };

    updateSecurityMode();
    const interval = setInterval(updateSecurityMode, 60000); // Check every minute
    
    return () => clearInterval(interval);
  }, []);

  // Demo: Manual trigger breach (for testing)
  const triggerBreach = () => {
    setSecurityState({
      mode: "breach_detected",
      isNightMode: !getIsWorkingHours(),
      breachDetected: true,
      lastBreachTime: new Date().toLocaleTimeString('id-ID'),
      breachLocation: "Gudang Utama - Pintu Darurat",
      intruderCount: 2,
    });
  };
  return (
    <div className="flex h-full flex-col gap-6 overflow-hidden pb-8 text-slate-900 dark:text-slate-200">
      
      {/* TOP BAR: Security Status + Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        {/* Security Status Widget */}
        <div className="lg:col-span-2">
          <SecurityStatusWidget securityState={securityState} />
        </div>
        
        {/* Quick Stats */}
        <div className="bg-white dark:bg-slate-800/80 rounded-xl border border-slate-200 dark:border-slate-700/50 p-5 flex items-center gap-4">
          <div className="p-3 bg-emerald-100 dark:bg-emerald-500/20 rounded-xl">
            <Shield className="w-8 h-8 text-emerald-600 dark:text-emerald-400" />
          </div>
          <div>
            <p className="text-sm text-slate-500 dark:text-slate-400">Kepatuhan Hari Ini</p>
            <p className="text-2xl font-bold text-slate-900 dark:text-white">94.2%</p>
          </div>
        </div>
        
        {/* Demo Trigger Button */}
        <div className="bg-white dark:bg-slate-800/80 rounded-xl border border-slate-200 dark:border-slate-700/50 p-5 flex flex-col justify-center">
          <p className="text-xs text-slate-500 dark:text-slate-400 mb-2 uppercase tracking-wider">Demo Mode</p>
          <button 
            onClick={triggerBreach}
            className="w-full py-2 bg-red-600 hover:bg-red-700 text-white font-bold rounded-lg text-sm transition-colors flex items-center justify-center gap-2"
          >
            <Siren className="w-4 h-4" />
            Simulasi Breach
          </button>
        </div>
      </div>

      {/* BENTO GRID LAYOUT */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 lg:gap-8">
        
        {/* 1. CAMERA COVERAGE MAP (Main Visual - 2x2) */}
        <div className="lg:col-span-2 row-span-2 bg-white dark:bg-slate-800/80 backdrop-blur-md rounded-xl border border-slate-200 dark:border-slate-700/50 shadow-sm dark:shadow-xl overflow-hidden relative group min-h-[450px] flex flex-col">
          <WidgetHeader title="Peta Pantauan Langsung & Analisis Area" icon={Eye} />
          
          {/* Map Container */}
          <div className="relative flex-1 w-full bg-slate-100 dark:bg-slate-900/50 p-0">
             <FloorPlanMap />
             
             {/* Overlay Stats */}
             <div className="absolute bottom-4 left-4 right-4 flex gap-4 pointer-events-none">
                <div className="bg-white/90 dark:bg-slate-900/90 backdrop-blur border border-slate-200 dark:border-slate-700 px-4 py-2 rounded-lg shadow-lg flex items-center gap-3">
                    <div className="h-3 w-3 bg-emerald-500 rounded-full animate-pulse"></div>
                    <div>
                        <div className="text-[10px] uppercase text-slate-500 dark:text-slate-400 font-semibold">Kamera Aktif</div>
                        <div className="text-xl font-bold text-slate-900 dark:text-white">4/5</div>
                    </div>
                </div>
             </div>
          </div>
        </div>

        {/* 2. VIOLATION BREAKDOWN (1x1) */}
        <div className="col-span-1 bg-white dark:bg-slate-800/80 backdrop-blur-md rounded-xl border border-slate-200 dark:border-slate-700/50 shadow-sm dark:shadow-xl flex flex-col">
          <WidgetHeader title="Distribusi Pelanggaran" icon={AlertCircle} />
          <div className="flex-1 p-6 flex flex-col items-center justify-center relative">
            <div className="h-48 w-full">
               <ResponsiveContainer width="100%" height="100%">
                 <PieChart>
                   <Pie
                     data={VIOLATION_TYPE_DATA}
                     cx="50%"
                     cy="50%"
                     innerRadius={55}
                     outerRadius={75}
                     paddingAngle={5}
                     dataKey="value"
                   >
                     {VIOLATION_TYPE_DATA.map((entry, index) => (
                       <Cell key={`cell-${index}`} fill={entry.color} stroke="rgba(0,0,0,0.2)" strokeWidth={2} />
                     ))}
                   </Pie>
                   <Tooltip 
                      contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }} 
                      itemStyle={{ color: '#f1f5f9', fontWeight: 600 }}
                   />
                 </PieChart>
               </ResponsiveContainer>
               {/* Center Text */}
               <div className="absolute inset-0 flex items-center justify-center pointer-events-none mb-12">
                  <div className="text-center">
                      <span className="text-3xl font-bold text-slate-900 dark:text-white">100</span>
                      <span className="text-xs block text-slate-500 dark:text-slate-400 uppercase tracking-wider">Total</span>
                  </div>
               </div>
            </div>
            {/* Legend */}
            <div className="w-full space-y-3 mt-2">
               {VIOLATION_TYPE_DATA.map((item) => (
                 <div key={item.name} className="flex items-center justify-between text-sm group hover:bg-slate-50 dark:hover:bg-white/5 p-1.5 rounded transition-colors cursor-default">
                    <div className="flex items-center gap-3">
                       <div className="w-3 h-3 rounded-full ring-2 ring-opacity-20 ring-slate-200 dark:ring-white" style={{ backgroundColor: item.color }}></div>
                       <span className="text-slate-600 dark:text-slate-300 font-medium">{item.name}</span>
                    </div>
                    <span className="font-bold text-slate-700 dark:text-white bg-slate-100 dark:bg-slate-700/50 px-2 py-0.5 rounded text-xs">{item.value}%</span>
                 </div>
               ))}
            </div>
          </div>
        </div>

        {/* 3. REAL-TIME LOG (1x1 - Scrollable) */}
        <div className="col-span-1 bg-white dark:bg-slate-800/80 backdrop-blur-md rounded-xl border border-slate-200 dark:border-slate-700/50 shadow-sm dark:shadow-xl flex flex-col overflow-hidden h-[400px] lg:h-auto">
          <WidgetHeader title="Log Sistem Langsung" icon={Activity} />
          <div className="flex-1 overflow-y-auto p-0 custom-scrollbar bg-slate-50 dark:bg-slate-900/20">
            <div className="flex flex-col divide-y divide-slate-200 dark:divide-slate-700/50">
               {REALTIME_LOGS.map((log, i) => (
                 <div key={i} className="px-5 py-4 hover:bg-slate-100 dark:hover:bg-slate-700/40 transition-colors flex gap-4 items-start group">
                    <div className="text-[11px] font-mono text-slate-500 dark:text-slate-500 mt-1 min-w-[60px] group-hover:text-slate-700 dark:group-hover:text-slate-400 transition-colors">{log.time}</div>
                    <div className="flex-1">
                       <div className="flex flex-col gap-1">
                          <div className="flex items-center justify-between">
                              <span className="text-[10px] font-bold text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-500/10 px-2 py-0.5 rounded border border-blue-200 dark:border-blue-500/20 tracking-wide">{log.cam}</span>
                          </div>
                          <p className={`text-sm font-semibold ${
                            log.type === 'danger' ? 'text-red-600 dark:text-red-400 drop-shadow-sm' : 
                            log.type === 'safe' ? 'text-emerald-600 dark:text-emerald-400' : 
                            log.type === 'info' ? 'text-blue-600 dark:text-blue-300' : 'text-slate-700 dark:text-slate-300'
                          }`}>
                             {log.msg}
                          </p>
                       </div>
                    </div>
                 </div>
               ))}
               {/* Infinite scroll dummy */}
               {[...Array(3)].map((_, i) => (
                 <div key={`dummy-${i}`} className="px-5 py-4 opacity-30 flex gap-4 items-start grayscale">
                    <div className="text-[11px] font-mono text-slate-400 dark:text-slate-600 mt-1">10:41:xx</div>
                    <div className="text-sm text-slate-400 dark:text-slate-500 font-medium">Memeriksa status sistem...</div>
                 </div>
               ))}
            </div>
          </div>
        </div>

        {/* 4. EQUIPMENT STATUS (2x1) */}
        <div className="lg:col-span-2 bg-white dark:bg-slate-800/80 backdrop-blur-md rounded-xl border border-slate-200 dark:border-slate-700/50 shadow-sm dark:shadow-xl flex flex-col">
          <WidgetHeader title="Status Perangkat & Konektivitas" icon={Server} />
          <div className="p-0 overflow-x-auto">
             <table className="w-full text-left border-collapse">
               <thead>
                 <tr className="bg-slate-50 dark:bg-slate-900/50 text-xs uppercase tracking-wider text-slate-500 dark:text-slate-400 border-b border-slate-200 dark:border-slate-700/50">
                   <th className="px-6 py-4 font-semibold">ID Kamera</th>
                   <th className="px-6 py-4 font-semibold">Lokasi</th>
                   <th className="px-6 py-4 font-semibold">Status</th>
                   <th className="px-6 py-4 font-semibold">Latensi</th>
                   <th className="px-6 py-4 font-semibold">Akurasi AI</th>
                 </tr>
               </thead>
               <tbody className="text-sm text-slate-600 dark:text-slate-300 divide-y divide-slate-200 dark:divide-slate-700/30">
                 {EQUIPMENT_STATUS.map((eq, index) => (
                   <tr key={eq.id} className={`hover:bg-slate-50 dark:hover:bg-white/5 transition-colors ${index % 2 === 0 ? 'bg-transparent' : 'bg-slate-50/50 dark:bg-slate-800/30'}`}>
                     <td className="px-6 py-4 font-mono font-medium text-orange-600 dark:text-orange-400 flex items-center gap-2">
                        <Camera className="w-3 h-3 opacity-50" />
                        {eq.id}
                     </td>
                     <td className="px-6 py-4 text-slate-700 dark:text-slate-300 font-medium">{eq.loc}</td>
                     <td className="px-6 py-4"><StatusIndicator status={eq.status} /></td>
                     <td className="px-6 py-4 font-mono text-slate-500 dark:text-slate-400">{eq.ping}</td>
                     <td className="px-6 py-4">
                        {eq.status === 'online' ? (
                             <div className="flex items-center gap-3">
                                <div className="w-24 h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden shadow-inner">
                                    <div 
                                        className={`h-full rounded-full shadow-lg ${
                                            parseInt(eq.ai) > 90 ? 'bg-emerald-500' : 'bg-yellow-500'
                                        }`} 
                                        style={{ width: eq.ai }}
                                    ></div>
                                </div>
                                <span className="font-bold text-slate-700 dark:text-white">{eq.ai}</span>
                             </div>
                        ) : (
                            <span className="text-slate-400 dark:text-slate-600 text-xs italic">Tidak Tersedia</span>
                        )}
                     </td>
                   </tr>
                 ))}
               </tbody>
             </table>
          </div>
        </div>

        {/* 5. SHIFT PERFORMANCE (1x1) */}
        <div className="col-span-1 bg-white dark:bg-slate-800/80 backdrop-blur-md rounded-xl border border-slate-200 dark:border-slate-700/50 shadow-sm dark:shadow-xl flex flex-col">
          <WidgetHeader title="Analisis Performa Shift" icon={Clock} />
          <div className="flex-1 p-6 min-h-[250px]">
            <ResponsiveContainer width="100%" height="100%">
               <BarChart data={SHIFT_DATA} layout="vertical" barSize={24} barGap={4}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#94a3b8" horizontal={false} opacity={0.2} />
                  <XAxis type="number" stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
                  <YAxis dataKey="name" type="category" stroke="#64748b" fontSize={12} width={100} tickLine={false} axisLine={false} fontWeight={500} />
                  <Tooltip 
                     contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                     cursor={{ fill: '#334155', opacity: 0.1 }}
                  />
                  <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '20px' }} iconType="circle" />
                  <Bar dataKey="aman" name="Aman (Compliant)" stackId="a" fill="#10B981" radius={[0, 0, 0, 0]} />
                  <Bar dataKey="pelanggaran" name="Pelanggaran" stackId="a" fill="#EF4444" radius={[0, 4, 4, 0]} />
               </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>
    </div>
  );
}
