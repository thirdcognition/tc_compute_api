from langchain_core.runnables import (
    ConfigurableField
)

configurable_fields = {
    "supa_client": ConfigurableField(
        id="supa_client",
        name="Supabase Client",
        description="The Supabase client instance."
    )
}