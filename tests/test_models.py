from datetime import date

from async_uds_api.models import (
    Action,
    ActionState,
    BaseDiscountPolicy,
    BranchInfo,
    CashierInput,
    CompanySettings,
    CreateOperation,
    CreateOperationReceipt,
    Customer,
    CustomerDetail,
    CustomersPage,
    FindCustomerResponse,
    Gender,
    GoodsCategoryType,
    GoodsDetailed,
    GoodsItemType,
    GoodsMeasurement,
    GoodsOffer,
    GoodsOrderItem,
    GoodsOrderItemType,
    GoodsVariantType,
    GoodsVaryingItemType,
    ImageUploadUrl,
    ImageUploadUrlHeaders,
    MembershipTier,
    MembershipTierConditions,
    MembershipTierConditionsEffectiveInvitedCount,
    MembershipTierConditionsTotalCashSpent,
    Operation,
    OperationOrigin,
    Participant,
    PurchaseCalcExtras,
    PurchaseTokenAction,
    TagModel,
    TagsPage,
)


class TestCustomerModel:
    def test_customer_model_creation(self):
        """Test Customer model creation."""
        customer = Customer.model_validate(
            {
                "uid": "abc123",
                "displayName": "John Doe",
                "phone": "+79001234567",
            }
        )

        assert customer.uid == "abc123"
        assert customer.display_name == "John Doe"
        assert customer.phone == "+79001234567"

    def test_customer_model_with_aliases(self):
        """Test Customer model field aliases."""
        customer = Customer.model_validate(
            {
                "displayName": "Jane Smith",
                "birthDate": "1990-01-01",
            }
        )

        assert customer.display_name == "Jane Smith"
        assert customer.birth_date == date(1990, 1, 1)

    def test_customer_with_participant(self):
        """Test Customer with nested Participant."""
        customer = Customer.model_validate(
            {
                "uid": "abc123",
                "participant": {
                    "id": 123,
                    "points": 100.0,
                    "discountRate": 5.0,
                },
            }
        )

        assert customer.participant is not None
        assert customer.participant.points == 100.0
        assert customer.participant.discount_rate == 5.0

    def test_customer_detail_with_tags(self):
        """Test CustomerDetail with tags."""
        customer = CustomerDetail(
            uid="abc123",
            tags=[
                TagModel(id=1, name="VIP"),
                TagModel(id=2, name="Regular"),
            ],
        )

        assert len(customer.tags) == 2
        assert customer.tags[0].name == "VIP"

    def test_customers_page(self):
        """Test CustomersPage model."""
        page = CustomersPage(
            rows=[
                Customer(uid="abc123"),
                Customer(uid="def456"),
            ],
        )

        assert len(page.rows) == 2


class TestParticipantModel:
    def test_participant_model_creation(self):
        """Test Participant model creation."""
        participant = Participant.model_validate(
            {
                "id": 123,
                "points": 100.0,
                "discountRate": 5.0,
                "cashbackRate": 3.0,
            }
        )

        assert participant.id == 123
        assert participant.points == 100.0
        assert participant.discount_rate == 5.0
        assert participant.cashback_rate == 3.0

    def test_participant_with_membership_tier(self):
        """Test Participant with MembershipTier."""
        participant = Participant.model_validate(
            {
                "id": 123,
                "points": 100.0,
                "membershipTier": {
                    "name": "VIP",
                    "rate": 10.0,
                },
            }
        )

        assert participant.membership_tier is not None
        assert participant.membership_tier.name == "VIP"
        assert participant.membership_tier.rate == 10.0

    def test_participant_with_aliases(self):
        """Test Participant field aliases."""
        participant = Participant.model_validate(
            {
                "inviterId": 456,
                "cashSpent": 10000.0,
                "savedFunds": 500.0,
                "invitedCount": 10,
                "effectiveInvitedCount": 5,
                "operationsCount": 20,
                "fullRefundsCount": 1,
                "dateCreated": "2023-01-01T00:00:00Z",
                "lastTransactionTime": "2024-01-01T12:00:00Z",
                "pointsExpireIn": "2025-01-01T00:00:00Z",
            }
        )

        assert participant.inviter_id == 456
        assert participant.cash_spent == 10000.0
        assert participant.saved_funds == 500.0
        assert participant.invited_count == 10
        assert participant.effective_invited_count == 5
        assert participant.operations_count == 20
        assert participant.full_refunds_count == 1


class TestPurchaseTokenAction:
    def test_purchase_token_action_enum(self):
        """Test PurchaseTokenAction enum."""
        assert PurchaseTokenAction.PURCHASE == "PURCHASE"
        assert (
            PurchaseTokenAction.BONUS_ITEMS_PURCHASE == "BONUS_ITEMS_PURCHASE"
        )
        assert (
            PurchaseTokenAction.GOODS_ORDER_COMPLETE == "GOODS_ORDER_COMPLETE"
        )
        assert PurchaseTokenAction.CERTIFICATE == "CERTIFICATE"


class TestGender:
    def test_gender_enum(self):
        """Test Gender enum."""
        assert Gender.MALE == "MALE"
        assert Gender.FEMALE == "FEMALE"
        assert Gender.NOT_SPECIFIED == "NOT_SPECIFIED"

    def test_customer_with_gender(self):
        """Test Customer with Gender enum."""
        customer = Customer.model_validate(
            {
                "uid": "abc123",
                "gender": "MALE",
            }
        )

        assert customer.gender == Gender.MALE


class TestPurchaseCalcExtras:
    def test_purchase_calc_extras(self):
        """Test PurchaseCalcExtras model."""
        extras = PurchaseCalcExtras.model_validate(
            {
                "delivery": 100.0,
            }
        )

        assert extras.delivery == 100.0

    def test_purchase_calc_extras_empty(self):
        """Test PurchaseCalcExtras with no delivery."""
        extras = PurchaseCalcExtras()

        assert extras.delivery is None


class TestFindCustomerResponse:
    def test_find_customer_response(self):
        """Test FindCustomerResponse model."""
        response = FindCustomerResponse.model_validate(
            {
                "user": {
                    "uid": "abc123",
                    "displayName": "John Doe",
                    "tags": [],
                },
                "purchase": {
                    "maxPoints": 100.0,
                    "total": 1000.0,
                    "cash": 900.0,
                    "points": 100.0,
                },
                "code": "123456",
                "type": "PURCHASE",
            }
        )

        assert response.user.uid == "abc123"
        assert response.code == "123456"
        assert response.token_type == PurchaseTokenAction.PURCHASE

    def test_find_customer_response_without_code(self):
        """Test FindCustomerResponse without code and type."""
        response = FindCustomerResponse.model_validate(
            {
                "user": {
                    "uid": "abc123",
                    "displayName": "John Doe",
                    "tags": [],
                },
                "purchase": {
                    "maxPoints": 100.0,
                    "total": 1000.0,
                },
            }
        )

        assert response.code is None
        assert response.token_type is None


class TestGoodsModels:
    def test_goods_category_type(self):
        """Test GoodsDetailed with CATEGORY type."""
        goods = GoodsDetailed(
            name="Test Category",
            data=GoodsCategoryType(type="CATEGORY"),
        )

        assert goods.name == "Test Category"
        assert goods.data.type == "CATEGORY"

    def test_goods_item_type(self):
        """Test GoodsDetailed with ITEM type."""
        goods = GoodsDetailed(
            name="Test Item",
            data=GoodsItemType(
                type="ITEM",
                price=100.0,
                description="Test description",
            ),
        )

        assert goods.name == "Test Item"
        assert goods.data.type == "ITEM"
        if isinstance(goods.data, GoodsItemType):
            assert goods.data.price == 100.0
            assert goods.data.description == "Test description"

    def test_goods_varying_item_type(self):
        """Test GoodsDetailed with VARYING_ITEM type."""
        goods = GoodsDetailed(
            name="Test Varying Item",
            data=GoodsVaryingItemType(
                type="VARYING_ITEM",
                variants=[
                    GoodsVariantType(name="Red", price=100.0),
                    GoodsVariantType(name="Blue", price=120.0),
                ],
            ),
        )

        assert goods.name == "Test Varying Item"
        assert goods.data.type == "VARYING_ITEM"
        if isinstance(goods.data, GoodsVaryingItemType):
            assert goods.data.variants is not None
            assert len(goods.data.variants) == 2

    def test_goods_measurement_enum(self):
        """Test GoodsMeasurement enum."""
        assert GoodsMeasurement.PIECE == "PIECE"
        assert GoodsMeasurement.KILOGRAM == "KILOGRAM"
        assert GoodsMeasurement.LITRE == "LITRE"

    def test_goods_with_external_id(self):
        """Test GoodsDetailed with external ID."""
        goods = GoodsDetailed.model_validate(
            {
                "name": "Test Item",
                "data": {"type": "ITEM", "price": 100.0},
                "externalId": "external-123",
            }
        )

        assert goods.external_id == "external-123"

    def test_goods_item_type_photos_not_optional(self):
        """Test that photos is not optional in GoodsItemType."""
        goods = GoodsDetailed.model_validate(
            {
                "name": "Test Item",
                "data": {"type": "ITEM", "price": 100.0},
            }
        )

        if isinstance(goods.data, GoodsItemType):
            assert goods.data.photos == []

    def test_goods_varying_item_type_photos_not_optional(self):
        """Test that photos is not optional in GoodsVaryingItemType."""
        goods = GoodsDetailed.model_validate(
            {
                "name": "Test Varying Item",
                "data": {
                    "type": "VARYING_ITEM",
                    "variants": [{"name": "Red", "price": 100.0}],
                },
            }
        )

        if isinstance(goods.data, GoodsVaryingItemType):
            assert goods.data.photos == []

    def test_goods_offer_skip_loyalty_default(self):
        """Test that skip_loyalty default is False."""
        offer = GoodsOffer()
        assert offer.skip_loyalty is False

        offer_with_price = GoodsOffer.model_validate({"offerPrice": 50.0})
        assert offer_with_price.skip_loyalty is False
        assert offer_with_price.offer_price == 50.0

    def test_goods_image_urls_not_optional(self):
        """Test that image_urls is not optional."""
        goods = GoodsDetailed.model_validate(
            {
                "name": "Test Item",
                "data": {"type": "ITEM", "price": 100.0},
            }
        )

        assert goods.image_urls == []


class TestImageModels:
    def test_image_upload_url_model(self):
        """Test ImageUploadUrl model."""
        upload_url = ImageUploadUrl.model_validate(
            {
                "imageId": "test-image-id",
                "url": "https://example.com/upload",
                "method": "PUT",
            }
        )

        assert upload_url.image_id == "test-image-id"
        assert upload_url.url == "https://example.com/upload"
        assert upload_url.method == "PUT"

    def test_image_upload_url_headers(self):
        """Test ImageUploadUrlHeaders model."""
        headers = ImageUploadUrlHeaders(**{"Content-Type": ["image/jpeg"]})

        assert headers.content_type == ["image/jpeg"]

    def test_image_upload_url_with_headers(self):
        """Test ImageUploadUrl with headers."""
        upload_url = ImageUploadUrl.model_validate(
            {
                "imageId": "test-image-id",
                "url": "https://example.com/upload",
                "method": "PUT",
                "headers": {"Content-Type": ["image/jpeg"]},
            }
        )

        assert upload_url.headers is not None
        assert upload_url.headers.content_type == ["image/jpeg"]


class TestTagsModels:
    def test_tag_model(self):
        """Test TagModel."""
        tag = TagModel(id=1, name="VIP")

        assert tag.id == 1
        assert tag.name == "VIP"

    def test_tags_page(self):
        """Test TagsPage model."""
        page = TagsPage(
            rows=[
                TagModel(id=1, name="VIP"),
                TagModel(id=2, name="Regular"),
            ],
            total=2,
        )

        assert len(page.rows) == 2
        assert page.total == 2


class TestOperationModels:
    def test_operation_model(self):
        """Test Operation model."""
        operation = Operation(
            id=123,
            action=Action.PURCHASE,
            state=ActionState.NORMAL,
            points=50.0,
            total=1000.0,
            cash=950.0,
        )

        assert operation.id == 123
        assert operation.action == Action.PURCHASE
        assert operation.state == ActionState.NORMAL
        assert operation.total == 1000.0
        assert operation.cash == 950.0

    def test_operation_with_branch(self):
        """Test Operation with BranchInfo."""
        operation = Operation(
            id=123,
            action=Action.PURCHASE,
            branch=BranchInfo(id=1, displayName="Main Branch"),
        )

        assert operation.branch is not None
        assert operation.branch.id == 1
        assert operation.branch.display_name == "Main Branch"

    def test_operation_with_origin(self):
        """Test Operation with origin."""
        operation = Operation(
            id=123,
            action=Action.PURCHASE,
            state=ActionState.REVERSAL,
            origin=OperationOrigin(id=100),
        )

        assert operation.origin is not None
        assert operation.origin.id == 100

    def test_cashier_input(self):
        """Test CashierInput model."""
        cashier = CashierInput.model_validate(
            {
                "externalId": "ext-123",
                "name": "John",
            }
        )

        assert cashier.external_id == "ext-123"
        assert cashier.name == "John"

    def test_create_operation_with_cashier(self):
        """Test CreateOperation with CashierInput."""
        operation = CreateOperation(
            receipt=CreateOperationReceipt(
                total=1000.0,
                cash=900.0,
                points=100.0,
            ),
            cashier=CashierInput.model_validate(
                {
                    "externalId": "ext-123",
                    "name": "John",
                }
            ),
        )

        assert operation.cashier is not None
        assert operation.cashier.external_id == "ext-123"


class TestActionEnums:
    def test_action_enum(self):
        """Test Action enum."""
        assert Action.PURCHASE == "PURCHASE"
        assert Action.GOODS_PURCHASE == "GOODS_PURCHASE"

    def test_action_enum_unknown_value(self):
        """Unknown action values fall back to UNKNOWN instead of raising."""
        assert Action("SOMETHING_NEW") is Action.UNKNOWN

    def test_operation_parses_goods_purchase(self):
        """Operation parses transactions created by goods order completion."""
        operation = Operation.model_validate(
            {
                "id": 1454045580,
                "action": "GOODS_PURCHASE",
                "state": "NORMAL",
                "total": 3000.0,
            }
        )

        assert operation.action == Action.GOODS_PURCHASE

    def test_operation_parses_undocumented_action(self):
        """Undocumented action values do not break Operation parsing."""
        operation = Operation.model_validate(
            {"id": 1, "action": "FUTURE_ACTION"}
        )

        assert operation.action is Action.UNKNOWN

    def test_action_state_enum(self):
        """Test ActionState enum."""
        assert ActionState.NORMAL == "NORMAL"
        assert ActionState.CANCELED == "CANCELED"
        assert ActionState.REVERSAL == "REVERSAL"


class TestBranchInfo:
    def test_branch_info_model(self):
        """Test BranchInfo model."""
        branch = BranchInfo.model_validate(
            {
                "id": 1,
                "displayName": "Main Branch",
            }
        )

        assert branch.id == 1
        assert branch.display_name == "Main Branch"


class TestModelSerialization:
    def test_model_dump_by_alias(self):
        """Test model_dump with by_alias=True."""
        customer = Customer.model_validate(
            {
                "uid": "abc123",
                "displayName": "John Doe",
            }
        )

        data = customer.model_dump(by_alias=True, exclude_none=True)

        assert "displayName" in data
        assert data["displayName"] == "John Doe"

    def test_model_validation_from_dict(self):
        """Test model validation from dict with aliases."""
        data = {
            "uid": "abc123",
            "displayName": "John Doe",
            "phone": "+79001234567",
        }

        customer = Customer.model_validate(data)

        assert customer.uid == "abc123"
        assert customer.display_name == "John Doe"


class TestBaseDiscountPolicy:
    def test_base_discount_policy_enum(self):
        """Test BaseDiscountPolicy enum."""
        assert BaseDiscountPolicy.APPLY_DISCOUNT == "APPLY_DISCOUNT"
        assert BaseDiscountPolicy.CHARGE_SCORES == "CHARGE_SCORES"


class TestMembershipTierConditions:
    def test_total_cash_spent_with_optional_target(self):
        """Test MembershipTierConditionsTotalCashSpent with optional target."""
        condition = MembershipTierConditionsTotalCashSpent()
        assert condition.target is None

        condition_with_target = MembershipTierConditionsTotalCashSpent(
            target=10000.0
        )
        assert condition_with_target.target == 10000.0

    def test_effective_invited_count_with_optional_target(self):
        """Test MembershipTierConditionsEffectiveInvitedCount optional."""
        condition = MembershipTierConditionsEffectiveInvitedCount()
        assert condition.target is None

        condition_with_target = MembershipTierConditionsEffectiveInvitedCount(
            target=5
        )
        assert condition_with_target.target == 5

    def test_membership_tier_conditions_with_aliases(self):
        """Test MembershipTierConditions with aliases."""
        conditions = MembershipTierConditions.model_validate(
            {
                "totalCashSpent": {"target": 10000.0},
                "effectiveInvitedCount": {"target": 5},
            }
        )

        assert conditions.total_cash_spent is not None
        assert conditions.total_cash_spent.target == 10000.0
        assert conditions.effective_invited_count is not None
        assert conditions.effective_invited_count.target == 5


class TestMembershipTier:
    def test_membership_tier_minimal(self):
        """Test MembershipTier with minimal required fields."""
        tier = MembershipTier(name="Base", rate=5.0)

        assert tier.name == "Base"
        assert tier.rate == 5.0
        assert tier.uid is None
        assert tier.max_scores_discount is None
        assert tier.conditions is None

    def test_membership_tier_with_all_fields(self):
        """Test MembershipTier with all fields."""
        tier = MembershipTier.model_validate(
            {
                "uid": "vip-tier",
                "name": "VIP",
                "rate": 10.0,
                "maxScoresDiscount": 50.0,
                "conditions": {
                    "totalCashSpent": {"target": 50000.0},
                    "effectiveInvitedCount": {"target": 10},
                },
            }
        )

        assert tier.uid == "vip-tier"
        assert tier.name == "VIP"
        assert tier.rate == 10.0
        assert tier.max_scores_discount == 50.0
        assert tier.conditions is not None
        assert tier.conditions.total_cash_spent is not None
        assert tier.conditions.total_cash_spent.target == 50000.0


class TestCompanySettings:
    def test_company_settings_with_enum(self):
        """Test CompanySettings with BaseDiscountPolicy enum."""
        settings = CompanySettings.model_validate(
            {
                "id": 123456,
                "name": "Test Company",
                "promoCode": "TEST",
                "currency": "RUB",
                "baseDiscountPolicy": "CHARGE_SCORES",
                "purchaseByPhone": True,
                "usePointsByPhone": True,
                "writeInvoice": False,
                "slug": "test-company",
            }
        )

        assert settings.id == 123456
        assert (
            settings.base_discount_policy == BaseDiscountPolicy.CHARGE_SCORES
        )

    def test_company_settings_apply_discount(self):
        """Test CompanySettings with APPLY_DISCOUNT policy."""
        settings = CompanySettings.model_validate(
            {
                "id": 123456,
                "name": "Test Company",
                "promoCode": "TEST",
                "baseDiscountPolicy": "APPLY_DISCOUNT",
                "purchaseByPhone": False,
                "usePointsByPhone": False,
                "writeInvoice": True,
                "slug": "test-company",
            }
        )

        assert (
            settings.base_discount_policy == BaseDiscountPolicy.APPLY_DISCOUNT
        )

    def test_company_settings_with_loyalty_program(self):
        """Test CompanySettings with LoyaltyProgramSettings."""
        settings = CompanySettings.model_validate(
            {
                "id": 123456,
                "name": "Test Company",
                "promoCode": "TEST",
                "baseDiscountPolicy": "CHARGE_SCORES",
                "purchaseByPhone": True,
                "usePointsByPhone": True,
                "writeInvoice": False,
                "slug": "test-company",
                "loyaltyProgramSettings": {
                    "baseMembershipTier": {"name": "Base", "rate": 5.0},
                    "membershipTiers": [],
                    "referralCashbackRates": [0.05, 0.03, 0.01],
                },
            }
        )

        assert settings.loyalty_program_settings is not None
        assert (
            settings.loyalty_program_settings.base_membership_tier.name
            == "Base"
        )


class TestGoodsOrderItemType:
    def test_goods_order_item_type_enum(self):
        """Test GoodsOrderItemType enum."""
        assert GoodsOrderItemType.ITEM == "ITEM"
        assert GoodsOrderItemType.VARYING_ITEM == "VARYING_ITEM"


class TestGoodsOrderItem:
    def test_goods_order_item_required_fields(self):
        """Test GoodsOrderItem with required fields."""
        item = GoodsOrderItem.model_validate(
            {
                "name": "Test Item",
                "type": "ITEM",
                "qty": 2,
                "price": 100.0,
            }
        )

        assert item.name == "Test Item"
        assert item.type == GoodsOrderItemType.ITEM
        assert item.qty == 2
        assert item.price == 100.0

    def test_goods_order_item_with_variant(self):
        """Test GoodsOrderItem with variant."""
        item = GoodsOrderItem.model_validate(
            {
                "name": "Test Item",
                "type": "VARYING_ITEM",
                "variantName": "Red",
                "qty": 1,
                "price": 150.0,
            }
        )

        assert item.type == GoodsOrderItemType.VARYING_ITEM
        assert item.variant_name == "Red"

    def test_goods_order_item_skip_loyalty_default(self):
        """Test that skip_loyalty default is False."""
        item = GoodsOrderItem.model_validate(
            {
                "name": "Test Item",
                "type": "ITEM",
                "qty": 1,
                "price": 100.0,
            }
        )

        assert item.skip_loyalty is False
