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
        "filename": "sample3_paper_a_low_label_transfer.pdf",
        "title": "When Does ImageNet Pretraining Still Help Chest X-Ray Classification?",
        "authors": "Maya Deshpande, Leo Hart, Priya Nair",
        "affiliation": "Center for Medical Vision, Northeastern Institute of Technology",
        "abstract": (
            "We study whether ImageNet initialization remains useful for chest X-ray classification under realistic labeling budgets. "
            "Across five hospitals and four architectures, ImageNet pretraining improved mean AUROC by 3.8 points when only 5% of labels were available, "
            "but the gain fell to 0.6 points under full supervision. A medical-domain pretraining checkpoint trained on 1.8 million unlabeled radiology images "
            "outperformed ImageNet initialization in the lowest-data regime. These results suggest that transfer still helps, but mostly when annotation is scarce."
        ),
        "sections": {
            "1. Introduction": [
                "Natural-image transfer remains common in radiology pipelines, yet it is unclear when the benefit is practically meaningful rather than habitual. "
                "Recent deployments have better optimizers, stronger augmentations, and wider model families than the early transfer-learning literature.",
                "We therefore asked three focused questions: does ImageNet pretraining still help in low-label settings, do the gains persist once label budgets increase, "
                "and is medical-domain pretraining a stronger source of initialization than ImageNet when data are scarce."
            ],
            "2. Methods": [
                "We trained DenseNet-121 and ConvNeXt-T models on four chest X-ray tasks with label budgets of 5%, 10%, 25%, 50%, and 100%. "
                "Each experiment compared random initialization, ImageNet initialization, and medical-domain pretraining learned from de-identified radiology images. "
                "Hyperparameters were matched across settings and evaluated over five random seeds.",
                "Primary endpoints were AUROC and expected calibration error. We also recorded wall-clock training cost from initialization through early stopping."
            ],
            "3. Results": [
                "ImageNet pretraining helped in low-label settings. At 5% labels, ImageNet initialization improved mean AUROC from 0.781 to 0.819. "
                "At 10% labels the gain was 2.4 points, while at 100% labels the gain shrank to 0.6 points and was no longer statistically robust across all tasks. "
                "In practical terms, ImageNet pretraining helps substantially when only 5% or 10% of labels are available.",
                "Medical-domain pretraining beat ImageNet in low-data settings. In the 5% and 10% label regimes, the radiology checkpoint exceeded ImageNet initialization by "
                "1.9 and 1.4 AUROC points, respectively. Once label budgets reached 50%, the gap between the two pretrained sources narrowed to less than 0.3 points. "
                "Medical-domain pretraining is better than ImageNet pretraining in low-data settings.",
                "The extra compute of the medical-domain checkpoint was justified only in very small datasets. For fully supervised runs, architecture choice explained more variance than initialization."
            ],
            "4. Discussion": [
                "Our results support a conditional view of transfer learning. ImageNet pretraining still helps in low-label settings, but the gains shrink at high label budgets. "
                "The operational lesson is not that pretraining is obsolete, but that its value depends on the scarcity regime.",
                "The stronger low-data performance of radiology pretraining suggests that source-domain match matters when labels are scarce. "
                "However, the practical advantage over ImageNet becomes small once the supervised dataset is sufficiently large."
            ],
            "5. Conclusion": [
                "ImageNet pretraining remains useful for chest X-ray classification when labels are scarce. "
                "Medical-domain pretraining is better in low-data settings, while the advantage of any pretrained initialization narrows sharply as label budgets rise. "
                "A limitation of this excerpt is that all tasks were classification problems rather than dense prediction tasks."
            ],
        },
        "table_caption": "Table 1. Mean AUROC by label budget and initialization source.",
        "table_headers": ["Label budget", "Scratch", "ImageNet", "Medical-domain"],
        "table_rows": [
            ["5%", "0.781", "0.819", "0.838"],
            ["25%", "0.846", "0.861", "0.866"],
            ["100%", "0.884", "0.890", "0.892"],
        ],
        "references": [
            "A. Kline and J. Mercer. Benchmarking low-label medical vision systems. Journal of Clinical Computation, 2022.",
            "L. Zhang et al. Transfer initialization under annotation scarcity. Medical Representation Review, 2023.",
            "P. Moreno and T. Ives. Calibration trends in radiology classifiers. Imaging Systems Letters, 2021.",
            "S. Holm. Domain-matched pretraining for hospital imaging archives. Transactions on Applied Vision, 2024.",
            "Y. Banerjee et al. Practical optimization for chest X-ray models. Clinical ML Notes, 2022.",
            "R. Fawcett and M. Lin. Seed sensitivity in compact medical classifiers. Machine Learning in Practice, 2023.",
            "D. Fischer. Cost-aware evaluation of pretrained backbones. Systems for Health AI, 2024.",
        ],
    },
    {
        "filename": "sample3_paper_b_transfer_baseline.pdf",
        "title": "Transfer Learning Remains a Strong Baseline for Small-Scale Medical Imaging",
        "authors": "Daniel Wu, Ananya Bose",
        "affiliation": "Applied Clinical ML Lab, Pacific State University",
        "abstract": (
            "We revisit transfer learning as a baseline for small-scale medical imaging studies spanning pathology, ultrasound, and radiography. "
            "ImageNet transfer remained broadly useful across thirteen tasks and provided measurable benefits even beyond very small label budgets. "
            "We found no consistent evidence that domain-specific pretraining was superior once site-level variation and optimization fairness were controlled."
        ),
        "sections": {
            "1. Introduction": [
                "Transfer learning is often criticized as a stale baseline in medical imaging, yet many real clinical datasets still contain far fewer labels than large natural-image benchmarks. "
                "The relevant question for practitioners is not whether transfer is philosophically elegant, but whether it remains a strong baseline under modest annotation budgets.",
                "We focus on three claims under debate: whether ImageNet transfer remains broadly useful, whether benefits persist beyond very small label budgets, and whether domain-specific pretraining is consistently better in practice."
            ],
            "2. Methods": [
                "We aggregated thirteen classification tasks from six institutions and trained identical ResNet and EfficientNet variants with scratch initialization, ImageNet transfer, and domain-specific medical checkpoints. "
                "Budget sweeps used 10%, 25%, 50%, and 100% labels. We matched augmentations, stopping criteria, and optimizer schedules.",
                "Performance was summarized with AUROC and macro F1. We also tracked setup time for each baseline because deployment teams often prefer solutions with low operational friction."
            ],
            "3. Results": [
                "ImageNet transfer remained a strong baseline. Compared with scratch training, ImageNet initialization improved mean AUROC by 3.1 points at 10% labels, 2.0 points at 25%, and 1.2 points at 50% labels. "
                "Even at full supervision, ImageNet transfer retained a 0.9-point average advantage across tasks. ImageNet transfer remains broadly useful.",
                "Benefits persisted beyond very small label budgets. The transfer advantage narrowed with more labels, but it did not collapse immediately after the smallest regime. "
                "The benefits of ImageNet transfer persist beyond very small label budgets.",
                "Domain-specific pretraining was not consistently better. In four tasks it exceeded ImageNet transfer, in five tasks it was statistically tied, and in four tasks it underperformed after fairness controls. "
                "Reusing an ImageNet checkpoint added little operational cost relative to the benefit. Domain-specific pretraining is not consistently better than ImageNet transfer."
            ],
            "4. Discussion": [
                "These findings argue for a pragmatic baseline hierarchy. Transfer learning remains broadly useful, and the evidence against it is weaker once optimization parity is enforced.",
                "We do not claim that domain-specific pretraining never helps. Rather, the gains are not consistent enough to displace ImageNet transfer as the default baseline for small-scale studies."
            ],
            "5. Conclusion": [
                "ImageNet transfer remains a strong baseline for small-scale medical imaging and its benefits can persist beyond the smallest label budgets. "
                "Domain-specific pretraining is useful in some cases, but it is not consistently better. "
                "A limitation is that our study emphasized classification datasets more than temporal or multimodal settings."
            ],
        },
        "table_caption": "Table 1. Average AUROC improvement over scratch training across 13 tasks.",
        "table_headers": ["Label budget", "ImageNet gain", "Medical gain", "Tie / win pattern"],
        "table_rows": [
            ["10%", "+3.1", "+3.4", "Medical better on 4 tasks"],
            ["50%", "+1.2", "+1.0", "Mostly tied"],
            ["100%", "+0.9", "+0.6", "ImageNet more stable"],
        ],
        "references": [
            "C. Doyle et al. Baseline discipline in clinical machine learning. Evaluation Quarterly, 2021.",
            "M. Sato and V. Hines. Small-data imaging benchmarks across sites. Health Data Systems, 2023.",
            "E. Romero. Fair optimization comparisons for pretrained vision models. Applied AI Methods, 2022.",
            "N. Fraser and R. Cole. Operational costs of medical model selection. Clinical Informatics Practice, 2024.",
            "S. Patel et al. Transfer gains beyond extreme label scarcity. Journal of Imaging Analytics, 2024.",
            "A. Kraft. Practical reproducibility in hospital computer vision. Medical ML Reports, 2023.",
            "F. Li and G. Moore. When domain checkpoints fail to travel. Cross-Site Learning Review, 2022.",
        ],
    },
    {
        "filename": "sample3_paper_c_scratch_catches_up.pdf",
        "title": "Rethinking Natural-Image Transfer for Radiology: Strong Scratch Baselines Narrow the Gap",
        "authors": "Elena Markovic, Harsh Verma, Sofia Klein",
        "affiliation": "Institute for Reliable ML in Medicine",
        "abstract": (
            "Natural-image transfer is often credited with large performance gains in radiology, but many comparisons use weak scratch baselines. "
            "When scratch models are tuned with longer schedules, stronger regularization, and modern augmentations, the gap to ImageNet initialization narrows sharply. "
            "We find that most reported ImageNet gains are overstated and that the residual benefit is frequently too small to justify additional compute and checkpoint management."
        ),
        "sections": {
            "1. Introduction": [
                "Claims about the necessity of natural-image transfer in radiology often rest on comparisons against under-tuned scratch baselines. "
                "This is especially problematic when operational recommendations are made from small benchmark differences.",
                "We reassessed transfer claims under matched tuning and asked whether scratch training catches up, whether most ImageNet gains are overstated, and whether the extra compute is worth the remaining performance gap."
            ],
            "2. Methods": [
                "We evaluated three public radiology datasets and two internal hospital datasets using ConvNeXt-S and DenseNet-121. "
                "Scratch models received longer cosine schedules, heavier augmentation, selective layer scaling, and stronger label smoothing. "
                "ImageNet models used the identical downstream training recipe.",
                "Beyond AUROC, we measured total experiment time, checkpoint storage burden, and rerun overhead because these costs matter in iterative hospital studies."
            ],
            "3. Results": [
                "With proper tuning, scratch catches up. At 50% labels, scratch training matched ImageNet initialization within 0.2 AUROC points on four of five tasks and exceeded it on one task. "
                "At 100% labels, the mean gap was 0.1 points and not practically meaningful. Strong scratch training removes most of the ImageNet advantage once tuning is fair.",
                "Most ImageNet gains were overstated. Large improvements appeared only when scratch baselines used short schedules or weak augmentation. "
                "Under matched tuning, the remaining advantage was confined to the smallest label regimes.",
                "The extra compute was often not worth it. Teams using transfer still paid for checkpoint management, compatibility checks, and repeated warm starts, yet the residual benefit above 50% labels was negligible. "
                "The extra compute for ImageNet transfer is often not worth the small residual gain."
            ],
            "4. Discussion": [
                "These results do not imply that pretraining never helps. They imply that conclusions about transfer must be compared against credible scratch baselines.",
                "From a systems perspective, the compute cost is often not worth it once annotation budgets are moderate and tuning discipline is high."
            ],
            "5. Conclusion": [
                "Strong scratch baselines narrow the gap to ImageNet transfer in radiology. "
                "The remaining advantage is concentrated in low-label settings, and most broader claims about ImageNet gains appear overstated. "
                "A limitation is that we did not evaluate self-supervised medical pretraining as a separate source of initialization."
            ],
        },
        "table_caption": "Table 1. Matched-tuning comparison between scratch and ImageNet initialization.",
        "table_headers": ["Label budget", "Scratch AUROC", "ImageNet AUROC", "Total rerun cost"],
        "table_rows": [
            ["10%", "0.792", "0.812", "1.00x vs 1.07x"],
            ["50%", "0.861", "0.863", "1.00x vs 1.10x"],
            ["100%", "0.889", "0.890", "1.00x vs 1.11x"],
        ],
        "references": [
            "J. Keane and M. Ochoa. Reassessing baseline strength in clinical computer vision. Reliable AI Review, 2023.",
            "P. Held. Long-schedule training for medium-scale medical datasets. Systems in Medicine, 2022.",
            "R. Ahmed et al. Augmentation fairness in radiology benchmarks. Vision in Health, 2024.",
            "T. Benson. Storage and reproducibility costs in hospital ML. Practice and Deployment, 2023.",
            "L. Yoon and K. Drake. Operational views on pretrained checkpoints. Applied Model Management, 2022.",
            "S. Weber. Practical significance versus leaderboard significance. Measurement in AI, 2021.",
            "N. Ellis. Scratch baselines in low-resource imaging tasks. Medical Data Analysis, 2024.",
        ],
    },
    {
        "filename": "sample3_paper_d_data_scarcity_driver.pdf",
        "title": "Data Scarcity, Not Initialization Alone, Drives Performance in Medical Vision Models",
        "authors": "Sara Iqbal, Thomas Reed",
        "affiliation": "Clinical AI Group, Midvale Research Hospital",
        "abstract": (
            "We analyze whether initialization itself drives performance in medical vision models or whether the apparent benefit is mainly a symptom of data scarcity. "
            "Across six chest and pathology benchmarks, pretrained initializations mattered most when labels were scarce, while architecture choice and training stability dominated once data scaled. "
            "Medical-domain pretraining was the strongest option in low-data regimes."
        ),
        "sections": {
            "1. Introduction": [
                "Initialization is often treated as a first-order decision in medical vision, but that framing may confuse a scarcity effect for an initialization effect. "
                "If the primary driver is label scarcity, then the right operational recommendation is conditional rather than universal.",
                "We test whether pretraining mainly matters when data are scarce, whether architecture matters more at scale, and whether medical-domain pretraining is the best low-data option."
            ],
            "2. Methods": [
                "Six classification tasks were trained with scratch initialization, ImageNet transfer, and medical-domain transfer across budget sweeps from 2% to 100% labels. "
                "We repeated each run over four seeds and separately modeled the contribution of architecture, optimization, and initialization to performance variance.",
                "We report AUROC, macro F1, and a simple decomposition of variance explained by each design decision."
            ],
            "3. Results": [
                "Pretraining mainly mattered when data were scarce. At 2% and 5% labels, initialization accounted for 21% of explained performance variance, but above 50% labels it accounted for less than 5%. "
                "Pretraining mainly matters when labels are scarce and does not provide a meaningful advantage once more than half of labels are available.",
                "Architecture mattered more at scale. Once datasets exceeded half of the available labels, backbone choice explained more variance than initialization across every benchmark.",
                "Medical-domain pretraining was best in low-data regimes. In the 2% and 5% label settings it outperformed ImageNet transfer by 1.6 AUROC points on average, while both approaches converged at full supervision. "
                "Medical-domain pretraining is best in low-data regimes."
            ],
            "4. Discussion": [
                "The recurring pattern is that scarcity drives the apparent value of initialization. "
                "This explains why transfer can look essential in under-labeled studies yet become secondary in larger curated cohorts.",
                "Our results are compatible with using ImageNet transfer as a pragmatic baseline, but they argue that medical-domain pretraining is the best option when labels are especially scarce."
            ],
            "5. Conclusion": [
                "Data scarcity, not initialization alone, drives much of the observed benefit from pretraining in medical vision. "
                "Pretraining matters most when labels are scarce, architecture matters more at scale, and medical-domain pretraining is best in low-data regimes. "
                "A limitation is that we did not include foundation-model adapters or multimodal supervision."
            ],
        },
        "table_caption": "Table 1. Variance explained by initialization versus architecture.",
        "table_headers": ["Label budget", "Init. variance", "Arch. variance", "Best low-data source"],
        "table_rows": [
            ["2%", "21%", "9%", "Medical-domain"],
            ["25%", "10%", "14%", "Medical-domain"],
            ["100%", "4%", "19%", "Tie"],
        ],
        "references": [
            "I. Novak and P. Shah. Scarcity effects in medical machine learning. Journal of Hospital Data Science, 2022.",
            "D. Cormier. Variance decomposition for model design choices. Statistical Engineering Letters, 2021.",
            "K. Lawson and R. Bell. Architecture sensitivity in full-data imaging studies. Medical Systems Research, 2024.",
            "T. Green et al. When initialization stops mattering. Applied Representation Analysis, 2023.",
            "S. Narang. Low-data regimes in radiology classification. Clinical Vision Benchmarks, 2023.",
            "J. Ruiz and H. Martin. Cross-benchmark stability of pretrained features. Learning for Medicine, 2022.",
            "E. Ford. Practical lessons from scarce-label hospital datasets. AI in Care Delivery, 2024.",
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
        table_height = row_height * (len(rows) + 1) + 10
        self.ensure_space(table_height + 26)
        self.page.insert_text((LEFT, self.y), caption, fontname="Times-Italic", fontsize=10)
        self.y += 14
        widths = [95, 95, 95, RIGHT - LEFT - 285]
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
                    fontsize=9.2,
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
