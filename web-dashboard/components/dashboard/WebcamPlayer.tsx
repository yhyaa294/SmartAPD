"use client";

import { useEffect, useRef, useState } from "react";
import { Camera, AlertCircle, Maximize2, Radio, RefreshCw } from "lucide-react";

export default function WebcamPlayer() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentTime, setCurrentTime] = useState("");

  // Clock Update
  useEffect(() => {
    const interval = setInterval(() => {
      const now = new Date();
      setCurrentTime(now.toLocaleTimeString("en-US", { hour12: false }));
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  // Main Camera Logic
  useEffect(() => {
    let stream: MediaStream | null = null;

    const startCamera = async () => {
      try {
        console.log("Mencoba akses kamera...");
        
        stream = await navigator.mediaDevices.getUserMedia({ 
          video: { width: { ideal: 1280 }, height: { ideal: 720 } } 
        });

        console.log("Kamera berhasil diakses!");

        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          
          // --- BRUTE FORCE FIX ---
          // 1. Langsung matikan loading, jangan tunggu apa-apa
          setIsLoading(false); 
          
          // 2. Play video
          videoRef.current.play().catch(e => console.error("Play error:", e));
        }
      } catch (err) {
        console.error("Camera Error:", err);
        setError("Gagal akses kamera. Cek izin browser.");
        setIsLoading(false); 
      }
    };

    startCamera();

    // --- SAFETY NET ---
    // Paksa loading hilang setelah 3 detik apapun yang terjadi
    const timeout = setTimeout(() => {
        setIsLoading(false);
    }, 3000);

    return () => {
      clearTimeout(timeout);
      if (stream) {
        stream.getTracks().forEach((track) => track.stop());
      }
    };
  }, []);

  return (
    <div className="relative w-full h-full min-h-[400px] bg-black rounded-2xl overflow-hidden border border-slate-800 shadow-2xl">
      
      {/* VIDEO LAYER - Z-INDEX 10 */}
      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted
        className="absolute inset-0 w-full h-full object-cover transform scale-x-[-1] z-10"
      />

      {/* LOADING LAYER - Z-INDEX 50 */}
      {/* Hanya muncul jika isLoading TRUE */}
      {isLoading && (
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-slate-950/90 z-50">
          <div className="w-12 h-12 border-4 border-orange-500 border-t-transparent rounded-full animate-spin mb-4"></div>
          <p className="text-slate-400 text-sm">Menghubungkan...</p>
          
          {/* TOMBOL DARURAT KALAU MACET */}
          <button 
            onClick={() => setIsLoading(false)}
            className="mt-4 text-xs text-red-400 underline hover:text-red-300"
          >
            Force Show Video (Klik jika macet)
          </button>
        </div>
      )}

      {/* ERROR LAYER */}
      {error && (
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-slate-900 z-50">
          <AlertCircle className="w-10 h-10 text-red-500 mb-2" />
          <p className="text-red-400 font-medium text-sm">{error}</p>
          <button onClick={() => window.location.reload()} className="mt-4 flex items-center gap-2 px-4 py-2 bg-slate-800 rounded hover:bg-slate-700 text-white text-xs">
            <RefreshCw size={14} /> Reload
          </button>
        </div>
      )}

      {/* UI OVERLAY - Z-INDEX 40 */}
      <div className="absolute inset-0 z-40 pointer-events-none flex flex-col justify-between p-4">
        <div className="flex justify-between items-start">
          <div className="flex items-center gap-3">
            <div className="bg-red-600/90 px-2 py-1 rounded shadow-lg flex items-center gap-2">
              <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
              <span className="text-[10px] font-bold text-white tracking-wider">LIVE</span>
            </div>
            <div className="bg-black/50 px-2 py-1 rounded text-xs text-slate-300 font-mono">CAM-01</div>
          </div>
          <div className="text-lg font-mono font-bold text-white drop-shadow-md">{currentTime}</div>
        </div>
      </div>
    </div>
  );
}
