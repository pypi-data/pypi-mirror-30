from colin.checks.abstract.labels import LabelCheck


class BZComponentDeprecatedCheck(LabelCheck):

    def __init__(self):
        super().__init__(name="bzcomponent_deprecated",
                         message="Label 'BZComponent' is deprecated.",
                         description="Replace with 'com.redhat.component'.",
                         reference_url="?????",
                         tags=["com.redhat.component", "bzcomponent", "label", "deprecated"],
                         label="BZComponent",
                         required=False,
                         value_regex=None)
