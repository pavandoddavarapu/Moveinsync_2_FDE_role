import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#718096"))
        self.drawString(36, 20, "MoveInSync Play Store Ratings Diagnosis | Candidate Executive Briefing")
        self.drawRightString(letter[0] - 36, 20, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()

def build_pdf():
    os.makedirs("output", exist_ok=True)
    pdf_path = os.path.join("output", "recommendation.pdf")
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=colors.HexColor('#1A365D'),
        spaceAfter=2
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#4A5568'),
        spaceAfter=8
    )

    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=13,
        textColor=colors.HexColor('#2B6CB0'),
        spaceBefore=6,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.8,
        leading=10.2,
        textColor=colors.HexColor('#2D3748')
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=body_style,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=2
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.2,
        leading=9,
        textColor=colors.white
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=6.8,
        leading=8.5,
        textColor=colors.HexColor('#1A202C')
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=table_cell_style,
        fontName='Helvetica-Bold'
    )

    story = []

    # Title & Subtitle
    story.append(Paragraph("MoveInSync Play Store Ratings Diagnosis & Engineering Roadmap", title_style))
    story.append(Paragraph("<b>Target:</b> com.moveinsync.ets | <b>Scope:</b> 114,874 lifetime ratings (4.64 avg), 24,315 full scraped reviews, 7,516 1–2 star reviews analyzed", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E0"), spaceAfter=6))

    # Executive Summary
    story.append(Paragraph("1. Executive Summary & Headline Finding", h2_style))
    exec_summary = (
        "MoveInSync holds an official Play Store rating of <b>4.64</b> based on 114,874 lifetime ratings, but current user sentiment has severely deteriorated: "
        "the trailing 12-month review average has plummeted to <b>3.82</b>, with the latest production release (<b>v12.19.0</b>) registering an average of <b>3.62</b> "
        "and a <b>34.3% 1–2 star complaint share</b>. While management frequently attributes low ratings to external operational factors (cabs arriving late or traffic), "
        "our journey classification reveals that <b>40.5% of low-star ratings stem directly from solvable Product & Engineering defects</b>—led by GPS tracking freezes and map auto-zoom resets "
        "(<b>14.8%</b> of low ratings; <b>+0.0312</b> rating gain), app launch hangs and update crashes (<b>7.9%</b>; <b>+0.0164</b> gain), and shift cutoff booking lockouts (<b>6.4%</b>; <b>+0.0132</b> gain). "
        "Crucially, a newly introduced blocking in-app rating modal without a 'Skip' option has weaponized frustrated commuters into submitting retaliatory 1-star reviews on the Google Play Store, "
        "turning the public store into an unmanaged grievance desk."
    )
    story.append(Paragraph(exec_summary, body_style))
    story.append(Spacer(1, 4))

    # Ranked Fix List Table
    story.append(Paragraph("2. Ranked Fix List (Top High-Impact Product & Engineering Interventions)", h2_style))
    
    headers = [
        Paragraph("Rank & Step", table_header_style),
        Paragraph("Defect & Technical Solution", table_header_style),
        Paragraph("Real Review Evidence", table_header_style),
        Paragraph("Owner / Effort", table_header_style),
        Paragraph("Rating Gain", table_header_style),
        Paragraph("Success Metric", table_header_style),
    ]

    table_data = [headers]

    fixes = [
        ("1. Tracking<br/>& ETA",
         "<b>Map Camera Auto-Reset:</b> Stop 30s map auto-reset to full bounding box. Retain user zoom level. Migrate GPS polling to resilient WebSocket location stream.",
         "• <i>fdc328ac</i> (v12.6, 10 upvotes): 'App has very poor logic of setting zoom level and reset it every 30s... makes impossible to see cab.'<br/>• <i>66b46471</i> (v7.0.1, 25 upvotes): 'When cab is at location, app shows 20-25 mins away.'",
         "Eng (Geo)<br/><b>M Effort</b>",
         "<b>+0.0312</b><br/>(14.8% low)",
         "Tracking tickets drop >60%; view time >45s without crash."),

        ("2. Stability<br/>& Launch",
         "<b>Fix Launch Hang & Cache Corruption:</b> In v12.19.0, app freezes on splash or crashes on open. Add SQLite migration safeguards, wipe stale auth cache on upgrade, lazy-load SDKs.",
         "• <i>b8d80e8e</i> (v12.19.0): 'Unable to open app... Closes as soon as I try to open.'<br/>• <i>1ec8231a</i> (v11.2.1, 13 upvotes): 'Screen just loading. Logged in/out, reinstalled 10 times.'",
         "Eng (Client)<br/><b>S Effort</b>",
         "<b>+0.0164</b><br/>(7.9% low)",
         "Play Vitals crash rate <0.35%; zero cold-start launch freezes."),

        ("3. Support /<br/>Intercept",
         "<b>Remove Blocking Rating Modal:</b> Abolish mandatory feedback modal locking UI. Add 'Skip' button. Route ratings ≤3 directly to in-app Helpdesk; invoke Play Store API only after smooth trips.",
         "• <i>86c67ef8</i> (v12.19.0): 'Forcing me to rate every ride, came to give 1 star. If I don't rate, can't use app.'<br/>• <i>b4096ad8</i> (v11.4.7, 30 upvotes): 'Blocks me upon opening asking for feedback.'",
         "Product/Eng<br/><b>S Effort</b>",
         "<b>+0.0068 direct</b><br/>(+0.030 intercept)",
         "90% reduction in 'forced rating' complaints; >50% resolved in-app."),

        ("4. Booking<br/>& Slots",
         "<b>Grace Period Booking Queue:</b> Replace binary cutoff lockouts with countdown grace timer and automated waitlist bump. Clarify inverted Night Shift 'Login/Logout' labels.",
         "• <i>c14aec97</i> (v11.5.15, 23 upvotes): 'Under Bookings Logout and Login is inverted causing No-Show.'<br/>• <i>7d79fa4b</i> (v11.1.4, 33 upvotes): 'Pain to use for a single booking.'",
         "Product/Eng<br/><b>M Effort</b>",
         "<b>+0.0132</b><br/>(6.4% low)",
         "Cutoff failure tickets down by 45%; booking latency <15s."),

        ("5. Login &<br/>Auth",
         "<b>Background Token Refresh:</b> Eliminate aggressive morning session timeouts. Implement background OAuth refresh tokens and fallback biometric auth to prevent repeated OTP on open.",
         "• <i>21c73b13</i> (v6.1, 50 upvotes): 'Does not show log out if we stretch... had to arrange transport myself.'<br/>• <i>8fca71da</i> (v12.19.0): 'Logs you off randomly, doesn't send OTP in time.'",
         "Eng (Sec)<br/><b>S Effort</b>",
         "<b>+0.0131</b><br/>(6.3% low)",
         "Unintended logout rate <1%; auth tickets down >75%."),

        ("6. Route &<br/>Detours",
         "<b>Detour & Co-Passenger Transparency:</b> Display planned route sequence before boarding. Alert commuter if added stop increases trip by >20 mins. Allow ops routing feedback loop.",
         "• <i>58c92b90</i> (v6.8, 12 upvotes): 'After update unable to find route assigned... now only me and driver.'<br/>• <i>e2bdb62d</i> (v5.2.5.3, 25 upvotes): 'Clubs opposite route, took 1 hr instead of 15 min.'",
         "Product/Ops<br/><b>L Effort</b>",
         "<b>+0.0092</b><br/>(4.3% low)",
         "Route dissatisfaction tickets down by 35%; predictability >85%.")
    ]

    for step, sol, evid, own, gain, succ in fixes:
        table_data.append([
            Paragraph(step, table_cell_bold),
            Paragraph(sol, table_cell_style),
            Paragraph(evid, table_cell_style),
            Paragraph(own, table_cell_style),
            Paragraph(gain, table_cell_bold),
            Paragraph(succ, table_cell_style),
        ])

    col_widths = [58, 125, 175, 56, 56, 70]
    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1A365D')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F7FAFC')]),
    ]))
    story.append(t)
    story.append(Spacer(1, 6))

    # Page Break to strictly maintain Page 2 layout
    story.append(PageBreak())

    # Page 2: Do First & Three Strategic Levers
    story.append(Paragraph("3. 'Do First' Section: 2-Week Engineering Sprint", h2_style))
    story.append(Paragraph(
        "The highest return on effort comes from <b>Fix #2 (Cold-Start Launch Crash/Freeze)</b> and <b>Fix #3 (Remove Blocking Rating Modal)</b>. "
        "Both require low engineering effort (S), have zero cross-team dependencies, and immediately stem the active rating bleeding in <b>v12.19.0</b>.",
        body_style
    ))
    story.append(Spacer(1, 3))

    sprint_text = (
        "<b>Week 1: Rapid Client Triage & Hotfix (Target: v12.19.1)</b><br/>"
        "• <b>Day 1–2 (Rating Modal Intercept):</b> Remove mandatory backdrop touch lock on post-trip rating popup. Add prominent 'Dismiss' / 'Skip' button. "
        "Gate `Google ReviewManager` to trigger strictly after two consecutive 5-star ratings; never prompt after delays.<br/>"
        "• <b>Day 3–4 (Stability Patch):</b> Profile Android cold-start path on low-memory devices. Move synchronous DB/network initializations off `Application.onCreate()`. "
        "Add database migration fallback to eliminate upgrade crash loops on Android 12–15.<br/>"
        "• <b>Day 5 (Tracking Patch):</b> Disable the 30-second camera zoom override in `GoogleMapFragment`. Respect user touch zoom.<br/>"
        "<b>Week 2: Verification, Staged Rollout & Impact Monitoring</b><br/>"
        "• <b>Day 6–7 (Internal QA):</b> Validate across Android 10–15 on low-spec hardware (2GB/3GB RAM) and throttled 2G/3G connections.<br/>"
        "• <b>Day 8–9 (Staged Rollout):</b> Release v12.19.1 hotfix to 10% of users. Monitor Google Play Console Vitals crash rate for 48 hours.<br/>"
        "• <b>Day 10 (Full Rollout):</b> Expand to 100%. Run automated rating monitor (<code>python run.py</code>) to confirm 1-2 star share drops toward <20%."
    )
    story.append(Paragraph(sprint_text, bullet_style))
    story.append(Spacer(1, 6))

    # Section 4: Three Strategic Levers
    story.append(Paragraph("4. The Three Strategic Levers (Backed by Empirical Data)", h2_style))
    
    levers = [
        ("Lever 1: Fix Core Product Defects First (40.5% Root Cause)",
         "<b>Empirical Evidence:</b> 3,047 out of 7,516 low-star reviews (40.5%) point unequivocally to software bugs—not driver rudeness or vehicle cleanliness. "
         "Addressing the top 4 product defects (Tracking, Stability, Booking, Login) yields a <b>+0.0739 rating point gain</b>, pushing MoveInSync to <b>4.71+</b> "
         "(surpassing peer Safetrax at 4.72). App engineering fixes can be shipped in weeks, whereas renegotiating vendor SLAs takes quarters."),

        ("Lever 2: Intercept Complaints & Protect the Play Store Door",
         "<b>Empirical Evidence:</b> Intercept analysis reveals that 151 reviews explicitly cite unanswered tickets, disconnected helpdesk lines, or forced modal lockouts. "
         "When employees face an imminent commute failure without in-app recourse, Google Play becomes their only escalation channel. "
         "<b>Action:</b> Never show an app store rating prompt after a delayed ride (ETA delta >10 min). Provide an immediate in-app 1-tap 'Report Cab Issue' "
         "with automated 5-minute Ops triage, intercepting angry reviews before they reach the Play Store."),

        ("Lever 3: Replace Canned Boilerplate with Actionable Developer Responses",
         "<b>Empirical Evidence:</b> The developer currently replies to <b>54.6%</b> of 1–2 star reviews with a median response time of <b>0.8 days</b>, "
         "yet <b>18.7%</b> of responses are identical canned templates (<i>'We regret the inconvenience caused. Please write to support@moveinsync.com'</i>). "
         "Users treat canned replies as automated brush-offs. <b>Action:</b> Deploy problem-specific responses referencing exact patch versions "
         "(e.g., <i>'Map zoom auto-reset is resolved in v12.19.1. Update and tap Settings > Report Location Lag if cab location jumps'</i>).")
    ]

    for title, text in levers:
        story.append(Paragraph(title, ParagraphStyle('LeverTitle', parent=body_style, fontName='Helvetica-Bold', textColor=colors.HexColor('#1A365D'))))
        story.append(Paragraph(text, body_style))
        story.append(Spacer(1, 4))

    # Peer Benchmarking Summary Box
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E0"), spaceAfter=4))
    peer_text = (
        "<b>Competitive Peer Context (Safetrax & Routematic):</b> MoveInSync's booking cutoff complaint share (6.4%) is <b>2x to 5x higher</b> than Safetrax (2.8%) "
        "and Routematic (1.2%), reflecting over-rigid shift cutoff lockouts. Conversely, MoveInSync outperforms peers in core stability (7.9% low-star share vs "
        "18.1% for Safetrax and 20.1% for Routematic), proving that MoveInSync's underlying platform is sound, but suffers from isolated UX anti-patterns."
    )
    story.append(Paragraph(peer_text, ParagraphStyle('PeerBox', parent=body_style, fontSize=7.2, leading=9.2, textColor=colors.HexColor('#4A5568'))))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated {pdf_path}")

if __name__ == "__main__":
    build_pdf()
