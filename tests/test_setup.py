from app import config
from app.llm import get_llm


def main():
    print("Config Loaded")
    print(f"OPENAI_MODEL: {config.OPENAI_MODEL}")
    print(f"ORDERS_FILE: {config.ORDERS_FILE}")
    print(f"PRODUCTS_FILE: {config.PRODUCTS_FILE}")

    llm = get_llm(temperature=0.0)
    print(f"LLM_Intialized: {llm.model_name}")
    print("Setuo ok")


if __name__ == "__main__":
    main()
