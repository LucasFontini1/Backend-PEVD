from support.models import CommercialAudit


def record_action(actor, action, target):
    CommercialAudit.objects.create(
        actor=actor, action=action, target_type=target._meta.model_name,
        target_id=target.pk,
    )
