from django.utils import timezone
from django.contrib import admin
from .models import *

admin.site.register(Activity)
admin.site.register(Application)
admin.site.register(ApplicationSystemRequirement)
admin.site.register(UserPreference)
admin.site.register(CPUBenchmark)
admin.site.register(DiskBenchmark)
admin.site.register(GPUBenchmark)


@admin.register(RecommendationLog)
class RecommendationLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created_at",
        "get_activities",
        "get_recommended_cpu",
        "admin_rating",
        "reviewed_at",
    )
    list_filter = ("admin_rating", "created_at")
    search_fields = ("final_recommendation__recommended_cpu_name",)

    # Make the rating and notes directly editable from the list view
    list_editable = ("admin_rating",)

    # Define which fields to show in the detail view
    readonly_fields = (
        "source_preference",
        "final_recommendation",
        "activities_json",
        "applications_json",
        "created_at",
        "reviewed_by",
        "reviewed_at",
    )
    fieldsets = (
        (
            "Decision Record",
            {
                "fields": (
                    "created_at",
                    "source_preference",
                    "final_recommendation",
                    "activities_json",
                    "applications_json",
                )
            },
        ),
        ("Admin Feedback (Your Grading)", {"fields": ("admin_rating", "admin_notes")}),
        ("Review Info", {"fields": ("reviewed_by", "reviewed_at")}),
    )

    def get_activities(self, obj):
        return ", ".join(obj.activities_json)

    get_activities.short_description = "Activities"

    def get_recommended_cpu(self, obj):
        return obj.final_recommendation.recommended_cpu_name

    get_recommended_cpu.short_description = "Recommended CPU"

    def save_model(self, request, obj, form, change):
        # When an admin saves a change (e.g., adds a rating),
        # automatically record who and when.
        if "admin_rating" in form.changed_data or "admin_notes" in form.changed_data:
            obj.reviewed_by = request.user
            obj.reviewed_at = timezone.now()
        super().save_model(request, obj, form, change)
