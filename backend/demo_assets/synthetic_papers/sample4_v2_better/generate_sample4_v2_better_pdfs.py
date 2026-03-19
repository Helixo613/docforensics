from __future__ import annotations

from pathlib import Path
from textwrap import wrap

import fitz


OUTPUT_DIR = Path(__file__).resolve().parent
PAGE_WIDTH, PAGE_HEIGHT = fitz.paper_size("a4")
LEFT = 54
RIGHT = PAGE_WIDTH - 54
TOP = 56
BOTTOM = PAGE_HEIGHT - 56


PAPERS = [
    {
        "filename": "sample4b_paper_a_adaptation_delivers_reliable_gains.pdf",
        "title": "Domain Adaptation Delivers Reliable Gains for Discharge Summary Generation",
        "authors": "Rina Patel, Omar Sheikh, Julia Stein",
        "affiliation": "Health Language Systems Lab, Metro University",
        "abstract": (
            "Broad medical domain adaptation improved discharge summary generation across three hospital systems. "
            "Section-level factual precision rose from 0.74 to 0.85, unsupported medication statements fell by 41%, and an adapted 7B model outperformed a generic 13B baseline. "
            "The resulting drafts were strong enough for supervised clinical support, although the study did not evaluate autonomous release."
        ),
        "sections": {
            "1. Introduction": [
                "Discharge summaries remain difficult to generate faithfully. Small factual errors still block operational use.",
                "Prior reports disagree on the source of measured gains. This excerpt focuses on outcome statements rather than system setup."
            ],
            "2. Methods": [
                "Three hospitals contributed de-identified note bundles. Clinicians rated factual precision and edit burden.",
                "Medication, hospital course, and follow-up sections were scored separately. Reporting emphasized release-relevant errors."
            ],
            "3. Results": [
                "Domain adaptation materially improved factual precision in discharge summary generation, raising section-level factual precision from 0.74 to 0.85 and cutting unsupported medication statements by 41 percent.",
                "A smaller adapted 7B model outperformed a larger generic 13B model, scoring 0.85 versus 0.81 in factual precision and winning 58 percent of clinician preference comparisons.",
                "Performance was strong enough for supervised clinical support workflows, where reviewers accepted 88 percent of drafts after only light edits and targeted verification."
            ],
            "4. Discussion": [
                "These gains were substantive rather than cosmetic because the largest improvements appeared in medication reconciliation, pending tests, and follow-up planning rather than boilerplate phrasing.",
                "Broad medical adaptation was sufficient for strong supervised support at our sites, although the evidence here does not justify autonomous or low-supervision release."
            ],
            "5. Conclusion": [
                "Domain adaptation delivered reliable gains for discharge summary generation, and the adapted smaller model outperformed a larger generic baseline. "
                "The resulting quality was strong enough for supervised clinical support, but not a claim of autonomous deployment. "
                "A limitation is that all three sites used similar medication reconciliation templates."
            ],
        },
        "table_caption": "Table 1. Results for generic and adapted summarization systems.",
        "table_headers": ["Model", "Factual precision", "Unsupported meds", "Light-edit accept"],
        "table_rows": [
            ["Generic 7B", "0.74", "14.2%", "61%"],
            ["Generic 13B", "0.81", "10.1%", "74%"],
            ["Adapted 7B", "0.85", "8.4%", "88%"],
        ],
        "references": [
            "L. Byrd et al. Factual error analysis for inpatient summarization. Clinical NLP Review, 2023.",
            "M. Ortega and H. Singh. Section-aware evaluation of discharge note generators. Language in Medicine, 2024.",
            "T. Brooks. Adaptation corpora for protected health text. Applied Clinical AI, 2022.",
            "J. Vance and K. Omar. Measuring edit burden in clinician-in-the-loop summarization. Hospital Informatics Letters, 2024.",
            "R. Silva et al. Scale versus specialization in health language models. Foundation Systems Quarterly, 2023.",
            "A. Bose and F. Kent. Lightweight adaptation recipes for medical documentation. Health ML Methods, 2024.",
            "C. Huang. Reviewer acceptance metrics for generated summaries. Medical Interface Research, 2022.",
        ],
    },
    {
        "filename": "sample4b_paper_b_prompting_and_formatting_explain_gains.pdf",
        "title": "Prompting and Workflow Formatting Explain Most Gains in Clinical Summarization",
        "authors": "Kevin Liu, Meera Sethi",
        "affiliation": "Foundation Model Evaluation Group, Redwood AI",
        "abstract": (
            "After prompt optimization and stable section formatting, generic summarization models remained competitive with domain-adapted systems. "
            "Formatting alone improved factual precision by 4.8 points, while broad adaptation added only 0.7 points on average. "
            "Adaptation increased maintenance cost and produced inconsistent improvement across sites."
        ),
        "sections": {
            "1. Introduction": [
                "Clinical summarization quality depends on presentation choices. Section templates often change outcomes more than expected.",
                "This study emphasizes post-formatting comparisons. Setup language is intentionally minimized in the report."
            ],
            "2. Methods": [
                "Four hospitals supplied discharge note pairs. All models used the same section template.",
                "Primary metrics were factual precision, section coverage, and maintenance cost. Prompt tuning was standardized."
            ],
            "3. Results": [
                "After prompt optimization and workflow formatting controls, a generic 13B model reached 0.82 factual precision and trailed the adapted model by only 0.6 points.",
                "Most measured gains were explained by workflow formatting rather than domain adaptation, because formatting alone improved factual precision by 4.8 points while adaptation added only 0.7 points on average.",
                "Generic models remained competitive, and broad adaptation added maintenance cost for inconsistent improvement across sites, increasing refresh time by 36 percent with no clear win at two hospitals."
            ],
            "4. Discussion": [
                "These findings suggest that broad adaptation is not the dominant source of improvement once prompts, note ordering, and section formatting are disciplined across sites.",
                "Broad adaptation was sometimes helpful, but generic models remained competitive enough that the added maintenance cost was difficult to justify as a default choice."
            ],
            "5. Conclusion": [
                "Prompting and workflow formatting explained most observed gains in this benchmark, while broad adaptation delivered only a small average improvement. "
                "Generic models remained competitive after prompt optimization, and adaptation introduced cost for inconsistent benefit. "
                "A limitation is that the benchmark emphasized routine adult medicine discharges rather than rare specialty pathways."
            ],
        },
        "table_caption": "Table 1. Incremental gains from formatting, prompting, and adaptation.",
        "table_headers": ["Configuration", "Factual precision", "Coverage", "Ops overhead"],
        "table_rows": [
            ["Generic, naive", "0.77", "0.76", "1.00x"],
            ["Generic, tuned", "0.82", "0.81", "1.06x"],
            ["Adapted, tuned", "0.826", "0.82", "1.44x"],
        ],
        "references": [
            "B. Carlson and S. Mehta. Prompt design in high-stakes summarization. NLP Systems Journal, 2024.",
            "P. Everett. Workflow formatting for discharge documentation. Health Language Engineering, 2023.",
            "D. Kwan et al. Cross-site variation in hospital text corpora. Medical Data Review, 2022.",
            "A. Shah and T. Leone. Readability and factuality tradeoffs in medical generation. Clinical AI Metrics, 2023.",
            "R. White. Competitive baselines for domain-adapted language models. Foundation Model Reports, 2024.",
            "M. Desai. Structured prompting for discharge note synthesis. Applied Healthcare NLP, 2024.",
            "J. Rivera and K. Doyle. Why site effects dominate deployment outcomes. Real-World ML in Care, 2022.",
        ],
    },
    {
        "filename": "sample4b_paper_c_adaptation_helps_but_not_low_supervision_ready.pdf",
        "title": "Adaptation Helps, but Discharge Summaries Are Not Ready for Low-Supervision Use",
        "authors": "Nina Alvarez, Robert Chen",
        "affiliation": "Safe Clinical NLP Initiative",
        "abstract": (
            "Domain adaptation improved discharge summary generation, but residual hallucination risk remained too high for low-supervision deployment. "
            "Factual precision improved from 0.76 to 0.82, yet clinically significant hallucinations still appeared in 6.1 percent of drafts. "
            "Human review remained necessary because one in five summaries required material correction."
        ),
        "sections": {
            "1. Introduction": [
                "Average gains can hide dangerous residual errors. Rare failures matter in discharge communication.",
                "This report focuses on deployment relevance. Only outcome statements are emphasized."
            ],
            "2. Methods": [
                "Held-out drafts were reviewed by clinicians and pharmacists. Severe errors received explicit adjudication.",
                "The analysis emphasized unsupported medications, follow-up timing, and missing precautions. Section prose was not scored separately."
            ],
            "3. Results": [
                "Domain adaptation improved factual precision from 0.76 to 0.82 and reduced unsupported follow-up instructions by 29 percent across the evaluation set.",
                "Hallucination risk remained too high for low-supervision deployment, because clinically significant hallucinations still appeared in 6.1 percent of drafts after adaptation.",
                "Human review was still required, since 21 percent of summaries needed material factual correction before release to the care team or patient portal."
            ],
            "4. Discussion": [
                "Adaptation clearly helped, but the remaining high-severity error rate was still incompatible with low-supervision use in discharge workflows.",
                "The practical implication is that adaptation supports reviewer efficiency rather than reviewer removal, especially in medication and follow-up sections."
            ],
            "5. Conclusion": [
                "Adaptation improved discharge summary quality, but the resulting system was not ready for low-supervision deployment and still required human review. "
                "This is a qualified positive result rather than a deployment endorsement. "
                "A limitation is that the adjudication protocol weighted severe factual errors more heavily than stylistic completeness."
            ],
        },
        "table_caption": "Table 1. Safety-oriented evaluation after adaptation.",
        "table_headers": ["System", "Factual precision", "Severe hallucinations", "Needs correction"],
        "table_rows": [
            ["Generic", "0.76", "9.0%", "31%"],
            ["Adapted", "0.82", "6.1%", "21%"],
            ["Adapted + checklist", "0.83", "5.8%", "18%"],
        ],
        "references": [
            "S. Hall and E. Ross. Rare failure analysis for clinical generation. Safety in NLP, 2024.",
            "K. Young. Hallucination audits in discharge summaries. Journal of Clinical Language Safety, 2023.",
            "M. Iyengar and T. Cole. Human review requirements for medical text generation. Care Delivery Informatics, 2024.",
            "R. Moss. Severity-weighted metrics for factual generation. Measurement for Trustworthy AI, 2022.",
            "L. Brennan et al. Medication section errors in generated notes. Clinical Documentation Studies, 2023.",
            "P. Vora. Unsafe optimism in average-score reporting. Reliable Generative Systems, 2024.",
            "J. Simon and A. Park. Deployment thresholds for high-risk language applications. Medical Governance Review, 2022.",
        ],
    },
    {
        "filename": "sample4b_paper_d_local_workflow_tuning_outperforms_broad_adaptation.pdf",
        "title": "Local Workflow Tuning Outperforms Broad Medical Adaptation for Discharge Summaries",
        "authors": "Ava Thompson, Nikhil Rao",
        "affiliation": "Hospital Language Engineering Lab, St. Anne's Medical Center",
        "abstract": (
            "Broad medical adaptation improved discharge summarization, but institution-specific tuning produced the strongest home-site performance. "
            "Factual precision increased from 0.81 with broad adaptation to 0.87 with local workflow tuning, while transfer to a partner site exposed persistent mismatch. "
            "These results argue that broad adaptation is helpful but not best-in-class where local tuning is feasible."
        ),
        "sections": {
            "1. Introduction": [
                "Discharge templates vary widely across hospitals. Local workflow details often determine factual completeness.",
                "This excerpt emphasizes outcome comparisons. Generic motivation is intentionally brief."
            ],
            "2. Methods": [
                "One home hospital and two partner hospitals were evaluated. All systems used the same release checklist.",
                "Primary metrics were factual precision, section completeness, and workflow mismatch errors. Edit style was ignored."
            ],
            "3. Results": [
                "Institution-specific tuning outperformed broad medical adaptation, improving factual precision from 0.81 with broad adaptation to 0.87 at the home site.",
                "Broad medical adaptation remained helpful relative to a generic baseline, but it was not best-in-class once local workflow tuning was available.",
                "Local workflow mismatch was a major bottleneck, because transferring the locally tuned model to a partner site reduced section completeness by 5.2 points and doubled templated instruction errors."
            ],
            "4. Discussion": [
                "The ranking was consistent across reviewer groups: generic prompting was weakest, broad adaptation was helpful, and local workflow tuning was best where feasible.",
                "These results do not dismiss broad adaptation, but they do show that broad adaptation is not enough when institutions differ in discharge workflow and templated instructions."
            ],
            "5. Conclusion": [
                "Local workflow tuning outperformed broad medical adaptation for discharge summaries, while broad adaptation remained clearly better than a generic baseline. "
                "Institution-specific tuning was the strongest option when local data and review infrastructure were available. "
                "A limitation is that the home-site tuning set was larger than what some smaller hospitals could assemble."
            ],
        },
        "table_caption": "Table 1. Home-site and transfer-site results for tuning strategies.",
        "table_headers": ["Strategy", "Home precision", "Partner completeness", "Mismatch errors"],
        "table_rows": [
            ["Generic prompt", "0.77", "0.74", "11.0%"],
            ["Broad adaptation", "0.81", "0.79", "7.2%"],
            ["Local tuning", "0.87", "0.82", "5.5%"],
        ],
        "references": [
            "E. Foster and H. Kim. Site-specific behavior in clinical language models. Hospital NLP Transactions, 2024.",
            "N. Gupta. Template mismatch across discharge workflows. Documentation Systems Letters, 2023.",
            "R. Stern and V. Hale. Local adaptation for high-stakes summarization. Medical Text Engineering, 2024.",
            "J. Webb. Institution transfer failures in generative systems. Deployment Science Review, 2022.",
            "A. Cole et al. Portability of hospital language models across workflows. Clinical AI Benchmarking, 2023.",
            "S. Pratt. Broad adaptation versus local specialization. Health Foundation Models, 2024.",
            "D. Xu and M. Larsen. Measuring mismatch in generated clinical instructions. Language Safety in Practice, 2023.",
        ],
    },
]


def wrap_block(text: str, width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        if not paragraph.strip():
            lines.append("")
            continue
        lines.extend(wrap(paragraph, width=width))
    return lines


def center_line(page: fitz.Page, text: str, y: float, fontsize: float, fontname: str) -> None:
    width = fitz.get_text_length(text, fontname=fontname, fontsize=fontsize)
    x = max(LEFT, (PAGE_WIDTH - width) / 2)
    page.insert_text((x, y), text, fontname=fontname, fontsize=fontsize)


class PDFBuilder:
    def __init__(self) -> None:
        self.doc = fitz.open()
        self.page = self.doc.new_page(width=PAGE_WIDTH, height=PAGE_HEIGHT)
        self.y = TOP

    def new_page(self) -> None:
        self.page = self.doc.new_page(width=PAGE_WIDTH, height=PAGE_HEIGHT)
        self.y = TOP

    def ensure_space(self, needed: float) -> None:
        if self.y + needed > BOTTOM:
            self.new_page()

    def add_centered_lines(self, lines: list[tuple[str, float, str, float]]) -> None:
        total = sum(item[3] for item in lines)
        self.ensure_space(total + 10)
        for text, size, fontname, leading in lines:
            center_line(self.page, text, self.y, size, fontname)
            self.y += leading
        self.y += 6

    def add_rule(self) -> None:
        self.ensure_space(10)
        self.page.draw_line((LEFT, self.y), (RIGHT, self.y), color=(0.2, 0.2, 0.2), width=0.7)
        self.y += 10

    def add_heading(self, text: str) -> None:
        self.ensure_space(18)
        heading = text if text[-1] in ".?!" else f"{text}."
        self.page.insert_text((LEFT, self.y), heading, fontname="Times-Bold", fontsize=12)
        self.y += 16

    def add_paragraph(self, text: str, width: int = 96, fontsize: float = 10.5, leading: float = 13.5) -> None:
        lines = wrap_block(text, width)
        self.ensure_space((len(lines) + 1) * leading)
        for line in lines:
            self.page.insert_text((LEFT, self.y), line, fontname="Times-Roman", fontsize=fontsize)
            self.y += leading
        self.y += 4

    def add_table(self, caption: str, headers: list[str], rows: list[list[str]]) -> None:
        row_height = 19
        self.ensure_space(row_height * (len(rows) + 1) + 36)
        self.page.insert_text((LEFT, self.y), caption, fontname="Times-Italic", fontsize=10)
        self.y += 14
        widths = [120, 100, 100, RIGHT - LEFT - 320]
        x_positions = [0]
        for width in widths:
            x_positions.append(x_positions[-1] + width)
        display_width = RIGHT - LEFT
        display_height = row_height * (len(rows) + 1)
        temp_doc = fitz.open()
        temp_page = temp_doc.new_page(width=display_width, height=display_height)
        for x in x_positions:
            temp_page.draw_line((x, 0), (x, display_height), color=(0, 0, 0), width=0.6)
        for idx in range(len(rows) + 2):
            y = idx * row_height
            temp_page.draw_line((0, y), (display_width, y), color=(0, 0, 0), width=0.6)
        all_rows = [headers] + rows
        for r_index, row in enumerate(all_rows):
            y = r_index * row_height + 13
            for c_index, cell in enumerate(row):
                temp_page.insert_text(
                    (x_positions[c_index] + 4, y),
                    cell,
                    fontname="Times-Bold" if r_index == 0 else "Times-Roman",
                    fontsize=9.0,
                )
        pix = temp_page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
        self.page.insert_image(fitz.Rect(LEFT, self.y, RIGHT, self.y + display_height), pixmap=pix)
        temp_doc.close()
        self.y += display_height + 10

    def add_references(self, references: list[str]) -> None:
        self.add_heading("References")
        for index, ref in enumerate(references, start=1):
            self.add_paragraph(f"[{index}] {ref}", width=94, fontsize=9.6, leading=12.4)

    def add_footer_numbers(self) -> None:
        for index, page in enumerate(self.doc, start=1):
            page.insert_text((PAGE_WIDTH / 2 - 8, PAGE_HEIGHT - 28), str(index), fontname="Times-Roman", fontsize=9)


def render_paper(spec: dict) -> None:
    title_lines = wrap_block(spec["title"], 58)
    if title_lines:
        title_lines[-1] = title_lines[-1] if title_lines[-1][-1] in ".?!" else f"{title_lines[-1]}."
    builder = PDFBuilder()
    builder.add_centered_lines(
        [(line, 15, "Times-Bold", 18) for line in title_lines]
        + [
            (f"{spec['authors']}.", 10.5, "Times-Roman", 14),
            (f"{spec['affiliation']}.", 10, "Times-Italic", 14),
        ]
    )
    builder.add_rule()
    builder.add_heading("Abstract")
    builder.add_paragraph(spec["abstract"], width=98)
    for heading, paragraphs in spec["sections"].items():
        builder.add_heading(heading)
        for paragraph in paragraphs:
            builder.add_paragraph(paragraph)
        if heading == "3. Results":
            builder.add_table(spec["table_caption"], spec["table_headers"], spec["table_rows"])
    builder.add_references(spec["references"])
    builder.add_footer_numbers()
    output_path = OUTPUT_DIR / spec["filename"]
    builder.doc.save(output_path)
    builder.doc.close()


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for spec in PAPERS:
        render_paper(spec)
        print(f"Wrote {OUTPUT_DIR / spec['filename']}")


if __name__ == "__main__":
    main()
