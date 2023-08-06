from colin.checks.abstract.labels import LabelCheck


class NameLabelCapitalDeprecatedCheck(LabelCheck):

    def __init__(self):
        super().__init__(name="name_label_capital_deprecated",
                         message="Label 'Name' is deprecated.",
                         description="Replace with 'name'.",
                         reference_url="?????",
                         tags=["name", "label", "capital", "deprecated"],
                         label="Name",
                         required=False,
                         value_regex=None)
