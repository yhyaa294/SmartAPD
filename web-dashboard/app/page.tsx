"use client";

import { useState, useEffect } from "react";
import Image from "next/image";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import { 
  ArrowRight, 
  ShieldCheck, 
  Play, 
  Phone, 
  Menu, 
  X, 
  Scan,
  AlertTriangle,
  Smartphone,
  Map as MapIcon,
  Instagram,
  Eye,
  CheckCircle2
} from "lucide-react";

// Array Gambar Pekerja
const workerImages = [
  "/images/orang landing page 1.png",
  "/images/orang landing page 2.png",
  "/images/orang landing page 3.png",
  "/images/orang landing page 4.png",
];

export default function LandingPage() {
  const [currentImage, setCurrentImage] = useState(0);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // Carousel Logic
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentImage((prev) => (prev + 1) % workerImages.length);
    }, 5000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-white overflow-x-hidden font-sans">
      
      {/* ========== NAVBAR ========== */}
      <nav className="fixed top-0 w-full z-50 bg-slate-950/80 backdrop-blur-md border-b border-white/10">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="relative w-10 h-10 overflow-hidden rounded-full border border-orange-500/50">
              <Image src="/images/logo-smartapd.jpg" alt="Logo" fill className="object-cover" />
            </div>
            <span className="text-xl font-bold tracking-wider">
              SMART<span className="text-orange-500">APD</span>
            </span>
          </div>

          {/* Desktop Menu */}
          <div className="hidden md:flex gap-8 text-sm font-medium text-slate-300">
            <a href="#fitur" className="hover:text-orange-500 transition">FITUR</a>
            <a href="#cara-kerja" className="hover:text-orange-500 transition">CARA KERJA</a>
            <a href="#kontak" className="hover:text-orange-500 transition">KONTAK</a>
          </div>

          {/* Login Button */}
          <div className="hidden md:block">
            <Link href="/login">
              <button className="px-6 py-2.5 bg-orange-600 hover:bg-orange-500 text-white font-bold rounded-lg transition-all shadow-[0_0_15px_rgba(249,115,22,0.4)]">
                LOGIN
              </button>
            </Link>
          </div>

          {/* Mobile Menu Toggle */}
          <button 
            className="md:hidden text-white" 
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          >
            {isMobileMenuOpen ? <X /> : <Menu />}
          </button>
        </div>

        {/* Mobile Menu Dropdown */}
        {isMobileMenuOpen && (
          <div className="md:hidden bg-slate-900 border-b border-slate-800 p-4 space-y-4">
            <Link 
              href="/login" 
              className="block w-full text-center py-3 bg-orange-600 rounded-lg font-bold"
            >
              LOGIN DASHBOARD
            </Link>
          </div>
        )}
      </nav>

      {/* ========== HERO SECTION ========== */}
      <section className="relative pt-32 pb-20 px-6 min-h-screen flex items-center">
        {/* Background Gradient */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-emerald-900/40 via-slate-950 to-slate-950 -z-20" />

        <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-12 items-center w-full">
          
          {/* LEFT: Text Content */}
          <motion.div 
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
            className="space-y-8 z-10 text-center lg:text-left"
          >
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-orange-500/30 bg-orange-500/10 text-orange-400 text-xs font-bold tracking-widest uppercase">
              <span className="w-2 h-2 rounded-full bg-orange-500 animate-pulse" />
              AI-Powered Safety System
            </div>

            <h1 className="text-5xl lg:text-7xl font-black leading-tight">
              AWASI <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-yellow-200">
                PEKERJAMU
              </span>{" "}
              <br />
              SECARA REAL-TIME
            </h1>

            <p className="text-slate-400 text-lg lg:text-xl max-w-lg mx-auto lg:mx-0 leading-relaxed">
              Platform pengawasan K3 berbasis AI untuk mendeteksi pelanggaran APD secara instan. 
              Tingkatkan keselamatan kerja dengan{" "}
              <span className="text-emerald-400 font-semibold">Computer Vision</span> tingkat industri.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
              <Link 
                href="/login" 
                className="px-8 py-4 bg-orange-600 hover:bg-orange-500 text-white font-bold rounded-xl flex items-center justify-center gap-2 transition-all shadow-lg hover:shadow-orange-500/25"
              >
                Pakai Sekarang <ArrowRight size={20} />
              </Link>
              <Link 
                href="https://wa.me/6282330919114" 
                target="_blank" 
                className="px-8 py-4 border border-slate-700 hover:border-slate-500 hover:bg-slate-800 text-white font-semibold rounded-xl flex items-center justify-center gap-2 transition-all"
              >
                <Phone size={20} /> Hubungi Sales
              </Link>
            </div>

            {/* Stats */}
            <div className="pt-8 flex gap-12 border-t border-white/5 justify-center lg:justify-start">
              <div>
                <h3 className="text-3xl font-bold text-white">99.8%</h3>
                <p className="text-xs text-slate-500 uppercase tracking-wider">Akurasi Deteksi</p>
              </div>
              <div>
                <h3 className="text-3xl font-bold text-white">&lt; 2s</h3>
                <p className="text-xs text-slate-500 uppercase tracking-wider">Respon Waktu</p>
              </div>
              <div>
                <h3 className="text-3xl font-bold text-white">24/7</h3>
                <p className="text-xs text-slate-500 uppercase tracking-wider">Uptime</p>
              </div>
            </div>
          </motion.div>

          {/* RIGHT: Visual Carousel */}
          <div className="relative h-[500px] lg:h-[700px] w-full flex items-center justify-center">
            
            {/* Hologram Ring Background */}
            <div className="absolute inset-0 flex items-center justify-center -z-10">
              <motion.div 
                animate={{ rotate: 360 }}
                transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                className="relative w-[400px] h-[400px] lg:w-[700px] lg:h-[700px] opacity-50"
              >
                <Image 
                  src="/images/background orang landing page.png" 
                  alt="Hologram" 
                  fill 
                  className="object-contain" 
                />
              </motion.div>
            </div>

            {/* Worker Carousel */}
            <div className="relative w-full h-full">
              <AnimatePresence mode="wait">
                <motion.div
                  key={currentImage}
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.8 }}
                  className="absolute inset-0"
                >
                  <Image 
                    src={workerImages[currentImage]} 
                    alt="Worker" 
                    fill 
                    className="object-contain object-bottom drop-shadow-[0_0_50px_rgba(0,0,0,0.8)]"
                    priority
                  />
                </motion.div>
              </AnimatePresence>

              {/* Carousel Dots */}
              <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-2 z-20">
                {workerImages.map((_, i) => (
                  <button
                    key={i}
                    onClick={() => setCurrentImage(i)}
                    className={`h-2 rounded-full transition-all ${
                      i === currentImage 
                        ? "bg-orange-500 w-8" 
                        : "bg-white/30 w-2 hover:bg-white/50"
                    }`}
                  />
                ))}
              </div>
            </div>

            {/* Floating Glass Cards */}
            <motion.div 
              animate={{ y: [0, -10, 0] }} 
              transition={{ repeat: Infinity, duration: 4, ease: "easeInOut" }}
              className="absolute top-1/3 right-0 lg:-right-10 bg-slate-900/60 backdrop-blur-xl border border-emerald-500/30 p-4 rounded-xl shadow-2xl flex items-center gap-3 z-20"
            >
              <div className="p-2 bg-emerald-500/20 rounded-lg">
                <ShieldCheck className="text-emerald-400" size={24} />
              </div>
              <div>
                <p className="text-xs text-emerald-400 font-bold uppercase">PPE DETECTED</p>
                <p className="text-white font-bold">Safe</p>
              </div>
            </motion.div>

            <motion.div 
              animate={{ y: [0, 10, 0] }} 
              transition={{ repeat: Infinity, duration: 5, ease: "easeInOut", delay: 1 }}
              className="absolute bottom-1/4 left-0 lg:-left-10 bg-slate-900/60 backdrop-blur-xl border border-orange-500/30 p-4 rounded-xl shadow-2xl flex items-center gap-3 z-20"
            >
              <div className="p-2 bg-orange-500/20 rounded-lg">
                <Play className="text-orange-400" size={24} />
              </div>
              <div>
                <p className="text-xs text-orange-400 font-bold uppercase">LIVE MONITOR</p>
                <p className="text-white font-bold">Active</p>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* ========== SECTION: SMART SURVEILLANCE ========== */}
      <section className="py-24 bg-slate-900 border-y border-white/5">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            {/* Image */}
            <motion.div 
              initial={{ opacity: 0, x: -50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="relative rounded-2xl overflow-hidden border border-slate-700 shadow-2xl"
            >
              <Image
                src="/images/cctv-cam.png"
                alt="Smart Surveillance CCTV"
                width={800}
                height={600}
                className="w-full h-auto"
              />
              <div className="absolute top-4 right-4 flex items-center gap-2 px-3 py-1.5 rounded-full bg-black/60 backdrop-blur">
                <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
                <span className="text-xs font-bold text-emerald-400 uppercase">RTSP Connected</span>
              </div>
            </motion.div>

            {/* Text */}
            <motion.div 
              initial={{ opacity: 0, x: 50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="space-y-6"
            >
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-bold uppercase">
                <Scan className="w-4 h-4" />
                Hardware Compatibility
              </div>

              <h2 className="text-3xl lg:text-5xl font-bold text-white">
                Ubah CCTV Lama Jadi{" "}
                <span className="text-emerald-400">Mata Cerdas</span>
              </h2>

              <p className="text-lg text-slate-400">
                Tidak perlu ganti kamera mahal. SmartAPD terintegrasi mulus dengan infrastruktur
                CCTV IP Camera (RTSP) yang sudah ada di pabrik Anda.
              </p>

              <ul className="space-y-3">
                {[
                  "Support 99% IP Camera (RTSP/ONVIF)",
                  "Low Latency Streaming (< 200ms)",
                  "Night Vision Enhanced AI Detection",
                ].map((item, i) => (
                  <li key={i} className="flex items-center gap-3 text-slate-300">
                    <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0" />
                    {item}
                  </li>
                ))}
              </ul>
            </motion.div>
          </div>
        </div>
      </section>

      {/* ========== SECTION: WORKFLOW ========== */}
      <section id="cara-kerja" className="py-24 bg-slate-950">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-5xl font-bold text-white mb-4">
              BAGAIMANA <span className="text-orange-500">SMARTAPD</span> BEKERJA
            </h2>
            <div className="h-1 w-24 bg-orange-500 mx-auto rounded-full" />
          </div>

          <motion.div 
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="relative max-w-5xl mx-auto rounded-2xl overflow-hidden border border-slate-800 shadow-2xl"
          >
            <Image
              src="/images/alur kerja.png"
              alt="Alur Kerja SmartAPD"
              width={1200}
              height={675}
              className="w-full h-auto"
            />
          </motion.div>
        </div>
      </section>

      {/* ========== SECTION: FITUR DETEKSI ========== */}
      <section id="fitur" className="py-24 bg-slate-900 border-y border-white/5">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            {/* Text */}
            <motion.div 
              initial={{ opacity: 0, x: -50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="space-y-6"
            >
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-400 text-xs font-bold uppercase">
                <Eye className="w-4 h-4" />
                Computer Vision
              </div>

              <h2 className="text-3xl lg:text-5xl font-bold text-white">
                DETEKSI PELANGGARAN{" "}
                <span className="text-blue-400">PRESISI TINGGI</span>
              </h2>

              <p className="text-lg text-slate-400">
                Menggunakan model <span className="text-white font-semibold">YOLOv8</span> yang
                telah dilatih pada ribuan dataset industri. Mendeteksi{" "}
                <span className="text-orange-500 font-bold">Helm, Rompi Safety, dan Sepatu Safety</span>{" "}
                dalam hitungan milidetik.
              </p>

              <ul className="space-y-2 text-slate-300">
                {["Latency < 50ms", "Multi-object Detection", "Low Light Performance"].map((item, i) => (
                  <li key={i} className="flex items-center gap-3">
                    <div className="h-2 w-2 rounded-full bg-blue-500" />
                    {item}
                  </li>
                ))}
              </ul>
            </motion.div>

            {/* Image */}
            <motion.div 
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="relative rounded-2xl overflow-hidden border border-blue-500/20 shadow-lg"
            >
              <Image
                src="/images/tampilan scan.png"
                alt="Tampilan Scan AI"
                width={800}
                height={600}
                className="w-full h-auto"
              />
            </motion.div>
          </div>
        </div>
      </section>

      {/* ========== SECTION: NOTIFIKASI ========== */}
      <section className="py-24 bg-slate-950">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            {/* Image */}
            <motion.div 
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="relative mx-auto max-w-sm order-2 lg:order-1"
            >
              <div className="rounded-[2rem] border-4 border-slate-800 bg-slate-900 overflow-hidden shadow-2xl">
                <Image
                  src="/images/gambar notif bahaya.png"
                  alt="Notifikasi Bahaya"
                  width={400}
                  height={800}
                  className="w-full h-auto"
                />
              </div>
            </motion.div>

            {/* Text */}
            <motion.div 
              initial={{ opacity: 0, x: 50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="space-y-6 order-1 lg:order-2"
            >
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-red-500/10 border border-red-500/30 text-red-400 text-xs font-bold uppercase">
                <AlertTriangle className="w-4 h-4" />
                Real-time Alert
              </div>

              <h2 className="text-3xl lg:text-5xl font-bold text-white">
                NOTIFIKASI BAHAYA{" "}
                <span className="text-red-500">REAL-TIME</span>
              </h2>

              <p className="text-lg text-slate-400">
                Jangan biarkan pelanggaran berlalu begitu saja. Sistem mengirimkan alert langsung
                ke <span className="text-white font-bold">WhatsApp & Dashboard Supervisor</span>{" "}
                detik itu juga saat pelanggaran terjadi.
              </p>

              <div className="flex items-center gap-4 p-4 rounded-xl bg-red-500/10 border border-red-500/20">
                <Smartphone className="w-8 h-8 text-red-500" />
                <div>
                  <div className="font-bold text-white">Instant Delivery</div>
                  <div className="text-sm text-slate-400">Rata-rata waktu pengiriman &lt; 2 detik</div>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* ========== SECTION: PEMETAAN ========== */}
      <section className="py-24 bg-slate-900 border-y border-white/5">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            {/* Text */}
            <motion.div 
              initial={{ opacity: 0, x: -50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="space-y-6"
            >
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-xs font-bold uppercase">
                <MapIcon className="w-4 h-4" />
                Spatial Analytics
              </div>

              <h2 className="text-3xl lg:text-5xl font-bold text-white">
                PEMETAAN ZONA{" "}
                <span className="text-indigo-400">RISIKO OTOMATIS</span>
              </h2>

              <p className="text-lg text-slate-400">
                Ubah data kamera CCTV menjadi{" "}
                <span className="text-indigo-400 font-bold">wawasan spasial</span>. Identifikasi
                area &quot;Red Zone&quot; di pabrik Anda berdasarkan frekuensi pelanggaran historis.
              </p>
            </motion.div>

            {/* Image */}
            <motion.div 
              initial={{ opacity: 0, scale: 0.95 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="relative rounded-2xl overflow-hidden border border-indigo-500/30 shadow-lg"
            >
              <Image
                src="/images/gambar pemetaan cctb.png"
                alt="Pemetaan Risiko CCTV"
                width={800}
                height={500}
                className="w-full h-auto"
              />
            </motion.div>
          </div>
        </div>
      </section>

      {/* ========== SECTION: COMMAND CENTER ========== */}
      <section className="py-24 bg-slate-950">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-5xl font-bold text-white mb-4">
              PUSAT KENDALI K3 ANDA
            </h2>
            <p className="text-lg text-slate-400 max-w-2xl mx-auto">
              Satu dashboard terintegrasi untuk memantau semua kamera, notifikasi, dan analitik
              kinerja keselamatan kerja.
            </p>
          </div>

          <motion.div 
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="relative max-w-6xl mx-auto rounded-xl border border-slate-700 overflow-hidden shadow-2xl"
          >
            <div className="bg-slate-800 h-8 flex items-center px-4 gap-2 border-b border-slate-700">
              <div className="w-3 h-3 rounded-full bg-red-500" />
              <div className="w-3 h-3 rounded-full bg-yellow-500" />
              <div className="w-3 h-3 rounded-full bg-green-500" />
            </div>
            <Image
              src="/images/gambar dashboard pemantauan.png"
              alt="Command Center Dashboard"
              width={1200}
              height={800}
              className="w-full h-auto"
            />
          </motion.div>
        </div>
      </section>

      {/* ========== SECTION: CTA ========== */}
      <section id="kontak" className="py-24 bg-slate-900 border-t border-white/5">
        <div className="max-w-7xl mx-auto px-6">
          {/* Tech Stack */}
          <p className="text-center text-sm font-bold text-slate-600 uppercase tracking-widest mb-8">
            Powered By Modern Technology
          </p>
          <div className="flex flex-wrap justify-center items-center gap-8 mb-20 opacity-50">
            <div className="relative h-12 w-12">
              <Image src="/images/gambar py.png" alt="Python" fill className="object-contain" />
            </div>
            <span className="text-xl font-bold text-slate-500">React</span>
            <span className="text-xl font-bold text-slate-500">TensorFlow</span>
            <span className="text-xl font-bold text-slate-500">FastAPI</span>
            <span className="text-xl font-bold text-slate-500">OpenCV</span>
          </div>

          {/* CTA Box */}
          <motion.div 
            whileHover={{ y: -5 }}
            className="max-w-3xl mx-auto bg-slate-800 rounded-2xl p-10 text-center border border-slate-700 shadow-2xl"
          >
            <div className="h-1.5 w-full bg-gradient-to-r from-orange-500 to-yellow-500 rounded-full mb-8" />

            <h2 className="text-3xl lg:text-4xl font-bold text-white mb-4">
              Siap Meningkatkan Standar Keselamatan?
            </h2>
            <p className="text-lg text-slate-400 mb-8">
              Bergabung dengan perusahaan industri terkemuka yang telah beralih ke pengawasan K3
              berbasis AI.
            </p>

            <Link
              href="https://wa.me/6282330919114"
              target="_blank"
              className="inline-flex items-center justify-center gap-3 bg-orange-500 hover:bg-orange-600 text-white font-bold px-10 py-4 rounded-xl transition-all shadow-lg"
            >
              Coba Sekarang di Proyekmu
              <ArrowRight className="w-5 h-5" />
            </Link>
          </motion.div>
        </div>
      </section>

      {/* ========== FOOTER ========== */}
      <footer className="py-8 bg-slate-950 border-t border-slate-900">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="text-slate-500 text-sm">
            &copy; 2025 SmartAPD. All rights reserved.
          </div>
          <Link
            href="https://instagram.com/syarfddn_yhya"
            target="_blank"
            className="flex items-center gap-2 text-slate-400 hover:text-orange-500 transition-colors"
          >
            <Instagram className="w-5 h-5" />
            <span className="text-sm font-medium">@syarfddn_yhya</span>
          </Link>
        </div>
      </footer>
    </div>
  );
}
