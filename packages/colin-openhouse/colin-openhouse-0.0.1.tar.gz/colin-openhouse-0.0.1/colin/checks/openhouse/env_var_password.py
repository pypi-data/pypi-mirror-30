from colin.checks.abstract.envs import EnvCheck


class MaintainerCheck(EnvCheck):

    def __init__(self):
        super().__init__(name="env_var_password",
                         message="Environment variable 'password' has to be specified and should be set to `secret`.",
                         description="Use `ENV labelname=labelvalue` for specifying label. Pro vytvoření labelu (=štítku) použij `LABEL klic=hodnota`.",
                         reference_url="https://fedoraproject.org/wiki/Container:Guidelines#env",
                         tags=["password", "env", "required"],
                         env_var="password",
                         required=True,
                         value_regex="^secret$")
