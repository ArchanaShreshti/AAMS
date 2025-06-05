from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from Schedules.models import ScheduleTask
from Root.models import Status
from OilAnalysis.models import OilAnalysis
from Report.models import OilAnalysisReport
from screen_views.generate_pdf_and_upload_to_s3 import generate_pdf_and_upload_to_s3
import logging
from Report.serializers import *

logger = logging.getLogger(__name__)

def save_oil_analysis_report(data: dict):
    """
    Save OilAnalysisReport based on minimal payload metadata.
    """
    oil_analysis_id = data.get('oilAnalysisId')
    oil_analysis = OilAnalysis.objects.filter(id=oil_analysis_id).first()
    if not oil_analysis:
        raise ValueError("Invalid oilAnalysisId")

    severity = None
    severity_key = data.get('severityId')
    if severity_key:
        severity = Status.objects.filter(key__iexact=severity_key).first()

    report = OilAnalysisReport(
        equipmentId=oil_analysis,
        sampleId=f"Report-{timezone.now().strftime('%Y%m%d%H%M%S')}",
        statusId=severity,
        recommendations=f"Priority: {data.get('priorityId')}, Report Type: {data.get('reportType')}",
        reportDate=timezone.now().date(),
    )
    report.save()
    return report

class OilAnalysisReportView(APIView):
    """
    API endpoint for generating and saving oil analysis reports.
    """
    def post(self, request):
        try:
            payload = request.data

            url = payload.get("url")
            token = payload.get("token")
            if not url or not token:
                return Response(
                    {"error": "Both url and token must be provided and not None."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            is_admin = str(payload.get("isAdmin", "")).lower() == "true"
            oil_analysis_id = payload.get("oilAnalysisId")
            schedule_id = payload.get("scheduleId")
            user_id = payload.get("userId")
            priority_id = payload.get("priorityId")
            severity_id = payload.get("severityId")
            report_type = payload.get("reportType")

            # Generate PDF & upload to S3
            logger.info(f"Generating PDF for url={url!r} and token={token!r}")
            report_url = generate_pdf_and_upload_to_s3(url, token)
            logger.info(f"PDF generated and uploaded: {report_url}")

            # Update Schedule Task report if scheduleId present and valid
            if schedule_id and str(schedule_id).lower() != "null":
                updated_count = ScheduleTask.objects.filter(id=schedule_id).update(report=report_url)
                if not updated_count:
                    logger.error(f"Invalid scheduleId: {schedule_id}")
                    return Response({"error": "Invalid scheduleId"}, status=status.HTTP_400_BAD_REQUEST)
                logger.info(f"ScheduleTask {schedule_id} updated with report URL.")

            # Else if admin, save new report
            elif is_admin:
                report = save_oil_analysis_report({
                    "oilAnalysisId": oil_analysis_id,
                    "severityId": severity_id,
                    "priorityId": priority_id,
                    "reportType": report_type,
                    "userId": user_id,
                    "reportUrl": report_url,
                })
                logger.info(f"OilAnalysisReport created with ID {report.id}")
                serializer = OilAnalysisReportSerializer(report)
                return Response(serializer.data, status=status.HTTP_200_OK)


            return Response(
                {"report_url": report_url},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.exception("Error in OilAnalysisReportView POST")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
