from colin.checks.labels.maintainer import MaintainerCheck


class MaintainerCheckOpenHouse(MaintainerCheck):

    def __init__(self):
        super().__init__()
        self.message = "Label 'maintainer' has to be specified."
        self.description = "Use `LABEL labelname=labelvalue` for specifying label. Pro vytvoření labelu (=štítku) použij `LABEL klic=hodnota`."
        self.reference_url = "https://fedoraproject.org/wiki/Container:Guidelines#LABELS"
