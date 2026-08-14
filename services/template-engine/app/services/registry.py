from app.models.template import Template


BUILTIN_TEMPLATES = {
    "backend-service": Template(
        name="backend-service",
        description=(
            "Golden path template for backend "
            "services managed by the platform."
        ),
        version="1.0.0",
        type="service"
    ),
    "worker-service": Template(
        name="worker-service",
        description=(
            "Golden path template for asynchronous "
            "worker services."
        ),
        version="1.0.0",
        type="service"
    ),
    "scheduled-job": Template(
        name="scheduled-job",
        description=(
            "Golden path template for scheduled "
            "platform workloads."
        ),
        version="1.0.0",
        type="service"
    )
}


def list_templates():
    return list(
        BUILTIN_TEMPLATES.values()
    )


def resolve_template(
    template_name: str
):
    return BUILTIN_TEMPLATES.get(
        template_name
    )
