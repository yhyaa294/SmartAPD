"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
import { 
  LayoutDashboard, 
  Cctv, 
  Map, 
  Bell, 
  Settings, 
  Menu,
  FileText
} from "lucide-react";
import { useState } from "react";

const menuItems = [
  {
    name: "Overview",
    href: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    name: "Live Monitoring",
    href: "/dashboard/monitoring",
    icon: Cctv,
  },
  {
    name: "Risk Map",
    href: "/dashboard/risk-map",
    icon: Map,
  },
  {
    name: "Reports",
    href: "/dashboard/reports",
    icon: FileText,
  },
  {
    name: "Settings",
    href: "/dashboard/settings",
    icon: Settings,
  },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [isExpanded, setIsExpanded] = useState(true);

  return (
    <aside
      className={`flex flex-col border-r border-slate-800 bg-slate-900 transition-all duration-300 ${
        isExpanded ? "w-60" : "w-16"
      } fixed left-0 top-0 h-full z-50`}
    >
      {/* Logo Section */}
      <div className="flex h-16 items-center justify-between px-4 border-b border-slate-800">
        <div className={`flex items-center gap-2 overflow-hidden ${!isExpanded && "hidden"}`}>
          <div className="h-8 w-8 rounded-lg overflow-hidden flex-shrink-0">
            <Image 
              src="/images/logo-smartapd.jpg" 
              alt="SmartAPD" 
              width={32} 
              height={32}
              className="object-cover"
            />
          </div>
          <span className="font-bold text-lg text-slate-100 tracking-tight">
            Smart<span className="text-orange-500">APD</span>
          </span>
        </div>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="rounded-lg p-1 text-slate-400 hover:bg-slate-800 hover:text-white transition-colors"
        >
          <Menu className="h-5 w-5" />
        </button>
      </div>

      {/* Navigation Items */}
      <nav className="flex-1 space-y-2 p-2 mt-4">
        {menuItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              href={item.href}
              title={!isExpanded ? item.name : ""}
              className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200 group relative ${
                isActive
                  ? "bg-orange-500/10 text-orange-500"
                  : "text-slate-400 hover:bg-slate-800 hover:text-slate-200"
              }`}
            >
              {/* Active Border Indicator */}
              {isActive && (
                <div className="absolute left-0 top-0 h-full w-1 rounded-r bg-orange-500" />
              )}

              <Icon
                className={`h-5 w-5 flex-shrink-0 transition-colors ${
                  isActive ? "text-orange-500" : "text-slate-400 group-hover:text-slate-200"
                }`}
              />
              
              <span
                className={`whitespace-nowrap transition-opacity duration-300 ${
                  isExpanded ? "opacity-100" : "opacity-0 hidden"
                }`}
              >
                {item.name}
              </span>
            </Link>
          );
        })}
      </nav>

      {/* Footer Section */}
      <div className="border-t border-slate-800 p-4">
        {isExpanded && (
          <div className="text-xs text-slate-500">
            <p>© 2025 SmartAPD</p>
            <p>v2.0.1 Command Center</p>
          </div>
        )}
      </div>
    </aside>
  );
}
