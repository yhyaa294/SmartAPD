"use client";

import { useState } from "react";
import { Inter } from 'next/font/google';
import Sidebar from '@/components/Sidebar';
import Topbar from '@/components/dashboard/Topbar';
import { Menu } from "lucide-react";

const inter = Inter({ subsets: ['latin'] });

interface DashboardLayoutProps {
  children: React.ReactNode;
}

import { ThemeProvider } from "@/components/providers/ThemeProvider";

// ... imports ...

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const [isSidebarOpen, setSidebarOpen] = useState(false);
  const [isSidebarCollapsed, setSidebarCollapsed] = useState(false);

  return (
    <ThemeProvider attribute="class" defaultTheme="dark" enableSystem={false}>
      <div className={`${inter.className} flex min-h-screen bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-100 transition-colors duration-300`}>
        
        {/* Mobile Menu Button - Only visible on LG screens and below */}
        <button
          onClick={() => setSidebarOpen(true)}
          className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-600 dark:text-white shadow-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          aria-label="Open Menu"
        >
          <Menu className="w-6 h-6" />
        </button>

        {/* Sidebar with Mobile Logic & Collapsible State */}
        <Sidebar 
          isOpen={isSidebarOpen} 
          onClose={() => setSidebarOpen(false)}
          isCollapsed={isSidebarCollapsed}
          toggleCollapse={() => setSidebarCollapsed(!isSidebarCollapsed)}
        />

        {/* Main Content Wrapper */}
        <div 
          className={`flex flex-1 flex-col w-full transition-all duration-300 ${
            isSidebarCollapsed ? "lg:pl-20" : "lg:pl-64"
          }`}
        >
          <Topbar />
          
          <main className="flex-1 p-4 lg:p-6 pt-16 lg:pt-6">
            {children}
          </main>
        </div>
      </div>
    </ThemeProvider>
  );
}
