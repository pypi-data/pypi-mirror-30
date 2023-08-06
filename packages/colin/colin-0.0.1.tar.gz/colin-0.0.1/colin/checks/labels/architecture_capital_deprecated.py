from colin.checks.abstract.labels import LabelCheck


class ArchitectureLabelCapitalDeprecatedCheck(LabelCheck):

    def __init__(self):
        super().__init__(name="architecture_label_capital_deprecated",
                         message="Label 'Architecture' is deprecated.",
                         description="Replace with 'architecture'.",
                         reference_url="?????",
                         tags=["architecture", "label", "capital", "deprecated"],
                         label="Architecture",
                         required=False,
                         value_regex=None)
