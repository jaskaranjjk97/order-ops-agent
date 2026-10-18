from app import config


def test_project_configuration():
    assert config.OPENAI_MODEL
    assert config.ORDERS_FILE.name == "orders.json"
    assert config.PRODUCTS_FILE.name == "products.json"
    assert config.ORDERS_FILE.parent.exists()
    assert config.PRODUCTS_FILE.exists()
