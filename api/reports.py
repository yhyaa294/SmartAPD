"""
Auto Reports PDF/Email Generator
Generates weekly/monthly safety reports and sends via email
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any
import os

# HTML Template for PDF Report
REPORT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Inter', 'Segoe UI', sans-serif; 
            background: #f8fafc;
            padding: 40px 20px;
        }}
        .container {{ 
            max-width: 800px; 
            margin: 0 auto; 
            background: white;
            border-radius: 16px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{ 
            background: linear-gradient(135deg, #FF7A00 0%, #34C759 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{ font-size: 32px; margin-bottom: 8px; }}
        .header p {{ font-size: 16px; opacity: 0.9; }}
        .content {{ padding: 40px; }}
        .section {{ margin-bottom: 32px; }}
        .section h2 {{ 
            font-size: 20px; 
            color: #1e293b; 
            margin-bottom: 16px;
            border-bottom: 2px solid #FF7A00;
            padding-bottom: 8px;
        }}
        .kpi-grid {{ 
            display: grid; 
            grid-template-columns: repeat(2, 1fr); 
            gap: 16px;
            margin-bottom: 24px;
        }}
        .kpi-card {{ 
            background: #f1f5f9; 
            padding: 20px; 
            border-radius: 12px;
            border-left: 4px solid #FF7A00;
        }}
        .kpi-card h3 {{ font-size: 32px; color: #FF7A00; margin-bottom: 4px; }}
        .kpi-card p {{ font-size: 14px; color: #64748b; }}
        .violation-table {{ 
            width: 100%; 
            border-collapse: collapse;
            margin-top: 16px;
        }}
        .violation-table th {{ 
            background: #f1f5f9; 
            padding: 12px; 
            text-align: left;
            font-size: 14px;
            color: #475569;
        }}
        .violation-table td {{ 
            padding: 12px; 
            border-bottom: 1px solid #e2e8f0;
            font-size: 14px;
        }}
        .badge {{ 
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        }}
        .badge-high {{ background: #fee2e2; color: #dc2626; }}
        .badge-medium {{ background: #fed7aa; color: #ea580c; }}
        .badge-low {{ background: #d1fae5; color: #059669; }}
        .footer {{ 
            background: #f1f5f9; 
            padding: 24px; 
            text-align: center;
            color: #64748b;
            font-size: 12px;
        }}
        .footer strong {{ color: #1e293b; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>SmartAPD™ Safety Report</h1>
            <p>{report_title}</p>
            <p style="font-size: 14px; margin-top: 8px;">Periode: {period}</p>
        </div>
        
        <div class="content">
            <!-- KPI Section -->
            <div class="section">
                <h2>📊 Ringkasan Eksekutif</h2>
                <div class="kpi-grid">
                    <div class="kpi-card">
                        <h3>{total_detections}</h3>
                        <p>Total Deteksi</p>
                    </div>
                    <div class="kpi-card">
                        <h3>{total_violations}</h3>
                        <p>Total Pelanggaran</p>
                    </div>
                    <div class="kpi-card">
                        <h3>{compliance_rate}%</h3>
                        <p>Tingkat Kepatuhan</p>
                    </div>
                    <div class="kpi-card">
                        <h3>{compliant_workers}</h3>
                        <p>Pekerja Patuh</p>
                    </div>
                </div>
            </div>
            
            <!-- Top Violations -->
            <div class="section">
                <h2>⚠️ Jenis Pelanggaran Teratas</h2>
                <table class="violation-table">
                    <thead>
                        <tr>
                            <th>Jenis Pelanggaran</th>
                            <th>Jumlah</th>
                            <th>Persentase</th>
                            <th>Tingkat</th>
                        </tr>
                    </thead>
                    <tbody>
                        {violation_rows}
                    </tbody>
                </table>
            </div>
            
            <!-- Recommendations -->
            <div class="section">
                <h2>💡 Rekomendasi</h2>
                <ul style="list-style: none; padding-left: 0;">
                    {recommendations}
                </ul>
            </div>
            
            <!-- Trend -->
            <div class="section">
                <h2>📈 Tren Mingguan</h2>
                <p style="color: #64748b; line-height: 1.6;">
                    {trend_summary}
                </p>
            </div>
        </div>
        
        <div class="footer">
            <strong>SmartAPD™</strong> — Aman Bekerja, Tenang Keluarga<br>
            Generated on {generated_at}<br>
            © 2025 SmartAPD. All rights reserved.
        </div>
    </div>
</body>
</html>
"""


class ReportGenerator:
    def __init__(self, db_path: str = "logs/detections.db"):
        self.db_path = db_path
    
    def generate_weekly_report(self) -> str:
        """Generate weekly safety report HTML"""
        # Calculate period
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        period = f"{start_date.strftime('%d %b')} - {end_date.strftime('%d %b %Y')}"
        
        # Get data (mock for now, will query DB later)
        data = self._get_report_data(start_date, end_date)
        
        # Build violation rows
        violation_rows = ""
        for v in data['top_violations']:
            severity_class = f"badge-{v['severity']}"
            violation_rows += f"""
                <tr>
                    <td>{v['type']}</td>
                    <td><strong>{v['count']}</strong></td>
                    <td>{v['percentage']}%</td>
                    <td><span class="badge {severity_class}">{v['severity'].upper()}</span></td>
                </tr>
            """
        
        # Build recommendations
        recommendations = ""
        for rec in data['recommendations']:
            recommendations += f"<li style='margin-bottom: 12px; padding-left: 24px; position: relative;'>"
            recommendations += f"<span style='position: absolute; left: 0;'>✓</span> {rec}</li>"
        
        # Fill template
        html = REPORT_TEMPLATE.format(
            report_title="Laporan Keselamatan Mingguan",
            period=period,
            total_detections=data['total_detections'],
            total_violations=data['total_violations'],
            compliance_rate=data['compliance_rate'],
            compliant_workers=data['compliant_workers'],
            violation_rows=violation_rows,
            recommendations=recommendations,
            trend_summary=data['trend_summary'],
            generated_at=datetime.now().strftime('%d %B %Y, %H:%M WIB')
        )
        
        return html
    
    def _get_report_data(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get report data from database (mock for now)"""
        # TODO: Query actual database
        return {
            'total_detections': 245,
            'total_violations': 42,
            'compliance_rate': 82.9,
            'compliant_workers': 203,
            'top_violations': [
                {'type': 'Tidak Pakai Helm', 'count': 18, 'percentage': 42.9, 'severity': 'high'},
                {'type': 'Tidak Pakai Rompi', 'count': 12, 'percentage': 28.6, 'severity': 'medium'},
                {'type': 'Tidak Pakai Sarung Tangan', 'count': 8, 'percentage': 19.0, 'severity': 'medium'},
                {'type': 'Tidak Pakai Kacamata', 'count': 4, 'percentage': 9.5, 'severity': 'low'},
            ],
            'recommendations': [
                "Tingkatkan pengawasan di area Workshop A (18 pelanggaran helm)",
                "Adakan briefing keselamatan setiap pagi shift",
                "Pasang signage peringatan APD di pintu masuk area kerja",
                "Berikan reward untuk tim dengan compliance rate >95%"
            ],
            'trend_summary': "Tingkat kepatuhan meningkat 5.2% dibanding minggu lalu. "
                           "Pelanggaran helm menurun 23%, namun pelanggaran rompi masih tinggi di shift malam. "
                           "Rekomendasi: fokus monitoring shift 19:00-23:00."
        }
    
    def save_pdf(self, html: str, filename: str) -> str:
        """Save HTML as PDF (requires wkhtmltopdf or pdfkit)"""
        # TODO: Implement PDF conversion
        # For now, save as HTML
        output_path = f"logs/reports/{filename}.html"
        os.makedirs("logs/reports", exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return output_path
    
    def send_email(self, to_email: str, subject: str, html_body: str, pdf_path: str = None):
        """Send email with report (requires SMTP config)"""
        # TODO: Implement email sending
        print(f"📧 Email would be sent to: {to_email}")
        print(f"   Subject: {subject}")
        print(f"   PDF: {pdf_path}")
        pass


# Example usage
if __name__ == "__main__":
    generator = ReportGenerator()
    html = generator.generate_weekly_report()
    pdf_path = generator.save_pdf(html, f"weekly_report_{datetime.now().strftime('%Y%m%d')}")
    print(f"✅ Report generated: {pdf_path}")
