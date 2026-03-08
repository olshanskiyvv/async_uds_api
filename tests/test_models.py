from datetime import date

from async_uds_api.models import (
    BranchInfo,
    Customer,
    CustomerDetail,
    CustomersPage,
    GoodsCategoryType,
    GoodsDetailed,
    GoodsItemType,
    GoodsMeasurement,
    GoodsType,
    GoodsVariantType,
    GoodsVaryingItemType,
    ImageUploadUrl,
    ImageUploadUrlHeaders,
    Operation,
    Participant,
    TagModel,
    TagsPage,
)


class TestCustomerModel:
    def test_customer_model_creation(self):
        """Test Customer model creation."""
        customer = Customer(
            uid="abc123",
            displayName="John Doe",
            phone="+79001234567",
        )

        assert customer.uid == "abc123"
        assert customer.display_name == "John Doe"
        assert customer.phone == "+79001234567"

    def test_customer_model_with_aliases(self):
        """Test Customer model field aliases."""
        customer = Customer(
            displayName="Jane Smith",
            birthDate=date(1990, 1, 1),
        )

        assert customer.display_name == "Jane Smith"
        assert customer.birth_date == date(1990, 1, 1)

    def test_customer_with_participant(self):
        """Test Customer with nested Participant."""
        customer = Customer(
            uid="abc123",
            participant=Participant(
                uid="participant123",
                scores=100.0,
                cash=500.0,
            ),
        )

        assert customer.participant is not None
        assert customer.participant.scores == 100.0

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


class TestGoodsModels:
    def test_goods_category_type(self):
        """Test GoodsDetailed with CATEGORY type."""
        goods = GoodsDetailed(
            name="Test Category",
            data=GoodsCategoryType(type=GoodsType.CATEGORY),
        )

        assert goods.name == "Test Category"
        assert goods.data.type == GoodsType.CATEGORY

    def test_goods_item_type(self):
        """Test GoodsDetailed with ITEM type."""
        goods = GoodsDetailed(
            name="Test Item",
            data=GoodsItemType(
                type=GoodsType.ITEM,
                price=100.0,
                description="Test description",
            ),
        )

        assert goods.name == "Test Item"
        assert goods.data.type == GoodsType.ITEM
        if isinstance(goods.data, GoodsItemType):
            assert goods.data.price == 100.0
            assert goods.data.description == "Test description"

    def test_goods_varying_item_type(self):
        """Test GoodsDetailed with VARYING_ITEM type."""
        goods = GoodsDetailed(
            name="Test Varying Item",
            data=GoodsVaryingItemType(
                type=GoodsType.VARYING_ITEM,
                variants=[
                    GoodsVariantType(name="Red", price=100.0),
                    GoodsVariantType(name="Blue", price=120.0),
                ],
            ),
        )

        assert goods.name == "Test Varying Item"
        assert goods.data.type == GoodsType.VARYING_ITEM
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
        goods = GoodsDetailed(
            name="Test Item",
            data=GoodsItemType(type=GoodsType.ITEM),
            externalId="external-123",
        )

        assert goods.external_id == "external-123"


class TestImageModels:
    def test_image_upload_url_model(self):
        """Test ImageUploadUrl model."""
        upload_url = ImageUploadUrl(
            imageId="test-image-id",
            url="https://example.com/upload",
            method="PUT",
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
        upload_url = ImageUploadUrl(
            imageId="test-image-id",
            url="https://example.com/upload",
            method="PUT",
            headers=ImageUploadUrlHeaders(**{"Content-Type": ["image/jpeg"]}),
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
            action="PURCHASE",
            state="COMPLETED",
            points=50.0,
        )

        assert operation.id == 123
        assert operation.action == "PURCHASE"
        assert operation.state == "COMPLETED"

    def test_operation_with_branch(self):
        """Test Operation with BranchInfo."""
        operation = Operation(
            id=123,
            branch=BranchInfo(id=1, displayName="Main Branch"),
        )

        assert operation.branch is not None
        assert operation.branch.id == 1
        assert operation.branch.display_name == "Main Branch"


class TestBranchInfo:
    def test_branch_info_model(self):
        """Test BranchInfo model."""
        branch = BranchInfo(
            id=1,
            displayName="Main Branch",
        )

        assert branch.id == 1
        assert branch.display_name == "Main Branch"


class TestModelSerialization:
    def test_model_dump_by_alias(self):
        """Test model_dump with by_alias=True."""
        customer = Customer(
            uid="abc123",
            displayName="John Doe",
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
