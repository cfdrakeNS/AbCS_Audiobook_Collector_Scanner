"""Accessible License Dialog for AbCS."""

from PySide6.QtWidgets import QHBoxLayout, QPushButton, QSizePolicy, QVBoxLayout
from PySide6.QtCore import Qt, QTimer

from src.accessibility.dialog_prose import create_dialog_html_text
from src.ui.accessible_dialog import AccessibleDialog


class LicenseDialog(AccessibleDialog):
    def __init__(self, scaler, parent=None):
        from src.accessibility.icon_helper import get_app_icon
        from src.accessibility.style_helpers import build_accessible_button_style

        super().__init__(parent)
        self.setWindowIcon(get_app_icon())
        self.scaler = scaler
        self.setWindowTitle("AbCS License")
        self.setAccessibleName("AbCS License")
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setMinimumWidth(self.scaler.get_scaled_size(480))
        self.setMinimumHeight(self.scaler.get_scaled_size(400))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            self.scaler.get_scaled_size(24),
            self.scaler.get_scaled_size(12),
            self.scaler.get_scaled_size(24),
            self.scaler.get_scaled_size(18),
        )
        layout.setSpacing(self.scaler.get_scaled_size(8))

        license_blocks = [
            ('body', 'AbCS - Audiobook Collector Scanner'),
            ('heading', 'AbCS Free Use and Non-Sale License, Version 1.0'),
            ('body', 'Copyright (c) 2025-2026 C.F. Drake & Contributors'),
            ('body', 'Published by Aurora Accessibility (https://auroraaccessibility.com/)'),
            ('heading', '1. Scope'),
            ('body', 'This license applies to the original AbCS code and accompanying materials for which the copyright holders have authority to grant these permissions (the "Software"). Third-party components are addressed in section 7. AbCS is free, source-available software under this custom license.'),
            ('heading', '2. Free use and modification'),
            ('body', 'Permission is granted, free of charge, to download, install, run, study, copy, and modify the Software. Individuals, educational institutions, libraries, charities, public bodies, and businesses may use the Software, including for their internal business activities, without a license fee.'),
            ('body', 'You may make and use modified versions. You may share original or modified versions in source or executable form, subject to sections 3 and 4.'),
            ('heading', '3. Free redistribution'),
            ('body', 'When distributing the Software or a modified version, you must:'),
            ('body', '(a) Provide it without a purchase price, distribution fee, subscription, required donation, or other payment required to obtain or use it.'),
            ('body', '(b) Include this complete license and retain existing copyright notices and attribution. You may add accurate notices for your contributions.'),
            ('body', '(c) Clearly identify modified versions as modified, describe the changes, and identify who made them. Do not present them as official releases.'),
            ('body', "(d) Preserve recipients' permissions under this license for the Software and its modifications; do not impose additional restrictions on them."),
            ('body', 'Free hosting and mirroring by software download directories are permitted, including on websites supported by advertising, provided access to the Software remains free and the other conditions of this license are met.'),
            ('heading', '4. Sale and paid bundling'),
            ('body', 'Without prior written permission from the applicable copyright holders, you may not sell, rent, sublicense for a fee, or otherwise charge for access to, distribution of, or use of the Software or modified versions. You may not bundle them into a paid product, paid software package, or paid service in which access to or use of the Software is part of what the customer purchases.'),
            ('body', 'These restrictions do not prohibit a business from using AbCS internally, or restrict the sale or use of independent work, catalogues, or other outputs created using AbCS. Independently supplied support or training may be charged for, provided the Software itself remains separately available free of charge and no payment is required to obtain or use it.'),
            ('heading', '5. Optional donations'),
            ('body', 'The official project may accept voluntary donations through its website. Donations are optional and are not a condition of downloading, installing, using, or receiving updates to AbCS. A donation does not purchase a software license, additional rights, or a promise of support or features. Redistributors must not collect donations on behalf of Aurora Accessibility without written authorization or imply that their own payments or donations are required by the official project.'),
            ('heading', '6. Attribution and endorsement'),
            ('body', 'This license does not grant rights to use the names, logos, or branding of AbCS, Aurora Accessibility, or its contributors to imply endorsement, sponsorship, or official status. Accurate identification and attribution of the Software are permitted.'),
            ('heading', '7. Third-party components and user content'),
            ('body', 'Third-party libraries, bundled components, and other materials supplied under separate licenses remain governed by those licenses. This license does not replace or restrict rights granted under those separate licenses. Retain and comply with their applicable notices and license requirements.'),
            ('body', 'This license does not claim ownership of your audiobook files, metadata, databases, or other content. Rights in that content remain with their respective owners.'),
            ('heading', '8. No warranty'),
            ('body', 'TO THE EXTENT PERMITTED BY APPLICABLE LAW, THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.'),
            ('heading', '9. Limitation of liability'),
            ('body', 'TO THE EXTENT PERMITTED BY APPLICABLE LAW, IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.'),
            ('heading', '10. Other permissions'),
            ('body', 'Rights not expressly granted by this license are reserved, subject to applicable law. For permission to sell, distribute for a fee, or include AbCS in a paid offering, contact Aurora Accessibility through https://auroraaccessibility.com/.'),
        ]

        license_label = create_dialog_html_text(
            self,
            license_blocks,
            "License information",
            "AbCS license terms. Use arrow keys to read line by line. Press Tab to move to OK button.",
        )
        license_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        font = license_label.font()
        font.setPointSize(self.scaler.get_scaled_size(12))
        license_label.setFont(font)
        license_label.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(license_label)

        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        ok_btn = QPushButton("OK", self)
        ok_btn.setAccessibleName("OK")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.accept)

        base_height = 20
        scale_pct = (
            self.scaler.current_scale if hasattr(self.scaler, "current_scale") else 150
        )
        scaled_height = int(base_height * (scale_pct / 100.0))
        btn_font = ok_btn.font()
        btn_font.setPointSize(self.scaler.get_scaled_size(12))
        ok_btn.setFont(btn_font)
        ok_btn.setMinimumHeight(max(scaled_height - 4, 14))
        ok_btn.setMaximumHeight(max(scaled_height - 4, 14))
        ok_btn.setStyleSheet(build_accessible_button_style(scaled_height))
        btn_row.addWidget(ok_btn)
        layout.addLayout(btn_row)

        self.license_label = license_label
        self.ok_btn = ok_btn
        QTimer.singleShot(100, lambda: license_label.setFocus(Qt.TabFocusReason))
