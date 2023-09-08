from aws_cdk import aws_iam as iam
from aws_cdk import aws_location as location
from constructs import Construct
from common.common_stack import CommonStack
from common.platforms import Platform
from common.region_aware_stack import RegionAwareStack


class LocationStack(RegionAwareStack):
    def __init__(
        self, scope: Construct, id: str, common_stack: CommonStack, **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)

        self._supported_in_region = self.is_service_supported_in_region()

        # Map #

        # Reusing the get_bucket_name function to get a unique name for the map
        mapName = self.get_bucket_name("map")
        self._parameters_to_save["map_name"] = mapName

        location.CfnMap(
            self,
            "integ_test_location_map",
            configuration=location.CfnMap.MapConfigurationProperty(
                style="VectorEsriStreets"
            ),
            map_name=mapName,
            pricing_plan="RequestBasedUsage",
        )

        location_map_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "geo:GetMapStyleDescriptor",
                "geo:GetMapGlyphs",
                "geo:GetMapSprites",
                "geo:GetMapTile",
            ],
            resources=[f"arn:aws:geo:{self.region}:{self.account}:map/*"],
        )
        common_stack.add_to_common_role_policies(
            self, policy_to_add=location_map_policy
        )

        # Search #

        # Reusing the get_bucket_name function to get a unique name for the place index.
        placeIndexName = self.get_bucket_name("placeIndex")
        self._parameters_to_save["place_index"] = placeIndexName

        location.CfnPlaceIndex(
            self,
            "integ_test_location_placeIndex",
            data_source="Esri",
            index_name=placeIndexName,
            pricing_plan="RequestBasedUsage",
        )

        location_placeIndex_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["geo:SearchPlaceIndexForPosition", "geo:SearchPlaceIndexForText"],
            resources=[f"arn:aws:geo:{self.region}:{self.account}:place-index/*"],
        )
        common_stack.add_to_common_role_policies(
            self, policy_to_add=location_placeIndex_policy
        )

        self.save_parameters_in_parameter_store(platform=Platform.IOS)
