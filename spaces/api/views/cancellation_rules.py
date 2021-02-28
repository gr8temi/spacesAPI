from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import UpdateAPIView

from ..models.cancellation_rules import CancellationRules
from ..serializers.cancellation_rules import CancellationRulesSerializer


class CancellationRulesView(APIView):
    def get(self, request):
        query = CancellationRules.objects.all()
        serialized_data = CancellationRulesSerializer(query, many=True)

        return Response(
            {
                "message": "Cancellation rules fetched successfully",
                "payload": serialized_data.data,
            },
            status=status.HTTP_200_OK,
        )


class SingleCancelationRuleView(APIView):
    def get(self, request, cancelation_rule_id):
        try:
            query = CancellationRules.objects.get(
                cancellation_rule_id=cancelation_rule_id
            )
        except Exception as err:
            return Response(
                {"message": "Cancellation rule not retrieved", "error": str(err)},
                status=status.HTTP_404_NOT_FOUND,
            )

        serialized_data = CancellationRulesSerializer(query)

        return Response(
            {
                "message": "Cancellation rule fetched successfully",
                "payload": serialized_data.data,
            }
        )
