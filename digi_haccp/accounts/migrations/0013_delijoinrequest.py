from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0012_add_chemical_used_to_checklistitem"),
    ]

    operations = [
        migrations.CreateModel(
            name="DeliJoinRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(choices=[("pending", "Pending"), ("accepted", "Accepted"), ("rejected", "Rejected")], default="pending", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("responded_at", models.DateTimeField(blank=True, null=True)),
                ("deli", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="join_requests", to="accounts.deli")),
                ("invited_by", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="sent_deli_join_requests", to="accounts.user")),
                ("invited_user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="deli_join_requests", to="accounts.user")),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddConstraint(
            model_name="delijoinrequest",
            constraint=models.UniqueConstraint(
                condition=models.Q(("status", "pending")),
                fields=("deli", "invited_user"),
                name="unique_pending_deli_join_request",
            ),
        ),
    ]