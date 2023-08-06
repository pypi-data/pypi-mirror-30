from colin.checks.abstract.envs import EnvCheck
from colin.checks.abstract.containers import ContainerCheck
from colin.checks.abstract.images import ImageCheck
from colin.checks.result import CheckResult


class MaintainerCheck(EnvCheck):

    def __init__(self):
        super().__init__(name="fedora_base",
                         message="Use fedora:27 as a base image.",
                         description="Use `FROM image:tag` to specify base image. (Needs to be first instruction.) Použij `FROM obraz:tag` pro určení obrazu, na kterém budeme stavět. (Je třeba zadat jako první instrukci).",
                         reference_url="https://fedoraproject.org/wiki/Container:Guidelines#env",
                         tags=["fedora", "base", "env", "required"],
                         env_var="DISTTAG",
                         required=True,
                         value_regex="^f27container$")


class __WorkDirCheck(ContainerCheck, ImageCheck):

    def __init__(self):
        super().__init__(name="fedora_parent",
                         message="Use fedora:27 as a parent image",
                         description="Use `FROM image:tag` to specify base image. (Needs to be first instruction.) Použij `FROM obraz:tag` pro určení obrazu, na kterém budeme stavět. (Je třeba zadat jako první instrukci).",
                         reference_url="https://fedoraproject.org/wiki/Container:Guidelines#env",
                         tags=["fedora", "base", "env", "required"])

        self.parent = "sha256:65df79e41cefeac03d06d0618fe2ed2895d7a9c13c0ef507a18884ebcae754f8"

    def check(self, target):
        parent = target.instance.get_metadata()["Parent"]
        passed = parent is not None and self.parent == parent

        return CheckResult(ok=passed,
                           severity=self.severity,
                           description=self.description,
                           message=self.message,
                           reference_url=self.reference_url,
                           check_name=self.name,
                           logs=[])
