import os
import structlog
from typing import Optional, List, Dict, Any
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.graphics.shapes import Drawing, Polygon, String, Group, Rect

from app.mcp_servers.base import BaseMCPServer

logger = structlog.get_logger(__name__)

class PDFMCPServer(BaseMCPServer):
    name = "pdf-mcp"
    description = "Generates high-quality, professional PDF documents and incident summaries"

    def _create_shield_drawing(self) -> Drawing:
        """Create a shield logo drawing using ReportLab shapes."""
        d = Drawing(40, 40)
        # Draw a simple blue shield polygon
        # Coordinates for a shield shape
        shield = Polygon(
            points=[20, 2, 38, 12, 38, 26, 20, 38, 2, 26, 2, 12],
            fillColor=colors.HexColor("#1e1b4b"),
            strokeColor=colors.HexColor("#6366f1"),
            strokeWidth=2
        )
        d.add(shield)
        return d

    async def generate_incident_report(self, incident: dict, mission: Optional[dict] = None) -> bytes:
        """Generate a professional PDF incident response report."""
        async def _run():
            from io import BytesIO
            buffer = BytesIO()
            
            # Setup document
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=40,
                leftMargin=40,
                topMargin=40,
                bottomMargin=40
            )
            
            story = []
            styles = getSampleStyleSheet()
            
            # Custom Styles
            title_style = ParagraphStyle(
                "TitleStyle",
                parent=styles["Heading1"],
                fontSize=24,
                leading=28,
                textColor=colors.HexColor("#0d1226"),
                fontName="Helvetica-Bold"
            )
            
            section_heading = ParagraphStyle(
                "SectionHeading",
                parent=styles["Heading2"],
                fontSize=14,
                leading=18,
                textColor=colors.HexColor("#4f46e5"),
                fontName="Helvetica-Bold",
                spaceBefore=12,
                spaceAfter=6
            )
            
            body_style = ParagraphStyle(
                "BodyStyle",
                parent=styles["BodyText"],
                fontSize=10,
                leading=14,
                textColor=colors.HexColor("#334155")
            )
            
            label_style = ParagraphStyle(
                "LabelStyle",
                parent=body_style,
                fontName="Helvetica-Bold",
                textColor=colors.HexColor("#0f172a")
            )

            # Header Banner
            shield = self._create_shield_drawing()
            title_p = Paragraph("🛡️ AegisAI Emergency Response Brief", title_style)
            sub_p = Paragraph(f"Report Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC", body_style)
            
            header_table = Table([[shield, title_p]], colWidths=[50, 450])
            header_table.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (0, 0), "CENTER"),
                ("LEFTPADDING", (1, 0), (1, 0), 10),
            ]))
            story.append(header_table)
            story.append(sub_p)
            story.append(Spacer(1, 10))
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0"), spaceAfter=15))

            # 1. Incident Overview
            story.append(Paragraph("1. Incident Summary", section_heading))
            
            # Severity color coding
            sev = str(incident.get("severity", "medium")).lower()
            sev_color = "#22c55e" # low
            if sev == "critical":
                sev_color = "#f43f5e"
            elif sev == "high":
                sev_color = "#f97316"
            elif sev == "medium":
                sev_color = "#f59e0b"
                
            inc_data = [
                [Paragraph("Incident ID", label_style), Paragraph(str(incident.get("id", "N/A")), body_style)],
                [Paragraph("Disaster Type", label_style), Paragraph(str(incident.get("incident_type", "N/A")).replace("_", " ").upper(), body_style)],
                [Paragraph("Severity", label_style), Paragraph(f"<font color='{sev_color}'><b>{sev.upper()}</b></font>", body_style)],
                [Paragraph("Status", label_style), Paragraph(str(incident.get("status", "reported")).upper(), body_style)],
                [Paragraph("Reported Location", label_style), Paragraph(str(incident.get("location", {}).get("address", "Coordinates Provided")), body_style)],
                [Paragraph("Description", label_style), Paragraph(str(incident.get("description", "N/A")), body_style)]
            ]
            
            t_summary = Table(inc_data, colWidths=[130, 370])
            t_summary.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#94a3b8")),
            ]))
            story.append(t_summary)
            story.append(Spacer(1, 15))

            # 2. AI Intelligence Analysis
            det_res = incident.get("detection_result")
            loc_ctx = incident.get("location_context")
            if det_res or loc_ctx:
                story.append(Paragraph("2. Intelligence Assessment", section_heading))
                intel_text = ""
                if det_res:
                    intel_text += f"<b>Gemini Vision Classification:</b> Identifies event as <b>{det_res.get('incident_type', '').upper()}</b> with {int(det_res.get('confidence', 0)*100)}% confidence score.<br/>"
                if loc_ctx:
                    intel_text += f"<b>Geocoding Context:</b> Located at {loc_ctx.get('address', 'N/A')}.<br/>"
                    intel_text += f"<b>Weather Conditions:</b> {loc_ctx.get('weather_summary', 'N/A')}. Risk Assessment: <b>{loc_ctx.get('risk_level', '').upper()}</b>."
                
                story.append(Paragraph(intel_text, body_style))
                story.append(Spacer(1, 15))

            # 3. Resource Allocation & Recommendations
            res_plan = incident.get("resource_plan")
            if res_plan:
                story.append(Paragraph("3. Facility & Resource Logistics Plan", section_heading))
                res_data = []
                
                shelter = res_plan.get("recommended_shelter")
                if shelter:
                    res_data.append([
                        Paragraph("Recommended Shelter", label_style),
                        Paragraph(f"<b>{shelter.get('name', 'N/A')}</b><br/>{shelter.get('address', '')}<br/>Capacity occupancy: {shelter.get('current_occupancy', 0)}/{shelter.get('total_capacity', 1)}", body_style)
                    ])
                
                hospital = res_plan.get("recommended_hospital")
                if hospital:
                    res_data.append([
                        Paragraph("Recommended Hospital", label_style),
                        Paragraph(f"<b>{hospital.get('name', 'N/A')}</b><br/>{hospital.get('address', '')}<br/>Available beds: {hospital.get('available_beds', 0)}", body_style)
                    ])
                    
                allocations = res_plan.get("resources_allocated", [])
                if allocations:
                    alloc_str = ", ".join([f"{a.get('quantity')} {a.get('unit')} {a.get('type')}" for a in allocations])
                    res_data.append([
                        Paragraph("Supplies Dispatched", label_style),
                        Paragraph(alloc_str, body_style)
                    ])
                    
                if res_data:
                    t_res = Table(res_data, colWidths=[130, 370])
                    t_res.setStyle(TableStyle([
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
                        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#94a3b8")),
                    ]))
                    story.append(t_res)
                    story.append(Spacer(1, 15))

            # 4. Rescue Operation Roadmap
            if mission:
                story.append(Paragraph("4. Rescue Mission Directive", section_heading))
                story.append(Paragraph(f"<b>Mission Title:</b> {mission.get('title', 'Rescue Brief')}<br/><b>Status:</b> {str(mission.get('status')).upper()}  |  <b>Priority:</b> PRIORITY-{mission.get('priority')}", body_style))
                story.append(Spacer(1, 5))
                
                steps_p = []
                for step in mission.get("rescue_steps", []):
                    status_indicator = "✅" if step.get("status") == "completed" else "⏳"
                    steps_p.append(Paragraph(f"{status_indicator} Step {step.get('order')}: {step.get('description')} ({step.get('status')})", body_style))
                    
                for step_p in steps_p:
                    story.append(step_p)
                    story.append(Spacer(1, 3))
                    
            # Footer / Notice
            story.append(Spacer(1, 20))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#94a3b8"), spaceBefore=10, spaceAfter=10))
            story.append(Paragraph("<font size='8' color='#64748b'>🛡️ AegisAI Dispatch Notice: This document is an automatically compiled operational brief from the AegisAI Orchestrator Agent using Google ADK & Gemini AI. All details are validated via local emergency coordination centers.</font>", body_style))

            # Build document
            doc.build(story)
            pdf_bytes = buffer.getvalue()
            buffer.close()
            return pdf_bytes
            
        res = await self._execute_tool("generate_incident_report", _run)
        return res.data if res.success else b""

    async def generate_analytics_report(self, stats: dict, incidents: List[dict]) -> bytes:
        """Generate a system analytics PDF report."""
        async def _run():
            from io import BytesIO
            buffer = BytesIO()
            
            doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
            story = []
            styles = getSampleStyleSheet()
            
            title_style = ParagraphStyle("TitleStyle", parent=styles["Heading1"], fontSize=22, textColor=colors.HexColor("#0d1226"))
            heading_style = ParagraphStyle("HeadingStyle", parent=styles["Heading2"], fontSize=14, textColor=colors.HexColor("#4f46e5"))
            body_style = ParagraphStyle("BodyStyle", parent=styles["BodyText"], fontSize=10, leading=14)
            label_style = ParagraphStyle("LabelStyle", parent=body_style, fontName="Helvetica-Bold")
            
            shield = self._create_shield_drawing()
            header_table = Table([[shield, Paragraph("AegisAI Operational Dashboard Report", title_style)]], colWidths=[50, 450])
            story.append(header_table)
            story.append(Spacer(1, 10))
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0"), spaceAfter=15))
            
            # System Metrics Overview
            story.append(Paragraph("System Operational Metrics Overview", heading_style))
            metrics_data = [
                [Paragraph("Total Incidents Handled", label_style), Paragraph(str(stats.get("total_incidents", 0)), body_style)],
                [Paragraph("Active Emergency Tasks", label_style), Paragraph(str(stats.get("active_incidents", 0)), body_style)],
                [Paragraph("Resolved Incidents", label_style), Paragraph(str(stats.get("resolved_incidents", 0)), body_style)],
                [Paragraph("Shelter Occupancy Index", label_style), Paragraph(f"{stats.get('shelter_occupancy_pct', 0)}%", body_style)],
                [Paragraph("Active Rescue Deployments", label_style), Paragraph(str(stats.get("active_missions", 0)), body_style)]
            ]
            t_metrics = Table(metrics_data, colWidths=[200, 300])
            t_metrics.setStyle(TableStyle([
                ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
                ("BOTTOMPADDING", (0,0), (-1,-1), 8),
                ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#f8fafc")),
                ("INNERGRID", (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
                ("BOX", (0,0), (-1,-1), 1, colors.HexColor("#94a3b8")),
            ]))
            story.append(t_metrics)
            
            doc.build(story)
            pdf_bytes = buffer.getvalue()
            buffer.close()
            return pdf_bytes
            
        res = await self._execute_tool("generate_analytics_report", _run)
        return res.data if res.success else b""

    async def save_report_to_file(self, pdf_bytes: bytes, filename: str) -> str:
        """Save PDF bytes to local file storage."""
        async def _run():
            # Use temp directory inside project space or OS temp folder
            target_dir = os.path.join(os.environ.get("TEMP", "/tmp"), "aegisai_reports")
            os.makedirs(target_dir, exist_ok=True)
            path = os.path.join(target_dir, filename)
            
            with open(path, "wb") as f:
                f.write(pdf_bytes)
            logger.info("pdf_saved_to_file", path=path, size=len(pdf_bytes))
            return path
        res = await self._execute_tool("save_report_to_file", _run)
        return res.data if res.success else ""

pdf_mcp = PDFMCPServer()
