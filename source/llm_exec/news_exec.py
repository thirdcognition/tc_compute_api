from source.chains.init import get_chain


def rewrite_text(context) -> str:
    result = get_chain("text_formatter_simple").invoke({"context": context})

    return result  # Pass supabase
