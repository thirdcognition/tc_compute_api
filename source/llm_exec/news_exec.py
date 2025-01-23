from source.chains.init import get_chain


async def rewrite_text(context) -> str:
    result = await get_chain("text_formatter_simple").ainvoke({"context": context})

    return result  # Pass supabase


def rewrite_text_sync(context) -> str:
    result = get_chain("text_formatter_simple_sync").invoke({"context": context})

    return result  # Pass supabase
